# 🤖 Apna khud ka OWNER Assistant bot (5 minute)

Ye guide tumhare **apne** bot ke liye hai. Jo bot banega wo **tumhare account** pe
chalega, **tumhare apne host** pe. Tumhara session sirf tumhare paas rahega —
kisi aur ke (owner ke bhi) server pe nahi. Ye poori tarah individual aur private hai.

---

## ⚠️ Pehle ye padho (bahut zaroori)

- **Apni `SESSION` string kisi ko mat do** — kisi dost ko bhi nahi. Jiske paas
  tumhari SESSION hai, wo tumhara poora Telegram account chala sakta hai.
- **Session banane ke liye kisi random "session generator bot" ya website ka
  use mat karo.** 90% aise bots tumhari session chura lete hain. Sirf neeche diya
  **official tarika** use karo (jo tumhare apne control mein chalta hai).
- Koi tumhe bole "apni session mujhe bhej, main setup kar deta hoon" → **mana kar do.**

---

## Step 1 — SESSION string banao (safe tarika)

Ye ek baar ka kaam hai. Phone se bhi ho jata hai.

1. https://my.telegram.org kholo → login → **API development tools** → `api_id` aur
   `api_hash` copy kar lo.
2. Ek **free online Python** kholo jahan sirf tumhara control ho — jaise
   [replit.com](https://replit.com) (free account bana lo).
3. Ek naya Python project banao aur terminal/shell mein ye chalao:
   ```bash
   pip install telethon
   ```
4. Phir ye chalao aur poochi hui cheezein bharo (api_id, api_hash, phone, OTP):
   ```bash
   python3 -c "from telethon.sync import TelegramClient; from telethon.sessions import StringSession; api=int(input('api_id: ')); h=input('api_hash: '); c=TelegramClient(StringSession(), api, h); c.start(); print('\nYOUR SESSION (keep it secret):\n'+c.session.save())"
   ```
5. Jo lambi string aaye (`1A...` se shuru) — wo **copy kar lo**. Ye tumhari SESSION hai.
   Kisi ko mat bhejo.

> Replit ka project public mat rakhna (secrets dikh sakte hain). Kaam ho jaye to
> us project ko delete kar sakte ho.

---

## Step 2 — Bot deploy karo (ek button)

Sabse aasaan free host **Koyeb** hai (card nahi maangta).

1. [Koyeb](https://app.koyeb.com) pe free account banao.
2. **Create App → GitHub → ye repo** chuno: `Ownermood/OWNER-Assistant`
   (ya pehle apne GitHub pe **Fork** kar lo, phir apna fork chuno).
3. Build type: **Dockerfile** (apne aap aa jayega).
4. **Environment variables** mein daalo:
   | Name | Value |
   |---|---|
   | `SESSION` | Step 1 wali tumhari string |
   | `REDIS_URI` | neeche Step 3 wala (taaki restart pe data na mite) |
5. **Deploy** dabao. 2-3 min mein bot zinda. Telegram pe apne account se `.alive` likho.

**Render / Railway / Heroku** bhi chalega — wahan bhi same 2 cheezein (`SESSION` +
`REDIS_URI`) daalni hain, Docker se build hoga.

---

## Step 3 — Free database (taaki restart pe sab na mite)

Cloud host restart pe local file mita deta hai, isliye ek free DB do:

- **Redis:** https://upstash.com (free) → ek Redis banao → `REDIS_URI` copy karo
  (`redis://default:password@host:port`) → Step 2 mein daal do.
- **Ya MongoDB:** https://mongodb.com/atlas (free) → `MONGO_URI` daal do.

Bas. Ab bot tumhara, account tumhara, session tumhara — kisi aur ke paas kuch nahi. 🎉

---

## Help

- Setup ka bada guide: [SETUP.md](./SETUP.md)
- Commands kaise use karein: [OWNER_GUIDE.md](./OWNER_GUIDE.md)
- Kuch toote to `.logs` se error dekho.

**Yaad rakho:** `.spam` jaisi command kam use karo (account ban ho sakta hai), aur
apni SESSION / 2FA password kabhi kisi ko mat do.
