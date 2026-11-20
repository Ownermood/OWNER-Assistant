# 👑 OWNER Assistant — Full Guide (sab kuch ek jagah)

> Ye file `dev/make_full_guide.py` se banti hai. Commands ki list bot ki
> asli help se aati hai — kuch badle to `python3 dev/make_full_guide.py` chalao.

**Is guide mein:**
1. [Ye bot kya hai](#1-ye-bot-kya-hai)
2. [Pehli baar setup (VPS + Docker)](#2-pehli-baar-setup-vps--docker)
3. [Update kaise karein](#3-update-kaise-karein)
4. [Sabse kaam ke commands (examples)](#4-sabse-kaam-ke-commands-examples)
5. [API keys (optional)](#5-api-keys-optional)
6. [Safety rules](#6-safety-rules)
7. [Problem aaye to](#7-problem-aaye-to)
8. Every command — official plugins (~{COMMAND_COUNT} entries total)
9. Every command — extra addons
10. For Claude / developers (technical handoff)

---

## 1. Ye bot kya hai

**OWNER Assistant** aapke **apne Telegram account** se chalta hai (userbot).
Aap kisi bhi chat mein `.` se command likhte ho — jaise `.alive` — aur bot
aapke account se kaam kar deta hai. Saath mein ek **assistant bot**
(`@OWN_CLAT_bot`) bhi hai jo menus, buttons aur inline features chalata hai.

- 77 official plugins + 53 extra addons ≈ **360+ commands**
- AI, group management, DM safety, downloads, media, stickers, love animations, pranks
- Repo: `github.com/Ownermood/OWNER-Assistant` (based on Ultroid, AGPL-3.0)

---

## 2. Pehli baar setup (VPS + Docker)

Sirf **`SESSION`** zaroori hai. Bot khud assistant bot, log group aur database bana leta hai.

**1. VPS mein login** (Termux se):
```bash
ssh root@AAPKA_VPS_IP
```

**2. Docker install** (ek baar):
```bash
curl -fsSL https://get.docker.com | sh
```

**3. Code laao:**
```bash
git clone https://github.com/Ownermood/OWNER-Assistant && cd OWNER-Assistant
```
```bash
cp .env.sample .env
```

**4. SESSION banao** (API ID/HASH: my.telegram.org → API development tools):
```bash
docker compose run --rm ultroid python3 resources/session/ssgen.py
```
`1` chuno → API ID, API HASH, phone, OTP. Session **Saved Messages** mein aayega.

**5. `.env` bharo** (`SESSION=`, `API_ID=`, `API_HASH=`, optional `BOT_TOKEN=`):
```bash
nano .env
```
Save: `Ctrl+O` → Enter → `Ctrl+X`. Phir:
```bash
chmod 600 .env
```

**6. Chalao aur logs dekho:**
```bash
docker compose up -d --build
```
```bash
docker compose logs -f ultroid
```
Telegram mein `.alive` bhejo — jawab aaya to sab set ✅

> Termux (Android) ya bina Docker setup: `SETUP.md` dekho.

---

## 3. Update kaise karein

Docker mein `.update` kaam **nahi** karta. VPS par ye chalao:

```bash
cd ~/Ultroid && git pull && docker compose up -d --build
```
(Naye install mein folder `~/OWNER-Assistant` hai.)

Naya version aaya ya nahi:
```bash
git log --oneline -1
```
Crash report ke **"Last 5 commits"** mein bhi sabse naya merge dikhta hai.

---

## 4. Sabse kaam ke commands (examples)

"Reply karke" = jis message/insaan par chalana hai, us message ko reply karke command bhejo.

### ⚡ Roz ke kaam
| Command | Example | Kaam |
|---|---|---|
| `.alive` | `.alive` | Bot chal raha hai? |
| `.ping` | `.ping` | Speed |
| `.help` | `.help afk` | Menu / kisi plugin ki help |
| `.afk` | `.afk CLAT ki padhai 📚` | Busy auto-reply |
| `.id` | (reply) `.id` | ID |
| `.info` | DM mein `.info` | Poori profile info |
| `.sg` / `.sgu` | `.sg 123456789` | Purane naam / usernames |

### 💬 DM
| Command | Example |
|---|---|
| PM safety on | `.setdb PMSETTING True` |
| Approve / hatao | `.a` · `.da` |
| Block / unblock | `.block` · `.unblock` |
| Message bhejo | `.send @username Hello!` |
| Baad mein bhejo | `.schedule Happy Birthday 🎂 1h` |
| Whisper | `.wspr @username secret baat` |
| Save | (reply) `.save` |

### 🤖 AI
| Command | Example |
|---|---|
| Gemini (free key) | `.gemini Article 21 simple mein samjhao` |
| Claude | `.antr 5 CLAT legal reasoning questions` |
| ChatGPT | `.gpt motivational quote` |
| Auto AI reply | (reply) `.addai` · band `.remai` |

### 💖 Love & fun
| Command | Example |
|---|---|
| Proposal (~2 min) | `.propose Priya` |
| Dil | `.love Priya` |
| Gulaab | `.rose Priya` |
| Dil ki baarish | `.hearts` |
| Love meter | `.lovecalc Rahul Priya` |
| Prank hacking | `.hack` |
| Fake typing | `.ftyping 30` |
| Clone / wapas | (reply) `.clone` · `.revert` |

### 👮 Group (aap admin)
| Command | Example |
|---|---|
| Ban / kick / mute | (reply) `.ban` · `.kick` · `.tmute 1h` |
| Warn | (reply) `.warn spam mat karo` |
| Welcome | `.setwelcome Welcome {mention} 🎉` |
| Filter | (reply) `.addfilter hi` |
| Note | (reply) `.addnote rules` → `#rules` |

### 📥 Download & 🖼️ Media
| Command | Example |
|---|---|
| Gaana | `.song Kesariya` |
| YouTube | `.ytv <link>` · `.yta <link>` |
| Sticker kang | (reply) `.kang` |
| Convert | (reply) `.convert sticker` |
| Photo se text | (reply) `.ocr` |
| Code image | `.carbon print("hi")` |
| Bolkar sunao | `.tts en \| Good morning` |

### 🛠️ Settings
| Kaam | Command |
|---|---|
| Value set | `.setdb KEY value` |
| Value dekho (secret chhupe) | `.get var KEY` |
| Assistant bot DP | `.botpic` |
| Prefix badlo | `.setdb HNDLR !` |
| Logs | `.logs` |

---

## 5. API keys (optional)

Telegram mein **Saved Messages** mein bhejo, phir message **delete** karo. Restart nahi chahiye.

| Key | Kis ke liye | Kahan se |
|---|---|---|
| `.setdb GEMINI_API_KEY key` | `.gemini`, AI chatbot | aistudio.google.com (free) |
| `.setdb ANTHROPIC_KEY key` | `.antr` | console.anthropic.com (paid) |
| `.setdb OPENAI_API_KEY key` | `.gpt` | platform.openai.com (paid) |
| `.setdb DEEPSEEK_API_KEY key` | `.deepseek` | platform.deepseek.com |
| `.setdb CHATBOT_PROVIDER gemini` | chatbot kaunsi AI use kare | — |
| `.setdb OCR_API key` | `.ocr`, `.fastly` | ocr.space |
| `.setdb OPENWEATHER_API key` | `.weather`, `.air` | openweathermap.org |
| `.setdb RMBG_API key` | `.rmbg` | remove.bg |
| `.setdb DEEP_API key` | `.color`, NSFW filter | deepai.org |
| `.setdb GEMINI_MODEL name` | model badalna | — |

> Claude **Pro** plan ke saath API key nahi milti — API alag hai (console.anthropic.com).

---

## 6. Safety rules

- `SESSION`, `BOT_TOKEN`, API keys, VPS password **kabhi kisi ko mat do** (Claude ko bhi nahi).
- Galti se share ho gaya → turant badlo: BotFather `/revoke`, AI Studio mein key delete, naya session.
- Session sirf `bash sessiongen` / `ssgen.py` se — anjaan bot/website se kabhi nahi.
- `.spam` / `.bigspam` kam — account ban ho sakta hai. Check: `.limited`.
- `.addsudo` sirf poore bharose wale ko (sudo = aapke bot ka control).
- `.clone` sirf doston ke saath mazaak — kisi ko dhokha dena galat aur ban-worthy hai.
- `.info` / `.sg` public info hai — kisi ko stalk/pareshan mat karo.

---

## 7. Problem aaye to

| Problem | Hal |
|---|---|
| Fix ke baad bhi purana error | Docker mein update nahi hua → section 3 ka command |
| `FloodWaitError ... seconds` | Telegram ki rok. Utni der ruko, commands mat chalao. Animations ke beech 1-2 min gap |
| `Telegram paused animations for Xs` | Same — X second baad try |
| Bot restart-loop, BotFather spam | `.env` mein `BOT_TOKEN` daalo (BotFather se), phir `docker compose up -d` |
| Har restart naya log group | Update karo (fix ho chuka); `.id` se group ID lo → `.env` `LOG_CHANNEL=` |
| `AuthKeyDuplicated` / session expired | Same session do jagah chal raha tha → naya session banao |
| Gemini `503 high demand` | Google busy — bot khud ek baar retry karta hai; 1 min baad try |
| Gemini `404 model not available` | `.setdb GEMINI_MODEL <jo error mein bataya>` |
| `.carbon` "text or code file" | Photo/PDF nahi, text/code file ya text message par reply karo |
| Koi bhi crash | Log group ka **Error Report** Claude ko bhejo (secrets hata ke) |

---
