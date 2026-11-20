# OWNER Assistant - premium emoji commands.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).

"""
✘ Commands Available -

• `{i}pemoji` (reply to a message that has premium emojis)
    Save those premium emojis. After this, the bot's messages
    (alive, ping, help, ...) use them automatically.

• `{i}pemoji pack <link1> <link2> ...`
    Save whole premium emoji packs - many at once (up to 25).
    Put links on new lines or with spaces, or reply to a message
    that has the links. If two packs have the same emoji, the
    LAST pack wins.

• `{i}pemoji`
    Status + list of saved emojis.

• `{i}pemoji del <emoji>`  /  `{i}pemoji clear`
    Remove one / all saved emojis.

• `{i}pemoji on`  /  `{i}pemoji off`
    Turn the automatic premium emojis on or off.

• `{i}pemoji bot on`  /  `{i}pemoji bot off`
    Also use them in the assistant bot's messages
    (works only if Telegram allows it for your bot - see note).

• `{i}pemoji test`
    Send a sample message to see how it looks.

Note: premium emojis need Telegram Premium on your account.
Without Premium, normal emojis are shown (nothing breaks).
"""

import asyncio
import re

from telethon.errors import FloodWaitError, RPCError
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import DocumentAttributeCustomEmoji, InputStickerSetShortName

from pyUltroid.fns import pemoji as pe

from . import HNDLR, LOGS, asst, udB, ultroid_bot, ultroid_cmd

# Hook both clients once (the text parser upgrades emojis on send/edit).
pe.install(ultroid_bot)
if asst is not None and asst is not ultroid_bot:
    pe.install(asst, bot=True)

SAMPLE = (
    "✨ **OWNER Assistant** ✨\n\n"
    "👑 Owner  ⚡ Fast  🔥 Hot  ✅ Done  ❌ No\n"
    "❤️ Love  🎉 Party  🤖 Bot  ⏳ Time  🚀 Go"
)


def _premium():
    return bool(getattr(ultroid_bot.me, "premium", False))


def _shown(mapping):
    # each emoji is stored with and without the hidden FE0F; show it once
    return sorted({k for k in mapping if not (k + "\ufe0f") in mapping})


def _saved_count():
    return len(_shown(pe.get_map()))


def _status():
    mapping = pe.get_map()
    shown = _shown(mapping)
    lines = [
        "💎 **Premium Emoji**",
        "",
        f"• Your account Premium: {'✅ Yes' if _premium() else '❌ No (normal emojis will show)'}",
        f"• Auto upgrade: {'❌ Off' if udB.get_key(pe.OFF_KEY) else '✅ On'}",
        f"• In assistant bot: {'✅ On' if udB.get_key(pe.BOT_KEY) else '❌ Off'}",
        f"• Saved: `{len(shown)}`",
    ]
    if shown:
        lines += ["", " ".join(shown[:100])]
    else:
        lines += [
            "",
            f"Nothing saved yet. Send a message with premium emojis, reply to it with `{HNDLR}pemoji`,",
            f"or use `{HNDLR}pemoji pack <link>`.",
        ]
    return "\n".join(lines)


MAX_PACKS = 25


def _pack_names(text, links_only=False):
    """All pack names from links (t.me/addemoji/X) or plain names, in order."""
    names = []
    for word in re.split(r"[\s,]+", text or ""):
        word = word.strip()
        if not word:
            continue
        m = re.search(r"(?:t\.me|telegram\.me)/(?:addemoji|addstickers)/(\w+)", word)
        if m:
            name = m.group(1)
        elif not links_only and re.fullmatch(r"[A-Za-z]\w{0,63}", word):
            name = word
        else:
            continue
        if name not in names:
            names.append(name)
    return names


