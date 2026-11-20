# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help
from pyUltroid.branding import BOT_NAME, BOT_NAME_CAPS, BOT_NAME_FANCY, BRAND_IMAGES, assistant_buttons, brand_file

__doc__ = get_help("help_bot")

import os
import sys
import time
from platform import python_version as pyver
from random import choice

from telethon import __version__
from telethon.errors.rpcerrorlist import (
    BotMethodInvalidError,
    ChatSendMediaForbiddenError,
)

from pyUltroid.version import __version__ as UltVer

from . import HOSTED_ON, LOGS

try:
    from git import Repo
except ImportError:
    LOGS.error("bot: 'gitpython' module not found!")
    Repo = None

from telethon.utils import resolve_bot_file_id

from . import (
    ATRA_COL,
    LOGS,
    OWNER_NAME,
    ULTROID_IMAGES,
    Button,
    Carbon,
    Telegraph,
    Var,
    allcmds,
    asst,
    bash,
    call_back,
    callback,
    def_logs,
    eor,
    get_string,
    heroku_logs,
    in_pattern,
    inline_pic,
    restart,
    shutdown,
    start_time,
    time_formatter,
    udB,
    ultroid_bot,
    ultroid_cmd,
    ultroid_version,
    updater,
)


def ULTPIC():
    return inline_pic() or choice(ULTROID_IMAGES)


def _buttons():
    return assistant_buttons() or []


def _branch():
    try:
        return Repo().active_branch.name
    except Exception:
        return "main"


ALIVE_BULLETS = ("✵", "👑", "⚡", "🧩", "⏳", "🐍", "📡", "🌿")

# Will move to strings
alive_txt = """
The OWNER Assistant 

  ◍ Version - {}
  ◍ Core - {}
  ◍ Telethon - {}
"""

in_alive = "{}\n\n🌀 <b>Version -></b> <code>{}</code>\n🌀 <b>Core -></b> <code>{}</code>\n🌀 <b>Python -></b> <code>{}</code>\n🌀 <b>Uptime -></b> <code>{}</code>\n🌀 <b>Branch -></b>[ {} ]"


@callback("alive")
async def alive(event):
    text = alive_txt.format(ultroid_version, UltVer, __version__)
    await event.answer(text, alert=True)


@ultroid_cmd(
    pattern="alive( (.*)|$)",
)
async def lol(ult):
    match = ult.pattern_match.group(1).strip()
    inline = None
    if match in ["inline", "i"]:
        try:
            res = await ult.client.inline_query(asst.me.username, "alive")
            return await res[0].click(ult.chat_id)
        except BotMethodInvalidError:
            pass
        except BaseException as er:
            LOGS.exception(er)
        inline = True
    pic = udB.get_key("ALIVE_PIC")
    if pic is None:
        pic = brand_file("alive")
    if isinstance(pic, list):
        pic = choice(pic)
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get_key("ALIVE_TEXT") or get_string("bot_1")
    y = _branch()
    kk = y
    buttons = _buttons()
    if inline:
        kk = f"<code>{y}</code>"
        parse = "html"
        als = in_alive.format(
            header,
            f"{ultroid_version} [{HOSTED_ON}]",
            UltVer,
            pyver(),
            uptime,
            kk,
        )

        if _e := udB.get_key("ALIVE_EMOJI"):
            als = als.replace("🌀", _e)
    else:
        parse = "md"
        als = (get_string("alive_1")).format(
            header,
            OWNER_NAME,
            f"{ultroid_version} [{HOSTED_ON}]",
            UltVer,
            uptime,
            pyver(),
            __version__,
            kk,
        )

        if a := udB.get_key("ALIVE_EMOJI"):
            for b in ALIVE_BULLETS:
                als = als.replace(b, a)
    if pic:
        try:
            await ult.reply(
                als,
                file=pic,
                parse_mode=parse,
                link_preview=False,
                buttons=(buttons or None) if inline else None,
            )
            return await ult.try_delete()
        except ChatSendMediaForbiddenError:
            pass
        except BaseException as er:
            LOGS.exception(er)
            try:
                await ult.reply(file=pic)
                await ult.reply(
                    als,
                    parse_mode=parse,
                    buttons=(buttons or None) if inline else None,
                    link_preview=False,
                )
                return await ult.try_delete()
            except BaseException as er:
                LOGS.exception(er)
    await eor(
        ult,
        als,
        parse_mode=parse,
        link_preview=False,
        buttons=(buttons or None) if inline else None,
    )


