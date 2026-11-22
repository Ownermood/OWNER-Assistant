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
  asked). #32: coloured buttons removed from the userbot. #33–#36: premium
  emoji experiments in the manager. **#41: ALL premium emoji REMOVED** (owner
  asked "premium emojis hata do completely"): no `manager/emoji.py`, no
  `ui_emoji.json`, no `icon=` on buttons, no `.pemoji`, no `pyUltroid/fns/pemoji.py`.
  Buttons are plain text with normal emojis. Don't bring it back unless asked. Force join: `FORCE_JOIN` (default @VillanCommunity, `off` to
  disable) checked with `GetParticipantRequest` — fails OPEN with a warning if
  the bot isn't admin, so the owner is never locked out. Still owner-only.

## Layout

| Path | What |
|---|---|
| `pyUltroid/` | Core (package name kept on purpose, see "Don't") |
| `pyUltroid/branding.py` | Bot name, banners (`brand_file()` local / `brand_url()` web), `assistant_buttons()` — change branding here |
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
- **No premium (custom) emoji anywhere** (removed in #41, owner's choice). Old DB
  keys `PREMIUM_EMOJI*` may still exist on the VPS; nothing reads them.
- `.funuser` (#34): an allowlist (DB `FUN_USERS`) of user ids who may run
  ONLY `fun=True` commands (the love animations). Gate is in `ultroid_cmd`
  (`fun_users()` + `fun=` kwarg); fun users bypass the owner/sudo check for
  those commands only, never fullsudo or anything else. `.funuser clear` =
  back to owner-only. This is the SAFE answer to "make the bot public" —
  never build multi-user login/session-hosting. #35: Public/Private switch
  for the fun commands — DB-less flag in `data/fun_mode.json` (shared by the
  userbot and the manager, same container/cwd); `.funmode [public|private]`
  on the userbot, and a toggle button on the manager menu. Gate: owner/sudo OR
  fun_public() OR sender in FUN_USERS. **#37: fun mode now defaults to ON and
  also opens the MANAGER BOT to guests** — a non-owner who DMs it gets a
  fun-only menu (`manager/fun.py`, bot-side animations it plays by editing its
  own message) and can never reach login/logout/logs/settings. Force join still
  applies to guests. Earlier the switch only affected the userbot's `.` commands,
  so friends still saw "private bot" — that was the bug the owner hit.
  `manager/fun.py` duplicates love.py's ASCII art on purpose (love.py can't be
  imported outside the userbot); change both if you change a drawing.
  #38: the guest Fun Zone has 16 items (animations, joke, quote, 8-ball, dice,
  truth/dare, fortune, compliment, fake hack, matrix, rate) - all offline, all
  bot-side. The owner asked for "full access" for friends; DANGEROUS commands
  (.eval .bash .setdb .get .logout .restart .shutdown .addsudo) are deliberately
  NEVER exposed to guests - they would hand over the VPS and the owner's whole
  account. Say this plainly if asked again. Also #35: manager persists panel ids in
  the store so a restart deletes the old 'Manager online' panel instead of
  stacking a new one.
