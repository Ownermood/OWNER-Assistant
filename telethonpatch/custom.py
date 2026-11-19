# GNU V3
# https://github.com/New-dev0/Telethon-Patch
# Copyright  New-dev0
# Vendored into Ultroid and updated for Telethon >= 1.46 (see LICENSE here).

from telethon.tl import functions, types
from telethon.tl.custom import Button, Message
# Telethon >= 1.46 (layer 233) replaced the old KeyboardButton* types with
# KeyboardInlineButton + a button "type". Support both.
_NEW_BUTTONS = hasattr(types, "KeyboardInlineButton") and hasattr(
    types, "InputInlineButtonTypeUserProfile"
)


def mention(text, user):
    """Send Button with UserProfile mention.

    call 'get_input_entity' to fill in user parameter."""
    if _NEW_BUTTONS:
        return types.KeyboardInlineButton(
            text, types.InputInlineButtonTypeUserProfile(user)
        )
    return types.InputKeyboardButtonUserProfile(text, user)


def web(text, url):
    """Send Button with WebView."""
    if _NEW_BUTTONS:
        return types.KeyboardInlineButton(text, types.InlineButtonTypeWebView(url))
    return types.KeyboardButtonSimpleWebView(text, url)


b_is_inline = Button._is_inline


def is_inline(button):
    """Check if Button is Inline."""
    old_types = tuple(
        getattr(types, name)
        for name in ("InputKeyboardButtonUserProfile", "KeyboardButtonSimpleWebView")
        if hasattr(types, name)
    )
    if old_types and isinstance(button, old_types):
        return True
    return b_is_inline(button)


setattr(Button, "mention", mention)
setattr(Button, "web", web)
setattr(Button, "_is_inline", is_inline)

# Message


def message_link(self: "Message"):
    """Message link"""
    if self.chat.username:
        return f"https://t.me/{self.chat.username}/{self.id}"
    return f"https://t.me/c/{self.chat.id}/{self.id}"


setattr(Message, "message_link", property(message_link))


async def comment(self: "Message", *args, **kwargs):
    """Bound Method to comment."""
    if self._client:
        return await self._client.send_message(
            self.chat_id, comment_to=self.id, *args, **kwargs
        )


async def react(self: "Message", *args, **kwargs):
    """Bound method to react to messages"""
    if self._client:
        return await self._client.send_reaction(self.chat_id, self.id, *args, **kwargs)


setattr(Message, "comment", comment)
setattr(Message, "react", react)
