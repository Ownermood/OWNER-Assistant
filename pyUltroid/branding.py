# OWNER Assistant branding.
# Based on Ultroid (https://github.com/TeamUltroid/Ultroid), AGPL-3.0.
#
# Change the bot's visible name, links and banner pictures here.

from .configs import Var

BOT_NAME = "OWNER Assistant"
BOT_NAME_CAPS = "OWNER ASSISTANT"
BOT_NAME_FANCY = "Oᴡɴᴇʀ Assɪsᴛᴀɴᴛ"

REPO_URL = Var.UPSTREAM_REPO.replace(".git", "")
_RAW = REPO_URL.replace("https://github.com/", "https://raw.githubusercontent.com/")

# Banner pictures shipped in resources/extras (served from your repo).
BRAND_IMAGES = [
    f"{_RAW}/{Var.UPSTREAM_BRANCH}/resources/extras/owner_assistant_{n}.jpg"
    for n in (1, 2, 3)
]
