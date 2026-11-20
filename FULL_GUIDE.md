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
8. Every command — official plugins (~441 entries total)
9. Every command — extra addons
10. For Claude / developers (technical handoff)

---

## 1. Ye bot kya hai

**OWNER Assistant** aapke **apne Telegram account** se chalta hai (userbot).
Aap kisi bhi chat mein `.` se command likhte ho — jaise `.alive` — aur bot
aapke account se kaam kar deta hai. Saath mein ek **assistant bot**
bhi hai jo menus, buttons aur inline features chalata hai.

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
| Whisper (group mein bhi) | `.wspr @username secret baat` |
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
| YouTube: `Sign in to confirm you're not a bot` | YouTube VPS ka IP block karta hai. Laptop/PC browser mein **spare Google account** se YouTube login → "Get cookies.txt LOCALLY" extension se `cookies.txt` export → Telegram mein bhejo → reply `.ytcookies`. Cookies expire hon to dobara |
| `.carbon` "text or code file" | Photo/PDF nahi, text/code file ya text message par reply karo |
| Koi bhi crash | Log group ka **Error Report** Claude ko bhejo (secrets hata ke) |

---

## 8. Every command (official plugins)

### 🤖 AI

**aiwrapper**

- `.gemini <question>` — Ask Google Gemini.
- `.antr <question>` — Ask Anthropic Claude.
- `.gpt <question>` — Ask OpenAI ChatGPT.
- `.deepseek <question>` — Ask DeepSeek. Example: `.gemini explain the doctrine of res judicata in 5 lines` Tip: reply to a message to use its text as the question. **Setup (one time)** - add the key for the AI you want: `.setdb GEMINI_API_KEY <key>` / `ANTHROPIC_KEY` / `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` **Change the model (optional):** OPENAI_MODEL (default gpt-5-mini), ANTHROPIC_MODEL (default claude-opus-5-5), GEMINI_MODEL (default gemini-flash-latest), DEEPSEEK_MODEL (default deepseek-chat)

**chatbot**

- `.addai` (reply, or add @username) — Let AI reply to this person for you.
- `.remai` (reply, or add @username) — Stop AI replies for them.
- `.repai` (reply to a message) — Send one AI-written reply to that message.
- `.listai` — See who has AI replies on.

### 👮 Group management

**admintools**

- `.promote` (reply, or add @username) — Make someone an admin.
- `.demote` (reply, or add @username) — Remove someone as admin.
- `.ban <reason>` (reply, or add @username) — Ban someone from the group.
- `.unban` (reply, or add @username) — Let a banned person join again.
- `.kick <reason>` (reply, or add @username) — Remove someone. They can join again later.
- `.pin` (reply to a message) — Pin that message.
- `.tpin <time> <message>` — Pin a message for a short time only.
- `.unpin` (reply) or `.unpin all` — Unpin one message, or all of them.
- `.pinned` — Show the pinned message.
- `.listpinned` — Show all pinned messages.
- `.autodelete <24h / 7d / 1m / off>` — Delete new messages in this chat automatically after that time.
- `.purge` (reply to a message) — Delete every message from that one down to now.
- `.purgeme` (reply to a message) — Same, but only your own messages.
- `.purgeall` (reply to someone) — Delete all messages from that person.

**mute**

- `.mute` (reply, or add user ID) — Stop someone from sending messages here.
- `.unmute` (reply, or add user ID) — Let them talk again.
- `.dmute` (reply, or add user ID) — Mute someone by deleting every message they send.
- `.undmute` (reply, or add user ID) — Stop that.
- `.tmute <time>` (reply, or add user ID) — Mute for a while. Use s, m, h or d. Example: `.tmute 2h`

**warn**

- `.warn <reason>` (reply to someone) — Give a warning. Too many warnings and they get punished.
- `.resetwarn` (reply to someone) — Clear all their warnings.
- `.warns` (reply to someone) — See their warnings.
- `.setwarn <number> | <ban / mute / kick>` — Choose how many warnings are allowed and what happens after. Example: `.setwarn 5 | mute` Default: 3 warnings, then kick.

**locks**

- `.lock <what>` — Stop members from sending this in the group.
- `.unlock <what>` — Allow it again. You can lock: msgs, media, sticker, gif, games, inline, polls, invites, pin, changeinfo Example: `.lock sticker`

**antiflood**

- `.setflood <number>` — Mute people who send more than this many messages in a row. Example: `.setflood 5`
- `.remflood` — Turn the flood limit off.
- `.getflood` — See the current flood limit.

**autoban**

- `.autokick on` / `.autokick off` — Automatically remove everyone who joins the group.

**blacklist**

- `.blacklist <word>` — Delete any message in this chat that has this word. You can give many words with spaces.
- `.remblacklist <word>` — Remove a word from the list.
- `.listblacklist` — See all blocked words. You must be an admin in the chat for this to work.

