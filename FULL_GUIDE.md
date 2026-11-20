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
8. Every command — official plugins (~456 entries total)
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

- `.gemini <prompt>` — Get response from Google Gemini.
- `.antr <prompt>` — Get response from Anthropic Claude.
- `.gpt <prompt>` — Get response from OpenAI GPT.
- `.deepseek <prompt>` — Get response from DeepSeek AI. Reply to a message to use its text as the prompt. Set API keys using:
- GEMINI_API_KEY / ANTHROPIC_KEY / OPENAI_API_KEY / DEEPSEEK_API_KEY — Set custom models using:
- OPENAI_MODEL: default: gpt-5-mini
- ANTHROPIC_MODEL: default: claude-opus-5-5
- GEMINI_MODEL: default: gemini-flash-latest
- DEEPSEEK_MODEL: default: deepseek-chat

**chatbot**

- `.addai <reply to user/give username/userid>` — Add a AI ChatBot to reply to that user.
- `.remai <reply to user/give username/userid>` — Remove the AI ChatBot.
- `.repai <reply to user/give a message>` — Reply to the user with a message by an AI.
- `.listai` — List the currently AI added users.

### 👮 Group management

**admintools**

- `.promote <reply to user/userid/username>`
- `.demote` — Promote/Demote the user in the chat.
- `.ban <reply to user/userid/username> <reason>`
- `.unban` — Ban/Unban the user from the chat.
- `.kick <reply to user/userid/username> <reason>` — Kick the user from the chat.
- `.pin <reply to message>` — Pin the message in the chat
- `.tpin <time> <temp pin message>`
- `.unpin (all) <reply to message>` — Unpin the messages in the chat.
- `.pinned` — Get pinned message in the current chat.
- `.listpinned` — Get all pinned messages in current chat
- `.autodelete <24h/7d/1m/off>` — Enable Auto Delete Messages in Chat.
- `.purge <reply to message>` — Purge all messages from the replied message.
- `.purgeme <reply to message>` — Purge Only your messages from the replied message.
- `.purgeall` — Delete all msgs of replied user.

**mute**

- `.mute <reply to msg/ user id>` — Mute user in current chat.
- `.unmute <reply to msg/ user id>` — Unmute user in current chat.
- `.dmute <reply to msg/ user id>` — Mute user in current chat by deleting msgs.
- `.undmute <reply to msg/ use id>` — Unmute dmuted user in current chat.
- `.tmute <time> <reply to msg/ use id>` — s- seconds m- minutes h- hours d- days Mute user in current chat with time.

**warn**

- `.warn <reply to user> <reason>` — Gives Warn.
- `.resetwarn <reply to user>` — To reset All Warns.
- `.warns <reply to user>` — To Get List of Warnings of a user.
- `.setwarn <warn count> | <ban/mute/kick>` — Set Number in warn count for warnings After putting ' | ' mark put action like ban/mute/kick Its Default 3 kick Example : `setwarn 5 | mute`

**locks**

- `.lock <msgs/media/sticker/gif/games/inline/polls/invites/pin/changeinfo>` — Lock the Used Setting in Used Group.
- `.unlock <msgs/media/sticker/gif/games/inline/polls/invites/pin/changeinfo>` — UNLOCK the Used Setting in Used Group.

**antiflood**

- `.setflood <integer>` — Set flood limit in a chat.
- `.remflood` — Remove flood limit from a chat.
- `.getflood` — Get flood limit of a chat.

**autoban**

- `.autokick <on/off>` — on - To enable. off - To disable. Automatically kick new joined users from the group.

**blacklist**

- `.blacklist <word/all words with a space>` — blacklist the choosen word in that chat.
- `.remblacklist <word>` — Remove the word from blacklist..
- `.listblacklist` — list all blacklisted words. 'if a person uses blacklist Word his/her msg will be deleted' 'And u Must be Admin in that Chat'

**greetings**

- `.setwelcome <message/reply to message>` — Set welcome message in the current chat.
- `.clearwelcome` — Delete the welcome in the current chat.
- `.getwelcome` — Get the welcome message in the current chat. ---- GoodByes ----
- `.setgoodbye <message/reply to message>` — Set goodbye message in the current chat.
- `.cleargoodbye` — Delete the goodbye in the current chat.
- `.getgoodbye` — Get the goodbye message in the current chat.
- `.thankmembers on/off` — Send a thank you sticker on hitting a members count of 100*x in your groups.

**filter**

- `.addfilter <word><reply to a message>` — add the used word as filter relating to replied message.
- `.remfilter <word>` — Remove the filtered user..
- `.listfilter` — list all filters.

**notes**

- `.addnote <word><reply to a message>` — add note in the used chat with replied message and choosen word.
- `.remnote <word>` — Remove the note from used chat.
- `.listnote` — list all notes.
- Use : — set notes in group so all can use it. type `#(Keyword of note)` to get it

