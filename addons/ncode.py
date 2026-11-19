# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}ncode <file>`
   Use - Paste the contents of file and send as pic.
"""

import os, pygments
from pygments.formatters import ImageFormatter
from pygments.lexers import Python3Lexer
from . import ultroid_cmd, check_filename


@ultroid_cmd(pattern="ncode$")
async def coder_print(event):
    if not event.reply_to_msg_id:
        return await event.eor("`Reply to a file or message!`", time=5)
    msg = await event.get_reply_message()
    if msg.document:
        a = await event.client.download_media(
            await event.get_reply_message(), check_filename("ncode.txt")
        )
        with open(a, "r", errors="ignore") as s:
            c = s.read()
    else:
        a = None
        c = msg.text
    out = check_filename("result.png")
    font = "./resources/fonts/DroidSansMono.ttf"
    fmt = (
        ImageFormatter(line_numbers=True, font_name=font)
        if os.path.exists(font)
        else ImageFormatter(line_numbers=True)
    )
    with open(out, "wb") as f:
        pygments.highlight(c, Python3Lexer(), fmt, f)
    res = await event.client.send_message(
        event.chat_id,
        "**Pasting this code on my page...**",
        reply_to=event.reply_to_msg_id,
    )
    await event.client.send_file(
        event.chat_id, out, force_document=True, reply_to=event.reply_to_msg_id
    )
    await res.delete()
    await event.delete()
    if a:
        os.remove(a)
    os.remove(out)