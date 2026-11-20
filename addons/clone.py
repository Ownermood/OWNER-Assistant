# Ported From DarkCobra , Originally By Uniborg
# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📖 **Commands**

• `{i}clone` (reply, or add @username)
    Copy someone's name, bio and photo onto your account (for fun).

• `{i}revert`
    Go back to your own name, bio and photo.
"""
import os

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPhoto, MessageEntityMentionName

from . import *

def _normalise_avatar(path):
    """Return (path, is_video) with a file Telegram accepts for a profile picture.

    The downloaded avatar can be a JPEG, PNG/WebP, or an MP4 (animated avatar),
    and its file name extension isn't reliable, so check the real bytes.
    """
    with open(path, "rb") as f:
        head = f.read(12)
    if head[4:8] == b"ftyp":
        if not path.lower().endswith(".mp4"):
            new = os.path.splitext(path)[0] + ".mp4"
            os.replace(path, new)
            path = new
        return path, True
    if head.startswith(b"\xff\xd8") and path.lower().endswith((".jpg", ".jpeg")):
        return path, False
    from PIL import Image

    new = os.path.splitext(path)[0] + "_dp.jpg"
    Image.open(path).convert("RGB").save(new, "JPEG", quality=95)
    os.remove(path)
    return new, False


BACKUP_KEY = "CLONE_BACKUP"


async def _target_user(event):
    """Return the user to clone (reply / mention / username / id / private chat)."""
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        if msg.fwd_from and msg.fwd_from.from_id:
            return await event.client.get_entity(msg.fwd_from.from_id)
        return await msg.get_sender()
    arg = event.pattern_match.group(1).strip()
    for ent in event.message.entities or []:
        if isinstance(ent, MessageEntityMentionName):
            return await event.client.get_entity(ent.user_id)
    if arg:
        return await event.client.get_entity(int(arg) if arg.lstrip("-").isdigit() else arg)
    if event.is_private:
        return await event.client.get_entity(event.chat_id)
    return None


@ultroid_cmd(pattern="clone( (.*)|$)", fullsudo=True)
async def _(event):
    eve = await event.eor("Processing...")
    try:
        user = await _target_user(event)
        if not user or getattr(user, "broadcast", False) or not hasattr(user, "first_name"):
            return await eve.edit("Reply to a user or give a username to clone.")
        full = await event.client(GetFullUserRequest(user.id))
    except Exception as er:
        return await eve.edit(f"`{er}`")

    me = await event.client(GetFullUserRequest("me"))
    # Save the real identity only once, so cloning twice never loses it.
    if not udB.get_key(BACKUP_KEY):
        udB.set_key(
            BACKUP_KEY,
            {
                "first_name": me.users[0].first_name or OWNER_NAME,
                "last_name": me.users[0].last_name or "",
                "about": me.full_user.about or "",
                "photos": [],
            },
        )
    backup = udB.get_key(BACKUP_KEY)

    target = full.users[0]
    first_name = (target.first_name or "Deleted").replace("⁠", "")[:64]
    last_name = (target.last_name or "").replace("⁠", "")[:64]
    about = (full.full_user.about or "")[:70]
    await event.client(
        UpdateProfileRequest(first_name=first_name, last_name=last_name, about=about)
    )
    note = ""
    try:
        profile_pic = await event.client.download_profile_photo(user.id)
    except Exception:
        profile_pic = None
    if profile_pic:
        try:
            profile_pic, is_video = _normalise_avatar(profile_pic)
            pfile = await event.client.upload_file(profile_pic)
            # Animated (video) profile pictures must be sent as `video=`.
            if is_video:
                req = UploadProfilePhotoRequest(video=pfile)
            else:
                req = UploadProfilePhotoRequest(file=pfile)
            res = await event.client(req)
            backup["photos"].append([res.photo.id, res.photo.access_hash])
            udB.set_key(BACKUP_KEY, backup)
        except Exception as er:
            note = f"\n\n`Name/bio cloned, but the profile picture could not be copied: {er}`"
        finally:
            if os.path.exists(profile_pic):
                os.remove(profile_pic)
    await eve.delete()
    await event.client.send_message(
        event.chat_id,
        f"I am {first_name} from now...{note}",
        reply_to=event.reply_to_msg_id,
    )


@ultroid_cmd(pattern="revert$")
async def _(event):
    backup = udB.get_key(BACKUP_KEY)
    if not backup:
        return await event.eor("You haven't cloned anyone, nothing to revert.")
    client = event.client
    # Delete only the photos that .clone added - never your own DP.
    if backup.get("photos"):
        photos = [
            InputPhoto(id=pid, access_hash=ah, file_reference=b"")
            for pid, ah in backup["photos"]
        ]
        try:
            await client(DeletePhotosRequest(photos))
        except Exception:
            # file_reference may be stale; match against current photos instead
            ids = {pid for pid, _ in backup["photos"]}
            current = await client.get_profile_photos("me", limit=20)
            own = [p for p in current if p.id in ids]
            if own:
                await client(DeletePhotosRequest(own))
    await client(
        UpdateProfileRequest(
            first_name=backup.get("first_name") or OWNER_NAME,
            last_name=backup.get("last_name", ""),
            about=backup.get("about", ""),
        )
    )
    udB.del_key(BACKUP_KEY)
    await event.eor("Successfully reverted to your account back!")
