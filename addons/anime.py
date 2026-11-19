# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}character <character name>`
   Fetch anime character details.
"""

from . import *


@ultroid_cmd(pattern="character( (.*)|$)")
async def anime_char_search(event):
    char_name = event.pattern_match.group(1).strip()
    if not char_name:
        return await event.eor("`Enter the name of a character too please!`", time=5)
    xx = await event.eor(get_string("com_1"))
    try:
        res = await async_searcher(
            "https://api.jikan.moe/v4/characters",
            params={"q": char_name, "limit": 1, "order_by": "favorites", "sort": "desc"},
            re_json=True,
        )
        char_json = res["data"][0]
    except Exception:
        return await eod(xx, "`Couldn't find character!`", time=5)
    pic = char_json.get("images", {}).get("jpg", {}).get("image_url")
    msg = f"**[{char_json['name']}]({char_json['url']})**"
    if char_json.get("name_kanji"):
        msg += f" [{char_json['name_kanji']}]\n"
    else:
        msg += "\n"
    if char_json.get("nicknames"):
        msg += f"\n**Nicknames** : `{', '.join(char_json['nicknames'])}`\n"
    about = (char_json.get("about") or "No info.").split("\n", 1)[0].strip()
    msg += f"\n**About**: __{about[:800]}__"
    await event.reply(msg, file=pic, force_document=False)
    await xx.delete()
