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
    "propose":  ("💍", "Propose"),
    "love":     ("❤️", "Love"),
    "rose":     ("🌹", "Rose"),
    "hearts":   ("💕", "Hearts"),
    "lovecalc": ("💘", "Love calc"),
    "rate":     ("⭐️", "Rate me"),
    "joke":     ("😂", "Joke"),
    "quote":    ("✨", "Quote"),
    "8ball":    ("🎱", "8-ball"),
    "dice":     ("🎲", "Dice"),
    "truth":    ("🤫", "Truth"),
    "dare":     ("🔥", "Dare"),
    "fortune":  ("🔮", "Fortune"),
    "compliment": ("💝", "Compliment"),
    "hack":     ("💀", "Fake hack"),
    "matrix":   ("🟩", "Matrix"),
}


# ---------------------------------------------------------------- more fun
# Everything below runs offline inside the bot - no APIs, no owner account.

JOKES = [
    "Teacher: Why are you late?\nMe: Class started before I got here. 🤷",
    "I told my laptop I needed a break… it said 'same'. 💻",
    "My wallet is like an onion. Opening it makes me cry. 🧅",
    "I'm not lazy, I'm on energy saving mode. 🔋",
    "Exams are like relationships — I study everything except what's asked. 📚",
    "I don't snore. I dream I'm a motorcycle. 🏍",
    "I'm on a seafood diet. I see food and I eat it. 🍟",
    "Parents: Study!\nMe: *opens phone to check the time, returns 3 hours later* ⏰",
    "My brain has too many tabs open and one is playing music. 🎵",
]

QUOTES = [
    "Hard work beats talent when talent doesn't work hard. 💪",
    "You don't have to be great to start, but you have to start to be great. 🚀",
    "Little by little, a little becomes a lot. 🌱",
    "The pain you feel today is the strength you feel tomorrow. ⚡",
    "Discipline is choosing what you want most over what you want now. 🎯",
    "Fall seven times, stand up eight. 🔥",
    "Your only limit is you. 🌟",
    "Dreams don't work unless you do. ✨",
]

EIGHTBALL = [
    "Yes, definitely ✅", "Without a doubt 💯", "You may rely on it 👍",
    "Most likely 🙂", "Signs point to yes 🔮", "Ask again later ⏳",
    "Better not tell you now 🤐", "Cannot predict now 🌫",
    "Don't count on it ❌", "My reply is no 🙅", "Very doubtful 😬",
]

TRUTHS = [
    "What's the last lie you told? 😬",
    "Who was your first crush? 👀",
    "What's your most embarrassing moment? 🙈",
    "How many hours do you actually study? 📚",
    "What's the one app you'd never let anyone see? 📱",
    "Who do you text the most? 💬",
    "What's a secret you've never told anyone here? 🤫",
]

DARES = [
    "Send the 5th photo in your gallery 📸",
    "Text your crush 'hi' right now 😳",
    "Put your status as 'I'm in love' for 1 hour 💕",
    "Send a voice note singing 🎤",
    "Call a friend and speak only in English for 1 min 📞",
    "Change your DP to a baby photo for an hour 👶",
    "Type your last Google search here 🔍",
]

COMPLIMENTS = [
    "You light up every chat you're in ✨",
    "Your energy is contagious 🔥",
    "You're the friend everyone wishes they had 🫂",
    "Smart AND funny — that's rare 🧠",
    "You make hard things look easy 💪",
    "The world is better with you in it 🌍",
]

FORTUNES = [
    "Something good is coming your way this week 🍀",
    "A message you're waiting for will arrive soon 📩",
    "Say yes to the next invitation. Trust me. 🎉",
    "Your hard work is about to pay off 💰",
    "Someone is thinking about you right now 💭",
    "Rest today. Tomorrow needs you sharp. 😴",
]

