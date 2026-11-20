# Re-creates the OWNER Assistant banners in resources/extras.
# Run: python3 dev/make_banners.py
import os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
F = os.path.join(os.path.dirname(__file__), "..", "resources", "fonts") + "/"
OUT = os.path.join(os.path.dirname(__file__), "..", "resources", "extras") + "/"
def bg(w, h, seed, c1=(14,10,40), c2=(92,30,140)):
    r = random.Random(seed)
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        for x in range(0, w):
            t = (x / w * 0.6 + y / h * 0.4)
            px[x, y] = tuple(int(c1[i] + (c2[i]-c1[i]) * t) for i in range(3))
    glow = Image.new("RGB", (w, h), 0); g = ImageDraw.Draw(glow)
    for _ in range(3):
        cx, cy, rad = r.randint(0, w), r.randint(0, h), r.randint(h//3, h)
        g.ellipse((cx-rad, cy-rad, cx+rad, cy+rad), fill=(120, 50, 190))
    glow = glow.filter(ImageFilter.GaussianBlur(h//3))
    im = Image.blend(im, glow, 0.25)
    d = ImageDraw.Draw(im)
    for _ in range(int(w*h/9000)):
        x, y, s = r.randint(0, w), r.randint(0, h), r.choice([1,1,1,2,2,3])
        d.ellipse((x, y, x+s, y+s), fill=(255,255,255))
    return im
def center(d, w, y, text, font, fill):
    tw = d.textlength(text, font=font)
    d.text(((w - tw) / 2, y), text, font=font, fill=fill)
def banner(name, top, big, sub, icon, seed):
    w, h = 1280, 720
    im = bg(w, h, seed); d = ImageDraw.Draw(im)
    fT = ImageFont.truetype(F+"Roboto-Medium.ttf", 44)
    fB = ImageFont.truetype(F+"Roboto-Medium.ttf", 130)
    fS = ImageFont.truetype(F+"Roboto-Regular.ttf", 40)
    # small badge
    fT = ImageFont.truetype(F+"Roboto-Medium.ttf", 34)
    bw = d.textlength(top, font=fT) / 2 + 40
    d.rounded_rectangle((w/2-bw, 120, w/2+bw, 180), radius=30, outline=(200,160,255), width=3)
    center(d, w, 130, top, fT, (225,205,255))
    center(d, w, 250, big, fB, (255,255,255))
    d.line((w/2-210, 430, w/2+210, 430), fill=(255,255,255), width=6)
    center(d, w, 465, sub, fS, (220,210,240))
    # icon circle bottom
    d.ellipse((w/2-50, 550, w/2+50, 650), outline=(180,120,255), width=4)
    center(d, w, 578, icon, ImageFont.truetype(F+"Roboto-Medium.ttf", 36), (230,210,255))
    im.save(OUT + f"owner_assistant_{name}.jpg", quality=88, optimize=True)
banner("alive",  "OWNER ASSISTANT", "I'M ALIVE",  "Online  ·  Fast  ·  Secure", "ON", 11)
banner("help",   "OWNER ASSISTANT", "HELP MENU",  "All commands, one place", "?", 12)
banner("start",  "OWNER ASSISTANT", "WELCOME",    "Personal Telegram Assistant", "Hi", 13)
banner("deploy", "OWNER ASSISTANT", "DEPLOYED",   "Your assistant is ready", "OK", 14)
banner("pm",     "OWNER ASSISTANT", "PM SECURITY","Wait for the owner to reply", "PM", 15)
