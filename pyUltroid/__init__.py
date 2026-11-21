# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
import sys
import telethonpatch
from .version import __version__

run_as_module = __package__ in sys.argv or sys.argv[0] == "-m"


class ULTConfig:
    lang = "en"
    thumb = "resources/extras/owner_assistant_thumb.jpg"


if run_as_module:
    import time

    from .configs import Var
    from .startup import *
    from .startup._database import UltroidDB
    from .startup.BaseClient import UltroidClient
    from .startup.connections import validate_session, vc_connection
    from .startup.funcs import _version_changes, autobot, enable_inline, update_envs
    from .version import ultroid_version

    if not os.path.exists("./plugins"):
        LOGS.error(
            "'plugins' folder not found!\nMake sure that, you are on correct path."
        )
        exit()

    start_time = time.time()
    _ult_cache = {}
    _ignore_eval = []

    udB = UltroidDB()
    update_envs()

    LOGS.info(f"Connecting to {udB.name}...")
    if udB.ping():
        LOGS.info(f"Connected to {udB.name} Successfully!")

    BOT_MODE = udB.get_key("BOTMODE")
    DUAL_MODE = udB.get_key("DUAL_MODE")

    USER_MODE = udB.get_key("USER_MODE")
    if USER_MODE:
        DUAL_MODE = False

    if BOT_MODE:
        if DUAL_MODE:
            udB.del_key("DUAL_MODE")
            DUAL_MODE = False
        ultroid_bot = None

        if not udB.get_key("BOT_TOKEN"):
            LOGS.critical(
                '"BOT_TOKEN" not Found! Please add it, in order to use "BOTMODE"'
            )

            sys.exit()
    else:
        ultroid_bot = UltroidClient(
            validate_session(Var.SESSION, LOGS),
            udB=udB,
            app_version=ultroid_version,
            device_model="OWNER Assistant",
        )
        ultroid_bot.run_in_loop(autobot())

    if USER_MODE:
        asst = ultroid_bot
    else:
        asst = UltroidClient(
            "asst" + os.environ.get("OA_INSTANCE", ""),  # own file per account (manager)
            bot_token=udB.get_key("BOT_TOKEN"), udB=udB)

    if BOT_MODE:
        ultroid_bot = asst
        if udB.get_key("OWNER_ID"):
            try:
                ultroid_bot.me = ultroid_bot.run_in_loop(
                    ultroid_bot.get_entity(udB.get_key("OWNER_ID"))
                )
            except Exception as er:
                LOGS.exception(er)
    elif not asst.me.bot_inline_placeholder and asst._bot:
        ultroid_bot.run_in_loop(enable_inline(ultroid_bot, asst.me.username))

    vcClient = vc_connection(udB, ultroid_bot)

    _version_changes(udB)

    # Extra account run by the manager: the owner's main account controls it.
    # Main id becomes full sudo, and sudo commands use "!" (not ".") so a
    # command typed by the main account runs only on THIS account.
    _ctrl = (os.environ.get("OA_CONTROLLER") or "").strip()
    if _ctrl.isdigit():
        _cid = int(_ctrl)
        _sudos = udB.get_key("SUDOS") or []
        if _cid not in _sudos:
            udB.set_key("SUDOS", [*_sudos, _cid])
        udB.set_key("SUDO", "True")
        _full = str(udB.get_key("FULLSUDO") or "").split()
        if _ctrl not in _full:
            udB.set_key("FULLSUDO", " ".join([*_full, _ctrl]))
        if not udB.get_key("SUDO_HNDLR"):
            udB.set_key("SUDO_HNDLR", "!")

    HNDLR = udB.get_key("HNDLR") or "."
    DUAL_HNDLR = udB.get_key("DUAL_HNDLR") or "/"
    SUDO_HNDLR = udB.get_key("SUDO_HNDLR") or HNDLR
else:
    print("OWNER Assistant core")

    from logging import getLogger

    LOGS = getLogger("pyUltroid")

    ultroid_bot = asst = udB = vcClient = None
