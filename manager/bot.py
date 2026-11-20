# OWNER Manager - control bot for OWNER Assistant.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).

import asyncio
import collections
import json
import os
import re
import signal
import sys
import time

from telethon import Button, TelegramClient, errors, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetParticipantRequest

from . import emoji, fun


# ----------------------------------------------------------------- config

DATA_DIR = os.environ.get("OA_DATA_DIR", "data")
STORE_FILE = os.path.join(DATA_DIR, "manager.json")
BOT_SESSION = os.path.join(DATA_DIR, "manager_bot")


def _int(name, default=0):
    try:
        return int(str(os.environ.get(name) or default).strip())
    except ValueError:
        return default


TOKEN = (os.environ.get("MANAGER_BOT_TOKEN") or "").strip()
OWNER_ID = _int("OWNER_ID")
API_ID = _int("API_ID", 6) or 6
API_HASH = (os.environ.get("API_HASH") or "").strip() or "eb06d4abfb49dc3eeb1aeb98ae0f581e"
DEVICE = {"device_model": "OWNER Assistant", "system_version": "Manager", "app_version": "1.0"}
USERBOT_CMD = [sys.executable, "-m", "pyUltroid"]

LOGIN_TIMEOUT = 600  # a login must finish within 10 minutes
CRASH_WINDOW, MAX_CRASHES = 600, 5  # stop auto-restart after 5 crashes in 10 min
VAR_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,40}$")
BLOCKED_VARS = {"MANAGER_BOT_TOKEN", "OWNER_ID", "SESSION", "OA_DATA_DIR"}
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def mask(value):
    value = str(value)
    if len(value) <= 6:
        return "•" * len(value)
    return value[:3] + "•" * 6 + value[-2:]


def log(*a):
    print("[manager]", *a, flush=True)


# ----------------------------------------------------------------- storage


class Store:
    """Small JSON file in the data volume: saved session, account, extra vars."""

    def __init__(self, path=STORE_FILE):
        self.path = path
        # use_env_session: the SESSION from .env counts until the owner logs out here
        self.data = {"session": None, "account": None, "env": {}, "use_env_session": True}
        try:
            with open(path) as f:
                self.data.update(json.load(f))
        except FileNotFoundError:
            pass
        except Exception as er:
            log("could not read store:", er)

    def save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as f:
            json.dump(self.data, f)
        os.replace(tmp, self.path)

    @property
    def session(self):
        if self.data.get("session"):
            return self.data["session"]
        if self.data.get("use_env_session", True):
            return (os.environ.get("SESSION") or "").strip() or None
        return None

    def set_session(self, session, account):
        self.data.update(session=session, account=account, use_env_session=False)
        self.save()

    def clear_session(self):
        self.data.update(session=None, account=None, use_env_session=False)
        self.save()

    @property
    def env(self):
        return dict(self.data.get("env") or {})


def new_client(session=""):
    """User client for login / checks (replaced in tests)."""
    return TelegramClient(StringSession(session), API_ID, API_HASH, **DEVICE)


async def check_session(session):
    """Return (ok, account dict). Never run while the userbot uses the session."""
    if not session:
        return False, None
    client = new_client(session)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return False, None
        me = await client.get_me()
        return True, {"id": me.id, "name": " ".join(filter(None, [me.first_name, me.last_name])) or str(me.id),
                      "username": me.username}
    except (errors.AuthKeyUnregisteredError, errors.SessionRevokedError,
            errors.SessionExpiredError, errors.UserDeactivatedError, ValueError):
        return False, None
    finally:
        await client.disconnect()


# ----------------------------------------------------------------- userbot process