MATRIX = "01アイウエオカキクケコサシスセソタチツテト#$%&@*"
HACK_STEPS = [
    "Initialising…",
    "Connecting to server…",
    "Bypassing firewall…",
    "Cracking password…",
    "Accessing database…",
    "Downloading files…",
    "Clearing traces…",
]


def _pick(seq, seed):
    return random.Random(seed).choice(seq)


def joke_frames(seed):
    return ["🤔 **Thinking of a joke…**", "😄 " + _pick(JOKES, seed)]


def quote_frames(seed):
    return ["💭 **Finding something for you…**", "✨ **" + _pick(QUOTES, seed) + "**"]


def eightball_frames(seed):
    f = ["🎱 **Shaking the magic 8-ball…**", "🎱 . . .", "🎱 . .", "🎱 ."]
    f.append("🎱 **" + _pick(EIGHTBALL, seed) + "**")
    return f


def dice_frames(seed):
    r = random.Random(seed)
    faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    f = ["🎲 **Rolling…**"]
    for _ in range(5):
        f.append("🎲 " + r.choice(faces))
    final = r.randint(1, 6)
    f.append(f"🎲 **{faces[final - 1]}  You rolled {final}!**")
    return f


def truthdare_frames(seed, dare=False):
    pool, label, icon = (DARES, "DARE", "🔥") if dare else (TRUTHS, "TRUTH", "🤫")
    return [f"{icon} **Picking a {label}…**", f"{icon} **{label}**\n\n{_pick(pool, seed)}"]


def compliment_frames(name, seed):
    return [f"💝 **A little something for {name}…**", "💝 " + _pick(COMPLIMENTS, seed)]


def fortune_frames(seed):
    return ["🔮 **Looking into the future…**", "🔮 ✨ . . .", "🔮 ✨ . .",
            "🔮 **" + _pick(FORTUNES, seed) + "**"]


def hack_frames(name):
    f = [f"💀 **Hacking {name}'s phone…**"]
    for i in range(len(HACK_STEPS)):
        done = "\n".join(("[✔] " + s) if j <= i else "[ ] " + s
                         for j, s in enumerate(HACK_STEPS))
        pct = round((i + 1) / len(HACK_STEPS) * 100)
        f.append("```\n" + done + "\n" + bar(pct) + "\n```")
    f.append(f"💀 **Access granted!**\n\n__Just kidding {name} 😂 it's only an animation.__")
    return f


def matrix_frames(seed):
    r = random.Random(seed)
    f = ["🟩 **Entering the matrix…**"]
    for _ in range(8):
        f.append("```\n" + "\n".join(
            "".join(r.choice(MATRIX) for _ in range(18)) for _ in range(6)
        ) + "\n```")
    f.append("🟩 **Wake up… 🐇**")
    return f


def rate_frames(name, seed):
    r = random.Random(f"rate{seed}")
    score = r.randint(55, 100)
    f = [f"⭐️ **Rating {name}…**"]
    for pct in (10, 35, 60, 85, score):
        f.append(f"⭐️ **{name}**\n\n`{bar(pct)}`")
    tag = "legend 🔥" if score > 90 else "awesome ✨" if score > 75 else "pretty cool 😎"
    f.append(f"⭐️ **{name}** is `{score}%` {tag}")
    return f


def build(kind, name="you", who="Someone", second=None, seed=0):
    """Frames for one fun item. Never touches the network or the owner."""
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
    if kind == "rate":
        return rate_frames(name, seed)
    if kind == "joke":
        return joke_frames(seed)
    if kind == "quote":
        return quote_frames(seed)
    if kind == "8ball":
        return eightball_frames(seed)
    if kind == "dice":
        return dice_frames(seed)
    if kind == "truth":
        return truthdare_frames(seed)
    if kind == "dare":
        return truthdare_frames(seed, dare=True)
    if kind == "fortune":
        return fortune_frames(seed)
    if kind == "compliment":
        return compliment_frames(name, seed)
    if kind == "hack":
        return hack_frames(name)
    if kind == "matrix":
        return matrix_frames(seed)
    return []
