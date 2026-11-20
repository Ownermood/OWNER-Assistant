# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/UltroidAddons/>

"""
📖 **Commands**

• `{i}aniquote`
    Get a random anime quote.
"""

from . import ultroid_cmd, async_searcher


@ultroid_cmd(pattern="aniquote$")
async def _(ult):
    u = await ult.eor("...")
    try:
        # animechan moved from animechan.vercel.app to animechan.io (v1 API).
        resp = (
            await async_searcher(
                "https://api.animechan.io/v1/quotes/random", re_json=True
            )
        )["data"]
        results = f"**{resp['content']}**\n"
        results += f" — __{resp['character']['name']} ({resp['anime']['name']})__"
        return await u.edit(results)
    except Exception:
        await u.edit("Something went wrong LOL ...")