**snips**

- `.addsnip <word><reply to a message>` — add the used word as snip relating to replied message.
- `.remsnip <word>` — Remove the snip word..
- `.listsnip` — list all snips.
- Use : — type `$(ur snip word)` get setted reply.

**nightmode**

- At Night it will turn off everyone permission to send message in  an all groups which you added via `.addnight` — And Turn On auto at morning
- `.addnm` — Add NightMode To Add Group To Auto Night Mode.
- `.remnm` — Remove NightMode To remove Group From Auto Night Mode
- `.listnm` — List NightMode To Get All List of Groups where NightMode Active.
- `.nmtime <close hour> <close min> <open hour> <open min>` — NightMode Time By Default Its close 00:00 , open 07:00 Use 24hr format Ex- `nmtime 01 00 06 30`

**cleanaction**

- `.addclean` — Clean all Upcoming action msg in added chat like someone joined/left/pin etc.
- `.remclean` — Remove chat from database.
- `.listclean` — To get list of all chats where its activated.

**forcesubscribe**

- `.fsub <chat username><id>` — Enable ForceSub in Used Chat !
- `.checkfsub` — Check/Get Active ForceSub Setting of Used Chat.
- `.remfsub` — Remove ForceSub from Used Chat ! Note - You Need to be Admin in Both Channel/Chats in order to Use ForceSubscribe.

**nsfwfilter**

- `.addnsfw <ban/mute/kick>` — If someone sends 18+ content it will be deleted and action will be taken.
- `.remnsfw` — Remove Chat from nsfw filtering.

**profanityfilter**

- `.addprofanity` — If someone sends bad word in a chat, Then bot will delete that message.
- `.remprofanity` — From chat from Profanity list.

**tag**

- `.tagall` — Tag Top 100 Members of chat.
- `.tagadmins` — Tag Admins of that chat.
- `.tagowner` — Tag Owner of that chat
- `.tagbots` — Tag Bots of that chat.
- `.tagrec` — Tag recently Active Members.
- `.tagon` — Tag online Members(work only if privacy off).
- `.tagoff` — Tag Offline Members(work only if privacy off).

**polls**

- `.poll <question> ; <option> ; <option>` — Get the Anonymous Poll with Given Options
- `.poll <question> ; <option> ; <option> | <type>` — Get the poll specified with desired type! type should be any of  `public`,  `multiple` or `quiz`
- `.poll <question> ; <option> ; <option> | quiz_<answerno>` — Get the quiz poll where answerno is the number of option which is correct

**globaltools**

- `.gban <reply user/ username>`
- `.ungban` — Ban/Unban Globally.
- `.gstat <reply to user/userid/username>` — Check if user is GBanned.
- `.listgban` : List all GBanned users.
- `.gmute` | `.ungmute` <reply user/ username> — Mute/UnMute Globally.
- `.gkick <reply/username>` `Globally Kick User`
- `.gcast <text/reply>` `Globally Send msg in all grps`
- `.gadmincast <text/reply>` `Globally broadcast in your admin chats`
- `.gucast <text/reply>` `Globally send msg in all pm users`
- `.gblacklist <chat id/username/nothing (for current chat)` — Add chat to blacklist and ignores global broadcast.
- `.ungblacklist` `Remove the chat from blacklist.`
- `.gpromote <reply to user> <channel/group/all> <rank>` — globally promote user where you are admin - Set whether To promote only in groups/channels/all. Eg- `gpromote group boss` ~ promotes user in all grps. `gpromote @username all sar` ~ promote the user in all group & channel
- `.gdemote` - `demote user globally`

**chats**

- `.delchat <optional- username/id>` — Delete the group this cmd is used in.
- `.getlink`
- `.getlink r` - `create link with admin approval`
- `.getlink r title_here` - `admin approval with link title`
- `.getlink 10` - `usage limit in new link` — Get link of group this cmd is used in.
- `.create (g|b|c) <group_name> ; <optional-username>` — Create group woth a specific name. g - megagroup/supergroup b - small group c - channel
- `.setgpic <reply to Photo><chat username>` — Set Profile photo of Group.
- `.delgpic <chat username -optional>` — Delete Profile photo of Group.
- `.unbanall` — Unban all Members of a group.
- `.rmusers` — Remove users specifically.

### 🛡️ Privacy, DM & profile

**pmpermit**

- `.a` or `.approve` — Approve someone to PM.
- `.da` or `.disapprove` — Disapprove someone to PM.
- `.block` — Block someone.
- `.unblock` | `.unblock all` — Unblock someone.
- `.nologpm` — Stop logging messages from the user.
- `.logpm` — Start logging messages from the user.
- `.startarchive` — Archive new PMs.
- `.stoparchive` — Don't archive new PMs.
- `.cleararchive` — Unarchive all chats.
- `.listapproved` — List all approved PMs.

