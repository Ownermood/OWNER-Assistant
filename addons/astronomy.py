# Ultroid Userbot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}apod``
    Get Astronomy Picture of Day by NASA
"""


from . import async_searcher, udB, ultroid_cmd


@ultroid_cmd(pattern="apod$")
async def aposj(e):
    # NASA's official API (DEMO_KEY works without signup; set NASA_API for more).
    key = udB.get_key("NASA_API") or "DEMO_KEY"
    try:
        data = await async_searcher(
            "https://api.nasa.gov/planetary/apod", params={"api_key": key}, re_json=True
        )
        expla = data["explanation"]
    except Exception as E:
        return await eod(e, f"`APOD error: {E}`")
    if len(expla) > 900:
        expla = expla[:900] + "..."
    text = f"**{data.get('title', 'APOD')}**\n\n__{expla}__"
    img = data.get("url") if data.get("media_type") == "image" else None
    if not img and data.get("url"):
        text += f"\n\n{data['url']}"
    await e.reply(text, file=img)
    if e.out:
        await e.delete()
