# Dev check for OWNER Assistant. Run via dev/check_all.sh (see CLAUDE.md).
import ast, sys, importlib, glob
bad = []
for f in sys.argv[1:]:
    try: tree = ast.parse(open(f).read())
    except SyntaxError as e: print("SYNTAX", f, e); continue
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("telethon"):
            try: m = importlib.import_module(n.module)
            except Exception as e: print(f"{f}:{n.lineno}: module {n.module} -> {e}"); continue
            for a in n.names:
                if a.name != "*" and not hasattr(m, a.name):
                    try: importlib.import_module(n.module + "." + a.name)
                    except Exception: print(f"{f}:{n.lineno}: {n.module}.{a.name} MISSING")
        # attribute access like functions.x.YRequest / types.X
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Attribute) and isinstance(n.value.value, ast.Name) and n.value.value.id == "functions":
            try:
                mod = importlib.import_module("telethon.tl.functions." + n.value.attr)
                if not hasattr(mod, n.attr): print(f"{f}:{n.lineno}: functions.{n.value.attr}.{n.attr} MISSING")
            except Exception as e: print(f"{f}:{n.lineno}: functions.{n.value.attr} -> {e}")
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "types" and n.attr[0].isupper():
            import telethon.tl.types as T
            if not hasattr(T, n.attr): print(f"{f}:{n.lineno}: types.{n.attr} MISSING")
