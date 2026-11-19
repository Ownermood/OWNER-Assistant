# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}gemini <prompt>`
    Get response from Google Gemini.

• `{i}antr <prompt>`
    Get response from Anthropic Claude.

• `{i}gpt <prompt>`
    Get response from OpenAI GPT.

• `{i}deepseek <prompt>`
    Get response from DeepSeek AI.

  Reply to a message to use its text as the prompt.

Set API keys using:
    • GEMINI_API_KEY / ANTHROPIC_KEY / OPENAI_API_KEY / DEEPSEEK_API_KEY

Set custom models using:
    • OPENAI_MODEL: default: gpt-5-mini
    • ANTHROPIC_MODEL: default: claude-opus-5-5
    • GEMINI_MODEL: default: gemini-2.5-flash
    • DEEPSEEK_MODEL: default: deepseek-chat
"""

import time

from pyUltroid.fns.ai import API_KEYS, ai_response, get_model

from . import udB, ultroid_cmd

PROVIDERS = {
    "gemini": ("🤖 **Google Gemini**", "gemini"),
    "antr": ("🧠 **Anthropic Claude**", "antr"),
    "gpt": ("🌟 **OpenAI GPT**", "gpt"),
    "deepseek": ("🤖 **DeepSeek AI**", "deepseek"),
}

# Telegram allows ~4096 chars per message and rate-limits fast edits.
_MAX_LEN = 4000
_EDIT_GAP = 2.5


async def _run(event, provider):
    title, _ = PROVIDERS[provider]
    prompt = event.pattern_match.group(1).strip()
    if not prompt and event.is_reply:
        reply = await event.get_reply_message()
        prompt = (reply.message or "").strip()
    if not prompt:
        return await event.eor("❌ Please provide a prompt!")

    api_key = udB.get_key(API_KEYS[provider])
    if not api_key:
        return await event.eor(
            f"⚠️ Please set the API key using `setdb {API_KEYS[provider]} your_api_key`"
        )

    msg = await event.eor("🤔 Thinking...")
    model = get_model(provider, udB)
    header = (
        f"{title}\n"
        f"**Model:** `{model}`\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        f"**🔍 Prompt:**\n{prompt[:500]}\n\n"
        "**💡 Response:**\n"
    )

    response, last_edit = "", 0.0
    async for chunk in ai_response(provider, prompt, api_key, model=model, stream=True):
        response += chunk
        now = time.monotonic()
        if now - last_edit >= _EDIT_GAP:
            last_edit = now
            try:
                await msg.edit((header + response)[:_MAX_LEN])
            except Exception:
                pass

    text = header + (response or "_No response received._")
    try:
        await msg.edit(text[:_MAX_LEN])
    except Exception:
        pass
    # Send any overflow as extra messages instead of silently cutting it off.
    rest = text[_MAX_LEN:]
    while rest:
        await event.respond(rest[:_MAX_LEN])
        rest = rest[_MAX_LEN:]


@ultroid_cmd(pattern="gemini( (.*)|$)")
async def gemini_ai(event):
    await _run(event, "gemini")


@ultroid_cmd(pattern="antr( (.*)|$)")
async def anthropic_ai(event):
    await _run(event, "antr")


@ultroid_cmd(pattern="gpt( (.*)|$)")
async def openai_ai(event):
    await _run(event, "gpt")


@ultroid_cmd(pattern="deepseek( (.*)|$)")
async def deepseek_ai(event):
    await _run(event, "deepseek")