@ultroid_cmd(pattern="ping$", chats=[], type=["official", "assistant"])
async def _(event):
    start = time.time()
    x = await event.eor("Pong !")
    end = round((time.time() - start) * 1000)
    uptime = time_formatter((time.time() - start_time) * 1000)
    await x.edit(get_string("ping").format(end, uptime))


@ultroid_cmd(
    pattern="cmds$",
)
async def cmds(event):
    await allcmds(event, Telegraph)


heroku_api = Var.HEROKU_API


@ultroid_cmd(
    pattern="restart$",
    fullsudo=True,
)
async def restartbt(ult):
    ok = await ult.eor(get_string("bot_5"))
    call_back()
    who = "bot" if ult.client._bot else "user"
    udB.set_key("_RESTART", f"{who}_{ult.chat_id}_{ok.id}")
    if heroku_api:
        return await restart(ok)
    await bash("git pull && pip3 install -r requirements.txt")
    await bash("pip3 install -r requirements.txt --break-system-packages")
    if len(sys.argv) > 1:
        os.execl(sys.executable, sys.executable, "main.py")
    else:
        os.execl(sys.executable, sys.executable, "-m", "pyUltroid")


@ultroid_cmd(
    pattern="shutdown$",
    fullsudo=True,
)
async def shutdownbot(ult):
    await shutdown(ult)


@ultroid_cmd(
    pattern="logs( (.*)|$)",
    chats=[],
)
async def _(event):
    opt = event.pattern_match.group(1).strip()
    file = f"ultroid{sys.argv[-1]}.log" if len(sys.argv) > 1 else "ultroid.log"
    if opt == "heroku":
        await heroku_logs(event)
    elif opt == "carbon" and Carbon:
        event = await event.eor(get_string("com_1"))
        with open(file, "r") as f:
            code = f.read()[-2500:]
        file = await Carbon(
            file_name="owner-assistant-logs",
            code=code,
            backgroundColor=choice(ATRA_COL),
        )
        if isinstance(file, dict):
            await event.eor(f"`{file}`")
            return
        await event.reply(f"**{BOT_NAME} Logs.**", file=file)
    elif opt == "open":
        with open("ultroid.log", "r") as f:
            file = f.read()[-4000:]
        return await event.eor(f"`{file}`")
    elif (
        opt.isdigit() and 5 <= int(opt) <= 100
    ):  # Check if input is a number between 10 and 100
        num_lines = int(opt)
        with open("ultroid.log", "r") as f:
            lines = f.readlines()[-num_lines:]
            file = "".join(lines)
        return await event.eor(f"`{file}`")
    else:
        await def_logs(event, file)
    await event.try_delete()


