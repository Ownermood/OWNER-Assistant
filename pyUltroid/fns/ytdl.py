# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import glob
import os
import re
import time

from telethon import Button

from yt_dlp import YoutubeDL

from .. import LOGS, udB
from .helper import download_file, humanbytes, run_async, time_formatter
from .tools import set_attributes


async def ytdl_progress(k, start_time, event):
    if k["status"] == "error":
        return await event.edit("error")
    while k["status"] == "downloading":
        text = (
            f"`Downloading: {k['filename']}\n"
            + f"Total Size: {humanbytes(k['total_bytes'])}\n"
            + f"Downloaded: {humanbytes(k['downloaded_bytes'])}\n"
            + f"Speed: {humanbytes(k['speed'])}/s\n"
            + f"ETA: {time_formatter(k['eta']*1000)}`"
        )
        if round((time.time() - start_time) % 10.0) == 0:
            try:
                await event.edit(text)
            except Exception as ex:
                LOGS.error(f"ytdl_progress: {ex}")


def _format_count(num):
    if not num:
        return "N/A"
    for unit in ("", "K", "M", "B"):
        if abs(num) < 1000:
            return f"{num:.0f}{unit}" if unit == "" else f"{num:.1f}{unit}"
        num /= 1000
    return f"{num:.1f}T"


YT_COOKIE_FILE = "resources/auth/yt_cookies.txt"
_BOT_CHECK = ("confirm you’re not a bot", "confirm you're not a bot", "sign in to confirm")


def _cookie_file():
    """Write the cookies saved with .ytcookies (kept in the DB) to a file for yt-dlp."""
    data = udB.get_key("YT_COOKIES")
    if not data:
        return None
    try:
        os.makedirs(os.path.dirname(YT_COOKIE_FILE), exist_ok=True)
        if not os.path.exists(YT_COOKIE_FILE):
            with open(YT_COOKIE_FILE, "w") as f:
                f.write(str(data))
            os.chmod(YT_COOKIE_FILE, 0o600)
    except OSError as er:
        LOGS.error(f"yt cookies: {er}")
        return None
    return YT_COOKIE_FILE


def ytdl_opts(opts=None):
    """Common yt-dlp options: adds the YouTube cookies saved with .ytcookies.

    (yt-dlp finds the `deno` JS runtime on PATH by itself.)
    """
    opts = dict(opts or {})
    cookie = _cookie_file()
    if cookie and "cookiefile" not in opts:
        opts["cookiefile"] = cookie
    return opts


def yt_error_text(er):
    """Short, useful message for a yt-dlp error."""
    text = str(er)
    if any(x in text.lower() for x in _BOT_CHECK):
        if udB.get_key("YT_COOKIES"):
            return (
                "**YouTube blocked this request** (\"not a bot\" check) even with your cookies.\n"
                "Cookies may be expired: export fresh ones and send `.ytcookies` again."
            )
        return (
            "**YouTube blocked this server** (\"Sign in to confirm you're not a bot\").\n"
            "Fix: export YouTube cookies (cookies.txt) from a browser where you are logged in "
            "(use a spare Google account), send the file here, reply to it with `.ytcookies`.\n"
            "Help: `.help youtube`"
        )
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    return f"`{text[:900]}`"


