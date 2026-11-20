# OWNER Manager - premium (custom) emoji for the manager bot.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).
#
# The owner saves premium emojis once (send/forward a message that has them,
# or a pack link). Every message the manager sends then shows them, and the
# buttons get them as icons. If Telegram does not allow this bot to use
# premium emojis, normal emojis are shown.

from telethon import helpers
from telethon.tl.types import (
    MessageEntityCode,
    MessageEntityCustomEmoji,
    MessageEntityPre,
)

MAX_PER_MSG = 100
_SKIP = (MessageEntityCode, MessageEntityPre, MessageEntityCustomEmoji)


def variants(ch):
    """'❤️' and '❤' (without the hidden variation selector) both match."""
    yield ch
    plain = ch.replace("️", "")
    if plain and plain != ch:
        yield plain


def extract(message):
    """[(normal emoji, custom emoji id), ...] in a Telegram message."""
    text = getattr(message, "message", None) or ""
    surr = helpers.add_surrogate(text)
    found = []
    for ent in getattr(message, "entities", None) or []:
        if isinstance(ent, MessageEntityCustomEmoji):
            ch = helpers.del_surrogate(surr[ent.offset : ent.offset + ent.length]).strip()
            if ch:
                found.append((ch, ent.document_id))
    return found


def add_pairs(mapping, pairs):
    """Add (emoji, id) pairs into mapping (later ones win). Returns count."""
    seen = set()
    for ch, doc_id in pairs:
        if ch in seen:
            continue
        seen.add(ch)
        for v in variants(ch):
            mapping[v] = int(doc_id)
    return len(seen)


def lookup(mapping, ch):
    for v in variants(ch):
        if v in mapping:
            return int(mapping[v])
    return None


def apply(text, entities, mapping):
    """entities + custom-emoji entities for every saved emoji (not in code)."""
    entities = list(entities or [])
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
    for key in sorted(mapping, key=lambda k: len(helpers.add_surrogate(k)), reverse=True):
        ks = helpers.add_surrogate(key)
        start = 0
        while ks and already + len(new) < MAX_PER_MSG:
            idx = surr.find(ks, start)
            if idx < 0:
                break
            end = idx + len(ks)
            if not any(used[idx:end]):
                new.append(MessageEntityCustomEmoji(idx, len(ks), int(mapping[key])))
                used[idx:end] = b"\x01" * (end - idx)
            start = end
    if not new:
        return entities
    return sorted(entities + new, key=lambda e: e.offset)


def install(client, get_mapping):
    """Upgrade emojis in every message this client sends or edits."""
    if getattr(client, "_oa_emoji", False):
        return
    original = client._parse_message_text

    async def _parse_message_text(message, parse_mode):
        text, entities = await original(message, parse_mode)
        try:
            mapping = get_mapping()
            if mapping:
                entities = apply(text, entities, mapping)
        except Exception as er:  # never break a message because of emojis
            print("[manager] emoji:", er, flush=True)
        return text, entities

    client._parse_message_text = _parse_message_text
    client._oa_emoji = True
