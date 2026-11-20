# OWNER Assistant branding.
# Based on Ultroid (https://github.com/TeamUltroid/Ultroid), AGPL-3.0.
#
# Change the bot's visible name and banner pictures here.
# The repo link is NOT shown anywhere in the bot (kept private on purpose);
# REPO_URL is only used internally (updater / raw image links).

import os

from .configs import Var

BOT_NAME = "OWNER Assistant"
BOT_NAME_CAPS = "OWNER ASSISTANT"
BOT_NAME_FANCY = "Oᴡɴᴇʀ Assɪsᴛᴀɴᴛ"

REPO_URL = Var.UPSTREAM_REPO.replace(".git", "")
_RAW = REPO_URL.replace("https://github.com/", "https://raw.githubusercontent.com/")
_EXTRAS = "resources/extras"


def brand_url(name):
    """Web link of a banner (needed where Telegram wants a URL, e.g. inline thumbs)."""
    return f"{_RAW}/{Var.UPSTREAM_BRANCH}/{_EXTRAS}/owner_assistant_{name}.jpg"


def brand_file(name):
    """Local banner file; works even if the GitHub repo is private.
    Names: 1 2 3 avatar alive help start deploy pm"""
    path = f"{_EXTRAS}/owner_assistant_{name}.jpg"
    return path if os.path.exists(path) else brand_url(name)


# Banner pictures shipped in resources/extras (as web links).
BRAND_IMAGES = [brand_url(n) for n in (1, 2, 3)]


def assistant_buttons(text="🤖 Assistant"):
    """A button that opens your assistant bot (replaces the old 'Repo' button)."""
    from telethon import Button

    from . import asst

    try:
        uname = asst.me.username
    except AttributeError:
        return None
    if not uname:
        return None
    return [[Button.url(text, f"https://t.me/{uname}", style="primary")]]
