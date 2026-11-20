# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📖 **Commands**

• `{i}bored`
    Get an idea for something to do when you're bored.
"""

from . import async_searcher, ultroid_cmd


@ultroid_cmd(pattern="bored$")
async def bored_cmd(event):
    msg = await event.eor("Generating an Activity for you!")
    content = await async_searcher(
        "https://bored-api.appbrewery.com/random", re_json=True
    )
    m = f"**Activity:** `{content['activity']}`"
    if content.get("link"):
        m += f"\n**Read More:** {content['link']}"
    if content.get("participants"):
        m += f"\n**Participants Required:** `{content['participants']}`"
    if content.get("price"):
        m += f"\n**Price:** `{content['price']}`"
    await msg.edit(m)