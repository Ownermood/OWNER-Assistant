# (c) Shrimadhav U.K
# aka Spechide
#
# Ported for Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}type <msg>`
    Edits the Message and shows like someone is typing.
"""

import asyncio

from telethon.errors import FloodWaitError

from . import *


@ultroid_cmd(pattern="type( (.*)|$)", fullsudo=True)
async def _(event):
    input_str = event.pattern_match.group(1).strip()[:200]
    if not input_str:
        return await event.eor("Give me something to type !")
    shiiinabot = "\u2060" * 602
    okla = await event.eor(shiiinabot)
    typing_symbol = "|"
    previous_text = ""
    await okla.edit(typing_symbol)
    await asyncio.sleep(0.4)
    # One edit per word chunk: per-letter double edits hit Telegram's FloodWait.
    step = max(1, len(input_str) // 25)
    for i in range(step, len(input_str) + step, step):
        previous_text = input_str[:i]
        try:
            await okla.edit(previous_text + typing_symbol)
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
        except Exception:
            pass
        await asyncio.sleep(0.6)
    await okla.edit(input_str)
