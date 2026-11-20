# Ultroid Userbot
# <https://github.com/TeamUltroid/UltroidAddons/tree/main/imdb.py>

"""
📖 **Commands**

• `{i}imdb <movie name>`
    Get a movie's details from IMDb.
"""

from . import *


@ultroid_cmd(pattern="imdb( (.*)|$)")
async def imdb(e):
    m = await e.eor("...")
    movie_name = e.pattern_match.group(1).strip()
    if not movie_name:
        return await eor(m, "Provide a movie name too")
    try:
        mk = await e.client.inline_query("imdbot", movie_name)
        await mk[0].click(e.chat_id)
        await m.delete()
    except IndexError:
        return await eor(m, "No results found.")
    except Exception as er:
        return await eor(m, str(er))