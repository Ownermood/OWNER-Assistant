# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

"""Shared helpers for talking to AI providers (OpenAI, Anthropic, Gemini, DeepSeek).

Used by the `aiwrapper` plugin and by the chatbot (`addai` / `repai`).
"""

import json

import aiohttp

ENDPOINTS = {
    "gpt": "https://api.openai.com/v1/chat/completions",
    "antr": "https://api.anthropic.com/v1/messages",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "deepseek": "https://api.deepseek.com/chat/completions",
}

DEFAULT_MODELS = {
    "gpt": "gpt-5-mini",
    "antr": "claude-opus-5-5",
    "gemini": "gemini-2.5-flash",
    "deepseek": "deepseek-chat",
}

MODEL_KEYS = {
    "gpt": "OPENAI_MODEL",
    "antr": "ANTHROPIC_MODEL",
    "gemini": "GEMINI_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
}

API_KEYS = {
    "gemini": "GEMINI_API_KEY",
    "gpt": "OPENAI_API_KEY",
    "antr": "ANTHROPIC_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}

# Claude models that accept server-side refusal fallbacks.
_ANTHROPIC_FALLBACK_MODELS = {
    "claude-opus-5-5",
    "claude-opus-5",
    "claude-fable-5-2",
    "claude-fable-5-1",
    "claude-sonnet-5-5",
}

_TIMEOUT = aiohttp.ClientTimeout(total=300)


def get_model(provider, udB=None):
    """Model name from database or the default."""
    if udB is not None:
        if custom := udB.get_key(MODEL_KEYS[provider]):
            return custom
    return DEFAULT_MODELS[provider]


def first_configured_provider(udB):
    """(provider, api_key) of the first provider with a key set, else (None, None)."""
    preferred = udB.get_key("CHATBOT_PROVIDER")
    order = [preferred] if preferred in API_KEYS else []
    order += [p for p in API_KEYS if p not in order]
    for provider in order:
        if key := udB.get_key(API_KEYS[provider]):
            return provider, key
    return None, None


def _build_request(provider, prompt, api_key, model, stream, system=None):
    headers = {"Content-Type": "application/json"}
    if provider == "antr":
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = "2023-06-01"
        data = {
            "model": model,
            "max_tokens": 16000,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream,
        }
        if system:
            data["system"] = system
        if model in _ANTHROPIC_FALLBACK_MODELS:
            headers["anthropic-beta"] = "server-side-fallback-2026-07-01"
            data["fallbacks"] = "default"
        return headers, data

    headers["Authorization"] = f"Bearer {api_key}"
    messages = [{"role": "user", "content": prompt}]
    if system:
        messages.insert(0, {"role": "system", "content": system})
    return headers, {"model": model, "messages": messages, "stream": stream}


def _error_text(provider, payload, status):
    err = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(err, dict):
        msg = err.get("message") or str(err)
    elif err:
        msg = str(err)
    else:
        msg = str(payload)[:300]
    if status == 429:
        return f"⚠️ Rate limit exceeded ({provider}). Try again later.\n`{msg}`"
    return f"Error ({status}): {msg}"


def _extract_text(provider, payload):
    if provider == "antr":
        if payload.get("stop_reason") == "refusal":
            return "⚠️ Claude declined this request."
        return "".join(
            block.get("text", "")
            for block in payload.get("content", [])
            if block.get("type") == "text"
        )
    choices = payload.get("choices") or []
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content") or ""


async def ai_response(provider, prompt, api_key, model=None, stream=False, system=None):
    """Async generator yielding text from the provider.

    With stream=False it yields the whole answer once. Errors are yielded as text.
    """
    model = model or DEFAULT_MODELS[provider]
    headers, data = _build_request(provider, prompt, api_key, model, stream, system)
    try:
        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            async with session.post(
                ENDPOINTS[provider], headers=headers, json=data
            ) as resp:
                if resp.status != 200:
                    try:
                        payload = await resp.json(content_type=None)
                    except Exception:
                        payload = {"error": (await resp.text())[:300]}
                    yield _error_text(provider, payload, resp.status)
                    return

                if not stream:
                    payload = await resp.json(content_type=None)
                    yield _extract_text(provider, payload)
                    return

                # Server-sent events: one `data: {...}` line per event.
                async for raw in resp.content:
                    line = raw.decode("utf-8", "ignore").strip()
                    if not line.startswith("data:"):
                        continue
                    chunk = line[5:].strip()
                    if not chunk or chunk == "[DONE]":
                        continue
                    try:
                        event = json.loads(chunk)
                    except json.JSONDecodeError:
                        continue
                    if provider == "antr":
                        etype = event.get("type")
                        if etype == "content_block_delta":
                            delta = event.get("delta", {})
                            if delta.get("type") == "text_delta" and delta.get("text"):
                                yield delta["text"]
                        elif etype == "message_delta":
                            if event.get("delta", {}).get("stop_reason") == "refusal":
                                yield "\n⚠️ Claude declined this request."
                        elif etype == "error":
                            yield f"Error: {event.get('error', {}).get('message', event)}"
                    else:
                        choices = event.get("choices") or []
                        if choices:
                            text = (choices[0].get("delta") or {}).get("content")
                            if text:
                                yield text
    except Exception as er:
        yield f"Error: {er}"


async def ai_complete(provider, prompt, api_key, model=None, system=None):
    """Whole answer as one string."""
    out = ""
    async for part in ai_response(
        provider, prompt, api_key, model=model, stream=False, system=system
    ):
        out += part
    return out
