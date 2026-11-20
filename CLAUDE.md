# CLAUDE.md — handoff for the next Claude session

You are continuing work on **OWNER Assistant**: a Telegram userbot (it logs in
as the owner's own Telegram account) plus an assistant bot. It is a fork of
[Ultroid](https://github.com/TeamUltroid/Ultroid) (AGPL-3.0) that was fixed,
modernised and rebranded in an earlier long Claude session. Read this whole
file before changing anything.

## The owner (how to talk to them)

- Writes **Hinglish** (Hindi in Latin script). Reply in simple Hinglish, short
  sentences, no jargon. They are a Class 12 student preparing for **CLAT
  (exam on 6 December)** — a one-line study nudge at the end is welcome, don't lecture.
- They are not a programmer. Give copy-paste commands, one per code block.
- They often paste errors / screenshots from Telegram. The crash report's
  "Last 5 commits" tells you which version the VPS is running.
- They asked: **always push, open a PR and merge to `main`** after a change
  is tested ("merge kr do sub"). Keep doing that unless they say otherwise.
- Never ask them to paste secrets (SESSION, BOT_TOKEN, API keys, passwords).
  If they paste one, tell them to revoke/regenerate it. Don't repeat it back.

## Where it runs

- Repo: `Ownermood/OWNER-Assistant` (renamed from `Ownermood/Ultroid`; GitHub
  redirects the old name). Default branch `main`.
- Owner's VPS (Ubuntu, Docker). Bot folder on the VPS is still `~/Ultroid`
  (older clone). Update command the owner runs:
  ```bash
  cd ~/Ultroid && git pull && docker compose up -d --build
  ```
  `.update` from Telegram does **not** work under Docker (code is baked into
  the image) — always tell them to run the command above.
- `docker-compose.yml` runs the bot (service name `ultroid` — do NOT rename it,
  the old container would keep running with the same session → AuthKeyDuplicated)
  and its own Redis. The owner runs other, unrelated containers on the same
  VPS — never stop or touch them.
- Assistant bot: token in the VPS `.env` (`BOT_TOKEN`), not in the repo. Don't
  write its username in docs (owner didn't want "CLAT" in the bot's name; the
  username can only be changed by the owner at @BotFather).
- **OWNER Manager** (`manager/`, PR #30): a separate control bot
  (`MANAGER_BOT_TOKEN` + `OWNER_ID` in `.env`). `startup` runs `python3 -m manager`
  when the token is set; it runs the userbot as a child process
  (`python3 -m pyUltroid`, `SESSION` passed in env), so login/logout/run/stop/
  restart/logs/vars work from Telegram. Session + vars live in
  `data/manager.json` (docker volume `owner-data`, chmod 600). Login = phone →
  code (owner must type it with spaces, else Telegram kills the code) → 2FA
  (message deleted, never stored). After `/logout` the `.env` SESSION is NOT
  used again (`use_env_session`). Crash → auto-restart (max 5 / 10 min);
  exit 0 = `.shutdown` (no restart); session dead → "logged out" message.
  UI (PR #31): one live panel per chat (button press = edit; typed command =
  delete owner's message + old panel, send new), no coloured buttons (owner
  asked), premium emoji via `manager/emoji.py` (text entities + button `icon=`;
  saved in `manager.json`; any RPCError while emojis are on → auto-off and
  retry plain). #32: coloured buttons removed from the userbot. #33: premium
  emoji re-added to the manager as a BUILT-IN map (`manager/ui_emoji.json`,
  owner's UI_Icons pack ids) on buttons (`icon=`) + text; `emoji_ok` flips to
  False and persists if Telegram rejects it, so it never breaks. Note: most
  bots can't actually use custom emoji, so this often falls back silently. Force join: `FORCE_JOIN` (default @VillanCommunity, `off` to
  disable) checked with `GetParticipantRequest` — fails OPEN with a warning if
  the bot isn't admin, so the owner is never locked out. Still owner-only.

## Layout

| Path | What |
|---|---|
| `pyUltroid/` | Core (package name kept on purpose, see "Don't") |
| `pyUltroid/branding.py` | Bot name, banners (`brand_file()` local / `brand_url()` web), `assistant_buttons()` — change branding here |
| `pyUltroid/fns/pemoji.py` + `plugins/pemoji.py` | Premium (custom) emoji: saved map + auto-upgrade of every sent/edited message |
| `pyUltroid/configs.py` | Env config; empty values are tolerated |
| `pyUltroid/fns/ai.py` | Shared AI client (Gemini/OpenAI/Claude/DeepSeek): streaming, retries, retired-model fallback |
| `pyUltroid/fns/helper.py` | Helpers incl. `KEEP_SAFE`, `call_back`, `mask_secret`, `read_text_file` |
| `pyUltroid/startup/funcs.py` | Startup: `update_envs`, `autobot` (BotFather flow), `autopilot` (log group), `customize` |
| `pyUltroid/startup/loader.py` | Loads plugins, assistant and the **bundled** `addons/` |
| `plugins/` | Official commands (`.` prefix, owner) |
| `assistant/` | Assistant-bot handlers (inline, callbacks, pmbot, group manager) |
| `addons/` | Extra plugins bundled in this repo (53), incl. `addons/love.py` |
| `telethonpatch/` | Vendored Telethon-Patch (GPLv3), fixed for Telethon 1.46 |
| `strings/strings/*.yml` | All texts/help (25 languages; `en.yml` is the source) |
| `resources/extras/owner_assistant_*.jpg` | Owner's own AI-made art (black/blood-red/silver): anime villain king = avatar/alive/1/thumb, hooded shield = help/2, hooded = pm/3, crown = deploy, command-desk = start. 1024px squares (thumb 320). Replace only with images the owner sends — don't draw our own (owner found SVG drawings "cartoon") |
| `dev/` | Checks + boot test (see below) |
| `SETUP.md`, `OWNER_GUIDE.md` | Owner-facing docs (Hinglish) |

## How to test (no Telegram needed)

The sandbox usually has no internet except PyPI. Tests run locally:

```bash
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -q -r requirements.txt pyflakes pyyaml localdb.json
/tmp/venv/bin/pip install -q -r addons/addons.txt   # optional-requirements too if you need the boot test complete
bash dev/check_all.sh /tmp/venv/bin/python
```

`dev/check_all.sh` copies only **git-tracked** files (`git add` new files first!) and runs: compile (SyntaxWarning = error), undefined names
across star-imports, relative imports, Telethon names exist in the installed
Telethon, command regex clashes, and a **boot test** that starts the real bot
with a fake Telegram client and loads every plugin. Healthy output today:
`commands registered: 369 | help sections: {'Official': 78, 'Addons': 53}`
and no errors except "No DB requirement fullfilled" and network (graph.org)
errors. For behaviour (animations, BotFather flow, SangMata, AI) earlier
sessions wrote small fake-object tests — do the same for anything you change.
Say honestly that real-Telegram behaviour is only confirmed on the owner's bot.

## Rules learned the hard way (Don't / Do)

- **Don't rename internal names** (`pyUltroid`, `ultroid_bot`, `UltroidDB`, DB
  table `Ultroid`, the compose service). Users' saved data and updates depend on them.
- **Keep license notices**: file headers, `LICENSE`, `telethonpatch/LICENSE`
  and the README "Credits & License" section (AGPL). Visible UI branding is
  "OWNER Assistant" everywhere — don't reintroduce "Ultroid"/TeamUltroid
  links, support chats, or auto-joins.
- `DEVLIST` is empty on purpose (upstream devs had PM-permit/ban bypass).
- Telethon markdown: italic is `__x__` (not `_x_`), bold `**x**`. Custom
  (premium) emoji only parse in **HTML** mode (`<tg-emoji emoji-id="...">`).
- Telethon 1.46 = layer 233: old `KeyboardButton*` types are gone; buttons are
  `KeyboardInlineButton(text, type)`. `Button.inline/url(..., style="primary|danger|success", icon=<custom emoji id>)` exist.
- **Message-edit animations must be flood-safe**: use `play()` in
  `addons/love.py` (edits with `flood_sleep_threshold=0`, stops on FloodWait,
  shows the final frame after, one animation at a time, ~20 edits/min).
  The owner wants **long** animations — slow them down, don't cut frames.
- Never seed the global `random` (use `random.Random(seed)`).
- Read user-uploaded files with `read_text_file()` (binary → None).
- `.env` empty values must not overwrite saved DB values (`update_envs`).
- Talk to BotFather via `client.conversation()` + `_botfather_reply()` in
  `startup/funcs.py` (waits for real replies, handles "try again in N seconds").
- AI defaults: `gemini-flash-latest`, `claude-opus-5-5`, `gpt-5-mini`,
  `deepseek-chat`; on 404 "model retired" the provider's suggested model is
  used once; 429/5xx are retried once.
- YouTube on the VPS needs cookies ("not a bot" check): `.ytcookies` saves a
  cookies.txt in the DB (`YT_COOKIES`); every yt-dlp call goes through
  `ytdl_opts()` in `pyUltroid/fns/ytdl.py`. `deno` + `yt-dlp[default]` are
  installed, and `startup` upgrades yt-dlp on each boot.
- Secrets shown in chat are masked (`mask_secret`) in `.setdb` / `.get`.
- **Repo link is never shown** in the bot (owner asked "repo expose nah"):
  no Repo/Support buttons; `assistant_buttons()` (opens the assistant bot) replaced them.
  `REPO_URL` stays only for internal use (raw image URLs, updater). README keeps
  the AGPL credits.
- Send pictures with `brand_file(name)` (local file, survives a private repo);
  use `brand_url(name)` only where Telegram needs a URL (inline thumbs/InputWebDocument).
- Premium emoji: `pe.install(client)` wraps `client._parse_message_text`, so every
  send/edit gets `MessageEntityCustomEmoji` for emojis saved in DB `PREMIUM_EMOJI`
  ({emoji: document_id}). Userbot: only if `me.premium` and not `PREMIUM_EMOJI_OFF`.
  Assistant bot: only if `PREMIUM_EMOJI_BOT` (Telegram may refuse custom emoji for
  bots without a Fragment username / Premium owner — unverified). Never hard-code
  emoji IDs we haven't seen; the owner saves them with `.pemoji` / `.pemoji pack`.
- Buttons are plain (no `style=` colours) everywhere — owner disliked the
  coloured buttons (removed in #32). Keep new buttons plain.

## What's already done (PRs #1–#20 on `main`)

Fixed hundreds of broken commands (dead APIs, Python 3.12, Pillow 10, emoji 2,
pypdf, yt-dlp, shazamio, Telethon 1.46); addons bundled in repo; Docker/installer
build THIS repo; easy `.env` (only `SESSION` required); Redis URL support;
FloodWait-safe BotFather autobot; log group not recreated on restart; AI
rewrite; secret masking; `.clone` avatar types; SangMata `.sg` by id;
full rebrand to OWNER Assistant + `.botpic`; love animations
(`.propose .love .rose .hearts .lovecalc`, English, flirty, long, flood-safe);
`.carbon/.paste/.open/.ncode` safe on binary files; `.wspr` fixes (#24–#26).
Full A–Z rebrand pass (#27): repo/support links removed everywhere (25 languages,
incl. translated "Ultroid" words), new banners (alive/help/start/deploy/pm) +
upload thumbnail, log-channel photo replaced once (`OA_LOGPIC`), old Ultroid
images deleted, `.ultroid` → `.intro`, file names (logs/zip/updates) renamed,
premium emoji system (`.pemoji`), coloured buttons. #28: `.pemoji pack` takes up to 25 packs.
#29: owner's AI images (uploaded via GitHub) used as avatar/banners/thumb; log-channel
photo re-applied once via `OA_LOGPIC` = 2 (bump it when the avatar changes). Assistant bot DP
only changes when the owner runs `.botpic`. Never use Pinterest/other artists' images.

## Roadmap the owner agreed to (not started)

Order suggested to them: **A → B → C → D**.

- **A. Easy help**: category `.help` (AI, Group, Love/Fun, Download, Media,
  Privacy, Tools), one-line explanation + example per command, `.find <word>`,
  `.guide` first-time tour, `.setlang` (Hinglish/English).
- **B. Modern look**: coloured buttons (green on / red off / blue next),
  expandable blockquotes for long help, premium emoji with automatic fallback
  (needs the owner's account to have Telegram Premium), consistent message style, new `.alive` card.
- **C. Merge the owner's 2–3 other bots** — waiting for their repo links /
  what they do. Either port features as plugins or run them side by side in
  the same docker-compose.
- **D. Pending**: security pack (new-login alert via
  `account.GetAuthorizationsRequest`, `.sessions`, `.kill`, `.killall`,
  `.panic`, `.security` report, `.privacy strict`, `.autologout`, scam-link
  guard, login-code-leak guard, `.backup`); Group-Help-style `/` commands on the
  assistant bot (captcha, rules, report, staff, anti-link/forward/raid, warn
  limits, purge, slowmode, approve); `.hack/.kill/.type` flood-safety;
  non-blocking `requests` calls in youtube/imagetools/imdb/tools.

Open questions to the owner: links to their other bots; do they have
Telegram Premium (needed for `.pemoji`); help language (Hinglish or English); group commands with
`/` (assistant bot, admins can use) or `.` (owner only).

## Never do

- Don't build tools to access other people's accounts, scrape private data,
  mass-spam, or evade Telegram limits. Prank/fun commands are fine; warn about
  spam bans when relevant.
- Don't store the owner's password/2FA anywhere.
