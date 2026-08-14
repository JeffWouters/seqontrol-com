"""Icon set: white shield, purple cloud / ring / magnifier / check.

The delivered artwork paints the shield navy, which is drawn for a white page.
The lockup used across this site lifts that shield so it reads white with the
purple furniture on top, and the icons now match it: shield pure white, every
purple element untouched, background transparent.

That suits dark browser chrome. On a light strip a white shield disappears, so
the navy original is emitted too and linked behind
`media="(prefers-color-scheme: light)"`.

apple-touch-icon sits on an opaque dark tile — iOS drops alpha onto black, and a
white shield needs a dark ground to read against anyway.
"""
from PIL import Image, ImageDraw
import os

A = r"Z:\Websites\SeQontrol.com\assets"
ROOT = r"Z:\Websites\SeQontrol.com"

PURPLE = (108, 82, 217)
NAVY = (26, 27, 75)
WHITE = (255, 255, 255)
SITE_BG = (11, 15, 23)

src = Image.open(os.path.join(A, "seqontrol-symbol.png")).convert("RGBA")

def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

def shield_to(sym, colour):
    """Repaint only the navy (the shield); leave every purple pixel alone.
    Interpolating rather than thresholding keeps the anti-aliased rim clean."""
    o = sym.copy()
    p = o.load()
    for y in range(o.height):
        for x in range(o.width):
            r, g, b, a = p[x, y]
            if not a:
                continue
            dn, dp = dist((r, g, b), NAVY), dist((r, g, b), PURPLE)
            t = dn / (dn + dp) if (dn + dp) else 1.0     # 1 = purple, 0 = navy
            p[x, y] = tuple(
                int(colour[i] + (PURPLE[i] - colour[i]) * t) for i in range(3)
            ) + (a,)
    return o

white_shield = shield_to(src, WHITE)

def square(sym, size, inset=0.94):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    s = sym.copy()
    s.thumbnail((int(size * inset), int(size * inset)), Image.LANCZOS)
    canvas.alpha_composite(s, ((size - s.width) // 2, (size - s.height) // 2))
    return canvas

# favicon.ico — white shield, transparent, multi-resolution
ico = square(white_shield, 256)
ico.save(os.path.join(ROOT, "favicon.ico"), format="ICO",
         sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("favicon.ico:", os.path.getsize(os.path.join(ROOT, "favicon.ico")) // 1024, "KB — white shield")

for size, name in ((32, "favicon-32.png"), (512, "icon-512.png")):
    square(white_shield, size).save(os.path.join(A, name), "PNG", optimize=True)
    print(f"{name}: {size}x{size}  {os.path.getsize(os.path.join(A, name))//1024} KB — white shield")

# light-chrome fallback: the artwork's own navy shield
square(src, 32).save(os.path.join(A, "favicon-32-light.png"), "PNG", optimize=True)
print(f"favicon-32-light.png: 32x32  {os.path.getsize(os.path.join(A,'favicon-32-light.png'))//1024} KB — navy shield")

old = os.path.join(A, "favicon-32-dark.png")
if os.path.exists(old):
    os.remove(old)
    print("removed favicon-32-dark.png (superseded)")

# apple-touch: opaque, dark tile so the white shield has something to sit on
size = 180
tile = Image.new("RGB", (size, size), SITE_BG)
s = white_shield.copy()
s.thumbnail((int(size * 0.74), int(size * 0.74)), Image.LANCZOS)
tile.paste(s, ((size - s.width) // 2, (size - s.height) // 2), s)
tile.save(os.path.join(A, "apple-touch-icon.png"), "PNG", optimize=True)
print(f"apple-touch-icon.png: {size}x{size}  {os.path.getsize(os.path.join(A,'apple-touch-icon.png'))//1024} KB — dark tile")

# preview both against both chromes
sheet = Image.new("RGB", (460, 200), (128, 128, 128))
d = ImageDraw.Draw(sheet)
for row, (sym, note) in enumerate(((white_shield, "white shield (default)"),
                                   (src, "navy shield (light chrome)"))):
    y = 16 + row * 96
    d.rectangle([0, y, 230, y + 80], fill=(242, 242, 242))
    d.rectangle([230, y, 460, y + 80], fill=(32, 33, 36))
    d.text((6, y + 2), note, fill=(90, 90, 90))
    for half in (0, 230):
        x = half + 26
        for sz in (16, 32, 48):
            c = square(sym, sz)
            sheet.paste(c, (x, y + 26), c)
            x += sz + 30
sheet.save(r"Z:\tmp\favicon-final.png")
print("preview ok")