**afk**

- `.afk <optional reason>` — AFK means away from keyboard, After this is activated, if someone tags or messages you, he/she would get an automated reply from the bot. (Note : Set a media file in afk messages by replying to any media with `.afk <reason>`).

**profile**

- `.setname <first name // last name>` — Change your profile name.
- `.setbio <bio>` — Change your profile bio.
- `.setpic <reply to pic>` — Change your profile pic.
- `.delpfp <n>(optional)` — Delete one profile pic, if no value given, else delete n number of pics.
- `.poto <username>` — Upload the photo of Chat/User if Available.

**autopic**

- `.autopic <search query>` — Change your profile pic every few minutes with images of the query.
- `.autopic` — Stop AutoPic.
- Use `.setdb SLEEP_TIME <seconds>` to change the delay.

**echo**

- `.addecho <reply to anyone>` — Start Auto Echo message of Replied user.
- `.remecho <reply to anyone>` — Turn It off
- `.listecho <reply to anyone>` — To Get list.

**fakeaction**

- `.ftyping <time/in secs>` — `Show Fake Typing in current chat.`
- `.faudio <time/in secs>` — `Show Fake Recording Action in current chat.`
- `.fvideo <time/in secs>` — `Show Fake video action in current chat.`
- `.fgame <time/in secs>` — `Show Fake Game Playing Action in current chat.`
- `.fsticker <time/in secs>` — `Show Fake sticker choosing Action in current chat.`
- `.flocation <time/in secs>` — `Show Fake location Action in current chat.`
- `.fcontact <time/in secs>` — `Show Fake contact choosing Action in current chat.`
- `.fround <time/in secs>` — `Show Fake video message action in current chat.`
- `.fphoto <time/in secs>` — `Show Fake sending photo in current chat.`
- `.fdocument <time/in secs>` — `Show Fake sending document in current chat.`

**schedulemsg**

- `.schedule <text/reply to msg> <time>` — In time u can use second as number, or like 1h or 1m eg. `.schedule Hello 100` It deliver msg after 100 sec. eg. `.schedule Hello 1h` It deliver msg after an hour.

**other**

- `.send <username/id> <reply/type>` — send message to User/Chat.
- `.fwdreply <reply to msg>` — Reply to someone's msg by forwarding it in private.
- `.save <reply message>` — Save that replied msg to ur saved messages box.
- `.fsave <reply message>` — Forward that replied msg to ur saved messages.

**extra**

- `.del <reply to message>` — Delete the replied message.
- `.edit <new message>` — Edit your last message or replied msg.
- `.copy <reply to message>` — Copy replied message / media.
- `.reply` — Reply the last sent msg to replied user.

### 📢 Channels & broadcast

**channelhacks**

- 🔹 `.shift <from channel> | <to channel>` — This will transfer all old post from channel A to channel B. (u can use username or id of channel too) example : `.shift @abc | @xyz` [note - this (' | ') sign is nessesary] 🔹 For auto-posting/forwarding all new message from any source channel to any destination channel. `.asource <channel username or id>` This add source channel to database `.dsource <channel username or id>` This remove source channels from database `.listsource <channel username or id>` Show list of source channels `.adest <channel username or id>` This add Ur channels to database `.ddest <channel username or id>` This Remove Ur channels from database `.listdest <channel username or id>` Show List of Ur channels 'you can set many channels in database' 'For activating auto-post use `.setdb AUTOPOST True` '

**broadcast**

- `.addch <id/reply to list/none>` — Add chat to database. Adds current chat if no id specified.
- `.remch <all/id/none>` — Removes the specified chat (current chat if none specified), or all chats.
- `.broadcast <reply to msg>` — Send the replied message to all chats in database.
- `.forward <reply to msg>` — Forward the message to all chats in database.
- `.listchannels` — To get list of all added chats.

### 📥 Download & upload

**youtube**

- `.yta <(youtube/any) link>` — Download audio from the link.
- `.ytv <(youtube/any) link>` — Download video  from the link.
- `.ytsa <(youtube) search query>` — Search and download audio from youtube.
- `.ytsv <(youtube) search query>` — Search and download video from youtube.
- `.ytcookies <reply to cookies.txt>` — Fix "Sign in to confirm you're not a bot". Export YouTube cookies (cookies.txt, Netscape format) from a browser logged in to a spare Google account, send the file, reply to it with this command. `.ytcookies` = status · `.ytcookies del` = remove.

**downloadupload**

