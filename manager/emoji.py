# OWNER Manager - premium (custom) emoji for the manager bot.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).
#
# A built-in map (ui_emoji.json, from the public "UI_Icons" pack) turns the
# manager's normal emojis into premium ones: in message text and as button
# icons. If Telegram refuses custom emoji for this bot, it switches itself
# off and everything falls back to normal emojis - nothing breaks.

import json
import os

from telethon import helpers
from telethon.tl.types import (
    MessageEntityCode,
    MessageEntityCustomEmoji,
    MessageEntityPre,
)

_SKIP = (MessageEntityCode, MessageEntityPre, MessageEntityCustomEmoji)
MAX_PER_MSG = 100


def _variants(ch):
    """'❤️' and '❤' (with/without the hidden variation selector) both match."""
    yield ch
    plain = ch.replace("️", "")
    if plain and plain != ch:
        yield plain


def load_map():
    """{emoji: document_id} from ui_emoji.json (empty on any problem)."""
    path = os.path.join(os.path.dirname(__file__), "ui_emoji.json")
    try:
        with open(path, encoding="utf-8") as f:
            raw = (json.load(f) or {}).get("map", {})
    except Exception:
        return {}
    out = {}
    for ch, doc_id in raw.items():
        try:
            doc_id = int(doc_id)
        except (TypeError, ValueError):
            continue
        for v in _variants(ch):
            out[v] = doc_id
    return out


def lookup(mapping, ch):
    for v in _variants(ch):
        if v in mapping:
            return mapping[v]
    return None


def apply(text, entities, mapping):
    """entities + a custom-emoji entity for every mapped emoji (not inside code)."""
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


def install(client, is_on):
    """Upgrade emojis in every message this client sends/edits while is_on()."""
    if getattr(client, "_oa_emoji", False):
        return
    mapping = load_map()
    original = client._parse_message_text

    async def _parse_message_text(message, parse_mode):
        text, entities = await original(message, parse_mode)
        try:
            if mapping and is_on():
                entities = apply(text, entities, mapping)
        except Exception as er:
            print("[manager] emoji:", er, flush=True)
        return text, entities

    client._parse_message_text = _parse_message_text
    client._oa_emoji = True
    client._oa_emoji_map = mapping
