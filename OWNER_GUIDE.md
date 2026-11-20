# 👑 OWNER Assistant — Owner Guide (examples ke saath)

Har command `.` se shuru hota hai aur aapke apne account se chalta hai.
"Reply karke" = jis message/insaan par command chalana hai uske message ko
reply karo, phir command bhejo.

> Poori list Telegram mein: `.help` · kisi plugin ki detail: `.help afk`

---

## ⚡ Roz ke kaam

| Command | Example | Kya hota hai |
|---|---|---|
| `.alive` | `.alive` | Bot chal raha hai ya nahi |
| `.ping` | `.ping` | Bot ki speed |
| `.help` | `.help` | Saare commands ka menu |
| `.afk` | `.afk CLAT ki padhai 📚` | Koi DM/tag kare to bot khud jawab de |
| `.id` | (reply karke) `.id` | User / chat ki ID |
| `.info` | DM mein `.info` | Poori profile jaankari |
| `.sg` / `.sgu` | `.sg 123456789` | Purane naam / usernames (SangMata) |

---

## 💬 DM (private chat)

Pehle ek baar: `.setdb PMSETTING True` — anjaan log DM karein to warning, zyada spam par auto-block.

| Command | Example |
|---|---|
| Approve / hatao | `.a` · `.da` (us DM mein) |
| Block / unblock | `.block` · `.unblock` |
| Approved list | `.listapproved` |
| Message bhejo | `.send @username Hello!` |
| Baad mein bhejo | `.schedule Happy Birthday 🎂 1h` |
| Secret whisper | `.wspr @username ye sirf tum padh sakte ho` |
| Saved Messages mein | (reply karke) `.save` |

---

## 🤖 AI

Key ek baar set karo (Saved Messages mein bhejo, phir message delete karo):
`.setdb GEMINI_API_KEY aapki-key` (free: aistudio.google.com)

| Command | Example |
|---|---|
| Gemini | `.gemini Article 21 simple bhasha mein samjhao` |
| Claude | `.antr CLAT ke liye 5 legal reasoning questions do` |
| ChatGPT | `.gpt Ek motivational quote do` |
| Kisi ko AI se auto-reply | (reply karke) `.addai` · band: `.remai` |

---

## 💖 Love & fun

| Command | Example | Kya hota hai |
|---|---|---|
| Proposal (~2 min) | `.propose Priya` | Ladka, ring, gulaab, dil, "Will you be mine?" |
| Dil | `.love Priya` | Dots se dil banta hai aur dhadakta hai |
| Gulaab | `.rose Priya` | Dot-by-dot gulaab khilta hai |
| Dil ki baarish | `.hearts` | 💕 |
| Love meter | `.lovecalc Rahul Priya` | Love % |
| Nakli hacking | `.hack` | Prank animation |
| Typing dikhao | `.ftyping 30` | 30 sec "typing..." |
| Joke / Truth / Dare | `.joke` · `.truth` · `.dare` | |
| Kisi ka roop | (reply karke) `.clone` · wapas `.revert` | Sirf doston ke saath mazaak |

> Ek waqt mein ek love animation chalti hai. Telegram rok laga de to bot
> khud ruk kar final frame dikha deta hai.

---


**Public / Private switch (saari animations, ek button):**

- OWNER Manager bot ke menu mein **✅ FUN MODE: ON / ⛔ OFF** likha dikhega + button. **Default ON hai.** ON = (a) dost bot ko DM karke **16 fun features** aur (b) group mein tumhare saath **137 commands** (figlet, song, imdb, sticker, weather...) chala sakte hain. Owner/VPS wali commands (.eval .bash .get .setdb .open .ls .ban .spam...) **kabhi nahi** khulti. OFF = sabka band, sirf tum.\n\nPurana text: **16 fun features** (animations, joke, dice, truth/dare, fake hack, matrix...) chala sakta hai (login/settings unhe kabhi nahi dikhega). OFF = sirf tum.
- Ya command se: `.funmode public` / `.funmode private` (phone se bhi chalega).
- Private karte hi sabka band, sirf tum. Switch hamesha tumhare haath mein.

**2nd id / partner ko sirf animations dena (baaki kuch nahi):**

```
.funuser add
```
(us insaan ke message pe reply karke, ya `.funuser add @username`)

| Kaam | Command |
|---|---|
| List dekho | `.funuser` |
| Hatao | `.funuser del <id>` |
| Sab hatao (sirf tum) | `.funuser clear` |

Wo log sirf `.propose .love .rose .hearts .lovecalc` chala payenge — aur koi command nahi, settings nahi, kuch nahi.

## 👮 Group (aap admin ho)

