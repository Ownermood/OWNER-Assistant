# credit https://t.me/I_m_FlaSh

"""
📖 **Commands**

• `{i}totalmsgs`
    See how many messages you've sent in this chat.

• `{i}totalmsgs <username>` (or reply to someone)
    See how many messages they've sent here.
"""

from telethon.utils import get_display_name

from . import *


@ultroid_cmd(pattern="totalmsgs( (.*)|$)")
async def _(e):
    match = e.pattern_match.group(1).strip()
    if match:
        user = match
    elif e.is_reply:
        user = (await e.get_reply_message()).sender_id
    else:
        user = "me"
    try:
        a = await e.client.get_messages(e.chat_id, limit=0, from_user=user)
    except Exception as er:
        return await e.eor(str(er))
    try:
        user = await e.client.get_entity(user)
    except Exception as er:
        return await e.eor(str(er))
    await e.eor(f"Total msgs of `{get_display_name(user)}` here = {a.total}")