**greetings**

- **Welcome**
- `.setwelcome <message>` (or reply to a message) — Greet new members with this message.
- `.getwelcome` — See the welcome message.
- `.clearwelcome` — Delete it. **Goodbye**
- `.setgoodbye <message>` (or reply to a message) — Send this when someone leaves.
- `.getgoodbye` — See the goodbye message.
- `.cleargoodbye` — Delete it.
- `.thankmembers on` / `off` — Send a thank-you sticker every time the group reaches another 100 members.

**filter**

- `.addfilter <word>` (reply to a message) — When someone says this word in the chat, I reply with that message. Example: `.addfilter hello`
- `.remfilter <word>` — Delete a filter.
- `.listfilter` — See all filters in this chat.

**notes**

- `.addnote <word>` (reply to a message) — Save a note in this chat. Anyone can get it by typing `#word`. Example: `.addnote rules`  →  type `#rules`
- `.remnote <word>` — Delete a note.
- `.listnote` — See all notes in this chat.

**snips**

- `.addsnip <word>` (reply to a message) — Save a quick reply. Type `$word` anywhere to send it. Example: `.addsnip hi`  →  type `$hi`
- `.remsnip <word>` — Delete a snip.
- `.listsnip` — See all snips.

**nightmode**

- Night mode closes your groups at night (nobody can send messages) and opens them again in the morning.
- `.addnm` — Add this group to night mode.
- `.remnm` — Remove this group from night mode.
- `.listnm` — See all groups with night mode.
- `.nmtime <close hour> <close minute> <open hour> <open minute>` — Choose the times (24-hour clock). Default: close 00:00, open 07:00. Example: `.nmtime 23 00 06 30` closes at 11 PM and opens at 6:30 AM.

**cleanaction**

- `.addclean` — In this chat, delete service messages like 'X joined', 'X left' or 'X pinned a message'.
- `.remclean` — Stop doing that here.
- `.listclean` — See the chats where it's on.

**forcesubscribe**

- `.fsub <channel username or ID>` — New members must join this channel before they can talk in this group.
- `.checkfsub` — See which channel is set for this group.
- `.remfsub` — Turn force-join off for this group. You must be an admin in both the group and the channel.

**nsfwfilter**

- `.addnsfw <ban / mute / kick>` — Delete 18+ pictures in this group and punish the sender. Example: `.addnsfw mute`
- `.remnsfw` — Turn the 18+ filter off.

**profanityfilter**

- `.addprofanity` — Delete messages with bad words in this chat.
- `.remprofanity` — Turn that off.

**tag**

- `.tagall` - tag up to 100 members
- `.tagadmins` - tag the admins
- `.tagowner` - tag the group owner
- `.tagbots` - tag the bots
- `.tagrec` - tag recently active members
- `.tagon` - tag members who are online
- `.tagoff` - tag members who are offline — Online/offline only works for people who show their last seen. ⚠️ Don't tag too often - people get annoyed and may report you.

**polls**

- `.poll <question> ; <option> ; <option>` — Make a poll. Example: `.poll Tea or coffee? ; Tea ; Coffee`
- Add `| <type>` at the end to change the kind of poll: — `| public` - show who voted `| multiple` - allow more than one answer `| quiz_2` - a quiz where option 2 is correct

**globaltools**

- These work in every group where you're an admin.
- `.gban` / `.ungban` (reply, or add @username) — Ban or unban someone everywhere.
- `.gstat` (reply, or add @username) — Check if someone is globally banned.
- `.listgban` — See everyone you've globally banned.
- `.gmute` / `.ungmute` (reply, or add @username) — Mute or unmute someone everywhere.
- `.gkick` (reply, or add @username) — Kick someone from every group.
- `.gcast <text>` (or reply) — Send a message to all your groups.
- `.gadmincast <text>` (or reply) — Send it only to groups where you're an admin.
- `.gucast <text>` (or reply) — Send it to all your private chats. ⚠️ Sending to many chats at once can get your account limited. Use it rarely.
- `.gblacklist` (or `.gblacklist <chat>`) — Skip this chat in all global messages.
- `.ungblacklist` — Stop skipping it.
- `.gpromote <group / channel / all> <title>` (reply to someone) — Make someone an admin everywhere you can. Example: `.gpromote group boss`
- `.gdemote` (reply to someone) — Remove them as admin everywhere.

**chats**

- `.delchat` (or `.delchat <username/id>`) — Delete this group (you must be its owner).
- `.getlink` — Get an invite link for this group.
- `.getlink r` - link where admins must approve joins
- `.getlink r <title>` - same, with a link title
- `.getlink 10` - link that only 10 people can use
- `.create g <name>` - make a new group
- `.create c <name>` - make a new channel
- `.create b <name>` - make a small basic group — Add `; <username>` at the end to give it a public username.
- `.setgpic` (reply to a photo) — Change the group's photo.
- `.delgpic` — Remove the group's photo.
- `.unbanall` — Unban everyone in the group.
- `.rmusers` — Remove members by type (deleted accounts, bots, etc.).

