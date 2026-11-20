#    Ultroid - UserBot
#    Copyright 2020 (c)

# Lyrics ported from Dark Cobra
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


"""
📖 **Commands**

• `{i}song <song name>`
    Find the song on YouTube and send the audio.

• `{i}lyrics <song name>`
    Get the song's lyrics.
"""

import asyncio

from pyUltroid.fns.ytdl import download_yt, get_yt_link

from . import *

# lrclib.net: free, keyless lyrics database.
LRCLIB = "https://lrclib.net/api/search"


@ultroid_cmd(pattern=r"lyrics( (.*)|$)")
async def original(event):
    noob = event.pattern_match.group(1).strip()
    if not noob:
        return await event.eor("give query to search.")
    ab = await event.eor("Getting lyrics.")
    try:
        res = await async_searcher(
            LRCLIB,
            params={"q": noob},
            headers={"User-Agent": "OWNER-Assistant"},
            re_json=True,
        )
    except Exception as er:
        return await ab.edit(f"`Lyrics service error: {er}`")
    song = next((x for x in res or [] if x.get("plainLyrics")), None)
    if not song:
        return await ab.edit("No results found")
    text = (
        f"**{song.get('trackName')}** - __{song.get('artistName')}__\n\n"
        f"{song['plainLyrics']}"
    )
    for i in range(0, len(text), 4000):
        await event.client.send_message(
            event.chat_id, text[i : i + 4000], reply_to=event.reply_to_msg_id
        )
    await ab.delete()


@ultroid_cmd(pattern="song( (.*)|$)")
async def _(event):
    args = event.pattern_match.group(1).strip()
    if not args:
        return await event.eor("Enter song name")
    okla = await event.eor("Searching...")
    url = await asyncio.to_thread(get_yt_link, args)
    if not url:
        return await okla.edit("Song not found.")
    ytd = {
        "prefer_ffmpeg": True,
        "addmetadata": True,
        "geo-bypass": True,
        "nocheckcertificate": True,
        "format": "bestaudio",
        "outtmpl": "%(id)s.m4a",
    }
    await okla.edit("Downloading...")
    await download_yt(okla, url, ytd)
