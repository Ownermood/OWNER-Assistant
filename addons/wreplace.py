# credits to @Harpia-Vieillot
# For @TeamUltroid
"""
📖 **Commands**

• `{i}wreplace <how many messages> <old word>;<new word>`
    Replace a word in your own recent messages.
    Example: `{i}wreplace 10 Hi;Hello` changes 'Hi' to 'Hello' in your last 10 messages.
"""

import asyncio

from . import *
from telethon.errors.rpcerrorlist import InlineBotRequiredError


@ultroid_cmd(pattern="wreplace( (.*)|$)")
async def harpia(e):
    try:
        sed = e.text.split(" ", 1)[1]
        lst = sed.split(" ", 1)
        lmt = int(lst[0]) + 1
        pist = lst[1].split(";")
        _ = pist[1]
    except (IndexError, ValueError):
        return await eod(e, f"Check Example : `{HNDLR}help wreplace`")
    msg = await e.eor("Processing...")
    async for x in e.client.iter_messages(
        e.chat_id, search=pist[0], limit=lmt, from_user="me"
    ):
        try:
            msg = x.text
            m = msg.replace(pist[0], pist[1])
            await x.edit(m)
            await asyncio.sleep(1)
        except InlineBotRequiredError:
            pass
    await eod(msg, "Finished.")