### 🛡️ Privacy, DM & profile

**pmpermit**

- PM security: strangers can't keep messaging you until you approve them.
- `.a` or `.approve` — Allow this person to message you.
- `.da` or `.disapprove` — Take that permission back.
- `.block` / `.unblock` — Block or unblock someone.
- `.unblock all` — Unblock everyone.
- `.logpm` / `.nologpm` — Start or stop saving this person's messages in your log group.
- `.startarchive` / `.stoparchive` — Move new PMs to the archive, or stop doing that.
- `.cleararchive` — Take all chats out of the archive.
- `.listapproved` — See everyone you've approved.

**afk**

- `.afk <reason (optional)>` — Turn on away mode. If someone messages or tags you, they get an automatic reply. Send any message to turn it off. Example: `.afk studying for exams` Tip: reply to a photo or GIF with `.afk <reason>` to show it in the reply.

**profile**

- `.setname <first name> // <last name>` — Change your name. Example: `.setname Rohit // Sharma`
- `.setbio <text>` — Change your bio.
- `.setpic` (reply to a photo) — Change your profile photo.
- `.delpfp` (or `.delpfp <number>`) — Delete your latest profile photo (or that many photos).
- `.poto <username>` — Get someone's profile photo.

**autopic**

- `.autopic <topic>` — Change your profile photo every few minutes with pictures of that topic. Example: `.autopic mountains`
- `.autopic` — Stop it.
- To change how often: `.setdb SLEEP_TIME <seconds>`

**echo**

- `.addecho` (reply to someone) — Repeat everything this person says.
- `.remecho` (reply to someone) — Stop repeating them.
- `.listecho` — See who is being echoed.

**fakeaction**

- Show a fake status at the top of the chat for some seconds. — Example: `.ftyping 30` shows 'typing...' for 30 seconds.
- `.ftyping <seconds>` - typing...
- `.faudio <seconds>` - recording audio...
- `.fvideo <seconds>` - sending video...
- `.fgame <seconds>` - playing a game...
- `.fsticker <seconds>` - choosing a sticker...
- `.flocation <seconds>` - sending location...
- `.fcontact <seconds>` - choosing a contact...
- `.fround <seconds>` - recording a video message...
- `.fphoto <seconds>` - sending a photo...
- `.fdocument <seconds>` - sending a file...

**schedulemsg**

- `.schedule <message> <time>` (or reply to a message) — Send a message later. Time can be seconds (`100`), minutes (`10m`) or hours (`1h`). Example: `.schedule Hello 1h`

**other**

- `.send <username / id> <message>` (or reply to a message) — Send a message to another chat.
- `.fwdreply` (reply to a message) — Reply to that person in your private chat with them.
- `.save` (reply to a message) — Copy it to your Saved Messages.
- `.fsave` (reply to a message) — Forward it to your Saved Messages.

**extra**

- `.del` (reply to a message) — Delete that message.
- `.edit <new text>` — Edit your last message (or the one you reply to).
- `.copy` (reply to a message) — Send a copy of that message or file.
- `.reply` (reply to someone) — Make your last message a reply to them.

### 📢 Channels & broadcast

**channelhacks**

- 🔹 **Copy old posts**
- `.shift <from channel> | <to channel>` — Copy all old posts from one channel to another. Example: `.shift @abc | @xyz` (the ` | ` is needed) 🔹 **Auto-forward new posts** New posts in a *source* channel are copied to your *destination* channels.
- `.asource <channel>` - add a source channel
- `.dsource <channel>` - remove a source channel
- `.listsource` - see source channels
- `.adest <channel>` - add a destination channel
- `.ddest <channel>` - remove a destination channel
- `.listdest` - see destination channels — You can add many channels. Use a username or ID. To turn auto-forwarding on: `.setdb AUTOPOST True`

**broadcast**

- `.addch` (or `.addch <chat id>`) — Add this chat (or the given one) to your broadcast list.
- `.remch` / `.remch <chat id>` / `.remch all` — Remove this chat, the given one, or all chats from the list.
- `.broadcast` (reply to a message) — Send that message to every chat in your list.
- `.forward` (reply to a message) — Forward that message to every chat in your list.
- `.listchannels` — See your list.

### 📥 Download & upload

**youtube**

- `.yta <link>` — Download the audio from a YouTube (or other) link.
- `.ytv <link>` — Download the video from a link.
- `.ytsa <song name>` — Search YouTube and send the audio. Example: `.ytsa believer`
- `.ytsv <video name>` — Search YouTube and send the video.
- `.ytcookies` (reply to a cookies.txt file) — Fix the "Sign in to confirm you're not a bot" error. Export YouTube cookies (cookies.txt) from a browser logged in to a spare Google account, send the file here and reply to it with this command. `.ytcookies` - see status   ·   `.ytcookies del` - remove them

