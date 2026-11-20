# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
📖 **Commands**

• `{i}yta <link>`
    Download the audio from a YouTube (or other) link.

• `{i}ytv <link>`
    Download the video from a link.

• `{i}ytsa <song name>`
    Search YouTube and send the audio.
    Example: `{i}ytsa believer`

• `{i}ytsv <video name>`
    Search YouTube and send the video.

• `{i}ytcookies` (reply to a cookies.txt file)
    Fix the "Sign in to confirm you're not a bot" error.
    Export YouTube cookies (cookies.txt) from a browser logged in to a spare Google account, send the file here and reply to it with this command.
    `{i}ytcookies` - see status   ·   `{i}ytcookies del` - remove them
"""
import asyncio
import os

from pyUltroid.fns.helper import read_text_file
from pyUltroid.fns.ytdl import YT_COOKIE_FILE, download_yt, get_yt_link

from . import get_string, requests, udB, ultroid_cmd


def _clear_cookie_file():
    try:
        os.remove(YT_COOKIE_FILE)
    except OSError:
        pass


@ultroid_cmd(pattern="ytcookies( (.*)|$)")
async def yt_cookies(event):
    arg = event.pattern_match.group(1).strip().lower()
    if arg in ("del", "delete", "remove", "off"):
        udB.del_key("YT_COOKIES")
        _clear_cookie_file()
        return await event.eor("YouTube cookies removed.", time=5)
    reply = await event.get_reply_message()
    if not (reply and reply.file):
        status = "saved ✅" if udB.get_key("YT_COOKIES") else "not set ❌"
        return await event.eor(
            f"**YouTube cookies:** {status}\n\n"
            "Reply to a `cookies.txt` file with `.ytcookies` to save them.\n"
            "`.ytcookies del` removes them. Help: `.help youtube`"
        )
    if (reply.file.size or 0) > 1024 * 1024:
        return await event.eor("`File too big — send only the YouTube cookies.txt.`", time=8)
    msg = await event.eor("Checking cookies.")
    path = await reply.download_media("resources/downloads/")
    text = read_text_file(path) if path else None
    if path and os.path.exists(path):
        os.remove(path)
    lines = [l for l in (text or "").splitlines() if l.strip() and not l.startswith("#")]
    good = [l for l in lines if l.count("\t") >= 6 and ("youtube.com" in l or "google.com" in l)]
    if not good:
        return await msg.edit(
            "`This is not a YouTube cookies.txt (Netscape format).`\n"
            "Export it from youtube.com with a cookies.txt extension."
        )
    if not text.lstrip().startswith("# "):
        text = "# Netscape HTTP Cookie File\n" + text
    udB.set_key("YT_COOKIES", text)
    _clear_cookie_file()
    try:
        await reply.delete()
    except Exception:
        pass
    await msg.edit(
        f"`YouTube cookies saved ✅ ({len(good)} cookies).`\n"
        "The cookies file was deleted from this chat for safety. Try `.ytsa` again."
    )


@ultroid_cmd(
    pattern="yt(a|v|sa|sv) ?(.*)",
)
async def download_from_youtube_(event):
    ytd = {
        "prefer_ffmpeg": True,
        "addmetadata": True,
        "geo-bypass": True,
        "nocheckcertificate": True,
    }
    opt = event.pattern_match.group(1).strip()
    xx = await event.eor(get_string("com_1"))
    if opt == "a":
        ytd["format"] = "bestaudio"
        ytd["outtmpl"] = "%(id)s.m4a"
        url = event.pattern_match.group(2)
        if not url:
            return await xx.eor(get_string("youtube_1"))
        try:
            requests.get(url)
        except BaseException:
            return await xx.eor(get_string("youtube_2"))
    elif opt == "v":
        ytd["format"] = "bestvideo*+bestaudio/best"
        ytd["merge_output_format"] = "mp4"
        ytd["outtmpl"] = "%(id)s.mp4"
        ytd["postprocessors"] = [{"key": "FFmpegMetadata"}]
        url = event.pattern_match.group(2)
        if not url:
            return await xx.eor(get_string("youtube_3"))
        try:
            requests.get(url)
        except BaseException:
            return await xx.eor(get_string("youtube_4"))
    elif opt == "sa":
        ytd["format"] = "bestaudio"
        ytd["outtmpl"] = "%(id)s.m4a"
        try:
            query = event.text.split(" ", 1)[1]
        except IndexError:
            return await xx.eor(get_string("youtube_5"))
        url = await asyncio.to_thread(get_yt_link, query)
        if not url:
            return await xx.edit(get_string("unspl_1"))
        await xx.eor(get_string("youtube_6"))
    elif opt == "sv":
        ytd["format"] = "bestvideo*+bestaudio/best"
        ytd["merge_output_format"] = "mp4"
        ytd["outtmpl"] = "%(id)s.mp4"
        ytd["postprocessors"] = [{"key": "FFmpegMetadata"}]
        try:
            query = event.text.split(" ", 1)[1]
        except IndexError:
            return await xx.eor(get_string("youtube_7"))
        url = await asyncio.to_thread(get_yt_link, query)
        if not url:
            return await xx.edit(get_string("unspl_1"))
        await xx.eor(get_string("youtube_8"))
    else:
        return
    await download_yt(xx, url, ytd)
