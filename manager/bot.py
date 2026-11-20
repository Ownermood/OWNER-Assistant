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

HELP = """**OWNER Manager** - control your OWNER Assistant from here.

🔐 /login - log in your Telegram account (phone + code)
🚪 /logout - log out and stop the userbot
📊 /status - is it running? which account?
▶️ /run  ⏹ /stop  🔄 /restart - control the userbot
📜 /logs - last lines of the userbot log
⚙️ /vars  /setvar KEY value  /delvar KEY - extra settings (applied on restart)
❌ /cancel - cancel a login

Only you (OWNER_ID) can use this bot."""


def panel():
    return [
        [Button.inline("🔐 Login", b"m:login", style="success"),
         Button.inline("🚪 Logout", b"m:logout", style="danger")],
        [Button.inline("📊 Status", b"m:status", style="primary"),
         Button.inline("📜 Logs", b"m:logs")],
        [Button.inline("▶️ Run", b"m:run", style="success"),
         Button.inline("⏹ Stop", b"m:stop", style="danger"),
         Button.inline("🔄 Restart", b"m:restart", style="primary")],
        [Button.inline("⚙️ Vars", b"m:vars"), Button.inline("❓ Help", b"m:help")],
    ]


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

    # ---- helpers
    async def tell(self, text, **kw):
        if not OWNER_ID:
            return
        try:
            await self.bot.send_message(OWNER_ID, text, **kw)
        except Exception as er:  # owner never pressed /start, or blocked the bot
            log("could not message owner:", er)

    def account_text(self):
        acc = self.store.data.get("account")
        if not acc:
            return "unknown"
        user = f" (@{acc['username']})" if acc.get("username") else ""
        return f"{acc['name']}{user} `{acc['id']}`"

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
        tail = "\n".join(list(self.runner.lines)[-12:])[-1500:]
        if code == 0:
            await self.tell("⏹ Userbot stopped itself (`.shutdown`?). Press **Run** to start it again.",
                            buttons=panel())
            return
        ok, _ = await check_session(self.store.session)
        if not ok:
            self.logged_out = True
            await self.tell("🚪 **Your account is logged out** (session ended).\n"
                            "Userbot stopped. Press **Login** to connect again.", buttons=panel())
            return
        if self.runner.crash_too_often():
            await self.tell(f"❌ Userbot crashed {MAX_CRASHES} times in 10 min - auto restart stopped.\n"
                            f"```\n{tail}\n```\nFix the problem, then press **Run**.", buttons=panel())
            return
        await self.tell(f"⚠️ Userbot crashed (code `{code}`), restarting in 10s...\n```\n{tail}\n```")
        await asyncio.sleep(10)
        if not self.runner.running and not self.logged_out:
            await self.start_userbot(check=False)

    # ---- access
    async def allowed(self, event):
        if not OWNER_ID:
            text = (f"⚙️ Setup needed: put this line in your `.env` and restart:\n\n"
                    f"`OWNER_ID={event.sender_id}`")
            if isinstance(event, events.CallbackQuery.Event):
                await event.answer("OWNER_ID not set", alert=True)
            else:
                await event.reply(text)
            return False
        if event.sender_id != OWNER_ID:
            if isinstance(event, events.CallbackQuery.Event):
                await event.answer("This is a private bot.", alert=True)
            elif event.is_private:
                await event.reply("🔒 This is a private bot.")
            return False
        return True

    # ---- actions (shared by commands and buttons)
    async def do_status(self, respond):
        r = self.runner
        state = "🟢 Running" if r.running else ("🔴 Logged out" if self.logged_out or not self.store.session else "⚪ Stopped")
        lines = [f"**Userbot:** {state}", f"**Account:** {self.account_text()}"]
        if r.running and r.started:
            lines.append(f"**Uptime:** {fmt_uptime(time.time() - r.started)}")
        if r.crashes:
            lines.append(f"**Crashes (10 min):** {len(r.crashes)}")
        if self.login:
            lines.append(f"**Login in progress:** step `{self.login['step']}`")
        await respond("\n".join(lines), buttons=panel())

    async def do_run(self, respond):
        ok, msg = await self.start_userbot()
        await respond(("✅ " if ok else "❌ ") + msg + ("" if ok else "\nPress **Login** first."), buttons=panel())

    async def do_stop(self, respond):
        if not self.runner.running:
            return await respond("⚪ Userbot is not running.", buttons=panel())
        await self.runner.stop()
        await respond("⏹ Userbot stopped.", buttons=panel())

    async def do_restart(self, respond):
        await self.runner.stop()
        ok, msg = await self.start_userbot()
        await respond(("🔄 Restarted." if ok else "❌ " + msg), buttons=panel())

    async def do_logs(self, respond, event):
        lines = list(self.runner.lines)
        if not lines:
            return await respond("📜 No logs yet.")
        text = "\n".join(lines[-40:])
        if len(text) < 3500:
            return await respond(f"```\n{text}\n```")
        path = os.path.join(DATA_DIR, "userbot-logs.txt")
        with open(path, "w") as f:
            f.write("\n".join(lines))
        await self.bot.send_file(event.chat_id, path, caption="📜 Userbot logs")
        os.remove(path)

    async def do_vars(self, respond):
        env = self.store.env
        if not env:
            return await respond("⚙️ No extra vars. Add one: `/setvar KEY value`\n(Applied on next restart.)")
        body = "\n".join(f"`{k}` = `{mask(v)}`" for k, v in sorted(env.items()))
        await respond(f"⚙️ **Extra vars** (applied on restart):\n{body}")

    async def do_logout(self, respond):
        session = self.store.session
        await self.runner.stop()
        self.logged_out = True
        if not session:
            return await respond("🚪 Already logged out.", buttons=panel())
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
        await respond("🚪 **Logged out.** Userbot stopped and this session is removed from Telegram.\n"
                      "Press **Login** whenever you want to connect again.", buttons=panel())

    # ---- login conversation
    async def cancel_login(self):
        if self.login:
            client = self.login.get("client")
            self.login = None
            if client:
                try:
                    await client.disconnect()
                except Exception:
                    pass

    async def begin_login(self, respond):
        await self.cancel_login()
        self.login = {"step": "phone", "client": None, "tries": 0, "since": time.time()}
        warn = ""
        if self.runner.running:
            warn = f"\n\n⚠️ Currently running as {self.account_text()}. A new login replaces it."
        await respond(
            "🔐 **Login**\n\nSend your phone number with country code, like `+919876543210`,\n"
            "or tap the button below to share it." + warn + "\n\n/cancel to stop.",
            buttons=[[Button.request_phone("📱 Share my phone number", resize=True, single_use=True)]],
        )

    async def login_step(self, event):
        st = self.login
        if time.time() - st["since"] > LOGIN_TIMEOUT:
            await self.cancel_login()
            return await event.reply("⌛ Login timed out. Press /login to try again.", buttons=Button.clear())
        text = (event.raw_text or "").strip()

        if st["step"] == "phone":
            contact = getattr(event.message, "contact", None) if event.message else None
            phone = contact.phone_number if contact else text
            phone = "+" + re.sub(r"\D", "", phone or "")
            if len(phone) < 8:
                return await event.reply("Send a valid phone number with country code, like `+919876543210`.")
            client = new_client("")
            await client.connect()
            try:
                sent = await client.send_code_request(phone)
            except errors.FloodWaitError as fw:
                await client.disconnect()
                self.login = None
                return await event.reply(f"⏳ Telegram says wait {fw.seconds} seconds, then /login again.",
                                         buttons=Button.clear())
            except (errors.PhoneNumberInvalidError, errors.PhoneNumberBannedError,
                    errors.PhoneNumberUnoccupiedError) as er:
                await client.disconnect()
                self.login = None
                return await event.reply(f"❌ {er.__class__.__name__.replace('Error', '')}. Check the number and /login again.",
                                         buttons=Button.clear())
            st.update(step="code", client=client, phone=phone, hash=sent.phone_code_hash, tries=0)
            return await event.reply(
                "📩 Telegram sent you a login code.\n\n"
                "Send it here **with spaces**, like `1 2 3 4 5`\n"
                "(if you send it plain, Telegram blocks that code).",
                buttons=Button.clear(),
            )

        if st["step"] == "code":
            code = re.sub(r"\D", "", text)
            try:
                await event.delete()
            except Exception:
                pass
            if len(code) < 5:
                return await event.respond("Send the code with spaces, like `1 2 3 4 5`.")
            try:
                await st["client"].sign_in(st["phone"], code=code, phone_code_hash=st["hash"])
            except errors.SessionPasswordNeededError:
                st.update(step="password", tries=0)
                return await event.respond("🔑 Your account has 2-step verification.\n"
                                           "Send your **2FA password** (the message is deleted right away, "
                                           "and the password is never saved).")
            except errors.PhoneCodeInvalidError:
                st["tries"] += 1
                if st["tries"] >= 3:
                    await self.cancel_login()
                    return await event.respond("❌ Wrong code 3 times. Press /login to start again.")
                return await event.respond("❌ Wrong code, send it again (with spaces).")
            except errors.PhoneCodeExpiredError:
                await self.cancel_login()
                return await event.respond("⌛ That code expired (or Telegram blocked it because it was sent "
                                           "without spaces). Press /login and send the new code like `1 2 3 4 5`.")
            return await self.finish_login(event)

        if st["step"] == "password":
            try:
                await event.delete()
            except Exception:
                pass
            if not text:
                return await event.respond("Send your 2FA password.")
            try:
                await st["client"].sign_in(password=text)
            except errors.PasswordHashInvalidError:
                st["tries"] += 1
                if st["tries"] >= 3:
                    await self.cancel_login()
                    return await event.respond("❌ Wrong password 3 times. Press /login to start again.")
                return await event.respond("❌ Wrong password, try again.")
            except errors.FloodWaitError as fw:
                await self.cancel_login()
                return await event.respond(f"⏳ Telegram says wait {fw.seconds} seconds, then /login again.")
            return await self.finish_login(event)

    async def finish_login(self, event):
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
        await event.respond(f"✅ **Logged in as {self.account_text()}**\nUserbot is starting... "
                            "check /status in a minute.", buttons=panel())

    # ---- wiring
    def register(self):
        bot = self.bot

        @bot.on(events.NewMessage(func=lambda e: e.is_private))
        async def on_message(event):
            if not await self.allowed(event):
                return
            text = (event.raw_text or "").strip()
            cmd = text.split()[0].lower().split("@")[0] if text.startswith("/") else ""
            respond = event.reply

            if cmd == "/cancel":
                had = bool(self.login)
                await self.cancel_login()
                return await event.reply("❌ Cancelled." if had else "Nothing to cancel.", buttons=Button.clear())
            if self.login and not cmd:
                return await self.login_step(event)
            if cmd in ("/start", "/menu", "/help"):
                return await respond(HELP, buttons=panel())
            if cmd == "/login":
                return await self.begin_login(respond)
            if cmd == "/logout":
                return await respond("Log out your account from the userbot?",
                                     buttons=[[Button.inline("Yes, log out", b"m:logout_yes", style="danger"),
                                               Button.inline("No", b"m:status")]])
            if cmd == "/status":
                return await self.do_status(respond)
            if cmd == "/run":
                return await self.do_run(respond)
            if cmd == "/stop":
                return await self.do_stop(respond)
            if cmd == "/restart":
                return await self.do_restart(respond)
            if cmd == "/logs":
                return await self.do_logs(respond, event)
            if cmd == "/vars":
                return await self.do_vars(respond)
            if cmd == "/setvar":
                parts = text.split(maxsplit=2)
                try:
                    await event.delete()  # the value may be a secret
                except Exception:
                    pass
                if len(parts) < 3 or not VAR_RE.match(parts[1].upper()):
                    return await event.respond("Usage: `/setvar KEY value` (KEY like `GEMINI_API_KEY`)")
                key = parts[1].upper()
                if key in BLOCKED_VARS:
                    return await event.respond(f"`{key}` can't be set here.")
                self.store.data.setdefault("env", {})[key] = parts[2].strip()
                self.store.save()
                return await event.respond(f"✅ `{key}` saved (`{mask(parts[2].strip())}`). Press **Restart** to apply.",
                                           buttons=panel())
            if cmd == "/delvar":
                parts = text.split()
                key = parts[1].upper() if len(parts) > 1 else ""
                if self.store.data.get("env", {}).pop(key, None) is None:
                    return await respond("Not found. See /vars")
                self.store.save()
                return await respond(f"🗑 `{key}` removed. Press **Restart** to apply.", buttons=panel())
            if cmd:
                return await respond("Unknown command. /help")

        @bot.on(events.CallbackQuery(pattern=rb"^m:"))
        async def on_button(event):
            if not await self.allowed(event):
                return
            action = event.data.decode()[2:]
            await event.answer()

            async def respond(text, **kw):
                return await event.respond(text, **kw)

            actions = {
                "status": lambda: self.do_status(respond),
                "run": lambda: self.do_run(respond),
                "stop": lambda: self.do_stop(respond),
                "restart": lambda: self.do_restart(respond),
                "logs": lambda: self.do_logs(respond, event),
                "vars": lambda: self.do_vars(respond),
                "login": lambda: self.begin_login(respond),
                "logout_yes": lambda: self.do_logout(respond),
                "help": lambda: respond(HELP, buttons=panel()),
                "logout": lambda: respond("Log out your account from the userbot?",
                                          buttons=[[Button.inline("Yes, log out", b"m:logout_yes", style="danger"),
                                                    Button.inline("No", b"m:status")]]),
            }
            if action in actions:
                await actions[action]()

    async def boot(self):
        if not OWNER_ID:
            log("OWNER_ID is not set - open the bot and send /start to see your id.")
            return
        if self.store.session:
            ok, msg = await self.start_userbot()
            if ok:
                await self.tell(f"🟢 **OWNER Manager online.** Userbot started as {self.account_text()}.",
                                buttons=panel())
                return
        self.logged_out = True
        await self.tell("🔴 **OWNER Manager online.** Not logged in - press **Login** to connect your account.",
                        buttons=panel())


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
