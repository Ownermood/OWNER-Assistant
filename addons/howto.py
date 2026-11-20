# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📖 **Commands**

• `{i}htg <question>`
    Send a 'let me Google that for you' link.

• `{i}htd <question>`
    Same, with DuckDuckGo.
"""


from urllib.parse import quote_plus

from . import ultroid_cmd, async_searcher


API = {"g": "lmgtfy.app/?q={}", "d": "duckduckgo.com/?q={}"}


@ultroid_cmd(pattern="ht(g|d)( ?(.*)|$)")
async def _(e):
    key = e.pattern_match.group(1)
    text = (e.pattern_match.group(2) or "").strip()
    if not text:
        return await e.eor("Give some text", time=5)
    target = "https://" + API[key].format(quote_plus(text))
    try:
        response = await async_searcher("https://da.gd/s", params={"url": target})
    except Exception:
        response = target
    if response:
        return await e.eor(
            "[{}]({})\n`Thank me Later 🙃` ".format(text, response.rstrip()), time=8
        )
    await e.eor("something is wrong. please try again later.")
