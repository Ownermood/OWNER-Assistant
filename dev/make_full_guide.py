"""Build FULL_GUIDE.md: setup + every command (from the bot's own help) + Claude handoff.

Run from the repo root:   python3 dev/make_full_guide.py
Needs: pyyaml.   Re-run it whenever commands or help texts change.
"""

import ast
import glob
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PLUGIN_GROUPS = [
    ("🤖 AI", ["aiwrapper", "chatbot"]),
    ("👮 Group management", ["admintools", "mute", "warn", "locks", "antiflood", "autoban", "blacklist",
                             "greetings", "filter", "notes", "snips", "nightmode", "cleanaction",
                             "forcesubscribe", "nsfwfilter", "profanityfilter", "tag", "polls",
                             "globaltools", "chats"]),
    ("🛡️ Privacy, DM & profile", ["pmpermit", "afk", "profile", "autopic", "echo", "fakeaction",
                                   "schedulemsg", "other", "extra"]),
    ("📢 Channels & broadcast", ["channelhacks", "broadcast"]),
    ("📥 Download & upload", ["youtube", "downloadupload", "gdrive", "webupload", "fileshare", "ziptools"]),
    ("🖼️ Media, stickers & images", ["stickertools", "converter", "imagetools", "logo", "glitch", "giftools",
                                      "videotools", "audiotools", "compressor", "mediatools", "resize",
                                      "qrcode", "pdftools", "beautify", "writer", "fontgen", "unsplash"]),
    ("🔎 Search & info", ["search", "words", "weather", "misc", "utilities", "tools", "calculator",
                          "specialtools", "twitter", "stories"]),
    ("⚙️ Bot, settings & developer", ["bot", "core", "database", "variables", "sudo", "usage", "asstcmd",
                                      "button", "devtools", "vctools"]),
]

ADDON_GROUPS = [
    ("💖 Love", ["love"]),
    ("🎉 Fun & pranks", ["fun", "hack", "animations", "typing", "truthdare", "random", "inlinefun", "waifu",
                         "memify", "sticklet", "figlet", "fontsnew", "quote", "quotefancy", "howto",
                         "activitygen", "brainfuck", "morsecode", "encodedecode", "clone"]),
    ("⚠️ Spam (use carefully — can get your account limited)", ["spam", "stickerspam"]),
    ("🎵 Music & voice", ["song", "findsong", "whichsong", "speechtool"]),
    ("🔎 Info & search", ["wikipedia", "imdb", "anime", "animedb", "animechan", "pokedex", "astronomy",
                          "covid", "flaticon", "searchmsgs", "totalmsgs"]),
    ("🧰 Tools", ["ocr", "fastly", "spellcheck", "autocorrect", "ncode", "autoprofile", "wreplace",
                  "limited", "servertest"]),
]

INLINE_ADDONS = """
These run on your assistant bot — type them in any chat after `@YourAssistantBot ` (inline mode):

- `@bot gh <github username>` — someone's latest GitHub activity
- `@bot imdb <movie>` — movie details (needs `.setdb OMDb_API key`, free at omdbapi.com)
- `@bot npm <package>` — search npm packages
- `@bot pypi <package>` — search Python packages
- `@bot omgu <query>` — search OMG! Ubuntu articles
- `@bot winget <app>` — search Windows (winget) apps
- `@bot xda <query>` — search XDA Developers
"""


def items(help_text):
    """Turn Ultroid-style help into markdown bullet points."""
    text = (help_text or "").replace("{i}", ".")
    text = re.sub(r"✘\s*Commands Available\s*-?|📖 \*\*Commands\*\*", "", text)
    text = re.sub(r"✘\s*\*\*(CMD|Examples)\*\*\s*:", "", text).replace("✘", "")
    out = []
    for chunk in re.split(r"\n\s*•", "\n" + text):
        lines = [l.strip() for l in chunk.strip().splitlines() if l.strip()]
        if not lines or lines[0] in ("-", ""):
            continue
        head, rest = lines[0].lstrip("•").strip(), " ".join(lines[1:])
        if head.startswith("-"):
            continue
        out.append(f"- {head}" + (f" — {rest}" if rest else ""))
    return out


def plugin_help(name, strings):
    h = strings.get(f"help_{name}")
    if not h:
        h = ast.get_docstring(ast.parse(open(f"plugins/{name}.py").read()))
    return h


def addon_help(name):
    return ast.get_docstring(ast.parse(open(f"addons/{name}.py").read()))


def build_reference():
    strings = yaml.safe_load(open("strings/strings/en.yml"))
    lines, count = [], 0
    all_plugins = {os.path.basename(p)[:-3] for p in glob.glob("plugins/*.py")} - {"__init__"}
    all_plugins = {p for p in all_plugins if not p.startswith("_")}
    groups = PLUGIN_GROUPS + [("🧩 More", sorted(all_plugins - {n for _, g in PLUGIN_GROUPS for n in g}))]
    lines.append("## 8. Every command (official plugins)\n")
    for title, names in groups:
        names = [n for n in names if n in all_plugins]
        if not names:
            continue
        lines.append(f"### {title}\n")
        for n in names:
            its = items(plugin_help(n, strings))
            count += len(its)
            lines.append(f"**{n}**\n")
            lines += its + [""]
    all_addons = {os.path.basename(p)[:-3] for p in glob.glob("addons/*.py")} - {"__init__"}
    groups = ADDON_GROUPS + [("🧩 More addons", sorted(all_addons - {n for _, g in ADDON_GROUPS for n in g}))]
    lines.append("## 9. Every command (extra addons)\n")
    for title, names in groups:
        names = [n for n in names if n in all_addons]
        if not names:
            continue
        lines.append(f"### {title}\n")
        for n in names:
            its = items(addon_help(n))
            count += len(its)
            lines.append(f"**{n}**\n")
            lines += its + [""]
    lines.append("### 🔍 Inline (assistant bot)\n" + INLINE_ADDONS)
    return "\n".join(lines), count


def main():
    head = open("dev/full_guide_intro.md").read()
    reference, count = build_reference()
    claude = open("CLAUDE.md").read().split("\n", 1)[1]  # drop its H1
    doc = (
        head.replace("{COMMAND_COUNT}", str(count))
        + "\n"
        + reference
        + "\n---\n\n## 10. For Claude / developers (technical handoff)\n\n"
        + "> Same content as `CLAUDE.md` in the repo. Give this file to any Claude to continue the project.\n"
        + re.sub(r"^## ", "### ", claude, flags=re.M)
    )
    open("FULL_GUIDE.md", "w").write(doc)
    print(f"FULL_GUIDE.md written: {len(doc.splitlines())} lines, {count} command entries")


if __name__ == "__main__":
    main()
