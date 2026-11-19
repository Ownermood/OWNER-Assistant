# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}eod`
    `Get Event of the Today`

• `{i}pntrst <link/id>`
    Download and send pinterest pins

• `{i}gadget <search query>`
    Gadget Search from Telegram.

• `{i}randomuser`
   Generate details about a random user.

• `{i}ascii <reply image>`
    Convert replied image into html.
"""

import asyncio
import os
from datetime import datetime as dt

from bs4 import BeautifulSoup as bs

try:
    from htmlwebshot import WebShot
except ImportError:
    WebShot = None
try:
    from img2html.converter import Img2HTMLConverter
except ImportError:
    Img2HTMLConverter = None

from . import async_searcher, get_random_user_data, get_string, re, ultroid_cmd


@ultroid_cmd(pattern="eod$")
async def diela(e):
    m = await e.eor(get_string("com_1"))
    li = "https://daysoftheyear.com"
    te = "🎊 **Events of the Day**\n\n"
    da = dt.now()
    month = da.strftime("%b")
    li += f"/days/{month}/" + da.strftime("%F").split("-")[2]
    ct = await async_searcher(li, re_content=True)
    bt = bs(ct, "html.parser", from_encoding="utf-8")
    ml = bt.find_all("a", "js-link-target", href=re.compile("daysoftheyear.com/days"))
    for eve in ml[:5]:
        te += f'• [{eve.text}]({eve["href"]})\n'
    await m.edit(te, link_preview=False)


@ultroid_cmd(
    pattern="pntrst( (.*)|$)",
)
async def pinterest(e):
    m = e.pattern_match.group(1).strip()
    if not m:
        return await e.eor("`Give pinterest link.`", time=3)
    msg = await e.eor(get_string("com_1"))
    try:
        from yt_dlp import YoutubeDL

        def _get():
            with YoutubeDL({"quiet": True, "outtmpl": "resources/downloads/%(id)s.%(ext)s"}) as ydl:
                info = ydl.extract_info(m, download=True)
                if info.get("entries"):
                    info = info["entries"][0]
                return ydl.prepare_filename(info)

        file = await asyncio.to_thread(_get)
    except Exception as er:
        return await msg.edit(f"`Wrong link or private pin.`\n`{er}`")
    await e.client.send_file(e.chat_id, file, caption=f"Pin:- {m}")
    await msg.delete()
    if os.path.exists(file):
        os.remove(file)


@ultroid_cmd(pattern="gadget( (.*)|$)")
async def mobs(e):
    mat = e.pattern_match.group(1).strip()
    if not mat:
        await e.eor("Please Give a Mobile Name to look for.")
    query = mat.replace(" ", "%20")
    jwala = f"https://gadgets.ndtv.com/search?searchtext={query}"
    c = await async_searcher(jwala)
    b = bs(c, "html.parser", from_encoding="utf-8")
    co = b.find_all("div", "rvw-imgbox")
    if not co:
        return await e.eor("No Results Found!")
    bt = await e.eor(get_string("com_1"))
    out = "**📱 Mobile / Gadgets Search**\n\n"
    li = co[0].find("a")
    imu, title = None, li.find("img")["title"]
    cont = await async_searcher(li["href"])
    nu = bs(cont, "html.parser", from_encoding="utf-8")
    req = nu.find_all("div", "_pdsd")
    imu = nu.find_all(
        "img", src=re.compile("https://i.gadgets360cdn.com/products/large/")
    )
    if imu:
        imu = imu[0]["src"].split("?")[0] + "?downsize=*:420&output-quality=80"
    out += f"☑️ **[{title}]({li['href']})**\n\n"
    for fp in req:
        ty = fp.findNext()
        out += f"- **{ty.text}** - `{ty.findNext().text}`\n"
    out += "_"
    if imu == []:
        imu = None
    await e.reply(out, file=imu, link_preview=False)
    await bt.delete()


@ultroid_cmd(pattern="randomuser")
async def _gen_data(event):
    x = await event.eor(get_string("com_1"))
    msg, pic = await get_random_user_data()
    await event.reply(file=pic, message=msg)
    await x.delete()


@ultroid_cmd(
    pattern="ascii( (.*)|$)",
)
async def _(e):
    if not Img2HTMLConverter:
        return await e.eor("'img2html-converter' not installed!")
    if not e.reply_to_msg_id:
        return await e.eor(get_string("ascii_1"))
    m = await e.eor(get_string("ascii_2"))
    img = await (await e.get_reply_message()).download_media()
    char = e.pattern_match.group(1).strip() or "■"
    converter = Img2HTMLConverter(char=char)
    html = converter.convert(img)
    shot = WebShot(quality=85)
    pic = await shot.create_pic_async(html=html)
    await m.delete()
    await e.reply(file=pic)
    os.remove(pic)
    os.remove(img)