def yt_search(query, limit=10):
    """Search YouTube with yt-dlp (no API key, no extra library)."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
    }
    try:
        info = YoutubeDL(ytdl_opts(opts)).extract_info(f"ytsearch{limit}:{query}", download=False)
    except Exception as er:
        LOGS.info(f"yt_search: {er}")
        return []
    results = []
    for entry in info.get("entries") or []:
        if not entry or not entry.get("id"):
            continue
        duration = entry.get("duration")
        results.append(
            {
                "id": entry["id"],
                "link": f"https://www.youtube.com/watch?v={entry['id']}",
                "title": entry.get("title") or "Untitled",
                "duration": time.strftime(
                    "%H:%M:%S" if duration and duration >= 3600 else "%M:%S",
                    time.gmtime(duration),
                )
                if duration
                else "Live/Unknown",
                "views": _format_count(entry.get("view_count")),
                "channel": entry.get("channel") or entry.get("uploader") or "Unknown",
                "description": entry.get("description") or "",
            }
        )
    return results


def get_yt_link(query):
    search = yt_search(query, limit=1)
    return search[0]["link"] if search else None


async def download_yt(event, link, ytd):
    reply_to = event.reply_to_msg_id or event
    info = await dler(event, link, ytd, download=True)
    if not info:
        return
    if info.get("_type", None) == "playlist":
        total = info["playlist_count"]
        for num, file in enumerate(info["entries"]):
            num += 1
            id_ = file["id"]
            thumb = id_ + ".jpg"
            title = file["title"]
            await download_file(
                file.get("thumbnail", None) or file["thumbnails"][-1]["url"], thumb
            )
            ext = "." + ytd["outtmpl"]["default"].split(".")[-1]
            if ext == ".m4a":
                ext = ".mp3"
            id = None
            for x in glob.glob(f"{id_}*"):
                if not x.endswith("jpg"):
                    id = x
            if not id:
                return
            ext = "." + id.split(".")[-1]
            file = title + ext
            try:
                os.rename(id, file)
            except FileNotFoundError:
                try:
                    os.rename(id + ext, file)
                except FileNotFoundError as er:
                    if os.path.exists(id):
                        file = id
                    else:
                        raise er
            if file.endswith(".part"):
                os.remove(file)
                os.remove(thumb)
                await event.client.send_message(
                    event.chat_id,
                    f"`[{num}/{total}]` `Invalid Video format.\nIgnoring that...`",
                )
                return
            attributes = await set_attributes(file)
            res, _ = await event.client.fast_uploader(
                file, show_progress=True, event=event, to_delete=True
            )
            from_ = info["extractor"].split(":")[0]
            caption = f"`[{num}/{total}]` `{title}`\n\n`from {from_}`"
            await event.client.send_file(
                event.chat_id,
                file=res,
                caption=caption,
                attributes=attributes,
                supports_streaming=True,
                thumb=thumb,
                reply_to=reply_to,
            )
            os.remove(thumb)
        try:
            await event.delete()
        except BaseException:
            pass
        return
    title = info["title"]
    if len(title) > 20:
        title = title[:17] + "..."
    id_ = info["id"]
    thumb = id_ + ".jpg"
    await download_file(
        info.get("thumbnail", None) or f"https://i.ytimg.com/vi/{id_}/hqdefault.jpg",
        thumb,
    )
    ext = "." + ytd["outtmpl"]["default"].split(".")[-1]
    for _ext in [".m4a", ".mp3", ".opus"]:
        if ext == _ext:
            ext = _ext
            break
    id = None
    for x in glob.glob(f"{id_}*"):
        if not x.endswith("jpg"):
            id = x
    if not id:
        return
    ext = "." + id.split(".")[-1]
    file = title + ext
    try:
        os.rename(id, file)
    except FileNotFoundError:
        os.rename(id + ext, file)
    attributes = await set_attributes(file)
    res, _ = await event.client.fast_uploader(
        file, show_progress=True, event=event, to_delete=True
    )
    caption = f"`{info['title']}`"
    await event.client.send_file(
        event.chat_id,
        file=res,
        caption=caption,
        attributes=attributes,
        supports_streaming=True,
        thumb=thumb,
        reply_to=reply_to,
    )
    os.remove(thumb)
    try:
        await event.delete()
    except BaseException:
        pass


# ---------------YouTube Downloader Inline---------------
# @New-Dev0 @buddhhu @1danish-00


def get_formats(type, id, data):
    if type == "audio":
        audio = []
        for _quality in ["64", "128", "256", "320"]:
            _audio = {}
            _audio.update(
                {
                    "ytid": id,
                    "type": "audio",
                    "id": _quality,
                    "quality": _quality + "KBPS",
                }
            )
            audio.append(_audio)
        return audio
    if type == "video":
        video = []
        size = 0
        for vid in data["formats"]:
            if vid["format_id"] == "251":
                size += vid["filesize"] if vid.get("filesize") else 0
            if vid["vcodec"] != "none":
                _id = int(vid["format_id"])
                _quality = str(vid["width"]) + "×" + str(vid["height"])
                _size = size + (vid["filesize"] if vid.get("filesize") else 0)
                _ext = "mkv" if vid["ext"] == "webm" else "mp4"
                if _size < 2147483648:  # Telegram's Limit of 2GB
                    _video = {}
                    _video.update(
                        {
                            "ytid": id,
                            "type": "video",
                            "id": str(_id) + "+251",
                            "quality": _quality,
                            "size": _size,
                            "ext": _ext,
                        }
                    )
                    video.append(_video)
        return video
    return []


def get_buttons(listt):
    id = listt[0]["ytid"]
    butts = [
        Button.inline(
            text=f"[{x['quality']}"
            + (f" {humanbytes(x['size'])}]" if x.get("size") else "]"),
            data=f"ytdownload:{x['type']}:{x['id']}:{x['ytid']}"
            + (f":{x['ext']}" if x.get("ext") else ""),
        )
        for x in listt
    ]
    buttons = list(zip(butts[::2], butts[1::2]))
    if len(butts) % 2 == 1:
        buttons.append((butts[-1],))
    buttons.append([Button.inline("« Back", f"ytdl_back:{id}")])
    return buttons


async def dler(event, url, opts: dict = {}, download=False):
    await event.edit("`Getting Data...`")
    if "quiet" not in opts:
        opts["quiet"] = True
    opts.update(ytdl_opts(opts))
    if download:
        await ytdownload(url, opts)
    try:
        return await extract_info(url, opts)
    except Exception as e:
        LOGS.info(f"ytdl: {e}")
        await event.edit(yt_error_text(e))
        return


@run_async
def ytdownload(url, opts):
    try:
        return YoutubeDL(opts).download([url])
    except Exception as ex:
        LOGS.error(ex)


@run_async
def extract_info(url, opts):
    return YoutubeDL(opts).extract_info(url=url, download=False)


@run_async
def get_videos_link(url):
    to_return = []
    regex = re.search(r"\?list=([(\w+)\-]*)", url)
    if not regex:
        return to_return
    playlist_id = regex.group(1)
    opts = {"quiet": True, "skip_download": True, "extract_flat": "in_playlist"}
    try:
        info = YoutubeDL(ytdl_opts(opts)).extract_info(
            f"https://www.youtube.com/playlist?list={playlist_id}", download=False
        )
    except Exception as er:
        LOGS.info(f"get_videos_link: {er}")
        return to_return
    for vid in info.get("entries") or []:
        if vid and vid.get("id"):
            to_return.append(f"https://youtube.com/watch?v={vid['id']}")
    return to_return
