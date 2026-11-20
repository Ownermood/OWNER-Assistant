# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re

from telethon import Button
from telethon.errors.rpcerrorlist import (
    BotInlineDisabledError,
    BotResponseTimeoutError,
    ChatSendInlineForbiddenError,
    MessageNotModifiedError,
)
from telethon.tl import types
from telethon.tl.functions.users import GetFullUserRequest as gu

from . import (
    HNDLR,
    LOGS,
    udB,
    asst,
    callback,
    get_string,
    in_pattern,
    inline_mention,
    ultroid_bot,
    ultroid_cmd,
)

class _Whispers(dict):
    """Whispers survive restarts (kept in the DB, last 300 only)."""

    def __init__(self):
        super().__init__()
        try:
            for k, v in (udB.get_key("WHISPERS") or {}).items():
                self[int(k)] = v
        except Exception as er:
            LOGS.info(f"whispers: {er}")

    def _save(self):
        keep = dict(list(self.items())[-300:])
        if len(keep) != len(self):
            self.clear()
            dict.update(self, keep)
        udB.set_key("WHISPERS", {str(k): v for k, v in keep.items()})

    def update(self, *a, **k):
        dict.update(self, *a, **k)
        self._save()

    def pop(self, *a):
        val = dict.pop(self, *a)
        self._save()
        return val


buddhhu = _Whispers()
ALERT_LIMIT = 200  # Telegram shows at most 200 characters in a pop-up


@ultroid_cmd(
    pattern="wspr( (.*)|$)",
)
async def _(e):
    args = e.pattern_match.group(1).strip()
    text = ""
    if e.reply_to_msg_id:
        okk = await e.get_reply_message()
        sender = await okk.get_sender()
        put = f"@{sender.username}" if getattr(sender, "username", None) else str(okk.sender_id)
        text = args
    else:
        put, _, text = args.partition(" ")
        text = text.strip()
    if not put:
        return await e.eor(get_string("wspr_3"))
    try:
        user = await e.client.get_entity(int(put) if put.lstrip("-").isdigit() else put)
        if not isinstance(user, types.User):
            raise ValueError("not a user")
    except Exception:
        return await e.eor(
            f"`User {put} not found.`\nCheck the @username (it may have changed), "
            "or reply to their message with `.wspr <message>`.",
            time=10,
        )
    put = str(user.id)
    if len(text) > ALERT_LIMIT:
        return await e.eor(
            f"`Whisper too long ({len(text)}/{ALERT_LIMIT} characters). Telegram allows {ALERT_LIMIT}.`",
            time=8,
        )
    # with a message: send the whisper straight away; without: show the user card
    query = f"wspr {put} {text}" if text else f"msg {put}"
    try:
        results = await e.client.inline_query(asst.me.username, query)
    except BotResponseTimeoutError:
        return await e.eor(get_string("help_2").format(HNDLR))
    except BotInlineDisabledError:
        return await e.eor(get_string("help_3"))
    if not results:
        return await e.eor("`Assistant bot gave no result, try again.`", time=5)
    try:
        await results[0].click(e.chat_id, reply_to=e.reply_to_msg_id, hide_via=True)
    except ChatSendInlineForbiddenError:
        return await e.eor(
            "`This group does not allow inline bots.` Ask an admin to allow "
            "\"Send inline bots\" (or \"Embed links\") for members, or make yourself admin."
        )
    await e.delete()


