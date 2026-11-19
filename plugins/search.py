# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}saavn <search query>`
    Download songs from Saavn.

• `{i}google <query>`
    For doing google search.

• `{i}github <username>`
    Get full information of the users github profile.

• `{i}img <query>`
  `{i}img <query> ; <no of results>`
    For doing Images search.

• `{i}reverse`
    Reply an Image or sticker to find its sauce.
"""
import asyncio
import os
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup as bs

try:
    from PIL import Image
except ImportError:
    Image = None
try:
    import cv2
except ImportError:
    cv2 = None
from telethon.tl.types import DocumentAttributeAudio

from pyUltroid.fns.misc import google_search
from pyUltroid.fns.tools import get_google_images, saavn_search

from . import (
    LOGS,
    Button,
    async_searcher,
    cat_uploader,
    con,
    eod,
    fast_download,
    get_string,
    ultroid_cmd,
)


@ultroid_cmd(
    pattern="github (.*)",
)
async def gitsearch(event):
    usrname = event.pattern_match.group(1).strip()
    if not usrname:
        return await event.eor(get_string("srch_1"))
    url = f"https://api.github.com/users/{usrname}"
    ult = await async_searcher(url, re_json=True)
    try:
        uname = ult["login"]
        uid = ult["id"]
        upic = f"https://avatars.githubusercontent.com/u/{uid}"
        ulink = ult["html_url"]
        uacc = ult["name"]
        ucomp = ult["company"]
        ublog = ult["blog"]
        ulocation = ult["location"]
        ubio = ult["bio"]
        urepos = ult["public_repos"]
        ufollowers = ult["followers"]
        ufollowing = ult["following"]
    except BaseException:
        return await event.eor(get_string("srch_2"))
    fullusr = f"""
**[GITHUB]({ulink})**
**Name** - {uacc}
**UserName** - {uname}
**ID** - {uid}
**Company** - {ucomp}
**Blog** - {ublog}
**Location** - {ulocation}
**Bio** - {ubio}
**Repos** - {urepos}
**Followers** - {ufollowers}
**Following** - {ufollowing}
"""
    await event.respond(fullusr, file=upic)
    await event.delete()


@ultroid_cmd(
    pattern="google( (.*)|$)",
    manager=True,
)
async def google(event):
    inp = event.pattern_match.group(1).strip()
    if not inp:
        return await eod(event, get_string("autopic_1"))
    x = await event.eor(get_string("com_2"))
    gs = await google_search(inp)
    if not gs:
        return await eod(x, get_string("autopic_2").format(inp))
    out = ""
    for res in gs:
        text = res["title"]
        url = res["link"]
        des = res["description"]
        out += f" 👉🏻  [{text}]({url})\n`{des}`\n\n"
    omk = f"**Google Search Query:**\n`{inp}`\n\n**Results:**\n{out}"
    await x.eor(omk, link_preview=False)


@ultroid_cmd(pattern="img( (.*)|$)")
async def goimg(event):
    query = event.pattern_match.group(1).strip()
    if not query:
        return await event.eor(get_string("autopic_1"))
    nn = await event.eor(get_string("com_1"))
    lmt = 5
    if ";" in query:
        try:
            lmt = int(query.split(";")[1])
            query = query.split(";")[0]
        except BaseException:
            pass
    images = await get_google_images(query)
    for img in images[:lmt]:
        try:
            await event.client.send_file(event.chat_id, file=img["original"])
        except Exception as er:
            LOGS.exception(er)
    await nn.delete()


@ultroid_cmd(pattern="reverse$")
async def reverse(event):
    # Google's old "searchbyimage" endpoint was retired (it now redirects to
    # Lens and can't be scraped), so upload the image and link the engines.
    reply = await event.get_reply_message()
    if not (reply and (reply.photo or reply.sticker or reply.document)):
        return await event.eor("`Reply to an Image`")
    ult = await event.eor(get_string("com_1"))
    dl = await reply.download_media()
    file = await con.convert(dl, convert_to="png")
    try:
        img = Image.open(file)
        x, y = img.size
        link = await asyncio.to_thread(cat_uploader.upload_file, file)
    except Exception as er:
        LOGS.exception(er)
        return await ult.edit(f"`Failed to upload image: {er}`")
    finally:
        for path in {dl, file}:
            if path and os.path.exists(path):
                os.remove(path)
    enc = quote(link, safe="")
    buttons = [
        [Button.url("Google Lens", f"https://lens.google.com/uploadbyurl?url={enc}")],
        [
            Button.url(
                "Yandex", f"https://yandex.com/images/search?rpt=imageview&url={enc}"
            ),
            Button.url(
                "Bing", f"https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{enc}"
            ),
        ],
    ]
    await ult.edit(f"`Dimension ~ {x} : {y}`\nOpen a search engine below:", buttons=buttons)


@ultroid_cmd(
    pattern="saavn( (.*)|$)",
)
async def siesace(e):
    song = e.pattern_match.group(1).strip()
    if not song:
        return await e.eor("`Give me Something to Search", time=5)
    eve = await e.eor(f"`Searching for {song} on Saavn...`")
    try:
        data = (await saavn_search(song))[0]
    except (IndexError, TypeError, KeyError):
        return await eve.eor(f"`{song} not found on saavn.`")
    try:
        title = data["title"]
        url = data["url"]
        img = data["image"]
        duration = data["duration"]
        performer = data["artists"]
    except KeyError:
        return await eve.eor("`Something went wrong.`")
    song, _ = await fast_download(url, filename=f"{title}.m4a")
    thumb, _ = await fast_download(img, filename=f"{title}.jpg")
    song, _ = await e.client.fast_uploader(song, to_delete=True)
    await eve.eor(
        file=song,
        text=f"`{title}`\n`From Saavn`",
        attributes=[
            DocumentAttributeAudio(
                duration=int(duration),
                title=title,
                performer=performer,
            )
        ],
        supports_streaming=True,
        thumb=thumb,
    )
    await eve.delete()
    os.remove(thumb)
