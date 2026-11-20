# OWNER Assistant - love & proposal animations.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).

"""
✘ Commands Available -

• `{i}propose <name>` (or reply to someone)
    A long, flirty proposal story 💍 — walk-up, ring, a dot-by-dot rose,
    a beating heart, pick-up lines and the big question.

• `{i}love <name>`
    A heart drawn dot by dot that comes alive and beats for them ❤️

• `{i}rose <name>`
    A rose that blooms dot by dot 🌹

• `{i}hearts`
    It's raining hearts 💕

• `{i}lovecalc <name1> <name2>`
    The (totally scientific) love meter 💘
"""

import asyncio
import hashlib
import random
import re
import time

from telethon.errors import FloodWaitError, MessageNotModifiedError
from telethon.tl.functions.messages import EditMessageRequest

from . import HNDLR, udB, ultroid_cmd

# Telegram limits how often one account may edit messages. Too many edits
# in a row => FloodWait (minutes), during which *no* command can edit.
DELAY = 3.0  # seconds between frames (private chats) ~20 edits/min
GROUP_DELAY = 3.5  # groups are stricter
_STATE = {"busy": False, "cooldown_until": 0.0}

# Own random generator: never touch the global one other commands use.
_rng = random.Random()

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

SMALL_HEART = [
    " ••   •• ",
    "•••• ••••",
    "•••••••••",
    " ••••••• ",
    "  •••••  ",
    "   •••   ",
    "    •    ",
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


# ------------------------------------------------------------------ #
#  Helpers
# ------------------------------------------------------------------ #


def _clean(name):
    name = re.sub(r"[*_`\[\]~|]", "", name or "").strip()
    return name[:32] or "Beautiful"


async def _target_name(event):
    arg = event.pattern_match.group(1).strip()
    if arg:
        return _clean(arg)
    if event.is_reply:
        reply = await event.get_reply_message()
        sender = await reply.get_sender()
        if sender is not None:
            return _clean(getattr(sender, "first_name", None) or getattr(sender, "title", ""))
    return "Beautiful"


def it(text):
    """Italic in Telegram markdown (double underscores)."""
    return f"__{text}__"


def code(lines, title="", footer=""):
    out = f"{title}\n" if title else ""
    out += "```\n" + "\n".join(lines) + "\n```"
    if footer:
        out += f"\n{footer}"
    return out


async def _edit(msg, text):
    """Edit without Telethon's silent auto-sleep, so flood waits reach us."""
    client = msg.client
    message, entities = await client._parse_message_text(text, "md")
    await client(
        EditMessageRequest(
            peer=await msg.get_input_chat(),
            id=msg.id,
            message=message,
            entities=entities,
            no_webpage=True,
        ),
        flood_sleep_threshold=0,
    )


async def play(msg, frames, delay=None, event=None):
    """Edit one message frame by frame.

    On a Telegram flood wait the animation stops at once (more edits would
    only make the wait longer); after the wait it shows the final frame.
    Stops quietly if the message is deleted or can't be edited.
    """
    if delay is None:
        delay = GROUP_DELAY if event is not None and not event.is_private else DELAY
    frames = [f for k, f in enumerate(frames) if k == 0 or f != frames[k - 1]]
    _STATE["busy"] = True
    try:
        for n, frame in enumerate(frames):
            try:
                await _edit(msg, frame)
            except MessageNotModifiedError:
                pass
            except FloodWaitError as fw:
                _STATE["cooldown_until"] = time.time() + fw.seconds
                await asyncio.sleep(fw.seconds + 1)
                try:
                    await _edit(msg, frames[-1])
                except Exception:
                    pass
                return
            except Exception:
                return  # message deleted / no rights: just stop
            if n < len(frames) - 1:
                await asyncio.sleep(delay)
    finally:
        _STATE["busy"] = False


async def _start(event, first):
    """Common start for all animations; refuses while busy or rate-limited."""
    wait = int(_STATE["cooldown_until"] - time.time())
    if wait > 0:
        await event.eor(f"⏳ `Telegram paused animations for {wait}s. Try again after that.`")
        return None
    if _STATE["busy"]:
        await event.eor("💞 `Another love animation is still playing, wait for it to finish.`")
        return None
    return await event.eor(first)


def reveal(art, steps, reverse=False):
    """Frames that draw `art` gradually, dot by dot."""
    cells = [(r, c) for r, row in enumerate(art) for c, ch in enumerate(row) if ch != " "]
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


def emoji_art(art, fill="❤️", empty="🤍", size=(11, 13), sparkle=0):
    """Draw `art` with emoji, centred on a fixed-size canvas."""
    rows, cols = size
    top = (rows - len(art)) // 2
    left = (cols - len(art[0])) // 2
    grid = [[empty] * cols for _ in range(rows)]
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch != " ":
                grid[top + r][left + c] = fill
    rnd = random.Random(sparkle)
    for _ in range(sparkle):
        r, c = rnd.randrange(rows), rnd.randrange(cols)
        if grid[r][c] == empty:
            grid[r][c] = rnd.choice(["✨", "💫"])
    return "\n".join("".join(row) for row in grid)


def heart_fill(level, fill="❤️"):
    """Big heart filling up from the bottom (level 0..11 rows)."""
    n = len(HEART)
    return "\n".join(
        "".join("🤍" if ch == " " else (fill if r >= n - level else "🖤") for ch in row)
        for r, row in enumerate(HEART)
    )


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
    rnd = random.Random(hearts)
    for _ in range(hearts):
        sky[rnd.randint(boy_x + 2, girl_x + 1)] = rnd.choice(FLOAT)
    return ["".join(sky)] + ["".join(r) for r in rows] + ["‾" * width]


def bar(pct, width=12):
    full = round(width * pct / 100)
    return "▰" * full + "▱" * (width - full)


def typewriter(prefix, text, steps=3):
    words = text.split()
    return [
        prefix + " ".join(words[: max(1, round(len(words) * i / steps))])
        for i in range(1, steps + 1)
    ]


def heartbeat(title, beats=2):
    """Small heart / big heart / small heart... like a real heartbeat."""
    frames = []
    for b in range(beats):
        frames.append(f"{title}\n\n{emoji_art(SMALL_HEART, '💗', sparkle=b)}")
        frames.append(f"{title}\n\n{emoji_art(HEART, '❤️', sparkle=3 + b)}")
    return frames


# ------------------------------------------------------------------ #
#  Commands
# ------------------------------------------------------------------ #


@ultroid_cmd(pattern="propose( (.*)|$)", fun=True)
async def propose(event):
    name = await _target_name(event)
    msg = await _start(event, "💌")
    if not msg:
        return
    lines = _rng.sample(LINES, 3)
    f = []

    # 1. intro
    for p in (0, 35, 70, 100):
        f.append(f"📩 **Incoming: a very important message...**\n\n`{bar(p)}` {p}%")
    f.append(f"🌙 {it('Somewhere between hello and right now...')}")
    f.append(f"🌙 {it('Somewhere between hello and right now...')}\n💘 **I fell for you, {name}.**")

    # 2. the walk-up
    captions = [
        "🚶 Walking up to you like it's the scariest exam of my life 😅",
        "🚶 Okay... act cool, act cool...",
        "💓 Heart rate: 200 bpm. Totally normal.",
        "🙈 Almost there...",
    ]
    for x, cap in zip((0, 4, 8, 12), captions):
        f.append(code(scene(x), cap))

    # 3. the ring
    f.append(code(scene(13, BOY_KNEEL), "🧎 Down on one knee..."))
    f.append(code(scene(13, BOY_KNEEL_RING, hearts=1), "💍 The tiniest box, for the biggest question"))
    f.append(code(scene(13, BOY_KNEEL_RING, hearts=4, girl=GIRL_HAPPY), "😳 Wait... is that a smile? 🥹"))
    f.append(code(scene(13, BOY_KNEEL_RING, hearts=7, girl=GIRL_HAPPY), "💞 The air is literally full of love rn"))

    # 4. a rose, dot by dot (stem first)
    rose_caps = ["🌱 First, something for you...", "🌿 Growing...", "🌿 Growing...", "🌷 Almost...",
                 "🌹 Blooming...", "🌹 Roses are red..."]
    for step, cap in zip(reveal(ROSE, 6, reverse=True), rose_caps):
        f.append(code(step, cap))
    f.append(code(ROSE, f"🌹 Roses are red, but none of them are as pretty as you, **{name}**."))

    # 5. the heart: drawn dot by dot, comes alive, beats
    for step, cap in zip(reveal(HEART, 4), ["✍️ Now let me draw my heart...", "✍️ dot...", "✍️ dot... dot...", "✍️ done."]):
        f.append(code(step, cap))
    f.append(f"🎨 {it('Adding some colour...')}\n\n{heart_fill(5)}")
    f.append(f"❤️ {it('It only beats for you.')}\n\n{heart_fill(11)}")
    f += heartbeat("💓 **lub-dub... lub-dub...**", beats=2)

    # 6. three flirty lines, typed out
    for i, line in enumerate(lines, 1):
        f += typewriter(f"💬 **#{i}**\n\n", line)

    # 7. the question
    final_heart = emoji_art(HEART, "❤️", sparkle=6)
    f.append(f"{final_heart}\n\n💍 **{name},**")
    f.append(f"{final_heart}\n\n💍 **{name}, will you be mine?** 💍")
    f.append(
        f"{final_heart}\n\n💍 **{name}, will you be mine?** 💍\n\n"
        f"[ **YES** 💖 ]    [ **OF COURSE YES** 😍 ]\n\n"
        f"{it('No is not an option, sorry 😌')}"
    )
    await play(msg, f, event=event)


@ultroid_cmd(pattern="love( (.*)|$)", fun=True)
async def love(event):
    name = await _target_name(event)
    msg = await _start(event, "❤️")
    if not msg:
        return
    f = []
    for p in (0, 40, 80, 100):
        f.append(f"💘 **Loading love.exe**\n\n`{bar(p)}` {p}%")
    for step, cap in zip(reveal(HEART, 5), ["✍️ Drawing...", "✍️ Drawing...", "✍️ Drawing...", "✍️ Almost...", "✍️ Done."]):
        f.append(code(step, cap))
    f.append(f"🎨 {it('Filling it with feelings...')}\n\n{heart_fill(4, '💗')}")
    f.append(f"🎨 {it('A little more...')}\n\n{heart_fill(8, '💖')}")
    f.append(f"❤️ {it('Full.')}\n\n{heart_fill(11)}")
    f += heartbeat("💓 **lub-dub... lub-dub...**", beats=3)
    final_heart = emoji_art(HEART, "❤️", sparkle=6)
    f.append(f"{final_heart}\n\n💞 **{name}** 💞")
    f.append(f"{final_heart}\n\n💞 **{name}** 💞\n{it('You have my heart. Handle with care')} ❤️")
    await play(msg, f, event=event)


@ultroid_cmd(pattern="rose( (.*)|$)", fun=True)
async def rose(event):
    name = await _target_name(event)
    msg = await _start(event, "🌱")
    if not msg:
        return
    caps = ["🌱 Planting a little seed...", "🌱 Watering it with love...", "🌿 Growing...", "🌿 Growing...",
            "🌿 Leaves!", "🌷 A bud...", "🌷 Opening...", "🌹 Blooming...", "🌹 Blooming...", "🌹 Almost..."]
    f = [f"🌱 {it('Wait for it...')}"]
    for step, cap in zip(reveal(ROSE, 10, reverse=True), caps):
        f.append(code(step, cap))
    f.append(code(ROSE, f"🌹 **For you, {name}**"))
    f.append(code(ROSE, f"🌹 **For you, {name}**", it("A rose for the prettiest smile I know ❤️")))
    await play(msg, f, event=event)


@ultroid_cmd(pattern="hearts$", fun=True)
async def hearts(event):
    msg = await _start(event, "💕")
    if not msg:
        return
    width, height = 12, 8
    drops = []
    frames = []
    pool = ["❤️", "💖", "💗", "💕", "💘", "💞"]
    for _ in range(16):
        drops = [(r + 1, c, h) for r, c, h in drops if r + 1 < height]
        for _ in range(2):
            drops.append((0, _rng.randrange(width), _rng.choice(pool)))
        grid = [["▫️"] * width for _ in range(height)]
        for r, c, h in drops:
            grid[r][c] = h
        frames.append("💕 **It's raining hearts** 💕\n\n" + "\n".join("".join(row) for row in grid))
    frames.append("💕 **...and they all landed on you** 💕\n\n" + emoji_art(HEART, "💖", sparkle=5))
    await play(msg, frames, event=event)


@ultroid_cmd(pattern="lovecalc( (.*)|$)", fun=True)
async def lovecalc(event):
    names = event.pattern_match.group(1).strip().split()
    if len(names) < 2:
        return await event.eor("`Give two names: .lovecalc Romeo Juliet`")
    a, b = _clean(names[0]), _clean(" ".join(names[1:]))
    seed = "|".join(sorted([a.lower(), b.lower()]))
    pct = 40 + int(hashlib.md5(seed.encode()).hexdigest(), 16) % 61
    msg = await _start(event, "💘")
    if not msg:
        return
    head = f"💘 **Love Meter**\n\n**{a}** ➕ **{b}**\n\n"
    frames = [head + it("Scanning both hearts...")]
    for p in range(0, pct + 1, max(1, pct // 8)):
        frames.append(head + f"`{bar(p)}` **{p}%**")
    if pct >= 90:
        verdict = "Made for each other 💍 When's the wedding?"
    elif pct >= 75:
        verdict = "Serious chemistry ❤️ Someone make the first move already!"
    elif pct >= 60:
        verdict = "There's a spark ✨ Coffee date, maybe?"
    else:
        verdict = "Hmm... great friends for now 😅 (just for fun!)"
    frames.append(head + f"`{bar(pct)}` **{pct}%**\n\n{verdict}")
    await play(msg, frames, event=event)




# ----------------------------------------------------------------------------
# Who may use the fun animations besides you (2nd id, partner...).
#   .funuser              -> list
#   .funuser add          -> reply to them, or give @username / id
#   .funuser del <id>     -> remove one
#   .funuser clear        -> back to just you (private)
# Fun users can run ONLY the love animations, nothing else.
# ----------------------------------------------------------------------------


def _fun_ids():
    data = udB.get_key("FUN_USERS")
    return data if isinstance(data, list) else []


@ultroid_cmd(pattern="funuser( (.*)|$)")
async def funuser(event):
    arg = (event.pattern_match.group(1) or "").strip()
    low = arg.lower()
    ids = _fun_ids()

    if low.startswith("clear"):
        udB.del_key("FUN_USERS")
        return await event.eor("🔒 `Fun animations are private again (only you).`")

    if low.split()[:1] == ["del"] or low.split()[:1] == ["remove"]:
        rest = arg.split(maxsplit=1)[1].strip() if len(arg.split()) > 1 else ""
        try:
            uid = int(rest)
        except ValueError:
            return await event.eor("`Give the numeric id: .funuser del 123456`")
        if uid in ids:
            ids.remove(uid)
            udB.set_key("FUN_USERS", ids)
            return await event.eor("🗑 `Removed. Now {} allowed.`".format(len(ids)))
        return await event.eor("`That id is not in the list.`")

    if low.startswith("add"):
        rest = arg.split(maxsplit=1)[1].strip() if len(arg.split()) > 1 else ""
        uid = None
        if event.is_reply:
            uid = (await event.get_reply_message()).sender_id
        elif rest:
            try:
                uid = int(rest)
            except ValueError:
                try:
                    uid = (await event.client.get_entity(rest)).id
                except Exception:
                    return await event.eor("`Couldn't find that user. Reply to them, or give a valid @username / id.`")
        if not uid:
            return await event.eor("`Reply to the person, or: .funuser add @username (or their id).`")
        if uid in ids:
            return await event.eor("`Already added.`")
        ids.append(uid)
        udB.set_key("FUN_USERS", ids)
        return await event.eor(
            "💞 `Added {}. They can now use the love animations "
            "({h}propose {h}love {h}rose {h}hearts {h}lovecalc) — nothing else.`".format(uid, h=HNDLR)
        )

    if not ids:
        return await event.eor(
            "👥 **Fun users:** none (only you).\n\n"
            "Add someone: reply with `{h}funuser add`, or `{h}funuser add @username`.".format(h=HNDLR)
        )
    lines = "\n".join("• `{}`".format(i) for i in ids)
    await event.eor(
        "👥 **Fun users** (love animations only):\n{}\n\n"
        "`{h}funuser del <id>`  ·  `{h}funuser clear`".format(lines, h=HNDLR)
    )


# ----------------------------------------------------------------------------
# Public / Private switch for the fun animations.
#   .funmode            -> show + flip
#   .funmode public     -> anyone can use the love animations
#   .funmode private    -> only you (and your .funuser list)
# The Public/Private button in the OWNER Manager bot flips the same switch.
# ----------------------------------------------------------------------------

import json as _json
import os as _os


def _fun_mode_file():
    return _os.path.join(_os.environ.get("OA_DATA_DIR", "data"), "fun_mode.json")


def _get_public():
    try:
        with open(_fun_mode_file(), encoding="utf-8") as f:
            return bool(_json.load(f).get("public"))
    except Exception:
        return False


def _set_public(value):
    path = _fun_mode_file()
    _os.makedirs(_os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        _json.dump({"public": bool(value)}, f)


@ultroid_cmd(pattern="funmode( (.*)|$)")
async def funmode(event):
    arg = (event.pattern_match.group(1) or "").strip().lower()
    if arg in ("public", "on", "open"):
        new = True
    elif arg in ("private", "off", "close"):
        new = False
    else:
        new = not _get_public()  # no arg = flip
    _set_public(new)
    if new:
        await event.eor(
            "🔓 **Fun mode: PUBLIC**\n"
            "`Anyone can now use the love animations "
            f"({HNDLR}propose {HNDLR}love {HNDLR}rose {HNDLR}hearts {HNDLR}lovecalc).`\n"
            f"`Make it private again: {HNDLR}funmode private`"
        )
    else:
        await event.eor(
            "🔒 **Fun mode: PRIVATE**\n"
            "`Only you can use the love animations now.`\n"
            f"`(Specific friends only: {HNDLR}funuser add)`"
        )
