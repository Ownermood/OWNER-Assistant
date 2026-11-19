# OWNER Assistant Setup (Easy Guide)

Sab kuch isi ek repo mein hai: bot + saare extra plugins (`addons/` folder).
Alag addons repo ya `ADDONS_URL` ki zaroorat **nahi** hai.

## Sirf 1 cheez zaroori hai: `SESSION`

Baaki sab (assistant bot, log group, database) bot khud bana leta hai.

**SESSION kaise banaye** (repo folder ke andar):

```bash
bash sessiongen
```

Docker use kar rahe ho aur VPS par Python nahi hai, to ye chalao:

```bash
docker compose run --rm ultroid python3 resources/session/ssgen.py
```

`1` (Telethon) chuno, API ID/HASH, phone number aur OTP daalo.
Session aapke Telegram ke **Saved Messages** mein aa jaayega, wahi `SESSION` hai.
(Kisi anjaan bot/website se session mat banwana: wo aapka account le sakte hain.)

> ⚠️ SESSION kisi ko mat dena. Isse koi bhi aapka account chala sakta hai.

Session banane ke liye `API_ID` / `API_HASH` chahiye: https://my.telegram.org → *API development tools*.
Wahi dono `.env` mein bhi daal do (bot ke liye optional hain, par apne wale safe rehte hain).

---

## Tarika 1: Docker (sabse aasaan, VPS / PC)

Database (Redis) apne aap chalu ho jaata hai.

```bash
git clone https://github.com/Ownermood/Ultroid
```

```bash
cd Ultroid && cp .env.sample .env
```

`.env` kholo aur `SESSION=` bharo, phir:

```bash
docker compose up -d --build
```

Logs dekhne ke liye: `docker compose logs -f ultroid`

---

## Tarika 2: Bina Docker (VPS / PC / Termux)

```bash
git clone https://github.com/Ownermood/Ultroid
```

```bash
cd Ultroid && cp .env.sample .env
```

`.env` mein `SESSION=` bharo, phir:

```bash
bash installer.sh
```

```bash
bash startup
```

Database na diya to data ek local file mein save hota hai. VPS/PC ke liye ye theek hai.

---

## Tarika 2b: Termux (Android phone)

[Termux](https://f-droid.org/packages/com.termux/) **F-Droid se** install karo (Play Store wala purana hai), phir:

```bash
pkg install -y git && git clone https://github.com/Ownermood/Ultroid && cd Ultroid
```

```bash
bash install-termux
```

```bash
bash sessiongen
```

`.env` mein `SESSION`, `API_ID`, `API_HASH` bharo:

```bash
nano .env
```

```bash
termux-wake-lock && bash startup
```

- Phone ki **Battery optimization** Termux ke liye band karo, warna Android bot ko band kar dega.
- Termux band karoge / phone restart hoga to bot ruk jaayega; wapas `cd Ultroid && bash startup`.
- Kuch heavy commands (video compress, kuch image tools) phone par slow ya band ho sakte hain.

---

## Tarika 3: Heroku / Render / Koyeb / Railway (cloud)

1. Is repo ko deploy karo (Dockerfile se build hota hai, aapka hi code chalega).
2. Env vars mein `SESSION` daalo.
3. Cloud par local file restart par mit jaati hai, isliye ek **free database** do:
   - Redis: https://redis.io/try-free ya https://upstash.com → `REDIS_URI=redis://default:password@host:port`
   - ya MongoDB Atlas → `MONGO_URI=mongodb+srv://...`

---

## Commands ke liye keys (optional, Telegram se set karo)

Bot chalne ke baad apne chat mein likho, restart ki zaroorat nahi:

| Key | Kis command ke liye | Free kahan se |
|---|---|---|
| `.setdb GEMINI_API_KEY key` | `.gemini`, AI chatbot (`.addai`, `.repai`) | aistudio.google.com |
| `.setdb OPENAI_API_KEY key` | `.gpt` | platform.openai.com |
| `.setdb ANTHROPIC_KEY key` | `.antr` | console.anthropic.com |
| `.setdb DEEPSEEK_API_KEY key` | `.deepseek` | platform.deepseek.com |
| `.setdb CHATBOT_PROVIDER gemini` | chatbot kaunsi AI use kare (`gemini/gpt/antr/deepseek`) | - |
| `.setdb OCR_API key` | `.ocr`, `.fastly` | ocr.space/ocrapi |
| `.setdb OPENWEATHER_API key` | `.weather`, `.air` | openweathermap.org |
| `.setdb RMBG_API key` | `.rmbg` | remove.bg |
| `.setdb DEEP_API key` | `.color`, NSFW filter | deepai.org |
| `.setdb NASA_API key` | `.apod` (bina key bhi chalta hai) | api.nasa.gov |
| `.setdb TWITTER_USERNAME / TWITTER_EMAIL / TWITTER_PASSWORD` | `.tw`, `.twuser`, `.twdetail`, `.twl` | - |
| `.setdb GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET` | Google Drive (optional, default bhi hai) | console.cloud.google.com |
| `.setdb PISTON_URI url` | inline code runner (`@bot run`) | apna Piston server |

AI model badalna ho: `.setdb GEMINI_MODEL gemini-pro-latest` (aise hi `OPENAI_MODEL`, `ANTHROPIC_MODEL`, `DEEPSEEK_MODEL`).

---

## Useful settings

| Setting | Kaam |
|---|---|
| `ADDONS=False` (env) | Extra plugins band karna |
| `.setdb EXCLUDE_ADDONS spam hack` | Kuch addons hatana (naam space se) |
| `.setdb HNDLR !` | Command prefix `.` ki jagah `!` |
| `UPSTREAM_REPO` (env) | `.update` kis repo se update laaye (default: aapka fork) |

## Update

**Docker par chal raha hai** (Tarika 1) → VPS par ye chalao (`.update` Docker mein kaam nahi karta,
kyunki code image ke andar build hota hai):

```bash
cd ~/Ultroid && git pull && docker compose up -d --build
```

**Bina Docker** (Tarika 2 / Termux) → Telegram mein `.update` likho. Ye aapke repo (`UPSTREAM_REPO`) se naya code laata hai.

Naya code aaya ya nahi: crash log ke "Last 5 commits" ya `git log --oneline -1` mein sabse naya merge dekho.

## Problem aaye to

- Bot start nahi ho raha → `SESSION` sahi hai? Expire to nahi hua? Naya banao.
- `FloodWait` → Telegram ne thoda rok diya hai, kuch minute ruko. Spam commands kam use karo, warna account ban ho sakta hai.
- Koi command error de → log group mein error dekho, ya `.logs` likho.
