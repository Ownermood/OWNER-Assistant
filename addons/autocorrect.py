# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}autocorrect`
    To on/off Autocorrect Feature (English messages only).

  Messages ending with `..` are not corrected.
"""

import asyncio
import string

from telethon import events

from . import HNDLR, LOGS, get_string, udB, ultroid_bot, ultroid_cmd  # ignore: pylint

try:
    from textblob import TextBlob
except ImportError:
    LOGS.info("autocorrect: 'textblob' not installed.")
    TextBlob = None

_HANDLER_ADDED = []


def _add_handler():
    if _HANDLER_ADDED or not TextBlob:
        return
    ultroid_bot.add_handler(
        gramme, events.NewMessage(outgoing=True, func=lambda x: x.text)
    )
    _HANDLER_ADDED.append(True)


@ultroid_cmd(pattern="autocorrect$", fullsudo=True)
async def acc(e):
    if not TextBlob:
        return await e.eor("`Install textblob to use autocorrect.`", time=5)
    if not udB.get_key("AUTOCORRECT"):
        udB.set_key("AUTOCORRECT", "True")
        _add_handler()
        return await e.eor(get_string("act_1"), time=5)
    udB.del_key("AUTOCORRECT")
    await e.eor(get_string("act_2"), time=5)


def _looks_english(text):
    letters = [c for c in text if c.isalpha()]
    return letters and all(c in string.ascii_letters for c in letters)


async def gramme(event):
    if not udB.get_key("AUTOCORRECT"):
        return
    t = event.text
    if (
        not t
        or t.startswith(HNDLR)
        or t[0].lower() not in string.ascii_lowercase
        or t.endswith("..")
        or "http" in t
        or not _looks_english(t)
    ):
        return
    try:
        res = str(await asyncio.to_thread(lambda: TextBlob(t).correct()))
    except Exception as er:
        LOGS.info(f"autocorrect: {er}")
        return
    if res and res != t:
        try:
            await event.edit(res)
        except BaseException:
            pass


if TextBlob and udB.get_key("AUTOCORRECT"):
    _add_handler()
