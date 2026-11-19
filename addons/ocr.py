#
# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
#


"""
✘ Commands Available -

• `{i}ocr <language code><reply to a photo>`
    text recognition service.
"""


import os

from . import *


async def ocr_space(path, api_key, language=None):
    """Send an image file straight to OCR.space and return its text.

    (Telegraph no longer hosts uploads, so the old "upload then pass URL" flow broke.)
    """
    import aiohttp

    form = aiohttp.FormData()
    form.add_field("apikey", api_key)
    if language:
        form.add_field("language", language)
    with open(path, "rb") as f:
        form.add_field("file", f.read(), filename=os.path.basename(path))
    async with aiohttp.ClientSession() as ses:
        async with ses.post("https://api.ocr.space/parse/image", data=form) as resp:
            data = await resp.json(content_type=None)
    if data.get("IsErroredOnProcessing"):
        raise ValueError(data.get("ErrorMessage") or "OCR failed")
    return data["ParsedResults"][0]["ParsedText"]

TE = f"API not found, Please get it from ocr.space and set\n\ncommand `{HNDLR}setdb OCR_API your-api-key`"


@ultroid_cmd(pattern="ocr( (.*)|$)")
async def ocrify(ult):
    if not ult.is_reply:
        return await ult.eor("`Reply to Photo...`")
    msg = await ult.eor("`Processing..`")
    OAPI = udB.get_key("OCR_API")
    if not OAPI:
        return await msg.edit(TE)
    pat = ult.pattern_match.group(1).strip()
    repm = await ult.get_reply_message()
    if not repm.photo:
        return await msg.edit("`Not a Photo..`")
    dl = await repm.download_media()
    try:
        trt = await ocr_space(dl, OAPI, pat or None)
    except Exception as er:
        return await msg.edit(f"**OCR Error:** `{er}`")
    finally:
        os.remove(dl)
    await msg.edit(f"**🎉 OCR PORTAL\n\nRESULTS ~ ** `{trt or 'No text found.'}`")
