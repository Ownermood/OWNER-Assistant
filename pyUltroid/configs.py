# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import sys

from decouple import config

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def _int(name, default):
    value = str(config(name, default="") or "").strip()
    try:
        return int(value) if value else default
    except ValueError:
        return default


def _bool(name, default):
    value = str(config(name, default="") or "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "yes", "on")


def _str(name, default=None):
    value = str(config(name, default="") or "").strip()
    return value or default


class Var:
    # mandatory
    API_ID = (
        int(sys.argv[1]) if len(sys.argv) > 1 else _int("API_ID", 6)
    )
    API_HASH = (
        sys.argv[2]
        if len(sys.argv) > 2
        else _str("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
    )
    SESSION = sys.argv[3] if len(sys.argv) > 3 else _str("SESSION")
    REDIS_URI = (
        sys.argv[4]
        if len(sys.argv) > 4
        else (_str("REDIS_URI") or _str("REDIS_URL"))
    )
    REDIS_PASSWORD = (
        sys.argv[5] if len(sys.argv) > 5 else _str("REDIS_PASSWORD")
    )
    # extras
    BOT_TOKEN = _str("BOT_TOKEN")
    LOG_CHANNEL = _int("LOG_CHANNEL", 0)
    HEROKU_APP_NAME = _str("HEROKU_APP_NAME")
    HEROKU_API = _str("HEROKU_API")
    VC_SESSION = _str("VC_SESSION")
    ADDONS = _bool("ADDONS", True)
    # repo used by .update / installer (your own fork)
    UPSTREAM_REPO = _str("UPSTREAM_REPO", "https://github.com/Ownermood/Ultroid")
    UPSTREAM_BRANCH = _str("UPSTREAM_BRANCH", "main")
    VCBOT = _bool("VCBOT", False)
    # for railway
    REDISPASSWORD = _str("REDISPASSWORD")
    REDISHOST = _str("REDISHOST")
    REDISPORT = _str("REDISPORT")
    REDISUSER = _str("REDISUSER")
    # for sql
    DATABASE_URL = _str("DATABASE_URL")
    # for MONGODB users
    MONGO_URI = _str("MONGO_URI")
