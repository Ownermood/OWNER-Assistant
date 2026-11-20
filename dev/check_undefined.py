# Dev check for OWNER Assistant. Run via dev/check_all.sh (see CLAUDE.md).
"""Find names used in plugin/addon files that are not defined anywhere along the star-import chain."""
import ast, sys, os, builtins
from pyflakes import api, reporter, messages
import io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def top_names(path, seen=None):
    """Names a module exports via star import (statically)."""
    seen = seen if seen is not None else set()
    if path in seen or not os.path.exists(path):
        return set()
    seen.add(path)
    tree = ast.parse(open(path).read())
    names = set()
    base = os.path.dirname(path)
    def walk(nodes):
        for n in nodes:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(n.name)
            elif isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                tg = n.targets if isinstance(n, ast.Assign) else [n.target]
                for t in tg:
                    for x in ast.walk(t):
                        if isinstance(x, ast.Name): names.add(x.id)
            elif isinstance(n, ast.Import):
                for a in n.names: names.add((a.asname or a.name).split(".")[0])
            elif isinstance(n, ast.ImportFrom):
                for a in n.names:
                    if a.name == "*":
                        mod = resolve(base, n.module, n.level, path)
                        if mod: names.update(top_names(mod, seen))
                    else:
                        names.add(a.asname or a.name)
            elif isinstance(n, (ast.If, ast.Try, ast.With)):
                for f in ("body", "orelse", "finalbody"):
                    walk(getattr(n, f, []) or [])
                for h in getattr(n, "handlers", []) or []:
                    walk(h.body)
    walk(tree.body)
    return names

def resolve(base, module, level, src):
    if level == 0:
        p = os.path.join(ROOT, *(module or "").split("."))
    else:
        d = base
        for _ in range(level - 1): d = os.path.dirname(d)
        p = os.path.join(d, *(module.split(".") if module else []))
    for c in (p + ".py", os.path.join(p, "__init__.py")):
        if os.path.exists(c): return c
    return None

INJECTED = {"ultroid_cmd","eod","eor","asst_cmd","callback","in_pattern","LOG_CHANNEL","udB","asst","tgbot",
            "ultroid_bot","ub","bot","Redis","con","get_help","get_string","HNDLR","LOGS","Var","OWNER_NAME"}

def check(path, extra):
    out = io.StringIO()
    class R(reporter.Reporter):
        pass
    msgs = []
    w = api.checker.Checker(ast.parse(open(path).read()), filename=path)
    for m in w.messages:
        if isinstance(m, (messages.ImportStarUsage, messages.UndefinedName)):
            name = m.message_args[0]
            if name in extra or hasattr(builtins, name): continue
            msgs.append(f"{path}:{m.lineno}: {name}")
    return msgs

def main(paths, addon_root=None):
    for p in paths:
        base = os.path.dirname(p)
        tree = ast.parse(open(p).read())
        star = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names):
                mod = resolve(base, n.module, n.level, p)
                if mod is None and addon_root and n.level == 1:
                    mod = os.path.join(ROOT, "plugins", "__init__.py")
                if mod: star |= top_names(mod)
        extra = star | (INJECTED if addon_root else set())
        if addon_root and any(isinstance(n, ast.ImportFrom) and n.level==1 for n in ast.walk(tree)):
            # addons: `from . import X` resolves to plugins/__init__ namespace (addons/__init__ does `from plugins import *`)
            pass
        for line in check(p, extra): print(line.replace(addon_root or "\0", "ADDON"))

if __name__ == "__main__":
    addon = os.environ.get("ADDON")
    main(sys.argv[1:], addon)