**downloadupload**

- `.ul <path to file>` — Send a file from the server to Telegram. Extra options (add before or after the path): `--stream` - send as a playable video/audio `--delete` - delete the file after sending `--no-thumb` - send without a cover image
- `.dl <file name (optional)>` (reply to a file) — Save a Telegram file to the server.
- `.download <link> | <file name (optional)>` — Download a file from a direct link.

**gdrive**

- `.gdul` (reply to a file) or `.gdul <file path>` — Upload a file to your Google Drive.
- `.gdown <link or file ID> | <file name (optional)>` — Download a file from Google Drive.
- `.gdsearch <name>` — Search your Google Drive and get links.
- `.gdlist` — List all your Google Drive files.
- `.gdfolder` — Get the link to your upload folder. If one is set, every upload goes there.

**webupload**

- `.webupload` (reply to a file) — Upload a file to a website and get a download link.

**fileshare**

- `.store` (reply to a message or file) — Save it and get a share link. Anyone with the link can get it from your assistant bot.
- `.delstored <link>` — Delete a stored file.
- `.liststored` — See all your stored files.
- Type your assistant bot's username and then `filestore` in any chat to see them there.

**ziptools**

- `.zip` (reply to a file) — Put the file in a .zip. Add a password: `.zip <password>`
- `.unzip` (reply to a .zip file) — Open a .zip and send the files inside.
- `.addzip` (reply to a file) — Add a file to a list to zip together later.
- `.dozip` — Zip all files you added with `.addzip`. Add a password: `.dozip <password>`

### 🖼️ Media, stickers & images

**stickertools**

- `.kang` (reply to a photo or sticker) — Add it to your own sticker pack.
- `.packkang <pack name>` (reply to a sticker) — Copy the whole sticker pack into a new pack of yours.
- `.tiny` (reply to a photo or sticker) — Make a tiny sticker.
- `.round` (reply to a photo or video) — Make a round sticker.
- `.destroy` (reply to an animated sticker) — Mess up an animated sticker for fun.

**converter**

- `.convert <gif / img / sticker / webm>` (reply to media) — Change a photo, sticker or video into another type. Example: `.convert gif`
- `.doc <file name>` (reply to a text message) — Save the text as a file. Example: `.doc notes.txt`
- `.open` (reply to a file) — Show the text inside a file.
- `.rename <new name>` (reply to a file) — Rename a file. Include the extension, like `.pdf`.
- `.thumbnail` (reply to an image) — Use this image as the cover for files you upload.

**imagetools**

- Reply to a photo or sticker with any of these:
- `.border` - add a border — Example: `.border 12,22,23 ; 5` (colour as R,G,B ; width)
- `.grey` - black and white
- `.color` - add colour to a black and white photo
- `.toon` - cartoon look
- `.danger` - red danger look
- `.negative` - negative colours
- `.blur` - blur it
- `.quad` - swirl effect
- `.mirror` - mirror image
- `.flip` - flip upside down
- `.sketch` - pencil sketch
- `.blue` - blue look
- `.pixelator` - pixel look
- `.csample <colour>` — Show a sample of a colour. Example: `.csample red` or `.csample #ffffff`

**logo**

- `.logo <text>` — Make a logo with your text. Reply to a photo to write the text on it. Reply to a font file to use that font.

**glitch**

- `.glitch` (reply to a photo or sticker) — Make a glitchy GIF from it.

**giftools**

- `.invertgif` (reply to a GIF) — Invert the colours.
- `.bwgif` (reply to a GIF) — Make it black and white.
- `.rvgif` (reply to a GIF) — Play it backwards.
- `.vtog` (reply to a video) — Turn a video into a GIF.
- `.gif <search>` — Find and send a GIF. Example: `.gif happy dance`

**videotools**

- `.sample <seconds>` (reply to a video) — Make a short clip from the video.
- `.vshots <number>` (reply to a video) — Take that many screenshots from the video.
- `.vtrim <start> - <end>` (reply to a video) — Cut the video. Times are in seconds. Example: `.vtrim 10 - 40`

**audiotools**

- `.makevoice` (reply to an audio) — Turn an audio file into a voice note.
- `.atrim <start>-<end>` — Cut an audio. Times are in seconds. Example: `.atrim 50-70`
- `.extractaudio` (reply to a video) — Get the sound from a video as an audio file.

**compressor**

- `.compress` (reply to a video) — Make a video smaller.
- `.compress <number>` (reply to a video) — Choose the quality. Lower number = better quality but bigger file. Default is 27. Example: `.compress 23`
- `.compress <number> stream` — Send the result as a playable video.

**mediatools**

- `.mediainfo` (reply to a file) — See details like size, length and quality.
- `.rotate <degrees>` (reply to a photo/video) — Turn it. For videos use 90, 180 or 270.