- `.ul <path/to/file>` — Upload files on telegram. Use following arguments before or after filename as per requirement: `--stream` to upload as stream. `--delete` to delete file after uploading. `--no-thumb` to upload without thumbnail.
- `.dl <filename(optional)>` — Reply to file to download.
- `.download <DDL> (| filename)` — Download using DDL. Will autogenerate filename if not given.

**gdrive**

- `.gdul <reply/file name>` — Reply to file to upload on Google Drive. Add file name to upload on Google Drive.
- `.gdown <file id/link> | <filename>` — Download from Gdrive link or file id.
- `.gdsearch <file name>` — Search file name on Google Drive and get link.
- `.gdlist` — List all GDrive files.
- `.gdfolder` — Link to your Google Drive Folder. If added then all files will be uploaded in this folder.

**webupload**

- `.webupload` — Upload files on another server.

**fileshare**

- `.store <reply_to_message>` — Store the replied message/media and generate a shareable link to that file, to be accessed via your assistant bot!
- `.delstored <link of stored file>` — Delete stored file.
- `.liststored` — Get all stored messages.
- Go Inline with your assistant bot with `filestore` to see stored files in inline.

**ziptools**

- `.zip <reply to file>` — zip the replied file To set password on zip: `.zip <password>` reply to file
- `.unzip <reply to zip file>` — unzip the replied file.
- `.azip <reply to file>` — add file to batch for batch upload zip
- `.dozip` — upload batch zip the files u added from `.azip` To set Password: `.dozip <password>`

### 🖼️ Media, stickers & images

**stickertools**

- `.destroy <reply to animated sticker>` — To destroy the sticker.
- `.tiny <reply to media>` — To create Tiny stickers.
- `.kang <reply to image/sticker>` — Kang the sticker (add to your pack).
- `.packkang <pack name>` — Kang the Complete sticker set (with custom name).
- `.round <reply to any media>` — To extract round sticker.

**converter**

- `.convert <gif/img/sticker/webm>` — Reply to media to convert it into gif / image / webm / normal sticker.
- `.doc <filename.ext>` — Reply to a text msg to save it in a file.
- `.open` — Reply to a file to reveal it's text.
- `.rename <file name with extension>` — Rename the file
- `.thumbnail <reply to image/thumbnail file>` — Upload Your file with your custom thumbnail.

**imagetools**

- `.border <reply to photo/sticker>` — To create border around that media.. Ex - `.border 12,22,23` - `.border 12,22,23 ; width (in number)`
- `.grey <reply to any media>` — To make it black nd white.
- `.color <reply to any Black nd White media>` — To make it Colorfull.
- `.toon <reply to any media>` — To make it toon.
- `.danger <reply to any media>` — To make it look Danger.
- `.negative <reply to any media>` — To make negative image.
- `.blur <reply to any media>` — To make it blurry.
- `.quad <reply to any media>` — create a Vortex.
- `.mirror <reply to any media>` — To create mirror pic.
- `.flip <reply to any media>` — To make it flip.
- `.sketch <reply to any media>` — To draw its sketch.
- `.blue <reply to any media>` — just cool.
- `.csample <color name /color code>` — example : `.csample red` `.csample #ffffff`
- `.pixelator <reply image>` — Create a Pixelated Image..

**logo**

- `.logo <text>` — Generate a logo of the given Text Or Reply To image , to write ur text on it. Or Reply To Font File, To write with that font.

**glitch**

- `.glitch <reply to media>` — gives a glitchy gif.

**giftools**

- `.invertgif` — Make Gif Inverted(negative).
- `.bwgif` — Make Gif black and white
- `.rvgif` — Reverse a gif
- `.vtog` — Reply To Video , It will Create Gif Video to Gif
- `.gif <query>` — Send video regarding to query.

**videotools**

- `.sample <duration in seconds>` — Creates Short sample of video..
- `.vshots <number of shots>` — Creates screenshot of video..
- `.vtrim <start time> - <end time> in seconds` — Crop a Lengthy video..

**audiotools**

- `.makevoice <reply to audio>` — creates a voice note from Audio. `.atrim <from time> - <to time>` trim audio as per given time. time must be in seconds. `.atrim 50-70` `.extractaudio <reply to media>` To extract the audio from it.

**compressor**

- `.compress <reply to video>` — Compress the video (default CRF 27).
- `.compress <crf> <reply to video>` — Lower CRF = better quality, bigger file (e.g. `.compress 23`).
- `.compress <crf> stream` — Upload the result as a streamable video.

**mediatools**

- `.mediainfo <reply to media>` — To get info about it.
- `.rotate <degree/angle> <reply to media>` — Rotate any video/photo/media.. Note : for video it should be angle of 90's

**resize**

- `.size <reply to media>` — To get size of it.
- `.resize <number> <number>` — To resize image on x, y axis. eg. `.resize 690 960`

**qrcode**

