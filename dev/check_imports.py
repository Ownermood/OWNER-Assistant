# Dev check for OWNER Assistant. Run via dev/check_all.sh (see CLAUDE.md).
import ast, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from check_undefined import top_names, resolve, ROOT
import glob
ADD = os.environ.get("ADDON") or os.path.join(ROOT, "addons")
plug = top_names(f"{ROOT}/plugins/__init__.py")
asstn = top_names(f"{ROOT}/assistant/__init__.py")
addn = plug | {"bot"}
def chk(files, ns, label_root):
    for f in files:
        base = os.path.dirname(f)
        for n in ast.walk(ast.parse(open(f).read())):
            if isinstance(n, ast.ImportFrom) and n.level >= 1:
                if n.module:   # from .x import y -> check sibling module defines y
                    mod = resolve(base, n.module, n.level, f)
                    if mod is None: print(f"{f.replace(label_root,'ADDON')}:{n.lineno}: module .{n.module} missing"); continue
                    names = top_names(mod)
                else:
                    if n.level == 1 and os.path.basename(base) in ("plugins","assistant") or (label_root in f and n.level==1):
                        names = ns
                    else:
                        mod = resolve(base, None, n.level, f); names = top_names(mod) if mod else set()
                        sub = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(os.path.dirname(mod or base), "*"))}
                        names |= sub
                for a in n.names:
                    if a.name != "*" and a.name not in names:
                        print(f"{f.replace(label_root,'ADDON')}:{n.lineno}: cannot import {a.name}")
chk(glob.glob(f"{ROOT}/plugins/*.py"), plug, "\0")
chk(glob.glob(f"{ROOT}/assistant/**/*.py", recursive=True), asstn, "\0")
chk(glob.glob(f"{ADD}/**/*.py", recursive=True), addn, ADD)