**resize**

- `.size` (reply to a photo) — See its width and height.
- `.resize <width> <height>` (reply to a photo) — Change its size. Example: `.resize 690 960`

**qrcode**

- `.qrcode <text>` (or reply to a message) — Make a QR code.
- `.addqr <text>` (reply to a photo) — Make a QR code and put it on the photo.
- `.qrdecode` (reply to a QR code) — Read what the QR code says.

**pdftools**

- `.pdf` (reply to a PDF) — Send every page as an image. `.pdf 3` - only page 3   ·   `.pdf 1-7` - pages 1 to 7
- `.pdtext` (reply to a PDF) — Get the text from the PDF. `.pdtext 3` - only page 3   ·   `.pdtext 1-7` - pages 1 to 7
- `.pdscan` (reply to a photo) — Scan a photo of a page (crop and clean it) and send it as a PDF.
- `.pdsave` (reply to a photo or PDF) — Scan it and keep it aside, so you can join many pages into one PDF.
- `.pdsend` — Join all the pages you saved with `.pdsave` and send one PDF.

**beautify**

- `.carbon <text>` (or reply to a message or text file) — Turn text or code into a nice-looking image.
- `.rcarbon <text>` — Same, with a random background colour.
- `.ccarbon <colour> <text>` — Same, with the colour you choose. Example: `.ccarbon red hello`
- `.rayso <theme> <text>` (or reply to a message) — Another code-image style.
- `.rayso list` — See the themes.

**writer**

- `.write <text>` (or reply to a message) — Write the text on a page, like handwriting.
- `.image <text>` (or reply to text or an HTML file) — Turn text or HTML into an image.

**fontgen**

- `.font <font name> : <text>` — Write text in a fancy font. Example: `.font bold : hello`
- `.font` — See all fonts.

**unsplash**

- `.unsplash <search> ; <how many>` — Get free photos from Unsplash. Example: `.unsplash beach ; 3`

### 🔎 Search & info

**search**

- `.saavn <song>` — Download a song from JioSaavn.
- `.google <search>` — Search Google.
- `.github <username>` — See someone's GitHub profile.
- `.img <search>`
- `.img <search> ; <how many>` — Search for pictures. Example: `.img red rose ; 5`
- `.reverse` (reply to a photo or sticker) — Find where a picture comes from.

**words**

- `.meaning <word>` — Get the meaning of a word. Example: `.meaning eloquent`
- `.synonym <word>` — Words with the same meaning.
- `.antonym <word>` — Words with the opposite meaning.
- `.ud <word>` — Look up slang on Urban Dictionary.

**weather**

- `.weather <city>` — See the weather in a city. Example: `.weather Delhi`
- `.air <city>` — See the air quality in a city. Needs an OpenWeatherMap API key: `.setdb OPENWEATHER_API <key>`

**misc**

- `.eod` — See what happened on this day in history.
- `.pntrst <link>` — Download a Pinterest pin.
- `.gadget <name>` — Search for a phone or gadget.
- `.randomuser` — Make up details for a random fake person.
- `.ascii` (reply to a photo) — Turn a photo into ASCII art.

**utilities**

- `.info` (reply, or add username/ID) — See details about a person or chat.
- `.stats` — See how many chats, groups and channels you have.
- `.date` — Show today's date and a calendar.
- `.kickme` — Leave this group.
- `.invite <username / id>` — Add someone to this group.
- `.listreserved` — See the public usernames (groups/channels) you own.
- `.paste <text>` (or reply to a text file) — Upload long text and get a link.
- `.telegraph` (reply to a photo or text) — Upload it to Telegraph and get a link.
- `.rmbg` (reply to a photo) — Remove the background from a photo.
- `.suggest` (reply to a message, or add a question) — Make a quick Yes/No poll.
- `.cpy` (reply to a message) then `.pst` — Copy a message with its formatting, then paste it anywhere. Works for 24 hours.
- `.getmsg <message link>` — Get a message from a chat that blocks forwarding or saving.
- `.thumb` (reply to a file) — Get the file's cover image.
- `.ipinfo <IP address>` — See where an IP address is from.
- `.json` (reply to a message) — See the message's raw data (for developers).

**tools**

- `.id` — Get an ID. Reply to a person or sticker for theirs, or send it alone for the chat's ID.
- `.sg` (reply, or add username/ID) — See someone's old names and usernames.
- `.tr <language code>` (reply to a message) — Translate it. Example: `.tr hi` (Hindi) or `.tr en` (English)
- `.webshot <link>` — Take a screenshot of a website.
- `.shorturl <link>` — Make a short link.
- `.circle` (reply to an audio or GIF) — Turn it into a round video message.
- `.hl <link> <text (optional)>` — Hide a link behind text.
- `.bots` — List the bots in this chat.
- `.ls` — See the files in a folder on your server.

**calculator**

