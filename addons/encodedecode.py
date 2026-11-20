# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📖 **Commands**

• `{i}encode <text>` (or reply)
    Turn text into base64 code.

• `{i}decode <code>` (or reply)
    Turn base64 code back into text.
"""

import base64

from . import ultroid_cmd


@ultroid_cmd(pattern="encode( (.*)|$)")
async def encod(e):
    match = e.pattern_match.group(1).strip()
    if not match and e.is_reply:
        gt = await e.get_reply_message()
        if gt.text:
            match = gt.text
    if not match:
        return await e.eor("Give me something to Encode.")
    byt = match.encode("utf-8")
    et = base64.b64encode(byt)
    atc = et.decode("utf-8")
    await e.eor(f"**=>> Encoded Text :** `{match}`\n\n**=>> OUTPUT :**\n`{atc}`")


@ultroid_cmd(pattern="decode( (.*)|$)")
async def encod(e):
    match = e.pattern_match.group(1).strip()
    if not match and e.is_reply:
        gt = await e.get_reply_message()
        if gt.text:
            match = gt.text
    if not match:
        return await e.eor("Give me something to Decode.")
    byt = match.encode("utf-8")
    try:
        et = base64.b64decode(byt)
        atc = et.decode("utf-8")
        await e.eor(f"**=>> Decoded Text :** `{match}`\n\n**=>> OUTPUT :**\n`{atc}`")
    except Exception as p:
        await e.eor("**ERROR :** " + str(p))
