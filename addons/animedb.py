# Made by : @Arnab431 || github.com/ArnabXD
# Made For : https://github.com/TeamUltroid/UltroidAddons

"""
📖 **Commands**

• `{i}manga <name>`
    Get details about a manga (from anilist.co).
"""


from . import *


@ultroid_cmd(
    pattern="manga(?: |$)(.*)",
)
async def manga(ult):
    msg = await ult.eor("Searching ...")
    keyword = ult.pattern_match.group(1)
    if not keyword:
        return await msg.edit("Provide a Keyword to search")
    try:
        animes = await ult.client.inline_query("animedb_bot", f"<m> {keyword}")
        await animes[0].click(
            ult.chat_id,
            reply_to=ult.reply_to_msg_id,
            silent=True if ult.is_reply else False,
            hide_via=True,
        )
        return await msg.delete()
    except Exception:
        return await msg.edit("No results found ...")