- `.calc` — Open a calculator with buttons.

**specialtools**

- `.wspr @username <message>` (or reply to someone with `.wspr <message>`) — Send a secret message in any chat. Only that person (and you) can open it. Up to 200 characters. `.wspr @username` alone shows their profile card.
- `.q` (reply to a message) — Turn messages into a quote sticker. `.q <colour>` - choose the background colour `.q 3` - quote 3 messages together (up to 20) `.q r` - include the message it replied to
- `.sticker <search>` — Find stickers.
- `.getaudio` (reply to an audio) — Pick an audio to add to a video.
- `.addaudio` (reply to a video or GIF) — Put that audio on this video.
- `.dob <dd/mm/yyyy>` — See age and birthday details. Example: `.dob 01/01/2008`
- `.wall <search>` — Find HD wallpapers.

**twitter**

- `.tw <text>` — Post a tweet.
- `.twdetail <tweet link or ID>` — See a tweet's details (likes, replies, quotes).
- `.twuser <username>` — See a Twitter/X profile.
- `.twl <tweet link>` — Download a tweet's photos and videos.

**stories**

- `.setstory` (reply to a photo or video) — Post it as your Telegram story.
- `.storydl <username or story link>` (or reply to someone) — Download someone's stories, or one story from its link.

### ⚙️ Bot, settings & developer

**bot**

- `.alive` | `.alive inline` — Check that your bot is running.
- `.ping` — See how fast the bot replies.
- `.botpic` (reply to a photo, optional) — Change your assistant bot's profile photo.
- `.update` — Check for new updates.
- `.cmds` — List all plugin names.
- `.restart` — Restart the bot.
- `.logs` — Get the bot's log file (useful when something breaks).
- `.logs carbon` — Get the logs as an image.
- `.logs heroku` — Get the last 100 lines of Heroku logs.
- `.shutdown` — Turn the bot off.

**core**

- `.install` (reply to a plugin file) — Add a new plugin.
- `.install f` — Force install it.
- `.uninstall <name>` — Remove a plugin you added.
- `.load <name>` — Turn on a plugin you turned off.
- `.unload <name>` — Turn off a plugin you added (until restart).
- `.help <name>` — Show the help for any plugin. Example: `.help afk`
- `.getaddons <raw link>` — Install a plugin from a link.

**database**

- ⚠️ **Advanced - only use these if you know what you're changing.**
- `.setdb <name> <value>` — Save a setting. Example: `.setdb PMWARNS 3` Use ` | ` if the value has spaces: `.setdb ALIVE_TEXT | I'm online!` Add `-e` to add to the existing value: `.setdb -e <name> <value>`
- `.deldb <name>` — Delete a setting.
- `.rendb <old name> | <new name>` — Rename a setting.

**variables**

- ⚠️ **Advanced.**
- `.get var <name>` — See the value of a setting.
- `.get type <name>` — See what type of value it is.
- `.get db <name>` — See a value saved in the database.
- `.get keys` — List all saved setting names.

**sudo**

- Sudo users can use your bot's commands. Only add people you fully trust.
- `.addsudo` (reply, or add user IDs with spaces) — Add sudo users.
- `.delsudo` (reply, or add user IDs with spaces) — Remove sudo users.
- `.listsudo` — See all sudo users.

**usage**

- `.usage` — See your server's CPU, RAM, disk and data use.
- `.usage heroku` — See Heroku usage.
- `.usage db` — See how much database space is used.

**asstcmd**

- `.addcmd <word>` (reply to a message) — Make a new /command for your assistant bot. It answers with the message you replied to. Example: `.addcmd rules`  →  people can send /rules
- `.remcmd <word>` — Delete that command.
- `.listcmd` — See all your commands.

**button**

- `.button <text with buttons>` — Send a message with link buttons. You can also reply to a photo. Write each button as `[Name | link]`. Put `| same` at the end to keep it on the same row. Example: `.button Hey there! 😎 [Google | https://google.com][YouTube | https://youtube.com | same] [Instagram | https://instagram.com]`

**devtools**

- ⚠️ **Advanced - these run code on your server.**
- `.bash <command>` — Run a Linux command.
- `.bash -c <command>` — Same, but show the result as an image.
- `.eval <code>` — Run Python code. Shortcuts you can use: client = bot = event.client e = event p = print reply = await event.get_reply_message() chat = event.chat_id
- `.cpp <code>` — Run C++ code.
- `.sysinfo` — See your server's details.

**vctools**

- `.startvc` — Start a voice chat in this group.
- `.stopvc` — End the voice chat.
- `.vctitle <title>` — Change the voice chat's title.
- `.vcinvite` — Invite all group members to the voice chat. (Join it yourself first.)

## 9. Every command (extra addons)

### 💖 Love

**love**

