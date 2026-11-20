# OWNER Manager - animations friends can play in the bot's DM.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).
#
# These run on the BOT (it sends a message and edits it frame by frame), so
# they never touch the owner's account. Only reachable when the owner has
# turned Fun mode ON.
#
# NOTE: addons/love.py has its own copy of this art for the userbot commands.
# If you change a drawing here, change it there too.

import hashlib
import random

HEART = [
    "  •••   •••  ",
    " ••••• ••••• ",
    "•••••••••••••",
    "•••••••••••••",
    "•••••••••••••",
    " ••••••••••• ",
    "  •••••••••  ",
    "   •••••••   ",
    "    •••••    ",
    "     •••     ",
    "      •      ",
]

ROSE = [
    "     ,•••,     ",
    "   •••• ••••   ",
    "  ••• ••• •••  ",
    "  ••••• •••••  ",
    "   •••••••••   ",
    "     •••••     ",
    "       ┃       ",
    "   ••  ┃       ",
    "  •••• ┃  ••   ",
    "   •• ╲┃ ••••  ",
    "       ┃╱ ••   ",
    "       ┃       ",
]

GIRL = ["  ●  ", " /▲\\ ", "  ╱╲ "]
GIRL_HAPPY = [" \\●/ ", "  ▲  ", "  ╱╲ "]
BOY = ["  ●  ", " /|\\ ", " / \\ "]
BOY_KNEEL = ["  ●   ", " /|\\◎ ", " /_   "]

LINES = [
    "Are you a magician? Every time I look at you, everyone else disappears ✨",
    "I'd pick you in every lifetime, in every universe 🌌",
    "You're my favourite notification 📲",
    "I tried to stop thinking about you... my heart said no 💓",
    "If kisses were snowflakes, I'd send you a blizzard ❄️",
    "You had me at hello. Honestly, even before that 😌",
    "My heart has been on silent mode... until you called 📞",
    "I'm not a photographer, but I can picture us together 📸",
]


def code(lines, title="", footer=""):
    out = f"{title}\n" if title else ""
    out += "```\n" + "\n".join(lines) + "\n```"
    if footer:
        out += f"\n{footer}"
    return out


def reveal(art, steps):
    """Frames that draw `art` gradually, dot by dot."""
    cells = [(r, c) for r, row in enumerate(art) for c, ch in enumerate(row) if ch != " "]
    frames = []
    for i in range(1, steps + 1):
        shown = set(cells[: round(len(cells) * i / steps)])
        frames.append(
            [
                "".join(ch if (r, c) in shown else " " for c, ch in enumerate(row))
                for r, row in enumerate(art)
            ]
        )
    return frames