class Runner:
    def __init__(self, on_exit):
        self.proc = None
        self.lines = collections.deque(maxlen=500)
        self.started = None
        self.want = False
        self.crashes = collections.deque()
        self.on_exit = on_exit

    @property
    def running(self):
        return self.proc is not None and self.proc.returncode is None

    async def start(self, session, extra_env):
        if self.running:
            return
        env = os.environ.copy()
        env.update({k: str(v) for k, v in extra_env.items()})
        env["SESSION"] = session
        env.pop("MANAGER_BOT_TOKEN", None)
        self.want = True
        self.started = time.time()
        self.proc = await asyncio.create_subprocess_exec(
            *USERBOT_CMD, env=env, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT, limit=2**20,
        )
        log("userbot started, pid", self.proc.pid)
        asyncio.create_task(self._pump(self.proc))

    async def _pump(self, proc):
        while True:
            try:
                line = await proc.stdout.readline()
            except (ValueError, asyncio.LimitOverrunError):
                continue
            if not line:
                break
            text = ANSI.sub("", line.decode(errors="replace").rstrip())
            print(text, flush=True)
            self.lines.append(text)
        code = await proc.wait()
        log("userbot exited with code", code)
        if proc is self.proc:
            self.proc = None
            if self.want:
                await self.on_exit(code)

    async def stop(self):
        self.want = False
        proc = self.proc
        if not proc or proc.returncode is not None:
            return
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), 20)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()

    def crash_too_often(self):
        now = time.time()
        self.crashes.append(now)
        while self.crashes and now - self.crashes[0] > CRASH_WINDOW:
            self.crashes.popleft()
        return len(self.crashes) >= MAX_CRASHES


# ----------------------------------------------------------------- the bot

FORCE_JOIN = (os.environ.get("FORCE_JOIN") or "@VillanCommunity").strip()
if FORCE_JOIN.lower() in ("off", "false", "no", "0", "none"):
    FORCE_JOIN = ""
FORCE_JOIN_ID = _int("FORCE_JOIN_ID", -1004443904846)
JOIN_URL = f"https://t.me/{FORCE_JOIN.lstrip('@')}" if FORCE_JOIN.startswith("@") else FORCE_JOIN

HELP = """❓ **Help**

🔐 **Login** – connect your Telegram account
🚪 **Logout** – remove it, userbot stops
▶️ **Run** · ⏹ **Stop** · 🔄 **Restart** – control the userbot
📜 **Logs** – see errors
⚙️ **Settings** – extra vars

Commands also work: /login /logout /status /restart /logs /cancel
`/setvar KEY value` · `/delvar KEY`

Your messages here are deleted automatically to keep the chat clean."""


def fmt_uptime(sec):
    sec = int(sec)
    d, sec = divmod(sec, 86400)
    h, sec = divmod(sec, 3600)
    m, s = divmod(sec, 60)
    return " ".join(f"{v}{u}" for v, u in ((d, "d"), (h, "h"), (m, "m"), (s, "s")) if v) or "0s"