- `.propose <name>` (or reply to someone) — A long, flirty proposal story 💍 - walk-up, ring, a rose drawn dot by dot, a beating heart, pick-up lines and the big question.
- `.love <name>` — A heart drawn dot by dot that comes alive and beats for them ❤️
- `.rose <name>` — A rose that blooms dot by dot 🌹
- `.hearts` — It's raining hearts 💕
- `.lovecalc <name 1> <name 2>` — The (totally scientific) love meter 💘

### 🎉 Fun & pranks

**fun**

- `.joke` — Get a joke.
- `.decide` — Can't decide? Get a yes / no / maybe.
- `.url <long link>` — Make a short link.
- `.phlogo <word 1> <word 2>` — Make a two-colour logo with your words.
- `.gps <place>` — Show a place on the map.
- `.xo` — Play tic-tac-toe (only in chats where inline bots are allowed).
- `.wordi` — Play a word game (only in chats where inline bots are allowed).

**hack**

- `.hack` — Do a Prank With Replied user.

**animations**

- `.kill` — A short, silly 'fire!' animation.
- `.fp` — Send a facepalm 🤦‍♂

**typing**

- `.type <message>` — Show your message appearing letter by letter, like live typing.

**truthdare**

- `.truth` — Get a truth question.
- `.dare` — Get a dare.

**random**

- Get something random:
- `.random dog` / `cat` / `fox` / `duck` - a cute photo
- `.random quote` / `quotable` - a quote
- `.random word` - a random word
- `.random celebrity` - a random celebrity

**inlinefun**

- `.uta <song>` — Search and download a song.
- `.gglax <text>` — Make a funny 'Google search' sticker.
- `.stic <emoji>` — Get random stickers for an emoji.
- `.frog <text>` — Make a frog sticker holding your text.
- `.tweet <text>` — Make a fake tweet image.
- `.quot <text>` — Write a quote on an animated sticker.

**waifu**

- `.waifu <text>` — Put your text on a random anime sticker.

**memify**

- `.mmf <top text> ; <bottom text>` (reply to a photo or sticker) — Make a meme sticker.
- `.mms <top text> ; <bottom text>` (reply to a photo or sticker) — Make a meme picture. Try other fonts by adding `_1` to `_10` at the end. Example: `.mms when the exam ; is tomorrow_3`

**sticklet**

- `.sticklet <text>` — Make a colourful text sticker.

**figlet**

- `.figlet <text>` — Write text in big ASCII letters.

**fontsnew**

- Write your text in a fun style:
- `.weeb <text>` - 山乇乇乃
- `.tantext <text>` - ᎿᎯᏁᎿᏋﾒᎿ
- `.linetext <text>` - 𝕃𝕀ℕ𝔼𝕋𝔼𝕏𝕋
- `.boxtext <text>` - 🄱🄾🅇🅃🄴🅇🅃
- `.bubbletext <text>` - ⒷⓊⒷⒷⓁⒺⓉⒺⓍⓉ
- `.cursive <text>` - 𝓬𝓾𝓻𝓼𝓲𝓿𝓮
- `.greekify <text>` - ϑгεεκιғψ
- `.sorcify <text>` - ֆօʀƈɛʀɛʀ
- `.fraktify <text>` - 𝖋𝖗𝖆𝖐𝖙𝖚𝖗𝖊
- `.rusify <text>` - яц$їfч

**quote**

- `.qbot` (reply to a message) — Make a quote sticker from a message.

**quotefancy**

- `.qfancy` — Get a random quote picture.

**howto**

- `.htg <question>` — Send a 'let me Google that for you' link.
- `.htd <question>` — Same, with DuckDuckGo.

**activitygen**

- `.bored` — Get an idea for something to do when you're bored.

**brainfuck**

- `.bf <text>` (or reply) — Turn text into Brainfuck code.
- `.rbf <code>` (or reply) — Run Brainfuck code and show the result.

**morsecode**

- `.mencode <text>` — Turn text into Morse code.
- `.mdecode <Morse code>` — Turn Morse code back into text.

**encodedecode**

- `.encode <text>` (or reply) — Turn text into base64 code.
- `.decode <code>` (or reply) — Turn base64 code back into text.

**clone**

- `.clone` (reply, or add @username) — Copy someone's name, bio and photo onto your account (for fun).
- `.revert` — Go back to your own name, bio and photo.

### ⚠️ Spam (use carefully — can get your account limited)

**spam**

- ⚠️ Spamming can get your account limited or banned by Telegram. Use with care.
- `.spam <count> <message>` (or reply to a message) — Send a message many times (1 to 99).
- `.bigspam <count> <message>` (or reply) — Send it 100 or more times.
- `.delayspam <seconds> <count> <message>` — Send it many times with a pause between each.
- `.tspam <text>` — Send the text one letter at a time.

**stickerspam**

- `.sspam <seconds between (optional)>` (reply to a sticker) — Send every sticker from that pack, one by one. ⚠️ Too many messages can get your account limited.

