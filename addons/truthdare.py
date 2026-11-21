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


import time

from manager import fun as _zone

from . import *

# Offline, same questions as the manager bot's Fun Zone (the old web API died).


@ultroid_cmd(pattern="truth$")
async def gtruth(ult):
    await ult.eor(_zone.build("truth", seed=int(time.time() * 1000))[-1])


@ultroid_cmd(pattern="dare$")
async def gdare(ult):
    await ult.eor(_zone.build("dare", seed=int(time.time() * 1000))[-1])
