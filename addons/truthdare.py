# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📖 **Commands**

• `{i}truth`
    Get a truth question.

• `{i}dare`
    Get a dare.
"""


from . import *

# Free keyless API (the old fungenerators.com scraping broke).
API = "https://api.truthordarebot.xyz/v1/{}"


async def _get(kind):
    try:
        res = await async_searcher(API.format(kind), params={"rating": "pg13"}, re_json=True)
        return res["question"]
    except Exception:
        return None


@ultroid_cmd(pattern="truth$")
async def gtruth(ult):
    m = await ult.eor("Generating a Truth Statement.. ")
    cm = await _get("truth")
    if not cm:
        return await m.edit("Service is down, try again later.")
    await m.edit(f"**#TruthTask**\n\n`{cm}`")


@ultroid_cmd(pattern="dare$")
async def gdare(ult):
    m = await ult.eor("Generating a Dare Task.. ")
    cm = await _get("dare")
    if not cm:
        return await m.edit("Service is down, try again later.")
    await m.edit(f"**#DareTask**\n\n`{cm}`")