- `.qrcode <text/reply to text>` — `Makes qrcode of text`
- `.addqr <reply image> <text>` — `Makes qr of text and add it to image.`
- `.qrdecode <reply to qrcode>` — `It decodes the qrcode.`

**pdftools**

- `.pdf <page num> <reply to pdf file>` — Extract & send page as an Image.(note-: For extracting all pages, just use .pdf) to upload selected range `.pdf 1-7`
- `.pdtext <page num> <reply to pdf file>` — Extract Text From the Pdf.(note-: For Extraction all text just use .pdtext) to extract selected pages `.pdf 1-7`
- `.pdscan <reply to image>` — It scan, crop & send image(s) as pdf.
- `.pdsave <reply to image/pdf>` — It scan, crop & save file to merge. you can merge many pages in a single pdf.
- `.pdsend ` — Merge & send the pdf, collected from .pdsave.

**beautify**

- `.carbon <text/reply to msg/reply to document>` — Carbonise the text with default settings.
- `.rcarbon <text/reply to msg/reply to document>` — Carbonise the text, with random bg colours.
- `.ccarbon <color ><text/reply to msg/reply to document>` — Carbonise the text, with custom bg colours.
- `.rayso <opt-theme> <text>/<reply to message>` — `.rayso list` - `Get list of themes.`

**writer**

- `.write <text or reply to text>` — It will write on a paper.
- `.image <text or reply to html or any doc file>` — Write a image from html or any text.

**fontgen**

- `.font <font name> : <text>` — Generate different fonts for the text.
- `.font` — To get list of fonts

**unsplash**

- .unsplash <search query> ; <no of pics> — Unsplash Image Search.

### 🔎 Search & info

**search**

- `.saavn <search query>` — Download songs from Saavn.
- `.google <query>` — For doing google search.
- `.github <username>` — Get full information of the users github profile.
- `.img <query>` — `.img <query> ; <no of results>` For doing Images search.
- `.reverse` — Reply an Image or sticker to find its sauce.

**words**

- `.meaning <word>` — Get the meaning of the word.
- `.synonym <word>` — Get all synonyms.
- `.antonym <word>` — Get all antonyms.
- `.ud <word>` — Fetch word defenition from urbandictionary.

**weather**

- **Get Weather Data using OpenWeatherMap API** — ❍  Commands Available -
- `.weather` <city name> — Shows the Weather of Cities
- `.air` <city name> — Shows the Air Condition of Cities

**misc**

- `.eod` — `Get Event of the Today`
- `.pntrst <link/id>` — Download and send pinterest pins
- `.gadget <search query>` — Gadget Search from Telegram.
- `.randomuser` — Generate details about a random user.
- `.ascii <reply image>` — Convert replied image into html.

**utilities**

- `.kickme` : Leaves the group.
- `.date` : Show Calender.
- `.listreserved` — List all usernames (channels/groups) you own.
- `.stats` : See your profile stats.
- `.paste` - `Include long text / Reply to text file.`
- `.info <username/userid/chatid>` — Reply to someone's msg.
- `.invite <username/userid>` — Add user to the chat.
- `.rmbg <reply to pic>` — Remove background from that picture.
- `.telegraph <reply to media/text>` — Upload media/text to telegraph.
- `.json <reply to msg>` — Get the json encoding of the message.
- `.suggest <reply to message> or <poll title>` — Create a Yes/No poll for the replied suggestion.
- `.ipinfo <ipAddress>` : Get info about that IP address.
- `.cpy <reply to message>` — Copy the replied message, with formatting. Expires in 24hrs.
- `.pst` — Paste the copied message, with formatting.
- `.thumb <reply file>` : Download the thumbnail of the replied file.
- `.getmsg <message link>` — Get messages from chats with forward/copy restrictions.

**tools**

- `.circle` — Reply to a audio song or gif to get video note.
- `.ls` — Get all the Files inside a Directory.
- `.bots` — Shows the number of bots in the current chat with their perma-link.
- `.hl <a link> <text-optional>` — Embeds the link with a whitespace as message.
- `.id` — Reply a Sticker to Get Its Id Reply a User to Get His Id Without Replying You Will Get the Chat's Id
- `.sg <reply to a user><username/id>` — Get His Name History of the replied user.
- `.tr <dest lang code> <(reply to) a message>` — Get translated message.
- `.webshot <url>` — Get a screenshot of the webpage.
- `.shorturl <url> <id-optional>` — shorten any url...

**calculator**

- `.calc` - Inline Calculator

**specialtools**

