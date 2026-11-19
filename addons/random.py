#
# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `Get some Random Content.`

• `{i}random dog`
• `{i}random duck`
• `{i}random cat`
• `{i}random fox`
• `{i}random quote`
• `{i}random word`
• `{i}random quotable`
• `{i}random celebrity`
"""

from bs4 import BeautifulSoup as bs
import re

from . import HNDLR, async_searcher, ultroid_cmd

# These Api's are Collected From
# ---- https://github.com/public-apis/public-apis

API_LIST = {
    "cat": "https://api.thecatapi.com/v1/images/search",
    "dog": "https://random.dog/woof.json",
    "duck": "https://random-d.uk/api/random",
    "fox": "https://randomfox.ca/floof/",
#   "funfact": "https://asli-fun-fact-api.herokuapp.com/",
    "quote": "https://api.themotivate365.com/stoic-quote",
    "quotable": "https://zenquotes.io/api/random",
#   "words": "https://random-word-api.herokuapp.com/word?number=10",
#   "food": "https://foodish-api.herokuapp.com/api/",
}

SCRAP_LIST = {
    "celebrity": "https://www.randomcelebritygenerator.com/",
    "word": "https://randomword.com/",
}


@ultroid_cmd(pattern="random( (.*)|$)")
async def random_magic(event):
    match = event.pattern_match.group(1).strip()
    if not (match and match in [*list(API_LIST.keys()), *list(SCRAP_LIST.keys())]):
        return await event.eor(f"`Input Missing/Wrong..`\n`{HNDLR}help random`")
    text, bsC, file = None, None, None
    ret = match in SCRAP_LIST
    try:
        req = await async_searcher(
            API_LIST.get(match) or SCRAP_LIST.get(match),
            re_json=not ret,
            re_content=ret,
        )
    except Exception as er:
        return await event.eor(str(er))
    try:
        text, file = _parse(match, req, ret)
    except Exception as er:
        return await event.eor(f"`Couldn't get {match}: {er}`")
    if text and not file:
        return await event.eor(text)
    await event.reply(text, file=file)
    await event.delete()


def _parse(match, req, ret):
    text, file, bsC = None, None, None
    if ret:
        bsC = bs(req, "html.parser", from_encoding="utf-8")
    if match == "cat":
        file = req[0]["url"]
    elif match in ["dog", "duck"]:
        file = req["url"]
    elif match in ["fox", "food"]:
        file = req["image"]
    elif match == "funfact":
        text = req["data"]["fact"]
    elif match == "quote":
        text = f"**{req['data']['quote']}**\n\n~ {req['data']['author']}"
    elif match == "quotable":
        text = f'`{req[0]["q"]}`' + f" ~ `{req[0]['a']}`"
    elif match == "word":
        req = req.decode("utf-8")
        word = re.search(r'<div id="random_word">([^<]+)</div>', req).group(1)
        definition = re.search(r'<div id="random_word_definition">([^<]*)</div>', req).group(1)
        text = f"**Random Word**\n- `{word}` : `{definition}`"
    elif match == "words":
        text = "**• Random Words**\n\n"
        for word in req:
            text += f"--`{word}`\n"
    elif match == "celebrity" and bsC:
        file = SCRAP_LIST[match] + bsC.find("img", "featured-celebrity-image")["src"]
        name = bsC.find("div", "info").find("h1").text
        text = f"• **Name :** `{name}`\n"
        desc = bsC.find("p", "fame").text.replace("\n", "")
        text += f"  - __{desc}__\n\n"
        bd = bsC.find("p", "birth-dates").text.replace("\n", "")
        text += f"• **Birth Dates :** {bd}\n"
        text += "-" * 10
    return text, file
