# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
import subprocess
import sys
from shutil import rmtree

from decouple import config
from git import Repo

from .. import *
from ..dB._core import HELP
from ..loader import Loader
from . import *
from .utils import load_addons


def _after_load(loader, module, plugin_name=""):
    if not module or plugin_name.startswith("_"):
        return
    from strings import get_help

    if doc_ := get_help(plugin_name) or module.__doc__:
        try:
            doc = doc_.format(i=HNDLR)
        except Exception as er:
            loader._logger.exception(er)
            loader._logger.info(f"Error in {plugin_name}: {module}")
            return
        if loader.key in HELP.keys():
            update_cmd = HELP[loader.key]
            try:
                update_cmd.update({plugin_name: doc})
            except BaseException as er:
                loader._logger.exception(er)
        else:
            try:
                HELP.update({loader.key: {plugin_name: doc}})
            except BaseException as em:
                loader._logger.exception(em)


def _addons_bundled():
    """True when `addons/` ships inside this repo (not a separate git clone)."""
    return os.path.isfile("addons/__init__.py") and not os.path.exists("addons/.git")


def _install_addon_requirements():
    """pip install addons/addons.txt, but only when it changed since last time."""
    req = "addons/addons.txt"
    if not os.path.exists(req):
        return
    import hashlib

    digest = hashlib.sha256(open(req, "rb").read()).hexdigest()
    marker = "addons/.installed"
    if os.path.exists(marker) and open(marker).read().strip() == digest:
        return
    res = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-cache-dir", "-q", "-r", req]
    )
    if res.returncode == 0:
        with open(marker, "w") as f:
            f.write(digest)


def _prepare_addons():
    url = udB.get_key("ADDONS_URL") or config("ADDONS_URL", None)
    if _addons_bundled() and not url:
        # Addons come with this repo: nothing to clone, just load them.
        LOGS.info("Using addons bundled with this repo.")
    else:
        if url and _addons_bundled():
            LOGS.info("ADDONS_URL is set, replacing bundled addons with it.")
            rmtree("addons")
        if os.path.exists("addons") and not os.path.exists("addons/.git"):
            rmtree("addons")
        if not os.path.exists("addons"):
            src = url or "https://github.com/TeamUltroid/UltroidAddons.git"
            subprocess.run(["git", "clone", "-q", src, "addons"])
        else:
            subprocess.run(["git", "-C", "addons", "pull", "-q"])
    _install_addon_requirements()


def load_other_plugins(addons=None, pmbot=None, manager=None, vcbot=None):

    # for official
    _exclude = udB.get_key("EXCLUDE_OFFICIAL") or config("EXCLUDE_OFFICIAL", None)
    _exclude = _exclude.split() if _exclude else []

    # "INCLUDE_ONLY" was added to reduce Big List in "EXCLUDE_OFFICIAL" Plugin
    _in_only = udB.get_key("INCLUDE_ONLY") or config("INCLUDE_ONLY", None)
    _in_only = _in_only.split() if _in_only else []
    Loader().load(include=_in_only, exclude=_exclude, after_load=_after_load)

    # for assistant
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        _ast_exc = ["pmbot"]
        if _in_only and "games" not in _in_only:
            _ast_exc.append("games")
        Loader(path="assistant").load(
            log=False, exclude=_ast_exc, after_load=_after_load
        )

    # for addons
    if addons:
        _prepare_addons()

        _exclude = udB.get_key("EXCLUDE_ADDONS")
        _exclude = _exclude.split() if _exclude else []
        _in_only = udB.get_key("INCLUDE_ADDONS")
        _in_only = _in_only.split() if _in_only else []

        Loader(path="addons", key="Addons").load(
            func=load_addons,
            include=_in_only,
            exclude=_exclude,
            after_load=_after_load,
            load_all=True,
        )

    if not USER_MODE:
        # group manager
        if manager:
            Loader(path="assistant/manager", key="Group Manager").load()

        # chat via assistant
        if pmbot:
            Loader(path="assistant/pmbot.py").load(log=False)

    # vc bot
    if vcbot and (vcClient and not vcClient.me.bot):
        try:
            import pytgcalls  # ignore: pylint

            if os.path.exists("vcbot"):
                if os.path.exists("vcbot/.git"):
                    subprocess.run("cd vcbot && git pull", shell=True)
                else:
                    rmtree("vcbot")
            if not os.path.exists("vcbot"):
                subprocess.run(
                    "git clone https://github.com/TeamUltroid/VcBot vcbot", shell=True
                )
            try:
                if not os.path.exists("vcbot/downloads"):
                    os.mkdir("vcbot/downloads")
                Loader(path="vcbot", key="VCBot").load(after_load=_after_load)
            except FileNotFoundError as e:
                LOGS.error(f"{e} Skipping VCBot Installation.")
        except ModuleNotFoundError:
            LOGS.error("'pytgcalls' not installed!\nSkipping loading of VCBOT.")