- `.wspr <@username/id> <message>`
- `.wspr <message>` (reply to someone) — Secret message in any chat — only that person (and you) can open it. Max 200 characters. `.wspr @username` alone shows their profile card.
- `.q <color-optional>`
- `.q @username`
- `.q r <color-optional>`
- `.q count` : `multiple quotes` — Create quotes..
- `.sticker <query>` — Search Stickers as Per ur Wish..
- `.getaudio <reply to an audio>` — Download Audio To put in ur Desired Video/Gif.
- `.addaudio <reply to Video/gif>` — It will put the above audio to the replied video/gif.
- `.dob <date of birth>` — Put in dd/mm/yy Format only(eg .dob 01/01/1999).
- `.wall <query>` — Search Hd Wallpaper as Per ur Wish..

**twitter**

- `.tw <tweet text>` — Tweet the text.
- `.twdetail <tweet id/link>` — Get tweet details with reply/quote/comment count.
- `.twuser <username>` — Get user details of the Twitter account.
- `.twl <tweet link>` — Upload the tweet media to telegram.

**stories**

- `.setstory <reply media>` — Set replied media as your story.
- `.storydl <username/reply user/story link>` — Download and upload user stories or specific story from link!

### ⚙️ Bot, settings & developer

**bot**

- `.botpic` (reply to a photo, optional) — Change the assistant bot's profile photo.
- `.alive` | `.alive inline` — Check if your bot is working.
- `.ping` — Check the bot's response time.
- `.update` — See changelogs if any update is available.
- `.cmds` — View all plugin names.
- `.restart` — To restart your bot.
- `.logs (sys)` — Get the full terminal logs.
- `.logs carbon` — Get the carbonized sys logs.
- `.logs heroku` — Get the latest 100 lines of heroku logs.
- `.shutdown` — Turn off your bot.

**core**

- `.install <reply to plugin>` — To install the plugin, `.install f` To force Install.
- `.uninstall <plugin name>` — To unload and remove the plugin.
- `.load <plugin name>` — To load unloaded unofficial plugin.
- `.unload <plugin name>` — To unload unofficial plugin.
- `.help <plugin name>` — Shows you a help menu (like this) for every plugin.
- `.getaddons <raw link to code>` — Load Plugins from the given raw link.

**database**

- **DataBase Commands, do not use if you don't know what it is.**
- `.setdb key | value` — Set Value in Database. e.g : `.setdb hi there` `.setdb hi there | OWNER Assistant here` `.setdb --extend variable value` or `.setdb -e variable value` to add the value to the exiting values in db.
- `.deldb key` — Delete Key from DB.
- `.rendb old keyname | new keyname` — Update Key Name

**variables**

- `.get var <variable name>` — Get value of the given variable name.
- `.get type <variable name>` — Get variable type.
- `.get db <key>` — Get db value of the given key.
- `.get keys` — Get all redis keys.

**sudo**

- `.addsudo` — Add Sudo Users by replying to user or using <space> separated userid(s)
- `.delsudo` — Remove Sudo Users by replying to user or using <space> separated userid(s)
- `.listsudo` — List all sudo users.

**usage**

- `.usage` — Get overall usage.
- `.usage heroku` — Get heroku stats.
- `.usage db` — Get database storage usage.

**asstcmd**

- `.addcmd <new cmd> <reply>` — It will set new cmd for your assistant bot with that reply message.
- `.remcmd <cmd name>` — It will remove your cmd.
- `.listcmd` — To Get list of all your custom cmd.

**button**

- `.button <text with button format>` — Create a message with buttons. You can reply to a picture too. Format:- `.button Hey There! 😎 [Google | https://google.com][YouTube | https://youtube.com | same] [Instagram | https://instagram.com]`

**devtools**

- `.bash <cmds>`
- `.bash -c <cmds>` Carbon image as command output. — Run linux commands on telegram.
- `.eval <code>` — Evaluate python commands on telegram. Shortcuts: client = bot = event.client e = event p = print reply = await event.get_reply_message() chat = event.chat_id
- `.cpp <code>` — Run c++ code from Telegram.
- `.sysinfo` — Shows System Info.

**vctools**

- `.startvc` — Start Group Call in a group.
- `.stopvc` — Stop Group Call in a group.
- `.vctitle <title>` — Change the title Group call.
- `.vcinvite` — Invite all members of group in Group Call. (You must be joined)

### 🧩 More

**pemoji**

- `.pemoji` (reply to a message that has premium emojis) — Save those premium emojis. After this, the bot's messages (alive, ping, help, ...) use them automatically.
- `.pemoji pack <t.me/addemoji/... link or pack name>` — Save a whole premium emoji pack at once.
- `.pemoji` — Status + list of saved emojis.
- `.pemoji del <emoji>`  /  `.pemoji clear` — Remove one / all saved emojis.
- `.pemoji on`  /  `.pemoji off` — Turn the automatic premium emojis on or off.
- `.pemoji bot on`  /  `.pemoji bot off` — Also use them in the assistant bot's messages (works only if Telegram allows it for your bot - see note).
- `.pemoji test` — Send a sample message to see how it looks. Note: premium emojis need Telegram Premium on your account. Without Premium, normal emojis are shown (nothing breaks).

