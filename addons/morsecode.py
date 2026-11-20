# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/UltroidAddons/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
📖 **Commands**

• `{i}mencode <text>`
    Turn text into Morse code.

• `{i}mdecode <Morse code>`
    Turn Morse code back into text.
"""

from . import ultroid_cmd

# Done locally (the old xditya morse API is gone).
MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---",
    "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----.", ".": ".-.-.-", ",": "--..--", "?": "..--..",
    "'": ".----.", "!": "-.-.--", "/": "-..-.", "(": "-.--.", ")": "-.--.-",
    "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-", "+": ".-.-.",
    "-": "-....-", "_": "..--.-", '"': ".-..-.", "$": "...-..-", "@": ".--.-.",
}
REVERSE = {v: k for k, v in MORSE.items()}


def to_morse(text):
    return " / ".join(
        " ".join(MORSE[c] for c in word.upper() if c in MORSE) for word in text.split()
    )


def from_morse(code):
    words = code.replace("|", "/").split("/")
    return " ".join("".join(REVERSE.get(c, "?") for c in w.split()) for w in words)


@ultroid_cmd(pattern="mencode( (.*)|$)")
async def mencode(event):
    text = event.pattern_match.group(1).strip()
    if not text:
        return await event.eor("Please give a text!")
    await event.eor("**Encoded.**\n\n**Morse Code:** `{}`".format(to_morse(text)))


@ultroid_cmd(pattern="mdecode( (.*)|$)")
async def mdecode(event):
    text = event.pattern_match.group(1).strip()
    if not text:
        return await event.eor("Please give a text!")
    await event.eor("**Decoded.**\n\n**Message:** `{}`".format(from_morse(text)))