- **Text style (#42, owner asked "smooth English, easy to understand")**: all
  user-facing text is plain friendly English - short sentences, say what to do
  next, give an example in help. No small-caps fonts, no whole message in
  `code` backticks, no "u/ur/plz/msg", no "him/his" (use "them"), no Title Case
  On Every Word. Help format: `• \`{i}cmd <arg>\` (reply to ...)` + one plain
  line + `Example:`. Official help lives in `strings/strings/en.yml`
  (`help_<plugin>`, wins over the docstring); addons and the rest use the
  module docstring starting with `📖 **Commands**`. Other 24 language files
  were NOT rewritten (they still hold old translations).
- **Second account (#43)**: the main owner adds another of THEIR OWN ids with
  `/addowner <id>` in the manager (Settings → Second account; max 10). Each gets its
  own slot: `data/manager_<id>.json`, own child userbot with Redis DB number N
  (`REDIS_URI/.../N`), no `BOT_TOKEN`/`LOG_CHANNEL` from .env (autobot makes its own
  assistant bot + log group), `OA_INSTANCE=_<id>` → own `asst_<id>.session` and
  `ultroid_<id>.log`. Same account can't run twice. Strangers see their id in the
  private / fun reply so the owner can copy it. Needs a `redis://` URI (docker default).
  #44: no typing needed - the other id taps **🔑 Get my own userbot** (private reply /
  Fun Zone), the main owner gets **Allow / Deny** buttons (`m:ok_<id>`/`m:no_<id>`,
  main owner only; 10-min cooldown per requester). Owner asked: no `/addowner` hassle.
  #45: **Public login** switch on the main menu (DB `public_login` in manager.json,
  default OFF). ON = anyone tapping the button gets a slot directly (max 10, owner is
  notified with a Remove button); OFF = those `public_users` are routed as guests,
  their userbots stop, and they see "bot is off". Approved (Allow) ids are not affected.
  Owner was warned: strangers' spam can get the VPS banned.
  #47: fun switch is per account (`fun_mode{OA_INSTANCE}.json`; extra accounts default
  private) and public fun mode ignores senders in `data/userbots.json` (all userbot
  account ids, written by the manager on start) - before, one `.love` played on BOTH
  accounts. Warned owner: any added account can `.bash` and read everyone's sessions.
  #51: main account CONTROLS extra accounts: manager passes `OA_CONTROLLER=<main
  account id>`; `pyUltroid/__init__.py` makes it SUDO + FULLSUDO and sets `SUDO_HNDLR`
  to `!` (if unset) so `!cmd` typed by main runs only on that extra account (`.` stays
  main's). Settings → Second account has Run/Restart/Stop per account (`m:sr_/m:ss_`).
  #53: main boots first. #54: **Stop ALL friends' bots** (main menu button `m:all_off`/
  `m:all_on`, `/stopall` `/startall`; DB `all_off` in manager.json): every extra userbot
  stops, those ids are routed as guests and only see "bot is off" (no Fun Zone, can't Run).
  #55: while `all_off`, the manager bot is off for EVERY non-owner (strangers too, no Fun
  Zone); button always shown ("Turn bot OFF/ON for everyone").
  #56: the OA_CONTROLLER block also adds the main id to the extra account's PM-permit
  approved list (`PMPERMIT`) and tries `UnblockRequest` once at boot - PM-permit used to
  warn/block the main account, so its `!` commands never arrived.
  #57: Second-account panel reads the SAVED `owners` dict (not just loaded `self.slots`),
  so an account that failed to load (e.g. REDIS_URI not `redis://` after a rebuild) shows
  as "⚠️ not loaded" instead of the whole list reading "None yet". `load_slots` logs each
  load/skip. If the panel says not loaded, the friend only gets Fun Zone (guest), not their userbot.
  #58: self-heal - `load_slots` scans leftover `manager_<id>.json` files and re-adds any
  account missing from the `owners` index (db number stored in the slot file as `db_index`),
  so accounts never vanish after a restart that lost the index. `/delowner` now deletes the
  slot file (+ fun_mode/log) so a removed account can't come back via self-heal.
  #59: Settings → Other accounts is now a clean list - one button per account (name +
  status) opening a per-account panel (`m:sa_<id>`) with Run/Stop, **Lock/Unlock**
  (`m:lk_`, DB `locked` list - frozen account routed as guest, in `is_off`), **Logout**
  (`m:lo_`, keeps it in the list to re-login), **Remove** (`m:rm_` = delowner).
  #60: clearer private reply - a non-owner DM (fun OFF) now says "This is a private bot
  ... tap Get my own userbot, owner taps Allow, then Login" instead of the misleading
  "bot is off". public_login ON says "get it right away".
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
premium emoji system (`.pemoji`, later removed in #41), coloured buttons.
#29: owner's AI images (uploaded via GitHub) used as avatar/banners/thumb; log-channel
photo re-applied once via `OA_LOGPIC` = 2 (bump it when the avatar changes). Assistant bot DP
only changes when the owner runs `.botpic`. Never use Pinterest/other artists' images.

## Roadmap the owner agreed to (not started)

Order suggested to them: **A → B → C → D**.

- **A. Easy help**: category `.help` (AI, Group, Love/Fun, Download, Media,
  Privacy, Tools), one-line explanation + example per command, `.find <word>`,
  `.guide` first-time tour, `.setlang` (Hinglish/English).
- **B. Modern look**: coloured buttons (green on / red off / blue next),
  expandable blockquotes for long help, consistent message style, new `.alive` card.
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
help language (Hinglish or English); group commands with
`/` (assistant bot, admins can use) or `.` (owner only).

## Never do

- Don't build tools to access other people's accounts, scrape private data,
  mass-spam, or evade Telegram limits. Prank/fun commands are fine; warn about
  spam bans when relevant.
- Don't store the owner's password/2FA anywhere.