## 9. Every command (extra addons)

### 💖 Love

**love**

- `.propose <name>` (or reply to someone) — A long, flirty proposal story 💍 — walk-up, ring, a dot-by-dot rose, a beating heart, pick-up lines and the big question.
- `.love <name>` — A heart drawn dot by dot that comes alive and beats for them ❤️
- `.rose <name>` — A rose that blooms dot by dot 🌹
- `.hearts` — It's raining hearts 💕
- `.lovecalc <name1> <name2>` — The (totally scientific) love meter 💘

### 🎉 Fun & pranks

**fun**

- `.joke` — To get joke.
- `.url <long url>` — To get a shorten link of long link.
- `.phlogo <first_name> <last_name>` — Make a phub based logo.
- `.decide` — Decide something.
- `.xo` — Opens tic tac game only where using inline mode is allowed.
- `.wordi` — Opens word game only where using inline mode is allowed.
- `.gps <name of place>` — Shows the desired place in the map.

**hack**

- `.hack` — Do a Prank With Replied user.

**animations**

- Animation Plugin
- `.kill`
- `.fp`

**typing**

- `.type <msg>` — Edits the Message and shows like someone is typing.

**truthdare**

- `.truth` — `Get Truth Task.`
- `.dare` — `Get Dare Task.`

**random**

- `Get some Random Content.`
- `.random dog`
- `.random duck`
- `.random cat`
- `.random fox`
- `.random quote`
- `.random word`
- `.random quotable`
- `.random celebrity`

**inlinefun**

- `.uta <search query>` — Inline song search and downloader.
- `.gglax <query>` — Create google search sticker with text.
- `.stic <emoji>` — Get random stickers from emoji.
- `.frog <text>` — make text stickers.
- `.tweet <text>` — make twitter posts.
- `.quot <text>` — write quote on animated sticker.

**waifu**

- `.waifu <text>` — paste text on random stickers.

**memify**

- `.mmf <upper text> ; <lower text> <reply to media>` — To create memes as sticker, for trying different fonts use (.mmf <text>_1)(u can use 1 to 10).
- `.mms <upper text> ; <lower text> <reply to media>` — To create memes as pic, for trying different fonts use (.mms <text>_1)(u can use 1 to 10).

**sticklet**

- `.sticklet <text>` — `create random sticker with text.`

**figlet**

- `.figlet <text>` — Make a text a figlet.

**fontsnew**

- `.weeb <text>` — turns text to 山乇乇乃 font
- `.tantext <text>` — turns text to ᎿᎯᏁᎿᏋﾒᎿ font
- `.linetext <text>` — turns text to 𝕃𝕀ℕ𝔼𝕋𝔼𝕏𝕋
- `.boxtext <text>` — turns text to 🄱🄾🅇🅃🄴🅇🅃
- `.bubbletext <text>` — turns text to ⒷⓊⒷⒷⓁⒺⓉⒺⓍⓉ
- `.cursive <text>` — turns text to 𝓬𝓾𝓻𝓼𝓲𝓿𝓮 font
- `.greekify <text>` — turns text to ϑгεεκιғψ font
- `.sorcify <text>` — turns text to ֆօʀƈɛʀɛʀ font
- `.fraktify <text>` — turns text to 𝖋𝖗𝖆𝖐𝖙𝖚𝖗𝖊 font
- `.rusify <text>` — turns text to яц$їfч font

**quote**

- `.qbot <reply>` — Make sticker quote without QuotlyBot

**quotefancy**

- `.qfancy` — Gets random quotes from QuoteFancy.com.

**howto**

- `.htg <text>` — How To Google. Some peoples don't know how to google so help them 🙃🙂.
- `.htd <text>` — How to duck duck go...

**activitygen**

- `.bored` — Get some activity to do when you get bored

**brainfuck**

- `.bf` — Text to Brainfuck String Generator with text or reply.
- `.rbf` — Brainfuck Interpreter with string or reply.

**morsecode**

- `.mencode <text>` — Encode the given text to Morse Code.
- `.mdecode <text>` — Decode the given text from Morse Code.

**encodedecode**

- .encode <text/reply to message> — encode the text
- .decode <text/reply to message> — decode the text

**clone**

- `.clone <reply/username>` — clone the identity of user.
- `.revert` — Revert to your original identity

### ⚠️ Spam (use carefully — can get your account limited)

**spam**

- `.spam <no of msgs> <your msg>` — `.spam <no of msgs> <reply message>` spams chat, the current limit for this is from 1 to 99.
- `.bigspam <no of msgs> <your msg>` — `.bigspam <no of msgs> <reply message>` Spams chat, the current limit is above 100.
- `.delayspam <delay time> <count> <msg>` — Spam chat with delays..
- `.tspam <text>` — Spam Chat with One-One Character..

