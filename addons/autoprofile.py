#
# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# Ported Plugin

"""
✘ Commands Available -

• `{i}autoname`
   `Starts AUTONAME`.

• `{i}stopname`
   `Stops AUTONAME.`

• `{i}autobio`
   `Starts AUTOBIO.`

• `{i}stopbio`
   `Stops AUTOBIO.`
"""

import asyncio
import random
import time

from telethon.tl.functions.account import UpdateProfileRequest

from . import *

BIOS = [
    "Busy Today !",
    "ULTROID USER",
    "Enjoying Life!",
    "Unique as Always!",
    "Sprinkling a bit of magic",
    "Intelligent !",
]
_TASKS = {}


async def _name_loop():
    while udB.get_key("AUTONAME"):
        DM = time.strftime("%d-%m-%y")
        HM = time.strftime("%H:%M")
        try:
            await ultroid_bot(
                UpdateProfileRequest(first_name=f"🕒{HM} ⚡{OWNER_NAME}⚡ {DM} 🗓️"[:64])
            )
        except Exception as er:
            LOGS.info(f"autoname: {er}")
        await asyncio.sleep(1111)


async def _bio_loop():
    while udB.get_key("AUTOBIO"):
        DM = time.strftime("%d-%m-%y")
        HM = time.strftime("%H:%M")
        try:
            await ultroid_bot(
                UpdateProfileRequest(about=f"📅{DM} | {random.choice(BIOS)} | ⌚️{HM}"[:70])
            )
        except Exception as er:
            LOGS.info(f"autobio: {er}")
        await asyncio.sleep(1111)


def _start(key, func):
    task = _TASKS.get(key)
    if task and not task.done():
        return
    _TASKS[key] = asyncio.get_event_loop().create_task(func())


@ultroid_cmd(pattern="(auto|stop)name$")
async def autoname_(event):
    if event.pattern_match.group(1) == "stop":
        udB.del_key("AUTONAME")
        return await event.eor("`AUTONAME has been Stopped !`")
    udB.set_key("AUTONAME", "True")
    _start("AUTONAME", _name_loop)
    await eod(event, "`Started AUTONAME`")


@ultroid_cmd(pattern="(auto|stop)bio$")
async def autobio_(event):
    if event.pattern_match.group(1) == "stop":
        udB.del_key("AUTOBIO")
        return await event.eor("`AUTOBIO has been Stopped !`")
    udB.set_key("AUTOBIO", "True")
    _start("AUTOBIO", _bio_loop)
    await eod(event, "`Started AUTOBIO`")


# Resume after a restart.
if udB.get_key("AUTONAME"):
    _start("AUTONAME", _name_loop)
if udB.get_key("AUTOBIO"):
    _start("AUTOBIO", _bio_loop)
