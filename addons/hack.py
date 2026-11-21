# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📖 **Commands**

• `{i}hack <name>` (or reply to someone)
    A fake hacking animation. Just a prank - nothing is really hacked.
    Example: `{i}hack Rahul`
"""

import asyncio

from . import *


@ultroid_cmd(pattern="hack( (.*)|$)")
async def _(event):
    """Fake hack animation (same as the Fun Zone). Flood-safe: slow edits,
    stops at once if Telegram says wait."""
    import time

    from telethon.errors import FloodWaitError, MessageNotModifiedError

    from manager import fun as _zone

    name = event.pattern_match.group(1).strip()
    if not name and event.is_reply:
        reply = await event.get_reply_message()
        sender = await reply.get_sender()
        name = getattr(sender, "first_name", None) or ""
    frames = _zone.build("hack", name=name or "target", seed=int(time.time() * 1000))
    msg = await event.eor(frames[0])
    for frame in frames[1:]:
        await asyncio.sleep(2.5)
        try:
            await msg.edit(frame)
        except MessageNotModifiedError:
            continue
        except FloodWaitError:
            break
        except Exception:
            return
