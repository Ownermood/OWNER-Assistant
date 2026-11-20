# Dev check for OWNER Assistant. Run via dev/check_all.sh (see CLAUDE.md).
import ast, glob, re, sys
files = glob.glob("plugins/*.py") + glob.glob((sys.argv[1] if len(sys.argv) > 1 else "addons") + "/*.py")
cmds = []  # (file, pattern_str, func_src)
for f in files:
    tree = ast.parse(open(f).read())
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.AsyncFunctionDef, ast.FunctionDef)):
            for d in fn.decorator_list:
                if isinstance(d, ast.Call) and getattr(d.func, "id", "") == "ultroid_cmd":
                    for k in d.keywords:
                        if k.arg == "pattern" and isinstance(k.value, ast.Constant):
                            cmds.append((f.split("/")[-1], k.value.value, ast.get_source_segment(open(f).read(), fn)))
names = set()
for f, p, _ in cmds:
    m = re.match(r"[a-zA-Z]+", p)
    if m: names.add(m.group(0))
for f, p, src in cmds:
    rx = re.compile(r"\." + p)
    own = re.match(r"[a-zA-Z]+", p)
    own = own.group(0) if own else ""
    for n in sorted(names):
        if n == own or not n.startswith(own) : continue
        # does pattern p wrongly fire on ".n" or ".n something"?
        for test in (f".{n}", f".{n} x"):
            mm = rx.match(test)
            if mm:
                guarded = "return" in (src or "").split("\n")[2] if src else False
                print(f"{f}: '{p}' also fires on '{test}'   (other cmd .{n})")
                break