@ultroid_cmd(pattern="pemoji( (.*)|$)")
async def pemoji_cmd(event):
    arg = (event.pattern_match.group(2) or "").strip()
    low = arg.lower()

    if not arg and event.is_reply:
        reply = await event.get_reply_message()
        pairs = pe.extract(reply)
        if not pairs:
            return await event.eor(
                "❌ That message has no premium emojis.\n"
                "Send premium emojis (from your Premium account) and reply to them."
            )
        n = pe.add_pairs(pairs)
        return await event.eor(
            f"✅ Saved `{n}` premium emoji(s): " + " ".join(dict.fromkeys(c for c, _ in pairs))
        )

    if low.startswith("pack"):
        # whole message (links may be on new lines), text after the word "pack"
        full = event.raw_text or arg
        text = re.split(r"(?i)\bpack\b", full, maxsplit=1)[-1]
        names = _pack_names(text)
        if event.is_reply:
            reply = await event.get_reply_message()
            for n in _pack_names(getattr(reply, "message", None) or "", links_only=True):
                if n not in names:
                    names.append(n)
        if not names:
            return await event.eor(
                f"Usage: `{HNDLR}pemoji pack t.me/addemoji/Pack1 t.me/addemoji/Pack2`"
            )
        if len(names) > MAX_PACKS:
            return await event.eor(f"❌ Max {MAX_PACKS} packs at once (you gave {len(names)}).")
        msg = await event.eor(f"⏳ Saving `{len(names)}` pack(s)...")
        ok, bad, total = [], [], 0
        for i, name in enumerate(names):
            try:
                res = await event.client(
                    GetStickerSetRequest(InputStickerSetShortName(name), hash=0)
                )
            except FloodWaitError as fw:
                bad.append(f"{name} (Telegram busy, wait {fw.seconds}s)")
                left = names[i + 1 :]
                if left:
                    bad.append("not tried yet: " + " ".join(left))
                break
            except RPCError:
                bad.append(f"{name} (not found)")
                continue
            pairs = []
            for doc in res.documents:
                for att in doc.attributes:
                    if isinstance(att, DocumentAttributeCustomEmoji) and att.alt:
                        pairs.append((att.alt.strip(), doc.id))
            if not pairs:
                bad.append(f"{name} (not a premium emoji pack)")
                continue
            n = pe.add_pairs(pairs)
            total += n
            ok.append(f"{name} ({n})")
            if i < len(names) - 1:
                await asyncio.sleep(1)  # be gentle with Telegram
        lines = [f"✅ Saved `{len(ok)}` pack(s), `{total}` emojis."]
        if ok:
            lines.append("• " + "\n• ".join(ok))
        if bad:
            lines += ["", f"❌ Skipped `{len(bad)}`:", "• " + "\n• ".join(bad)]
        lines.append(f"\nTotal saved now: `{_saved_count()}`")
        return await msg.edit("\n".join(lines))

    if low in ("on", "off"):
        if low == "off":
            udB.set_key(pe.OFF_KEY, True)
        else:
            udB.del_key(pe.OFF_KEY)
        return await event.eor(f"Premium emojis turned **{low}**.")

    if low in ("bot on", "bot off"):
        if low == "bot on":
            udB.set_key(pe.BOT_KEY, True)
            return await event.eor(
                "✅ Assistant bot will also use premium emojis.\n"
                "If its messages stop showing, turn it off again with "
                f"`{HNDLR}pemoji bot off` (Telegram may not allow it for your bot)."
            )
        udB.del_key(pe.BOT_KEY)
        return await event.eor("Assistant bot premium emojis turned **off**.")

    if low.startswith("del"):
        ch = arg[3:].strip()
        if not ch:
            return await event.eor(f"Usage: `{HNDLR}pemoji del ❤️`")
        ok = pe.remove(ch)
        return await event.eor("🗑 Removed." if ok else "That emoji is not saved.")

    if low == "clear":
        pe.set_map({})
        return await event.eor("🗑 All saved premium emojis removed.")

    if low == "test":
        if not _premium():
            return await event.eor(
                SAMPLE + "\n\n__Your account has no Premium, so normal emojis are shown.__"
            )
        return await event.eor(SAMPLE)

    await event.eor(_status())


LOGS.info("Premium emoji support loaded.")