**stickerspam**

- `.sspam <reply to sticker> <optional- time gap>` — it spam the whole stickers in that pack.

### 🎵 Music & voice

**song**

- `.lyrics <search query>` — get lyrics of song.
- `.song <search query>` — Search the song on YouTube and send its audio.

**findsong**

- `.findsong <reply to song>` — Identify the song name

**whichsong**

- `.whichsong` — Reply to a song file, to recognise the song.

**speechtool**

- `.tts` `LanguageCode <reply to a message>`
- `.tts` `LangaugeCode | text to speak`
- `.stt` `<reply to audio file>` — `Convert Speech to Text...` `Note - Sometimes Not 100% Accurate`

### 🔎 Info & search

**wikipedia**

- `.wiki <search query>`` — Wikipedia search from telegram.

**imdb**

- Search movie details from IMDB
- `.imdb <keyword>`

**anime**

- `.character <character name>` — Fetch anime character details.

**animedb**

- Search animes and manga from anilist.co using @animedb_bot
- `.manga <keyword>` — To get manga info

**animechan**

- Fetch Random anime quotes — Command : `.aniquote`

**pokedex**

- `.pokemon <query>` — Send details of Pokemon.
- `.pokecard <query>` — Send Card of Pokemon.

**astronomy**

- `.apod`` — Get Astronomy Picture of Day by NASA

**covid**

- `.covid country name` — Gets the Covid-19 Status of a given Country.

**flaticon**

- `.icon <query>` — Icon search from flaticon.com and uploading as sticker.

**searchmsgs**

- To Search Messages in chat easily :) — >> .search (some_text) >> .search -r (some_text) : 10 »» To search in Reverse order.
- `.search hello`
- `.search -r Heroku : 10`

**totalmsgs**

- `.totalmsgs` — Returns your total msg count in current chat
- `.totalmsgs [username]/<reply>` — Returns total msg count of user in current chat

### 🧰 Tools

**ocr**

- `.ocr <language code><reply to a photo>` — text recognition service.

**fastly**

- Fasly Bot Cheat.
- `.fastly` - On/Off command.
- Also Required : `OCR_API`. Add it using the command `.setdb OCR_API api_key`
- To get the API visit 'https://ocr.space/ocrapi' — The bot will try to auto reply first to the messages by @FastlyWriteBot
- Add User id of fastly clone to `FASTLY_CLONES` to allow this plugin work with them.

**spellcheck**

- .spcheck <text/reply to message> — check spelling of the text/sentence

**autocorrect**

- `.autocorrect` — To on/off Autocorrect Feature (English messages only). Messages ending with `..` are not corrected.

**ncode**

- `.ncode <file>` — Use - Paste the contents of file and send as pic.

**autoprofile**

- `.autoname` — `Starts AUTONAME`.
- `.stopname` — `Stops AUTONAME.`
- `.autobio` — `Starts AUTOBIO.`
- `.stopbio` — `Stops AUTOBIO.`

**wreplace**

- `.wreplace <count> <old word>;<new word>` — Note : Don't use brackets Ex. : `.wreplace 10 Hi;Hello` Use: It replaces a perticular word by new word (only in your msgs.) In many msgs at a time

**limited**

- `.limited` — Check you are limited or not !

**servertest**

- `.test` — Test Your Server Speed.

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
- Assistant bot: `@OWN_CLAT_bot` (token in the VPS `.env`, not in the repo).

### Layout

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
| `resources/extras/owner_assistant_*.jpg` | Banners (1,2,3, alive, help, start, deploy, pm), avatar, thumb. Re-create with `dev/make_banners.py` |
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
- Premium emoji: `pe.install(client)` wraps `client._parse_message_text`, so every
  send/edit gets `MessageEntityCustomEmoji` for emojis saved in DB `PREMIUM_EMOJI`
  ({emoji: document_id}). Userbot: only if `me.premium` and not `PREMIUM_EMOJI_OFF`.
  Assistant bot: only if `PREMIUM_EMOJI_BOT` (Telegram may refuse custom emoji for
  bots without a Fragment username / Premium owner — unverified). Never hard-code
  emoji IDs we haven't seen; the owner saves them with `.pemoji` / `.pemoji pack`.
- Buttons use colours (`style="primary|success|danger"`) in help/start/settings.

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
premium emoji system (`.pemoji`), coloured buttons.

### Roadmap the owner agreed to (not started)

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

### Never do

- Don't build tools to access other people's accounts, scrape private data,
  mass-spam, or evade Telegram limits. Prank/fun commands are fine; warn about
  spam bans when relevant.
- Don't store the owner's password/2FA anywhere.