### 🎵 Music & voice

**song**

- `.song <song name>` — Find the song on YouTube and send the audio.
- `.lyrics <song name>` — Get the song's lyrics.

**findsong**

- `.findsong` (reply to a song) — Find the song's name.

**whichsong**

- `.whichsong` (reply to a song file) — Find out which song it is.

**speechtool**

- `.tts <language code> | <text>` — Turn text into a voice message. Example: `.tts en | hello everyone` Or reply to a message: `.tts hi`
- `.stt` (reply to a voice or audio) — Turn speech into text. It isn't always 100% right.

### 🔎 Info & search

**wikipedia**

- `.wiki <search>` — Search Wikipedia.

**imdb**

- `.imdb <movie name>` — Get a movie's details from IMDb.

**anime**

- `.character <name>` — Get details about an anime character.

**animedb**

- `.manga <name>` — Get details about a manga (from anilist.co).

**animechan**

- `.aniquote` — Get a random anime quote.

**pokedex**

- `.pokemon <name>` — Get details about a Pokémon.
- `.pokecard <name>` — Get a Pokémon card picture.

**astronomy**

- `.apod` — Get NASA's astronomy picture of the day.

**covid**

- `.covid <country>` — See COVID-19 numbers for a country.

**flaticon**

- `.icon <search>` — Find an icon on flaticon.com and send it as a sticker.

**searchmsgs**

- `.search <text>` — Find messages in this chat that have this text.
- `.search -r <text> : <how many>` — Same, but start from the oldest messages. Examples: `.search hello`   ·   `.search -r exam : 10`

**totalmsgs**

- `.totalmsgs` — See how many messages you've sent in this chat.
- `.totalmsgs <username>` (or reply to someone) — See how many messages they've sent here.

### 🧰 Tools

**ocr**

- `.ocr <language code>` (reply to a photo) — Read the text in a photo. Example: `.ocr eng` Needs a free key from ocr.space: `.setdb OCR_API <key>`

**fastly**

- `.fastly` — Turn the @FastlyWriteBot auto-answer on or off. It tries to reply first to that bot's typing games. Needs an OCR key: get one at ocr.space/ocrapi, then `.setdb OCR_API <key>`. For copies of that bot, add their user IDs to `FASTLY_CLONES`.

**spellcheck**

- `.spcheck <text>` (or reply) — Check the spelling and get the corrected text.

**autocorrect**

- `.autocorrect` — Turn autocorrect on or off. It fixes spelling in your English messages. Messages that end with `..` are left as they are.

**ncode**

- `.ncode` (reply to a code file) — Send the code as a nice-looking image.

**autoprofile**

- `.autoname` / `.stopname` — Start or stop showing the live time and date in your name.
- `.autobio` / `.stopbio` — Start or stop a live bio with the date, time and a random line.

**wreplace**

- `.wreplace <how many messages> <old word>;<new word>` — Replace a word in your own recent messages. Example: `.wreplace 10 Hi;Hello` changes 'Hi' to 'Hello' in your last 10 messages.

**limited**

- `.limited` — Check if Telegram has limited your account (asks @SpamBot).

**servertest**

- `.test` — Test your server's internet speed.

### 🔍 Inline (assistant bot)

These run on your assistant bot — type them in any chat after `@YourAssistantBot ` (inline mode):

- `@bot gh <github username>` — someone's latest GitHub activity
- `@bot imdb <movie>` — movie details (needs `.setdb OMDb_API key`, free at omdbapi.com)
- `@bot npm <package>` — search npm packages
- `@bot pypi <package>` — search Python packages
- `@bot omgu <query>` — search OMG! Ubuntu articles
- `@bot winget <app>` — search Windows (winget) apps
- `@bot xda <query>` — search XDA Developers

---

## 10. For Claude / developers (technical handoff)

> Same content as `CLAUDE.md` in the repo. Give this file to any Claude to continue the project.

You are continuing work on **OWNER Assistant**: a Telegram userbot (it logs in
as the owner's own Telegram account) plus an assistant bot. It is a fork of
[Ultroid](https://github.com/TeamUltroid/Ultroid) (AGPL-3.0) that was fixed,
modernised and rebranded in an earlier long Claude session. Read this whole
file before changing anything.

### The owner (how to talk to them)

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

### Where it runs

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

### Layout

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

### How to test (no Telegram needed)

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

### Rules learned the hard way (Don't / Do)

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
- Buttons are plain (no `style=` colours) everywhere — owner disliked the
  coloured buttons (removed in #32). Keep new buttons plain.

### What's already done (PRs #1–#20 on `main`)

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

### Roadmap the owner agreed to (not started)

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

### Never do

- Don't build tools to access other people's accounts, scrape private data,
  mass-spam, or evade Telegram limits. Prank/fun commands are fine; warn about
  spam bans when relevant.
- Don't store the owner's password/2FA anywhere.
