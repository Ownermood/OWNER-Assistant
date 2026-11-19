# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}sticklet <text>`
   `create random sticker with text.`
"""

import io
import os
import random
import textwrap
from glob import glob

from PIL import Image, ImageDraw, ImageFont
from telethon.errors.rpcerrorlist import BotMethodInvalidError
from telethon.tl.types import InputMessagesFilterDocument

from . import *


@ultroid_cmd(pattern="sticklet(?: |$)(.*)")
async def sticklet(event):
    a = await event.eor(get_string("com_1"))
    R = random.randint(0, 255)
    G = random.randint(0, 255)
    B = random.randint(0, 255)
    if not event.pattern_match.group(1):
        try:
            msg = await event.get_reply_message()
            if msg and msg.text:
                sticktext = msg.text
            else:
                return await a.eor("`Give me some Text`")
        except BotMethodInvalidError:
            return await a.eor("`Give me some Text`")
    else:
        sticktext = event.pattern_match.group(1)
    if not sticktext:
        return await event.eor("`Give me some Text`")
    sticktext = textwrap.wrap(sticktext, width=10)
    # converts back the list to a string
    sticktext = "\n".join(sticktext)
    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230
    font_file_ = glob("resources/fonts/*ttf")
    FONT_FILE = random.choice(font_file_)
    font = ImageFont.truetype(FONT_FILE, size=fontsize)
    for _ in range(12):
        bbox = draw.multiline_textbbox((0, 0), sticktext, font=font)
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if width <= 500 and height <= 500:
            break
        fontsize = int(fontsize * 0.8)
        font = ImageFont.truetype(FONT_FILE, size=fontsize)
    draw.multiline_text(
        ((512 - width) / 2, (512 - height) / 2), sticktext, font=font, fill=(R, G, B)
    )
    image_stream = io.BytesIO()
    image_stream.name = check_filename("ult.webp")
    image.save(image_stream, "WebP")
    image_stream.seek(0)
    await a.delete()
    await event.client.send_message(
        event.chat_id,
        "{}".format(sticktext),
        file=image_stream,
        reply_to=event.message.reply_to_msg_id,
    )
