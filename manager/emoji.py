# OWNER Manager - premium (custom) emoji for the manager bot.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).
#
# A built-in map (ui_emoji.json, from the public "UI_Icons" pack) gives the
# manager's BUTTONS premium icons. Message text is left alone on purpose -
# premium emoji in every line looked bad. If Telegram refuses custom emoji
# for this bot, the buttons fall back to normal emojis - nothing breaks.

import json
import os

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
