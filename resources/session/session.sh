#!/usr/bin/env bash
# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# Generates a Telethon string session using the local ssgen.py.
# Does not upgrade your system and does not download code from anywhere.
cd "$(dirname "$0")" || exit 1

if ! python3 -c "import telethon" 2>/dev/null; then
    echo "Installing Telethon..."
    python3 -m pip install -q -U telethon 2>/dev/null \
        || python3 -m pip install -q -U --break-system-packages telethon
fi

python3 ssgen.py
