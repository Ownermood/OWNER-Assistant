# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from . import *
from pyUltroid.branding import BOT_NAME, BOT_NAME_CAPS, BOT_NAME_FANCY, BRAND_IMAGES, REPO_URL

STRINGS = {
    1: f"""🎇 **Thanks for Deploying {BOT_NAME}!**

• Here, are the Some Basic stuff from, where you can Know, about its Usage.""",
    2: f"""🎉** About {BOT_NAME}**

🧿 {BOT_NAME} is Pluggable and powerful Telethon Userbot, made in Python from Scratch. It is Aimed to Increase Security along with Addition of Other Useful Features.

❣ Based on **Ultroid** by @TeamUltroid""",
    3: """**💡• FAQs •**

-> [Username Tracker](https://t.me/UltroidUpdates/24)
-> [Keeping Custom Addons Repo](https://t.me/UltroidUpdates/28)
-> [Disabling Deploy message](https://t.me/UltroidUpdates/27)
-> [Setting up TimeZone](https://t.me/UltroidUpdates/22)
-> [About Inline PmPermit](https://t.me/UltroidUpdates/21)
-> [About Dual Mode](https://t.me/UltroidUpdates/18)
-> [Custom Thumbnail](https://t.me/UltroidUpdates/13)
-> [About FullSudo](https://t.me/UltroidUpdates/11)
-> [Setting Up PmBot](https://t.me/UltroidUpdates/2)
-> [Also Check](https://t.me/UltroidUpdates/14)

**• Updates**
  - Your repo: {REPO_URL}""".format(REPO_URL=REPO_URL),
    4: f"""• `To Know All Available Commands`

  - `{HNDLR}help`
  - `{HNDLR}cmds`""",
    5: f"""• **For Any Other Query or Suggestion**
  - Open an issue on your repo: {REPO_URL}/issues

• Thanks for Reaching till END.""",
}


@callback(re.compile("initft_(\\d+)"))
async def init_depl(e):
    CURRENT = int(e.data_match.group(1))
    if CURRENT == 5:
        return await e.edit(
            STRINGS[5],
            buttons=Button.inline("<< Back", "initbk_4"),
            link_preview=False,
        )

    await e.edit(
        STRINGS[CURRENT],
        buttons=[
            Button.inline("<<", f"initbk_{str(CURRENT - 1)}"),
            Button.inline(">>", f"initft_{str(CURRENT + 1)}"),
        ],
        link_preview=False,
    )


@callback(re.compile("initbk_(\\d+)"))
async def ineiq(e):
    CURRENT = int(e.data_match.group(1))
    if CURRENT == 1:
        return await e.edit(
            STRINGS[1],
            buttons=Button.inline("Start Back >>", "initft_2"),
            link_preview=False,
        )

    await e.edit(
        STRINGS[CURRENT],
        buttons=[
            Button.inline("<<", f"initbk_{str(CURRENT - 1)}"),
            Button.inline(">>", f"initft_{str(CURRENT + 1)}"),
        ],
        link_preview=False,
    )