@in_pattern("alive", owner=True)
async def inline_alive(ult):
    pic = udB.get_key("ALIVE_PIC")
    if pic is None:
        pic = brand_file("alive")
    if isinstance(pic, list):
        pic = choice(pic)
    uptime = time_formatter((time.time() - start_time) * 1000)
    header = udB.get_key("ALIVE_TEXT") or get_string("bot_1")
    kk = f"<code>{_branch()}</code>"
    buttons = _buttons()
    als = in_alive.format(
        header, f"{ultroid_version} [{HOSTED_ON}]", UltVer, pyver(), uptime, kk
    )

    if _e := udB.get_key("ALIVE_EMOJI"):
        als = als.replace("🌀", _e)
    builder = ult.builder
    if pic:
        try:
            if ".jpg" in pic:
                results = [
                    await builder.photo(
                        pic, text=als, parse_mode="html", buttons=buttons or None
                    )
                ]
            else:
                if _pic := resolve_bot_file_id(pic):
                    pic = _pic
                    buttons.insert(
                        0, [Button.inline(get_string("bot_2"), data="alive")]
                    )
                results = [
                    await builder.document(
                        pic,
                        title="Inline Alive",
                        description=BOT_NAME,
                        parse_mode="html",
                        buttons=buttons or None,
                    )
                ]
            return await ult.answer(results)
        except BaseException as er:
            LOGS.exception(er)
    result = [
        await builder.article(
            "Alive", text=als, parse_mode="html", link_preview=False, buttons=buttons or None
        )
    ]
    await ult.answer(result)


@ultroid_cmd(pattern="update( (.*)|$)")
async def _(e):
    xx = await e.eor(get_string("upd_1"))
    if e.pattern_match.group(1).strip() and (
        "fast" in e.pattern_match.group(1).strip()
        or "soft" in e.pattern_match.group(1).strip()
    ):
        await bash("git pull -f && pip3 install -r requirements.txt")
        await bash("pip3 install -r requirements.txt --break-system-packages")
        call_back()
        await xx.edit(get_string("upd_7"))
        os.execl(sys.executable, "python3", "-m", "pyUltroid")
        # return
    m = await updater()
    branch = (Repo.init()).active_branch
    if m:
        x = await asst.send_file(
            udB.get_key("LOG_CHANNEL"),
            ULTPIC(),
            caption="• **Update Available** •",
            force_document=False,
            buttons=Button.inline("Changelogs", data="changes"),
        )
        Link = x.message_link
        await xx.edit(
            f'<strong><a href="{Link}">[ChangeLogs]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )
    else:
        await xx.edit(
            f"<code>Your BOT is </code><strong>up-to-date</strong><code> with </code><strong>[{branch}]</strong>",
            parse_mode="html",
            link_preview=False,
        )


@callback("updtavail", owner=True)
async def updava(event):
    await event.delete()
    await asst.send_file(
        udB.get_key("LOG_CHANNEL"),
        ULTPIC(),
        caption="• **Update Available** •",
        force_document=False,
        buttons=Button.inline("Changelogs", data="changes"),
    )


AVATAR = "resources/extras/owner_assistant_avatar.jpg"


@ultroid_cmd(pattern="botpic$", fullsudo=True)
async def set_assistant_pic(e):
    """Change the assistant bot's profile photo (reply to a photo, or default avatar)."""
    from pyUltroid.startup.funcs import _botfather_reply

    if not asst.me.bot:
        return await e.eor("`Assistant bot is not active.`")
    msg = await e.eor("`Changing assistant bot photo at @BotFather...`")
    reply = await e.get_reply_message()
    file, temp = AVATAR, None
    if reply and reply.photo:
        file = temp = await reply.download_media("resources/downloads/")
    try:
        async with ultroid_bot.conversation("BotFather", timeout=60) as conv:
            await _botfather_reply(conv, "/cancel")
            await _botfather_reply(conv, "/setuserpic")
            answer = await _botfather_reply(conv, f"@{asst.me.username}")
            if "photo" not in answer.lower():
                return await msg.edit(f"`BotFather said:` {answer[:300]}")
            await conv.send_file(file)
            done = (await conv.get_response()).raw_text or ""
        await ultroid_bot.send_read_acknowledge("BotFather")
    except Exception as er:
        return await msg.edit(f"`Could not change photo: {er}`")
    finally:
        if temp and os.path.exists(temp):
            os.remove(temp)
    if "success" in done.lower():
        return await msg.edit(f"`Done! New photo set for` @{asst.me.username}")
    await msg.edit(f"`BotFather said:` {done[:300]}")