class Manager:
    def __init__(self, bot, store=None, runner=None):
        self.bot = bot
        self.store = store or Store()
        self.runner = runner or Runner(self.userbot_exited)
        self.login = None  # {"step", "client", "phone", "hash", "tries", "since"}
        self.logged_out = False
        self.panels = {int(k): v for k, v in (self.store.data.get("panels") or {}).items()}
        self.kb_msg = None  # "share phone" keyboard message during login
        self.join_cache = {}
        self.playing = {}  # chat -> an animation is running
        self.join_problem = None
        # Premium (custom) emoji on BUTTON ICONS only - message text keeps
        # plain emojis (premium everywhere looked bad). Turns itself off if
        # Telegram refuses custom emoji for this bot.
        self.emoji_ok = bool(self.store.data.get("emoji_ok", True))
        self.emap = emoji.load_map()

    def btn(self, em, label, data=None, url=None):
        icon = emoji.lookup(self.emap, em) if self.emoji_ok else None
        text = label if icon else f"{em} {label}"
        if url:
            return Button.url(text, url, icon=icon)
        return Button.inline(text, data.encode(), icon=icon)

    # ------------------------------------------------------------ the one panel
    async def show(self, chat, text, buttons=None, event=None, _retry=True):
        """Edit the live panel (button press) or replace it (typed command / alert)."""
        try:
            if isinstance(event, events.CallbackQuery.Event):
                try:
                    await event.edit(text, buttons=buttons, link_preview=False)
                    self.panels[chat] = event.message_id
                    self._save_panels()
                    return
                except errors.MessageNotModifiedError:
                    return
                except errors.MessageIdInvalidError:
                    pass
            old = self.panels.get(chat)
            msg = await self.bot.send_message(chat, text, buttons=buttons, link_preview=False)
            self.panels[chat] = msg.id
            self._save_panels()
            if old and old != msg.id:
                await self.drop(chat, old)
        except errors.RPCError:
            if _retry and self.emoji_ok and self.emap:
                # Telegram won't let this bot use custom emoji - go plain.
                self.emoji_ok = False
                self.store.data["emoji_ok"] = False
                self.store.save()
                return await self.show(chat, text, buttons, event, _retry=False)
            raise

    async def drop(self, chat, *ids):
        ids = [i for i in ids if i]
        if ids:
            try:
                await self.bot.delete_messages(chat, ids)
            except Exception:
                pass

    async def clean(self, event):
        """Delete the owner's typed message (keeps the chat tidy)."""
        try:
            await event.delete()
        except Exception:
            pass

    async def tell(self, text, extra=None):
        """Alert the owner: replaces the panel so it is the newest message."""
        if not OWNER_ID:
            return
        try:
            await self.show(OWNER_ID, text + "\n\n" + self.status_text(), self.menu_buttons())
        except Exception as er:  # owner never pressed /start, or blocked the bot
            log("could not message owner:", er)

    # ------------------------------------------------------------ views
    def account_text(self):
        acc = self.store.data.get("account")
        if not acc:
            return "—"
        user = f" (@{acc['username']})" if acc.get("username") else ""
        return f"{acc['name']}{user}"

    def state(self):
        if self.runner.running:
            return "running"
        if self.logged_out or not self.store.session:
            return "logged_out"
        return "stopped"

    def status_text(self):
        st = self.state()
        line = {"running": "🟢 Running", "stopped": "⚪ Stopped", "logged_out": "🔴 Not logged in"}[st]
        lines = [f"**Status:** {line}", f"👤 {self.account_text()}"]
        if st == "running" and self.runner.started:
            lines.append(f"⏳ {fmt_uptime(time.time() - self.runner.started)}")
        lines.append("")
        lines.append("✅ **FUN MODE: ON** — friends can use the bot"
                     if self.fun_public() else
                     "⛔ **FUN MODE: OFF** — only you can use the bot")
        if self.join_problem:
            lines.append(f"⚠️ {self.join_problem}")
        return "\n".join(lines)

    async def send_panel(self, chat, text, buttons=None, event=None):
        """show() for guests / the join gate - guest chats are not persisted."""
        if chat == OWNER_ID:
            return await self.show(chat, text, buttons, event)
        try:
            if isinstance(event, events.CallbackQuery.Event):
                try:
                    return await event.edit(text, buttons=buttons, link_preview=False)
                except errors.MessageNotModifiedError:
                    return
                except errors.MessageIdInvalidError:
                    pass
            old = self.panels.get(chat)
            msg = await self.bot.send_message(chat, text, buttons=buttons, link_preview=False)
            self.panels[chat] = msg.id
            if old and old != msg.id:
                await self.drop(chat, old)
        except errors.RPCError as er:
            log("send_panel:", er)

    def _save_panels(self):
        self.store.data["panels"] = {str(k): v for k, v in self.panels.items()}
        self.store.save()

    # ---- Public / Private switch for the fun animations (shared with userbot)
    def _fun_file(self):
        return os.path.join(DATA_DIR, "fun_mode.json")

    def fun_public(self):
        """Fun mode. Default is ON - the owner turns it off when they want."""
        try:
            with open(self._fun_file(), encoding="utf-8") as f:
                return bool(json.load(f).get("public", True))
        except FileNotFoundError:
            return True
        except Exception:
            return True

    def set_fun_public(self, value):
        try:
            with open(self._fun_file(), "w", encoding="utf-8") as f:
                json.dump({"public": bool(value)}, f)
        except Exception as er:
            log("fun mode:", er)

    def menu_buttons(self):
        st = self.state()
        rows = []
        if st == "logged_out":
            rows.append([self.btn("🔐", "Login", "m:login")])
        elif st == "running":
            rows.append([self.btn("🔄", "Restart", "m:restart"), self.btn("⏹", "Stop", "m:stop")])
        else:
            rows.append([self.btn("▶️", "Run", "m:run")])
        rows.append([self.btn("📜", "Logs", "m:logs"), self.btn("⚙️", "Settings", "m:settings")])
        if self.fun_public():
            rows.append([self.btn("⛔", "Turn fun mode OFF (only me)", "m:fun_off")])
        else:
            rows.append([self.btn("✅", "Turn fun mode ON (friends)", "m:fun_on")])
        if st != "logged_out":
            rows.append([self.btn("🔐", "Login again", "m:login"), self.btn("🚪", "Logout", "m:logout")])
        rows.append([self.btn("🔃", "Refresh", "m:menu")])
        return rows

    def back(self, to="m:menu"):
        return self.btn("◀️", "Back", to)

    async def view_menu(self, chat, event=None, note=""):
        head = "👑 **OWNER Manager**\n\n"
        await self.show(chat, head + (note + "\n\n" if note else "") + self.status_text(),
                        self.menu_buttons(), event)

    async def view_logs(self, chat, event=None):
        lines = list(self.runner.lines)
        body = "\n".join(lines[-25:])[-3300:] if lines else "No logs yet."
        await self.show(chat, f"📜 **Logs** (last lines)\n```\n{body}\n```",
                        [[self.btn("🔃", "Refresh", "m:logs"), self.btn("📄", "Full log", "m:logfile")],
                         [self.back()]], event)

    async def send_logfile(self, chat):
        lines = list(self.runner.lines)
        if not lines:
            return
        path = os.path.join(DATA_DIR, "userbot-logs.txt")
        with open(path, "w") as f:
            f.write("\n".join(lines))
        try:
            await self.bot.send_file(chat, path, caption="📄 Userbot log",
                                     buttons=[[self.btn("🗑", "Close", "m:close")]])
        finally:
            os.remove(path)

    async def view_settings(self, chat, event=None):
        await self.show(chat, "⚙️ **Settings**",
                        [[self.btn("🧩", "Extra vars", "m:vars"), self.btn("❓", "Help", "m:help")],
                         [self.back()]], event)

    async def view_vars(self, chat, event=None, note=""):
        env = self.store.env
        body = "\n".join(f"`{k}` = `{mask(v)}`" for k, v in sorted(env.items())) or "None yet."
        text = (f"🧩 **Extra vars** (used after Restart)\n\n{body}\n\n"
                "**Add:** `/setvar KEY value`\n**Remove:** `/delvar KEY`")
        if note:
            text = note + "\n\n" + text
        await self.show(chat, text, [[self.back("m:settings")]], event)

    # ------------------------------------------------------------ userbot control
    async def start_userbot(self, check=True):
        session = self.store.session
        if not session:
            self.logged_out = True
            return False, "Not logged in."
        if self.runner.running:
            return True, "Already running."
        if check:
            ok, acc = await check_session(session)
            if not ok:
                self.logged_out = True
                return False, "Session is logged out / expired."
            if acc and acc != self.store.data.get("account"):
                self.store.data["account"] = acc
                self.store.save()
        self.logged_out = False
        await self.runner.start(session, self.store.env)
        return True, "Started."

    async def userbot_exited(self, code):
        tail = "\n".join(list(self.runner.lines)[-10:])[-1200:]
        if code == 0:
            return await self.tell("⏹ Userbot stopped itself (`.shutdown`).")
        ok, _ = await check_session(self.store.session)
        if not ok:
            self.logged_out = True
            return await self.tell("🚪 **Your account got logged out.** Tap **Login** to connect again.")
        if self.runner.crash_too_often():
            return await self.tell(f"❌ Userbot crashed {MAX_CRASHES} times in 10 min, auto-restart is off.\n"
                                   f"```\n{tail}\n```")
        await self.tell(f"⚠️ Userbot crashed, restarting in 10s…\n```\n{tail}\n```")
        await asyncio.sleep(10)
        if not self.runner.running and not self.logged_out:
            await self.start_userbot(check=False)

    async def do_logout(self):
        session = self.store.session
        await self.runner.stop()
        self.logged_out = True
        if not session:
            return "🚪 Already logged out."
        client = new_client(session)
        try:
            await client.connect()
            if await client.is_user_authorized():
                await client.log_out()
        except Exception as er:
            log("logout:", er)
        finally:
            await client.disconnect()
        self.store.clear_session()
        return "🚪 **Logged out.** The session is removed from Telegram."

    # ------------------------------------------------------------ access
    async def is_member(self, uid):
        if not FORCE_JOIN:
            return True
        hit = self.join_cache.get(uid)
        if hit and time.time() - hit < 300:
            return True
        for channel in (FORCE_JOIN, FORCE_JOIN_ID):
            try:
                await self.bot(GetParticipantRequest(channel, uid))
                self.join_problem = None
                self.join_cache[uid] = time.time()
                return True
            except errors.UserNotParticipantError:
                return False
            except (errors.ChatAdminRequiredError, errors.ChannelPrivateError):
                self.join_problem = f"Make this bot an admin in {FORCE_JOIN} so it can check members."
                return True  # never lock the owner out of their own bot
            except Exception as er:
                log("force join check:", channel, er)
        self.join_problem = f"Can't find {FORCE_JOIN}. Check FORCE_JOIN in .env."
        return True

    async def allowed(self, event):
        cb = isinstance(event, events.CallbackQuery.Event)
        if not OWNER_ID:
            text = f"⚙️ Setup: put this in your `.env` and restart:\n\n`OWNER_ID={event.sender_id}`"
            return await (event.answer("OWNER_ID not set", alert=True) if cb else event.reply(text)) and False
        if event.sender_id != OWNER_ID:
            # Guests: the fun animations only, and only while fun mode is ON.
            # They never reach login / logout / settings / logs.
            if self.fun_public() and (cb or event.is_private):
                if not await self.is_member(event.sender_id):
                    await self.join_gate(event, cb)
                    return False
                await self.guest(event, cb)
                return False
            if cb:
                await event.answer("🔒 This bot is private right now.", alert=True)
            elif event.is_private:
                await event.reply("🔒 This bot is private right now.")
            return False
        if not await self.is_member(event.sender_id):
            await self.join_gate(event, cb)
            return False
        return True

    async def join_gate(self, event, cb):
        if not cb:
            await self.clean(event)
        elif event.data == b"m:joined":
            await event.answer("You haven't joined yet.", alert=True)
        await self.send_panel(event.chat_id,
                              f"📢 **Join {FORCE_JOIN} to use this bot.**\n\n"
                              "Join, then tap **I\'ve joined**.",
                              [[self.btn("📢", "Join channel", url=JOIN_URL)],
                               [self.btn("✅", "I\'ve joined", "m:joined")]],
                              event if cb else None)

    # ---------------------------------------------------------------- guests
    async def guest(self, event, cb):
        """Everything a non-owner can do: play an animation. Nothing else."""
        chat = event.chat_id
        data = event.data.decode() if cb else ""
        kind = data[6:] if data.startswith("m:fun_") and data[6:] in fun.MENU else ""
        if kind:
            await event.answer("💞 Playing…")
            return await self.play(chat, kind, event)
        if not cb:
            await self.clean(event)
        rows, row = [], []
        for key, (em, label) in fun.MENU.items():
            row.append(self.btn(em, label, f"m:fun_{key}"))
            if len(row) == 3:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        name = (getattr(event, "sender", None) and getattr(event.sender, "first_name", None)) or "you"
        await self.send_panel(chat,
                              f"🎉 **Fun Zone**\n\nHey {name}! {len(fun.MENU)} things to play with 👇",
                              rows, event if cb else None)

    async def play(self, chat, kind, event):
        """Send one message and edit it frame by frame (bot-side, flood safe)."""
        if self.playing.get(chat):
            return
        self.playing[chat] = True
        try:
            who = (getattr(event, "sender", None) and getattr(event.sender, "first_name", None)) or "Someone"
            frames = fun.build(kind, name=who, who=who, seed=int(time.time() * 1000) % 10**9)
            if not frames:
                return
            msg = await self.bot.send_message(chat, frames[0], link_preview=False)
            for frame in frames[1:]:
                await asyncio.sleep(1.2)
                try:
                    await msg.edit(frame, link_preview=False)
                except errors.MessageNotModifiedError:
                    continue
                except errors.FloodWaitError as fw:
                    await asyncio.sleep(min(fw.seconds, 30) + 1)
                except errors.RPCError:
                    break
            try:
                await msg.edit(buttons=[[self.btn("💞", "Play again", "m:fun_menu")]])
            except Exception:
                pass
        finally:
            self.playing[chat] = False

    # ------------------------------------------------------------ login
    async def cancel_login(self):
        if self.kb_msg:
            await self.remove_keyboard(OWNER_ID)
        if self.login:
            client = self.login.get("client")
            self.login = None
            if client:
                try:
                    await client.disconnect()
                except Exception:
                    pass

    async def remove_keyboard(self, chat):
        old, self.kb_msg = self.kb_msg, None
        try:
            tmp = await self.bot.send_message(chat, "·", buttons=Button.clear())
            await self.drop(chat, old, tmp.id)
        except Exception:
            await self.drop(chat, old)

    async def begin_login(self, chat, event=None):
        await self.cancel_login()
        self.login = {"step": "phone", "client": None, "tries": 0, "since": time.time()}
        warn = f"\n\n⚠️ Now running as {self.account_text()} — this will replace it." if self.runner.running else ""
        await self.show(chat, "🔐 **Login · step 1/3**\n\nSend your phone number with country code,\n"
                        "like `+919876543210` — or tap **📱 Share my phone** below." + warn,
                        [[self.btn("✖️", "Cancel", "m:cancel")]], event)
        try:
            msg = await self.bot.send_message(
                chat, "👇", buttons=[[Button.request_phone("📱 Share my phone", resize=True, single_use=True)]])
            self.kb_msg = msg.id
        except Exception as er:
            log("phone keyboard:", er)

    async def login_step(self, event):
        chat = event.chat_id
        st = self.login
        cancel = [[self.btn("✖️", "Cancel", "m:cancel")]]
        await self.clean(event)
        if time.time() - st["since"] > LOGIN_TIMEOUT:
            await self.cancel_login()
            return await self.view_menu(chat, note="⌛ Login timed out. Tap **Login** to try again.")
        text = (event.raw_text or "").strip()

        if st["step"] == "phone":
            contact = getattr(event.message, "contact", None) if event.message else None
            phone = "+" + re.sub(r"\D", "", (contact.phone_number if contact else text) or "")
            if len(phone) < 8:
                return await self.show(chat, "🔐 **Login · step 1/3**\n\n❌ Send a valid number, like `+919876543210`.",
                                       cancel)
            await self.remove_keyboard(chat)
            client = new_client("")
            await client.connect()
            try:
                sent = await client.send_code_request(phone)
            except errors.FloodWaitError as fw:
                await client.disconnect()
                self.login = None
                return await self.view_menu(chat, note=f"⏳ Telegram says wait {fw.seconds}s, then try again.")
            except (errors.PhoneNumberInvalidError, errors.PhoneNumberBannedError,
                    errors.PhoneNumberUnoccupiedError) as er:
                await client.disconnect()
                self.login = None
                return await self.view_menu(chat, note=f"❌ {er.__class__.__name__.replace('Error', '')} — check the number.")
            st.update(step="code", client=client, phone=phone, hash=sent.phone_code_hash, tries=0)
            return await self.show(chat, "🔐 **Login · step 2/3**\n\n📩 Telegram sent you a code.\n"
                                   "Send it **with spaces**, like `1 2 3 4 5`\n"
                                   "(sent without spaces, Telegram blocks it).", cancel)

        if st["step"] == "code":
            code = re.sub(r"\D", "", text)
            if len(code) < 5:
                return await self.show(chat, "🔐 **Login · step 2/3**\n\nSend the code with spaces, like `1 2 3 4 5`.",
                                       cancel)
            try:
                await st["client"].sign_in(st["phone"], code=code, phone_code_hash=st["hash"])
            except errors.SessionPasswordNeededError:
                st.update(step="password", tries=0)
                return await self.show(chat, "🔐 **Login · step 3/3**\n\n🔑 Send your **2FA password**.\n"
                                       "It is deleted at once and never saved.", cancel)
            except errors.PhoneCodeInvalidError:
                st["tries"] += 1
                if st["tries"] >= 3:
                    await self.cancel_login()
                    return await self.view_menu(chat, note="❌ Wrong code 3 times. Tap **Login** to start again.")
                return await self.show(chat, "🔐 **Login · step 2/3**\n\n❌ Wrong code, send it again (with spaces).",
                                       cancel)
            except errors.PhoneCodeExpiredError:
                await self.cancel_login()
                return await self.view_menu(chat, note="⌛ Code expired (or blocked because it was sent without "
                                            "spaces). Tap **Login** and send the new code like `1 2 3 4 5`.")
            return await self.finish_login(chat)

        if st["step"] == "password":
            if not text:
                return
            try:
                await st["client"].sign_in(password=text)
            except errors.PasswordHashInvalidError:
                st["tries"] += 1
                if st["tries"] >= 3:
                    await self.cancel_login()
                    return await self.view_menu(chat, note="❌ Wrong password 3 times. Tap **Login** to start again.")
                return await self.show(chat, "🔐 **Login · step 3/3**\n\n❌ Wrong password, try again.", cancel)
            except errors.FloodWaitError as fw:
                await self.cancel_login()
                return await self.view_menu(chat, note=f"⏳ Telegram says wait {fw.seconds}s, then try again.")
            return await self.finish_login(chat)

    async def finish_login(self, chat):
        client = self.login["client"]
        me = await client.get_me()
        session = client.session.save()
        await client.disconnect()
        self.login = None
        account = {"id": me.id, "name": " ".join(filter(None, [me.first_name, me.last_name])) or str(me.id),
                   "username": me.username}
        self.store.set_session(session, account)
        await self.runner.stop()
        await self.start_userbot(check=False)
        await self.view_menu(chat, note=f"✅ **Logged in as {self.account_text()}**")

    # ------------------------------------------------------------ wiring
    def register(self):
        bot = self.bot

        @bot.on(events.NewMessage(func=lambda e: e.is_private))
        async def on_message(event):
            if not await self.allowed(event):
                return
            chat = event.chat_id
            text = (event.raw_text or "").strip()
            cmd = text.split()[0].lower().split("@")[0] if text.startswith("/") else ""

            if cmd == "/cancel":
                await self.clean(event)
                had = bool(self.login)
                await self.cancel_login()
                return await self.view_menu(chat, note="✖️ Cancelled." if had else "")
            if self.login and not cmd:
                return await self.login_step(event)
            await self.clean(event)
            if cmd == "/login":
                return await self.begin_login(chat)
            if cmd == "/logout":
                return await self.show(chat, "🚪 **Log out** your account from the userbot?",
                                       [[self.btn("✅", "Yes, log out", "m:logout_yes"), self.back()]])
            if cmd in ("/run", "/stop", "/restart"):
                return await self.control(cmd[1:], chat)
            if cmd == "/logs":
                return await self.view_logs(chat)
            if cmd == "/vars":
                return await self.view_vars(chat)
            if cmd == "/help":
                return await self.show(chat, HELP, [[self.back()]])
            if cmd == "/setvar":
                parts = text.split(maxsplit=2)
                if len(parts) < 3 or not VAR_RE.match(parts[1].upper()):
                    return await self.view_vars(chat, note="Usage: `/setvar KEY value`")
                key = parts[1].upper()
                if key in BLOCKED_VARS:
                    return await self.view_vars(chat, note=f"`{key}` can't be set here.")
                self.store.data.setdefault("env", {})[key] = parts[2].strip()
                self.store.save()
                return await self.view_vars(chat, note=f"✅ `{key}` saved. Tap **Restart** to use it.")
            if cmd == "/delvar":
                parts = text.split()
                key = parts[1].upper() if len(parts) > 1 else ""
                gone = self.store.data.get("env", {}).pop(key, None) is not None
                self.store.save()
                return await self.view_vars(chat, note=f"🗑 `{key}` removed." if gone else "Not found.")
            return await self.view_menu(chat)  # /start, /menu, /status, anything else

        @bot.on(events.CallbackQuery(pattern=rb"^m:"))
        async def on_button(event):
            if not await self.allowed(event):
                return
            chat = event.chat_id
            action = event.data.decode()[2:]
            answer = ""
            if action in ("menu", "joined"):
                await self.view_menu(chat, event)
            elif action in ("run", "stop", "restart"):
                await event.answer("⏳ Working…")
                return await self.control(action, chat, event)
            elif action == "login":
                await self.begin_login(chat, event)
            elif action == "cancel":
                await self.cancel_login()
                await self.view_menu(chat, event, note="✖️ Cancelled.")
            elif action == "logout":
                await self.show(chat, "🚪 **Log out** your account from the userbot?",
                                [[self.btn("✅", "Yes, log out", "m:logout_yes"), self.back()]], event)
            elif action == "logout_yes":
                await event.answer("⏳ Logging out…")
                note = await self.do_logout()
                return await self.view_menu(chat, event, note=note)
            elif action == "logs":
                await self.view_logs(chat, event)
            elif action == "logfile":
                await self.send_logfile(chat)
            elif action in ("fun_on", "fun_off"):
                on = action == "fun_on"
                self.set_fun_public(on)
                note = ("✅ **FUN MODE IS ON** — anyone who opens this bot can play the "
                        "animations. Your login / settings stay yours only."
                        if on else
                        "⛔ **FUN MODE IS OFF** — nobody else can use this bot now.")
                await self.view_menu(chat, event, note=note)
            elif action == "close":
                await self.drop(chat, event.message_id)
            elif action == "settings":
                await self.view_settings(chat, event)
            elif action == "help":
                await self.show(chat, HELP, [[self.back("m:settings")]], event)
            elif action == "vars":
                await self.view_vars(chat, event)
            try:
                await event.answer(answer)
            except Exception:
                pass

    async def control(self, action, chat, event=None):
        if action == "stop":
            await self.runner.stop()
            note = "⏹ Stopped."
        else:
            if action == "restart":
                await self.runner.stop()
            ok, msg = await self.start_userbot()
            note = ("🔄 Restarted." if action == "restart" else "▶️ Started.") if ok else f"❌ {msg}"
        await self.view_menu(chat, event, note=note)

    async def boot(self):
        if not OWNER_ID:
            log("OWNER_ID is not set - open the bot and send /start to see your id.")
            return
        if self.store.session:
            ok, _ = await self.start_userbot()
            if ok:
                return await self.tell("🟢 **Manager online.**")
        self.logged_out = True
        await self.tell("🔴 **Manager online.** Tap **Login** to connect your account.")


async def amain():
    if not TOKEN:
        log("MANAGER_BOT_TOKEN missing")
        sys.exit(1)
    os.makedirs(DATA_DIR, exist_ok=True)
    bot = TelegramClient(BOT_SESSION, API_ID, API_HASH)
    await bot.start(bot_token=TOKEN)
    me = await bot.get_me()
    log(f"manager bot @{me.username} online; owner id = {OWNER_ID or 'NOT SET'}")
    manager = Manager(bot)
    manager.register()

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass

    await manager.boot()
    await stop.wait()
    log("shutting down")
    await manager.runner.stop()
    await bot.disconnect()


def main():
    asyncio.run(amain())
