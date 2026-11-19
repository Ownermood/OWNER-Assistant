# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

•`{i}sspam <reply to sticker> <optional- time gap>`
   it spam the whole stickers in that pack.

"""

import asyncio

from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import DocumentAttributeSticker, InputStickerSetEmpty
from telethon.utils import get_input_document

from . import *


@ultroid_cmd(pattern="sspam ?(.*)")
async def _(e):
    match = e.pattern_match.group(1)
    x = await e.get_reply_message()
    if not (x and x.sticker):
        return await eod(e, "`Reply To Sticker Only`")
    attr = next(
        (a for a in x.document.attributes if isinstance(a, DocumentAttributeSticker)),
        None,
    )
    if not attr or isinstance(attr.stickerset, InputStickerSetEmpty):
        return await eod(e, "`This sticker is not part of a pack.`")
    sset = await e.client(GetStickerSetRequest(attr.stickerset, hash=0))
    docs = [get_input_document(d) for d in sset.documents]
    try:
        match = int(match)
    except ValueError:
        match = None
    for xx in docs:
        await asyncio.sleep(match or 0.5)
        await e.respond(file=xx)
