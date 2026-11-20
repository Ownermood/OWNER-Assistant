# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📖 **Commands**

• `{i}fastly`
    Turn the @FastlyWriteBot auto-answer on or off. It tries to reply first to that bot's typing games.

    Needs an OCR key: get one at ocr.space/ocrapi, then `{i}setdb OCR_API <key>`.
    For copies of that bot, add their user IDs to `FASTLY_CLONES`.
"""

from telethon import events
from . import udB, LOGS, ultroid_bot, ultroid_cmd, async_searcher
from os import remove


BotList = [1806208310]

if udB.get_key("FASTLY_CLONES"):
    for i in udB.get_key("FASTLY_CLONES").split():
        try:
            BotList.append(int(i))
        except (TypeError, ValueError):
            LOGS.exception(f"Invalid Value in 'FASTLY_CLONES': {i}")


async def fastly_bot(event):
    if not udB.get_key("FASTLY"):
        return
    api = udB.get_key("OCR_API")
    if not (api and event.photo):
        return
    from .ocr import ocr_space

    med = await event.download_media()
    try:
        txt = await ocr_space(med, api)
    except Exception as er:
        LOGS.info(f"fastly: {er}")
        remove(med)
        return
    txt = txt.split("By@")[0].replace("\n", "").replace("\r", "")
    if txt:
        try:
            await event.reply(txt)
        except Exception as er:
            LOGS.exception(er)
    try:
        remove(med)
    except Exception as e:
        LOGS.exception(e)


@ultroid_cmd(pattern="fastly$")
async def fastOnOff(event):
    xx = await event.eor("...")
    get_ = udB.get_key("FASTLY")
    if not get_:
        if not udB.get_key("OCR_API"):
            return await xx.edit("`OCR_API` is missing.\nAdd it before using this..")
        udB.set_key("FASTLY", True)
        _add_handler()
        return await xx.edit("Auto Fastly Response Activated")
    udB.del_key("FASTLY")
    await xx.edit("Fastly stopped!")


_ADDED = []


def _add_handler():
    if _ADDED:
        return
    ultroid_bot.add_handler(
        fastly_bot,
        events.NewMessage(incoming=True, from_users=BotList),
    )
    _ADDED.append(True)


if udB.get_key("FASTLY"):
    _add_handler()
