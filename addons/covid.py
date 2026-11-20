# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📖 **Commands**

• `{i}covid <country>`
    See COVID-19 numbers for a country.
"""

from . import async_searcher, ultroid_cmd


@ultroid_cmd(pattern="covid( (.*)|$)")
async def coronish(event):
    country = event.pattern_match.group(1).strip()
    if not country:
        return await event.eor("Give a country name to search for it's Covid Cases!")
    try:
        cases = await async_searcher(
            f"https://disease.sh/v3/covid-19/countries/{country}", re_json=True
        )
        if cases.get("message"):
            return await event.eor(f"It seems that Country {country} is invalid!")
    except Exception as er:
        return await event.eor(f"`Covid data service error: {er}`")
    await event.eor(
        f"**Country:** **{cases['country']}**\n"
        f"**Active:** {cases['active']}\n**Confirmed:** {cases['cases']}\n"
        f"**Recovered:** {cases['recovered']}\n**Deceased:** {cases['deaths']}\n\n"
        "__Note: most countries stopped reporting in 2023, numbers are final totals.__",
    )
