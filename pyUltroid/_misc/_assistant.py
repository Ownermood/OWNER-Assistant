# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import inspect
import re
from traceback import format_exc

from telethon import Button
from telethon.errors import QueryIdInvalidError
from telethon.events import CallbackQuery, InlineQuery, NewMessage
from telethon.tl.types import InputWebDocument

from .. import LOGS, asst, udB, ultroid_bot
from ..fns.admins import admin_check
from . import append_or_update, owner_and_sudos
from ..branding import BOT_NAME, BRAND_IMAGES, assistant_buttons

OWNER = ultroid_bot.full_name

MSG = f"""
**OWNER Assistant**
➖➖➖➖➖➖➖➖➖➖
**Owner**: [{OWNER}](tg://user?id={ultroid_bot.uid})
➖➖➖➖➖➖➖➖➖➖
"""



# decorator for assistant


def asst_cmd(pattern=None, load=None, owner=False, **kwargs):
    """Decorator for assistant's command"""
    name = inspect.stack()[1].filename.split("/")[-1].replace(".py", "")
    kwargs["forwards"] = False

    def ult(func):
        if pattern:
            kwargs["pattern"] = re.compile(f"^/{pattern}")

        async def handler(event):
            if owner and event.sender_id not in owner_and_sudos():
                return
            try:
                await func(event)
            except Exception as er:
                LOGS.exception(er)

        asst.add_event_handler(handler, NewMessage(**kwargs))
        if load is not None:
            append_or_update(load, func, name, kwargs)

    return ult


def callback(data=None, from_users=[], admins=False, owner=False, **kwargs):
    """Assistant's callback decorator"""
    if "me" in from_users:
        from_users.remove("me")
        from_users.append(ultroid_bot.uid)

    def ultr(func):
        async def wrapper(event):
            if admins and not await admin_check(event):
                return
            if from_users and event.sender_id not in from_users:
                return await event.answer("Not for You!", alert=True)
            if owner and event.sender_id not in owner_and_sudos():
                return await event.answer(f"This is {OWNER}'s bot!!")
            try:
                await func(event)
            except Exception as er:
                LOGS.exception(er)

        asst.add_event_handler(wrapper, CallbackQuery(data=data, **kwargs))

    return ultr


def in_pattern(pattern=None, owner=False, **kwargs):
    """Assistant's inline decorator."""

    def don(func):
        async def wrapper(event):
            if owner and event.sender_id not in owner_and_sudos():
                res = [
                    await event.builder.article(
                        title=BOT_NAME,
                        description=f"(c) {OWNER}",
                        text=MSG,
                        thumb=InputWebDocument(
                            BRAND_IMAGES[0],
                            0,
                            "image/jpeg",
                            [],
                        ),
                        buttons=assistant_buttons(),
                    )
                ]
                return await event.answer(
                    res,
                    switch_pm=f"🤖: Assistant of {OWNER}",
                    switch_pm_param="start",
                )
            try:
                await func(event)
            except QueryIdInvalidError:
                pass
            except Exception as er:
                err = format_exc()

                def error_text():
                    return f"**#ERROR #INLINE**\n\nQuery: `{asst.me.username} {pattern}`\n\n**Traceback:**\n`{err}`"

                LOGS.exception(er)
                # full error goes to the log group only, never into the chat
                try:
                    await asst.send_message(udB.get_key("LOG_CHANNEL"), error_text()[:4000])
                except Exception as er2:
                    LOGS.exception(er2)
                try:
                    await event.answer(
                        [
                            await event.builder.article(
                                title="Something went wrong",
                                description="Details were sent to your log group.",
                                text="`Something went wrong. Details are in the log group.`",
                            )
                        ]
                    )
                except Exception:
                    LOGS.exception(err)

        asst.add_event_handler(wrapper, InlineQuery(pattern=pattern, **kwargs))

    return don
