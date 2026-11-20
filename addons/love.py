# OWNER Assistant - love & proposal animations.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).

"""
✘ Commands Available -

• `{i}propose <naam>` (ya kisi ke message ka reply)
    Lamba proposal animation 💍 — ladka, ring, dots se gulaab,
    dil aur aakhir mein "Will you be mine?"

• `{i}love <naam>`
    Dots se dil banta hai, laal hota hai, dhadakta hai aur naam aata hai.

• `{i}rose <naam>`
    Dot-by-dot gulaab khilta hai 🌹

• `{i}hearts`
    Dilon ki baarish 💕

• `{i}lovecalc <naam1> <naam2>`
    Love meter 💘
"""

import asyncio
import hashlib
import random
import re

from telethon.errors import FloodWaitError, MessageNotModifiedError

from . import ultroid_cmd

DELAY = 1.3

# ------------------------------------------------------------------ #
#  Drawings ("•" = dot). Shown inside ``` so every character lines up.
# ------------------------------------------------------------------ #

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
BOY_KNEEL_RING = ["  ●  ✦", " /|\\◎ ", " /_   "]

FLOAT = ["♥", "♡", "❥", "♥"]


# ------------------------------------------------------------------ #
#  Helpers
# ------------------------------------------------------------------ #


def _clean(name):
    name = re.sub(r"[*_`\[\]~|]", "", name or "").strip()
    return name[:32] or "Jaan"


async def _target_name(event):
    arg = event.pattern_match.group(1).strip()
    if arg:
        return _clean(arg)
    if event.is_reply:
        reply = await event.get_reply_message()
        sender = await reply.get_sender()
        if sender is not None:
            return _clean(getattr(sender, "first_name", None) or getattr(sender, "title", ""))
    return "Jaan"


def code(lines, title="", footer=""):
    body = "\n".join(lines)
    out = f"{title}\n" if title else ""
    out += f"```\n{body}\n```"
    if footer:
        out += f"\n{footer}"
    return out


async def play(msg, frames, delay=DELAY):
    """Edit one message frame by frame, surviving Telegram flood limits."""
    last = None
    for frame in frames:
        if frame == last:
            continue
        for _ in range(2):
            try:
                await msg.edit(frame)
                break
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 1)
            except MessageNotModifiedError:
                break
        last = frame
        await asyncio.sleep(delay)


def reveal(art, steps, order="rows", reverse=False):
    """Frames that draw `art` gradually (dot by dot)."""
    cells = [(r, c) for r, row in enumerate(art) for c, ch in enumerate(row) if ch != " "]
    if order == "rows":
        cells.sort(key=lambda rc: (rc[0], rc[1]))
    if reverse:
        cells.reverse()
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


def emoji_heart(fill="❤️", empty="🤍", rows_filled=None):
    """Heart made of emoji; `rows_filled` fills from the bottom up."""
    n = len(HEART)
    lines = []
    for r, row in enumerate(HEART):
        filled = rows_filled is None or r >= n - rows_filled
        lines.append(
            "".join((fill if filled else "💗") if ch != " " else empty for ch in row)
        )
    return "\n".join(lines)


def scene(boy_x, boy=BOY, hearts=0, width=24, girl=GIRL):
    """Boy at boy_x, girl on the right, optional floating hearts above."""
    girl_x = width - len(girl[0])
    rows = [[" "] * width for _ in range(3)]
    for r in range(3):
        for i, ch in enumerate(boy[r]):
            if 0 <= boy_x + i < width:
                rows[r][boy_x + i] = ch
        for i, ch in enumerate(girl[r]):
            rows[r][girl_x + i] = ch
    sky = [" "] * width
    random.seed(hearts)
    for _ in range(hearts):
        sky[random.randint(boy_x + 2, girl_x + 1)] = random.choice(FLOAT)
    return ["".join(sky)] + ["".join(r) for r in rows] + ["‾" * width]


def bar(pct, width=12):
    full = round(width * pct / 100)
    return "▰" * full + "▱" * (width - full)


# ------------------------------------------------------------------ #
#  Commands
# ------------------------------------------------------------------ #


