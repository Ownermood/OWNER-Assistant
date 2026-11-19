# Ported From DarkCobra , Originally By Uniborg
# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

• `{i}clone <reply/username>`
    clone the identity of user.

• `{i}revert`
    Revert to your original identity
"""
import os

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPhoto, MessageEntityMentionName

from . import *

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
            return await eve.edit("`Reply to a user or give a username to clone.`")
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
    profile_pic = await event.client.download_profile_photo(user.id)
    if profile_pic:
        try:
            pfile = await event.client.upload_file(profile_pic)
            res = await event.client(UploadProfilePhotoRequest(file=pfile))
            backup["photos"].append([res.photo.id, res.photo.access_hash])
            udB.set_key(BACKUP_KEY, backup)
        finally:
            os.remove(profile_pic)
    await eve.delete()
    await event.client.send_message(
        event.chat_id, f"I am {first_name} from now...", reply_to=event.reply_to_msg_id
    )


@ultroid_cmd(pattern="revert$")
async def _(event):
    backup = udB.get_key(BACKUP_KEY)
    if not backup:
        return await event.eor("`You haven't cloned anyone, nothing to revert.`")
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
    await event.eor("Succesfully reverted to your account back !")