@in_pattern("wspr", owner=True)
async def _(e):
    iuser = e.query.user_id
    zzz = e.text.split(maxsplit=2)
    try:
        query = zzz[1]
        if query.isdigit():
            query = int(query)
        logi = await ultroid_bot.get_entity(query)
        if not isinstance(logi, types.User):
            raise ValueError("Invalid Username.")
    except IndexError:
        sur = await e.builder.article(
            title="Give Username",
            description="You Didn't Type Username or id.",
            text="You Didn't Type Username or id.",
        )
        return await e.answer([sur])
    except Exception as er:
        LOGS.info(f"wspr: {er}")
        sur = await e.builder.article(
            title="User Not Found",
            description="Make sure username or id is correct.",
            text="Make sure username or id is correct.",
        )
        return await e.answer([sur])
    try:
        desc = zzz[2][:ALERT_LIMIT]
    except IndexError:
        sur = await e.builder.article(
            title="Type ur msg", text="You Didn't Type Your Msg"
        )
        return await e.answer([sur])
    button = [
        [
            Button.inline("Secret Msg", data=f"dd_{e.id}"),
            Button.inline("Delete Msg", data=f"del_{e.id}"),
        ],
        [
            Button.switch_inline(
                "New", query=f"wspr {logi.username or logi.id}", same_peer=True
            )
        ],
    ]
    if logi.username:
        wtext = get_string("wspr_1").format(logi.username)
    else:  # no username: show the plain name, without a wrong "@"
        name = (logi.first_name or "someone").replace("`", "").replace("*", "").replace("_", "")
        wtext = get_string("wspr_1").replace("@{}", "{}").format(name)
    sur = await e.builder.article(
        title=f"Whisper to {logi.first_name}",
        description=desc,
        text=wtext,
        buttons=button,
    )
    buddhhu.update({e.id: [logi.id, iuser, desc]})
    await e.answer([sur])


@in_pattern("msg", owner=True)
async def _(e):
    zzz = e.text.split(maxsplit=2)
    desc = "Touch me"
    try:
        query = zzz[1]
        if query.isdigit():
            query = int(query)
        logi = await ultroid_bot(gu(id=query))
        user = logi.users[0]
        mention = inline_mention(user)
        x = user.status
        if isinstance(x, types.UserStatusOnline):
            status = "Online"
        elif isinstance(x, types.UserStatusOffline):
            status = "Offline"
        elif isinstance(x, types.UserStatusRecently):
            status = "Last Seen Recently"
        elif isinstance(x, types.UserStatusLastMonth):
            status = "Last seen months ago"
        elif isinstance(x, types.UserStatusLastWeek):
            status = "Last seen weeks ago"
        else:
            status = "Can't Tell"
        text = f"**Name:**    `{user.first_name}`\n"
        text += f"**Id:**    `{user.id}`\n"
        if user.username:
            text += f"**Username:**    `{user.username}`\n"
            url = f"https://t.me/{user.username}"
        else:
            text += f"**Mention:**    `{mention}`\n"
            url = f"tg://user?id={user.id}"
        text += f"**Status:**    `{status}`\n"
        text += f"**About:**    `{logi.full_user.about}`"
        button = [
            Button.url("Private", url=url),
            Button.switch_inline(
                "Secret msg",
                query=f"wspr {query} Hello 👋",
                same_peer=True,
            ),
        ]
        sur = e.builder.article(
            title=user.first_name,
            description=desc,
            text=text,
            buttons=button,
        )
    except IndexError:
        sur = e.builder.article(
            title="Give Username",
            description="You Didn't Type Username or id.",
            text="You Didn't Type Username or id.",
        )
    except BaseException as er:
        LOGS.exception(er)
        name = get_string("wspr_4").format(query)
        sur = e.builder.article(
            title=name,
            text=name,
        )

    await e.answer([sur])


@callback(
    re.compile(
        "dd_(.*)",
    ),
)
async def _(e):
    ids = int(e.pattern_match.group(1).strip().decode("UTF-8"))
    if buddhhu.get(ids):
        if e.sender_id in buddhhu[ids]:
            await e.answer(buddhhu[ids][-1], alert=True)
        else:
            await e.answer("Not For You", alert=True)
    else:
        await e.answer(get_string("wspr_2"), alert=True)


@callback(re.compile("del_(.*)"))
async def _(e):
    ids = int(e.pattern_match.group(1).strip().decode("UTF-8"))
    if buddhhu.get(ids):
        if e.sender_id in buddhhu[ids]:
            buddhhu.pop(ids)
            try:
                await e.edit(get_string("wspr_2"))
            except MessageNotModifiedError:
                pass
        else:
            await e.answer(get_string("wspr_5"), alert=True)
