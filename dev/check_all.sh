#!/usr/bin/env bash
# Run all OWNER Assistant checks.   Usage:  bash dev/check_all.sh [path/to/python]
# The boot test needs the bot's requirements installed in that python
# (requirements.txt, resources/startup/optional-requirements.txt, addons/addons.txt).
PY="${1:-python3}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
export PYTHONPATH="$ROOT"
"$PY" -c "import pyflakes" 2>/dev/null || "$PY" -m pip install -q pyflakes

echo "== 1. compile (syntax warnings are errors)"
for f in $(git ls-files '*.py'); do
    "$PY" -W error::SyntaxWarning -c "import sys; compile(open(sys.argv[1]).read(), sys.argv[1], 'exec')" "$f" 2>&1 | tail -1 | sed "s#^#$f: #"
done
echo "== 2. undefined names"
"$PY" -W ignore dev/check_undefined.py $(git ls-files 'plugins/*.py' 'assistant/*.py' 'pyUltroid/*.py')
ADDON="$ROOT/addons" "$PY" -W ignore dev/check_undefined.py $(git ls-files 'addons/*.py')
echo "== 3. relative imports"
"$PY" -W ignore dev/check_imports.py
echo "== 4. Telethon names exist"
"$PY" -W ignore dev/check_telethon.py $(git ls-files 'plugins/*.py' 'assistant/*.py' 'pyUltroid/*.py' 'addons/*.py' 'telethonpatch/*.py') | grep -v "custom.py:.*MISSING"
echo "== 5. command regex clashes"
"$PY" dev/check_command_clash.py addons
echo "== 6. boot test (fake Telegram client, loads every plugin)"
TMP="$(mktemp -d)"
git ls-files -z | xargs -0 -I{} cp --parents {} "$TMP"
(cd "$TMP" && timeout 600 "$PY" -W ignore "$ROOT/dev/boot_test.py" 2>&1 | grep -E "commands registered|without help|ERRORS|^- |Traceback" | grep -v "ProxyError")
rm -rf "$TMP"
echo "== done (empty sections = OK)"
