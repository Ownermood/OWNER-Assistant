# Ported From DarkCobra Originally By UNIBORG
#
# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}test`
    Test Your Server Speed.

"""

from datetime import datetime

import asyncio

import speedtest

from . import *


@ultroid_cmd(pattern="test( (.*)|$)")
async def _(event):
    input_str = event.pattern_match.group(1).strip()
    as_document = None
    if input_str == "image":
        as_document = False
    elif input_str == "file":
        as_document = True
    xx = await event.eor("`Calculating your Server Speed. Please wait!`")
    start = datetime.now()
    def _run():
        st = speedtest.Speedtest(secure=True)
        st.get_best_server()
        st.download()
        st.upload()
        return st

    try:
        s = await asyncio.to_thread(_run)
    except Exception as er:
        return await xx.edit(f"`Speedtest failed: {er}`")
    end = datetime.now()
    ms = (end - start).seconds
    response = s.results.dict()
    download_speed = response.get("download")
    upload_speed = response.get("upload")
    ping_time = response.get("ping")
    client_infos = response.get("client")
    i_s_p = client_infos.get("isp")
    i_s_p_rating = client_infos.get("isprating")
    reply_msg_id = event.message.id
    if event.reply_to_msg_id:
        reply_msg_id = event.reply_to_msg_id
    try:
        response = await asyncio.to_thread(s.results.share)
        speedtest_image = response
        if as_document is None:
            await xx.edit(
                """`Ultroid Server Speed in {} sec`

`Download: {}`
`Upload: {}`
`Ping: {}`
`Internet Service Provider: {}`
`ISP Rating: {}`""".format(
                    ms,
                    f"{download_speed / 1_000_000:.2f} Mbps",
                    f"{upload_speed / 1_000_000:.2f} Mbps",
                    ping_time,
                    i_s_p,
                    i_s_p_rating,
                )
            )
        else:
            await event.client.send_file(
                event.chat_id,
                speedtest_image,
                caption="**SpeedTest** completed in {} seconds".format(ms),
                force_document=as_document,
                reply_to=reply_msg_id,
                allow_cache=False,
            )
            await event.delete()
    except Exception as exc:  # dc
        await xx.edit(
            """**SpeedTest** completed in {} seconds
Download: {}
Upload: {}
Ping: {}


__With the Following ERRORs__
{}""".format(
                ms,
                f"{download_speed / 1_000_000:.2f} Mbps",
                f"{upload_speed / 1_000_000:.2f} Mbps",
                ping_time,
                str(exc),
            )
        )