| Command | Example |
|---|---|
| Ban / kick / mute | (reply karke) `.ban` · `.kick` · `.mute` · `.tmute 1h` |
| Warn | (reply karke) `.warn spam mat karo` |
| Welcome message | `.setwelcome Welcome {mention} 🎉` |
| Auto-reply filter | (reply karke) `.addfilter hi` |
| Notes | (reply karke) `.addnote rules` → group mein `#rules` |
| Pin | (reply karke) `.pin` |
| Anti-flood | `.setflood 10` |

---

## 📥 Download & 🖼️ Media

| Command | Example |
|---|---|
| YouTube gaana | `.song Kesariya` |
| YouTube video/audio | `.ytv <link>` · `.yta <link>` |
| Sticker apne pack mein | (reply karke) `.kang` |
| Convert | (reply karke) `.convert sticker` |
| Photo se text | (reply karke) `.ocr` (key: `OCR_API`) |
| Code ki photo | `.carbon print("hello")` |
| Text se awaaz | `.tts en \| Good morning` |

---

## 🛠️ Bot settings

| Kaam | Command |
|---|---|
| Kuch bhi set karo | `.setdb KEY value` |
| Value dekho (secrets chhupe rehte hain) | `.get var KEY` |
| Assistant bot ki DP | `.botpic` (photo par reply karke apni photo) |
| Command prefix badlo | `.setdb HNDLR !` |
| Logs | `.logs` |
| Welcome tour (log group mein) | `.intro` |

### 🖼️ Pictures

Alive, help, /start, PM security, deploy aur log channel ki photos ab bot ke andar hi hain
(`resources/extras/owner_assistant_*.jpg`). Apni photo lagani ho:
`.setdb ALIVE_PIC <link>`, `.setdb STARTMEDIA <link>`, `.setdb PMPIC <link>`, `.setdb INLINE_PIC <link>`.
Photo hatani ho to value `False` rakho (jaise `.setdb PMPIC False`).

**Update (VPS par):**
```bash
cd ~/Ultroid && git pull && docker compose up -d --build
```

---

## 📱 OWNER Manager (control bot)

Chat hamesha saaf rehta hai: **ek hi menu message** jo button dabane par badalta hai.
Tumhare bheje messages (commands, code, password) khud delete ho jaate hain.

| Kaam | Kaise |
|---|---|
| Menu kholo | `/start` (upar status: 🟢 Running / ⚪ Stopped / 🔴 Not logged in) |
| Account connect | **🔐 Login** → phone → code **spaces ke saath** `1 2 3 4 5` → 2FA |
| Account hatao | **🚪 Logout** → Yes |
| Chalao / roko / restart | **▶️ Run** · **⏹ Stop** · **🔄 Restart** |
| Error dekhna | **📜 Logs** (poori file: **📄 Full log**) |
| API key jaisi setting | `/setvar GEMINI_API_KEY value`, phir **Restart** |

- Bot use karne ke liye pehle **@VillanCommunity** join karna padta hai. Manager bot ko us
  channel mein **admin** banao, tabhi wo check kar payega.
- Crash ho to manager khud restart karta hai aur message bhejta hai. Telegram se logout ho
  gaye to bhi message aayega — bas **Login** dabao.

---|---|
| Account connect karo | `/login` → phone → code **spaces ke saath** `1 2 3 4 5` → 2FA |
| Account hatao (logout) | `/logout` → "Yes" |
| Chal raha hai? | `/status` |
| Chalao / roko / restart | `/run` · `/stop` · `/restart` |
| Error dekhna | `/logs` |
| API key jaisi setting | `/setvar GEMINI_API_KEY value` (message khud delete hota hai), phir `/restart` |

Bot crash ho to manager khud restart karta hai aur tumhe message bhejta hai. Telegram se
logout ho gaye to bhi message aayega — bas **Login** dabao.

---

## 🛡️ Safety rules

- `SESSION`, `BOT_TOKEN`, API keys, VPS password **kabhi kisi ko mat do** — Claude ko bhi nahi.
- Galti se kahin share ho gaya → turant badlo (BotFather `/revoke`, AI Studio mein key delete, naya session).
- `.spam` / `.bigspam` kam use karo — account ban ho sakta hai. Limit check: `.limited`.
- Kisi anjaan bot/website se session mat banwao — sirf `bash sessiongen`.
- `.addsudo` sirf us insaan ko jis par poora bharosa ho (sudo = aapke bot ka control).

> Kuch toota? Error report (log group mein aata hai) Claude ko bhejo —
> "Last 5 commits" se pata chalta hai VPS par kaunsa version chal raha hai.
