# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
📖 **Commands**

• `{i}whichsong` (reply to a song file)
    Find out which song it is.
"""

from os import remove

from shazamio import Shazam

from . import eor, get_string, mediainfo, ultroid_cmd

shazam = Shazam()


@ultroid_cmd(pattern="whichsong$")
async def song_recog(event):
    reply = await event.get_reply_message()
    if not (reply and (reply.audio or reply.voice or reply.video)):
        return await event.eor(get_string("whs_1"), time=5)
    xx = await event.eor(get_string("com_5"))
    path_to_song = "./temp/shaazam_cache/unknown.mp3"
    await reply.download_media(path_to_song)
    await xx.edit(get_string("whs_2"))
    try:
        recognize = getattr(shazam, "recognize", None) or shazam.recognize_song
        res = await recognize(path_to_song)
    except Exception as e:
        return await eor(xx, str(e), time=10)
    finally:
        try:
            remove(path_to_song)
        except OSError:
            pass
    try:
        x = res["track"]
        await xx.edit(get_string("whs_4").format(x["title"]))
    except KeyError:
        return await eor(xx, get_string("whs_3"), time=5)