def heart_fill(level, fill="❤️"):
    """An emoji heart that fills up (level 0..1)."""
    grid = [
        " ##   ## ",
        "#########",
        "#########",
        " ####### ",
        "  #####  ",
        "   ###   ",
        "    #    ",
    ]
    cells = [(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "#"]
    cells.sort(key=lambda rc: -rc[0])  # fill from the bottom up
    on = set(cells[: round(len(cells) * level)])
    return [
        "".join(
            (fill if (r, c) in on else "🤍") if ch == "#" else "　"
            for c, ch in enumerate(row)
        )
        for r, row in enumerate(grid)
    ]


def scene(boy_x, boy=BOY, hearts=0, width=24):
    """Two people on a line, slowly walking together."""
    rows = []
    for i in range(3):
        left = " " * boy_x + boy[i]
        gap = " " * max(1, width - len(left) - len(GIRL[i]))
        rows.append(left + gap + GIRL[i])
    if hearts:
        rows.insert(0, " " * (boy_x + 6) + " ".join(["♥"] * hearts))
    return rows


def bar(pct, width=12):
    done = round(width * pct / 100)
    return "[" + "█" * done + "░" * (width - done) + f"] {pct}%"


def typewriter(prefix, text, steps=3):
    """Type `text` out a few characters at a time."""
    frames = []
    for i in range(1, steps + 1):
        cut = round(len(text) * i / steps)
        frames.append(prefix + text[:cut] + ("▌" if i < steps else ""))
    return frames


# ---------------------------------------------------------------- animations
# Each builder returns a list of message strings = the frames.


def propose_frames(name, who="Someone"):
    r = random.Random(f"{name}{who}")
    f = []
    f.append(f"💌 **{who} has something to say to {name}...**")
    for x in (0, 2, 4, 6, 7):
        f.append(code(scene(x), f"💞 **Walking up to {name}...**"))
    f.append(code(scene(7, BOY_KNEEL), "💍 **Going down on one knee...**"))
    f += [code(fr, "🌹 **A rose, just for you**") for fr in reveal(ROSE, 5)]
    f += [code(fr, "❤️ **And my whole heart**") for fr in reveal(HEART, 5)]
    for line in r.sample(LINES, 3):
        f += typewriter("💬 ", line, 2)
    f.append(code(scene(7, BOY_KNEEL, hearts=3), f"💘 **{name}...**"))
    f.append(f"💍 **{name}, will you be mine?**\n\n__Say yes. Please. 🥺__")
    f.append(
        code(scene(8, BOY, hearts=5), "🎉 **SHE SAID YES!**")
        + f"\n\n💑 **{who} ❤️ {name}** — happily ever after."
    )
    return f


def love_frames(name):
    f = [f"❤️ **Drawing a heart for {name}...**"]
    f += [code(fr) for fr in reveal(HEART, 6)]
    for level in (0.2, 0.5, 0.8, 1.0):
        f.append("\n".join(heart_fill(level)))
    for _ in range(3):  # beat
        f.append("\n".join(heart_fill(0.85)))
        f.append("\n".join(heart_fill(1.0)))
    f.append(f"💖 **This heart beats for {name}.**")
    return f


def rose_frames(name):
    f = [f"🌹 **A rose is growing for {name}...**"]
    f += [code(fr) for fr in reveal(ROSE, 8)]
    f.append(code(ROSE, "🌹 **Fully bloomed**", f"**For you, {name}** 💐"))
    return f


def hearts_frames():
    r = random.Random(7)
    f = ["💕 **It's raining hearts...**"]
    for step in range(10):
        grid = [list("　" * 9) for _ in range(7)]
        for _ in range(step + 2):
            grid[r.randrange(7)][r.randrange(9)] = r.choice(["❤️", "💖", "💗", "💓"])
        f.append("\n".join("".join(row) for row in grid))
    f.append("💞 **Sending you all of them.**")
    return f


def lovecalc_frames(a, b):
    seed = int(hashlib.sha256(f"{a.lower()}{b.lower()}".encode()).hexdigest(), 16)
    score = seed % 101
    f = [f"💘 **Calculating {a} ❤️ {b}...**"]
    for pct in (0, 20, 45, 70, 90, score):
        f.append(f"💘 **{a} ❤️ {b}**\n\n`{bar(pct)}`")
    if score > 80:
        verdict = "🔥 Made for each other!"
    elif score > 55:
        verdict = "💖 Looking good!"
    elif score > 30:
        verdict = "🙂 Worth a try."
    else:
        verdict = "😅 Maybe just friends."
    f.append(f"💘 **{a} ❤️ {b}**\n\n`{bar(score)}`\n\n{verdict}")
    return f


MENU = {
    "propose": ("💍", "Propose"),
    "love": ("❤️", "Love"),
    "rose": ("🌹", "Rose"),
    "hearts": ("💕", "Hearts"),
    "lovecalc": ("💘", "Love calc"),
}


def build(kind, name="you", who="Someone", second=None):
    if kind == "propose":
        return propose_frames(name, who)
    if kind == "love":
        return love_frames(name)
    if kind == "rose":
        return rose_frames(name)
    if kind == "hearts":
        return hearts_frames()
    if kind == "lovecalc":
        return lovecalc_frames(who, second or name)
    return []
