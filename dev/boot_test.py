# Boots the real bot code with a FAKE Telegram client and loads every
# plugin/addon. Run it from a throwaway copy of the repo: dev/check_all.sh
import sys, os, logging, asyncio, types
from unittest.mock import MagicMock
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/stubs")
sys.argv = ["pyUltroid"]
sys.path.insert(0, os.getcwd())
os.environ.pop("SESSION", None)

errors = []
class Catch(logging.Handler):
    def emit(self, rec):
        if rec.levelno >= logging.ERROR or rec.exc_info:
            msg = f"[{rec.name}] " + rec.getMessage()
            if rec.exc_info:
                import traceback
                msg += "\n" + "".join(traceback.format_exception(*rec.exc_info))[-1200:]
            errors.append(msg)
logging.getLogger().addHandler(Catch()); logging.getLogger().setLevel(logging.INFO)

def make_client(*args, **kwargs):
    c = MagicMock(name="client")
    is_bot = bool(args and args[0] == "asst")
    c._bot = is_bot; c.me.bot = is_bot; c.me.id = 777 if is_bot else 12345
    c.me.username = "test_asst_bot" if is_bot else "tester"; c.me.first_name = "Tester"
    c.uid = c.me.id; c.full_name = "Tester"
    c.run_in_loop = lambda coro: coro.close() if hasattr(coro, "close") else None
    c.handlers = []
    c.add_event_handler = lambda f, ev=None: c.handlers.append((f, ev))
    c.add_handler = lambda f, *a, **k: c.handlers.append((f, a))
    return c

bc = types.ModuleType("pyUltroid.startup.BaseClient"); bc.UltroidClient = make_client
conn = types.ModuleType("pyUltroid.startup.connections")
conn.validate_session = lambda s, l=None: s; conn.vc_connection = lambda *a, **k: None
sys.modules["pyUltroid.startup.BaseClient"] = bc
sys.modules["pyUltroid.startup.connections"] = conn

async def main():
    import pyUltroid
    from pyUltroid import udB, ultroid_bot, asst
    udB.set_key("LOG_CHANNEL", -100123)
    from pyUltroid.startup.loader import load_other_plugins
    load_other_plugins(addons=True, pmbot=True, manager=True, vcbot=False)
    from pyUltroid.dB._core import LOADED, LIST, HELP
    print("LOADED modules:", len(LOADED))
    cmds = sum(len(v) for v in LIST.values())
    print("commands registered:", cmds, "| help sections:", {k: len(v) for k, v in HELP.items()})
    print("userbot handlers:", len(ultroid_bot.handlers), "| assistant handlers:", len(asst.handlers))

loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
loop.run_until_complete(main())
print("\n===== ERRORS (%d) =====" % len(errors))
for e in errors: print("-", e); print()
from pyUltroid.dB._core import HELP
import glob
off = {os.path.basename(f)[:-3] for f in glob.glob("plugins/*.py")} - {"__init__"}
add = {os.path.basename(f)[:-3] for f in glob.glob("addons/*.py")+glob.glob("addons/inline/*.py")} - {"__init__"}
print("plugins without help (not loaded or no doc):", sorted(off - set(HELP.get("Official", {}))))
print("addons without help:", sorted(add - set(HELP.get("Addons", {}))))
# verify the real client module and the real telethonpatch import fine
import importlib, telethonpatch
print("telethonpatch from:", telethonpatch.__file__.replace(os.getcwd(), "."))
del sys.modules["pyUltroid.startup.BaseClient"]
real = importlib.import_module("pyUltroid.startup.BaseClient")
print("real UltroidClient:", real.UltroidClient.__mro__[1].__module__)
