# OWNER Assistant - premium (custom) emoji support.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).
#
# How it works
# ------------
# The owner saves premium emojis once (".pemoji" on a message that has them,
# or ".pemoji pack <link>"). We store  {normal emoji: custom emoji id}  in the
# DB key PREMIUM_EMOJI. After that, every message the bot sends or edits gets
# its normal emojis upgraded to the saved premium ones automatically.
#
# Fallback: if the account has no Telegram Premium, or nothing is saved, the
# text is sent unchanged (normal emojis) - nothing breaks.

from telethon import helpers
from telethon.tl.types import (
    MessageEntityCode,
    MessageEntityCustomEmoji,
    MessageEntityPre,
)

KEY = "PREMIUM_EMOJI"
OFF_KEY = "PREMIUM_EMOJI_OFF"  # True  => don't upgrade the user account's messages
BOT_KEY = "PREMIUM_EMOJI_BOT"  # True  => also upgrade the assistant bot's messages
MAX_PER_MSG = 100  # Telegram limit for custom emojis in one message
_SKIP = (MessageEntityCode, MessageEntityPre, MessageEntityCustomEmoji)


def _db():
    from .. import udB

    return udB


def get_map():
    data = _db().get_key(KEY)
    if not isinstance(data, dict):
        return {}
    out = {}
    for k, v in data.items():
        try:
            out[str(k)] = int(v)
        except (TypeError, ValueError):
            continue
    return out


def set_map(mapping):
    if mapping:
        _db().set_key(KEY, {k: int(v) for k, v in mapping.items()})
    else:
        _db().del_key(KEY)


def _variants(ch):
    """'❤️' and '❤' (without the invisible variation selector) both match."""
    yield ch
    plain = ch.replace("️", "")
    if plain and plain != ch:
        yield plain


def extract(message):
    """[(normal emoji, custom emoji id), ...] found in a Telegram message."""
    text = getattr(message, "message", None) or ""
    surr = helpers.add_surrogate(text)
    found = []
    for ent in getattr(message, "entities", None) or []:
        if isinstance(ent, MessageEntityCustomEmoji):
            ch = helpers.del_surrogate(surr[ent.offset : ent.offset + ent.length])
            if ch.strip():
                found.append((ch.strip(), ent.document_id))
    return found


def add_pairs(pairs, overwrite=True):
    """Save (emoji, id) pairs. Returns how many emojis were saved."""
    mapping = get_map()
    saved = 0
    seen = set()
    for ch, doc_id in pairs:
        if ch in seen:
            continue
        seen.add(ch)
        if not overwrite and ch in mapping:
            continue
        for v in _variants(ch):
            mapping[v] = int(doc_id)
        saved += 1
    set_map(mapping)
    return saved


def remove(ch):
    mapping = get_map()
    hit = False
    for v in _variants(ch):
        if mapping.pop(v, None) is not None:
            hit = True
    set_map(mapping)
    return hit


def apply(text, entities, mapping=None):
    """Return entities + custom-emoji entities for every saved emoji in text.
    Emojis inside `code` / ```pre``` blocks are left alone."""
    entities = list(entities or [])
    if mapping is None:
        mapping = get_map()
    if not text or not mapping:
        return entities
    surr = helpers.add_surrogate(text)
    used = bytearray(len(surr))
    for ent in entities:
        if isinstance(ent, _SKIP):
            for i in range(ent.offset, min(ent.offset + ent.length, len(surr))):
                used[i] = 1
    already = sum(isinstance(e, MessageEntityCustomEmoji) for e in entities)
    new = []
    keys = sorted(mapping, key=lambda k: len(helpers.add_surrogate(k)), reverse=True)
    for key in keys:
        ks = helpers.add_surrogate(key)
        if not ks:
            continue
        start = 0
        while already + len(new) < MAX_PER_MSG:
            idx = surr.find(ks, start)
            if idx < 0:
                break
            end = idx + len(ks)
            if not any(used[idx:end]):
                new.append(MessageEntityCustomEmoji(idx, len(ks), mapping[key]))
                used[idx:end] = b"\x01" * (end - idx)
            start = end
    if not new:
        return entities
    return sorted(entities + new, key=lambda e: e.offset)


def _enabled(client, bot):
    udB = _db()
    if bot:
        return bool(udB.get_key(BOT_KEY))
    if udB.get_key(OFF_KEY):
        return False
    me = getattr(client, "me", None)
    return bool(getattr(me, "premium", False))


def install(client, bot=False):
    """Hook the client's text parser so every sent/edited message gets the
    saved premium emojis. Safe to call twice."""
    if client is None or getattr(client, "_oa_pemoji", False):
        return
    original = client._parse_message_text

    async def _parse_message_text(message, parse_mode):
        text, entities = await original(message, parse_mode)
        try:
            if _enabled(client, bot):
                entities = apply(text, entities)
        except Exception:
            from .. import LOGS

            LOGS.exception("premium emoji: could not apply")
        return text, entities

    client._parse_message_text = _parse_message_text
    client._oa_pemoji = True