@ultroid_cmd(pattern="propose( (.*)|$)")
async def propose(event):
    name = await _target_name(event)
    msg = await event.eor("💌")
    frames = []

    # 1. intro
    for p in (0, 20, 45, 70, 100):
        frames.append(f"💌 **Ek special message aa raha hai...**\n\n`{bar(p)}` {p}%")
    frames.append("🌙 _Ek shaam... ek ladka... aur ek baat jo kab se dil mein thi..._")

    # 2. boy walks towards the girl
    for x in (0, 3, 6, 9, 12):
        frames.append(code(scene(x), "🚶 _Dheere dheere qadam badhte hain..._"))
    frames.append(code(scene(13), "💓 _Dil ki dhadkan tez ho gayi..._"))

    # 3. kneels and shows the ring
    frames.append(code(scene(13, BOY_KNEEL), "🧎 _Ghutno par baith kar..._"))
    frames.append(code(scene(13, BOY_KNEEL_RING, hearts=1), "💍 _Ek chhota sa ring box khula..._"))
    frames.append(code(scene(13, BOY_KNEEL_RING, hearts=3), "✨ _Ring chamak rahi hai..._"))
    frames.append(code(scene(13, BOY_KNEEL_RING, hearts=4, girl=GIRL_HAPPY), "😳 _Wo hairaan... phir muskura di..._"))
    frames.append(code(scene(13, BOY_KNEEL_RING, hearts=7, girl=GIRL_HAPPY), "💞 _Hawa mein pyaar hi pyaar..._"))

    # 4. a rose grows dot by dot (stem first, then the flower)
    for step in reveal(ROSE, 7, reverse=True):
        frames.append(code(step, f"🌹 _Ye phool sirf tumhare liye, {name}..._"))

    # 5. a heart is drawn dot by dot, then fills with colour
    for step in reveal(HEART, 6):
        frames.append(code(step, "💗 _Aur mera dil..._"))
    for k in (3, 6, 9, 11):
        frames.append(f"💗 _...jo sirf tumhare liye dhadakta hai_\n\n{emoji_heart(rows_filled=k)}")
    for fill in ("💖", "❤️", "💗", "❤️"):
        frames.append(f"💓 _dhak... dhak..._\n\n{emoji_heart(fill)}")

    # 6. the words
    words = [
        f"**{name}**,",
        "tum meri muskaan ho 😊",
        "meri har dua mein tum ho 🤲",
        "aur har sapne mein bhi ✨",
    ]
    for i in range(1, len(words) + 1):
        frames.append("💌\n\n" + "\n".join(words[:i]))

    # 7. the question
    frames.append(f"{emoji_heart()}\n\n💍 **Will you be mine, {name}?** 💍")
    frames.append(
        f"{emoji_heart()}\n\n💍 **Will you be mine, {name}?** 💍\n\n"
        "_Option sirf do hain: **Haan** ya **Haan** 😌❤️_"
    )
    await play(msg, frames)


@ultroid_cmd(pattern="love( (.*)|$)")
async def love(event):
    name = await _target_name(event)
    msg = await event.eor("❤️")
    frames = ["💘 _Dil banane ki taiyari..._"]
    for step in reveal(HEART, 7):
        frames.append(code(step, "✍️ _Dot... dot... dil..._"))
    for k in (2, 4, 6, 8, 10, 11):
        frames.append(f"❤️ _Rang bhar rahe hain..._\n\n{emoji_heart(rows_filled=k)}")
    for fill in ("💖", "❤️", "💗", "❤️"):
        frames.append(f"💓\n\n{emoji_heart(fill)}")
    frames.append(f"{emoji_heart()}\n\n💞 **{name}** 💞")
    frames.append(f"{emoji_heart()}\n\n💞 **{name}** 💞\n_Is dil mein sirf tum ho_ ❤️")
    await play(msg, frames)


@ultroid_cmd(pattern="rose( (.*)|$)")
async def rose(event):
    name = await _target_name(event)
    msg = await event.eor("🌱")
    frames = ["🌱 _Ek beej..._"]
    for step in reveal(ROSE, 10, reverse=True):
        frames.append(code(step, "🌿 _Dheere dheere khil raha hai..._"))
    frames.append(code(ROSE, "🌹 _Khil gaya!_"))
    frames.append(code(ROSE, f"🌹 **{name} ke liye** 🌹", "_Ek gulaab, dher saara pyaar_ ❤️"))
    await play(msg, frames)


@ultroid_cmd(pattern="hearts$")
async def hearts(event):
    msg = await event.eor("💕")
    width, height = 14, 8
    drops = []
    frames = []
    pool = ["❤️", "💖", "💗", "💕", "💘", "💞"]
    for t in range(16):
        drops = [(r + 1, c, h) for r, c, h in drops if r + 1 < height]
        for _ in range(2):
            drops.append((0, random.randrange(width), random.choice(pool)))
        grid = [["▫️"] * width for _ in range(height)]
        for r, c, h in drops:
            grid[r][c] = h
        frames.append("💕 **Dilon ki baarish** 💕\n\n" + "\n".join("".join(row) for row in grid))
    frames.append("💕 **Dilon ki baarish** 💕\n\n" + emoji_heart("💖"))
    await play(msg, frames, delay=1.1)


@ultroid_cmd(pattern="lovecalc( (.*)|$)")
async def lovecalc(event):
    names = event.pattern_match.group(1).strip().split()
    if len(names) < 2:
        return await event.eor("`Do naam do: .lovecalc Rahul Priya`")
    a, b = _clean(names[0]), _clean(" ".join(names[1:]))
    seed = "|".join(sorted([a.lower(), b.lower()]))
    pct = 40 + int(hashlib.md5(seed.encode()).hexdigest(), 16) % 61
    msg = await event.eor("💘")
    frames = [f"💘 **Love Meter**\n\n{a} ➕ {b}\n\n_Dilon ko scan kar rahe hain..._"]
    for p in range(0, pct + 1, max(1, pct // 8)):
        frames.append(f"💘 **Love Meter**\n\n{a} ➕ {b}\n\n`{bar(p)}` **{p}%**")
    if pct >= 90:
        verdict = "Made for each other! 💍 Shaadi ka card kab aa raha hai? 😄"
    elif pct >= 75:
        verdict = "Kamaal ki jodi! ❤️ Thoda aur time do, perfect ho jaoge."
    elif pct >= 60:
        verdict = "Spark hai! ✨ Dosti se shuru karo."
    else:
        verdict = "Hmm... dosti hi theek hai 😅 (sirf mazaak hai!)"
    frames.append(f"💘 **Love Meter**\n\n{a} ➕ {b}\n\n`{bar(pct)}` **{pct}%**\n\n{verdict}")
    await play(msg, frames, delay=1.0)
