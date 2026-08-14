"""Extract the SeQontrol symbol and wordmark from the flattened logo JPEG.

The source arrived as JPEG, so the original alpha is gone and the transparency
checkerboard (30px cells, ~#f2f2f2 / ~#fcfcfc) is baked in as real pixels.

Measuring the file settles what is background: the interior of the magnifying
glass alternates 241/252 down its middle, i.e. the checkerboard shows through
it, so the lens is a hole and not a white fill. Same for the letter counters.
That means every light, neutral pixel is background — no flood fill needed, and
a flood fill would in fact be wrong.

Edge pixels are blends of ink and white background. Keeping them as-is leaves a
pale halo on a dark page, so they are un-premultiplied: recover the true ink
colour from the blend and let alpha carry the coverage.
"""
from PIL import Image, ImageFilter
import os

SRC = r"Z:\tmp\seqontrol-src.jpg"
OUT = r"Z:\Websites\SeQontrol.com\assets"

LUM_BG = 232      # at/above this luminance a neutral pixel is pure background
LUM_INK = 168     # at/below this it is pure ink
SAT_BG = 26       # channel spread below which a pixel counts as neutral

img = Image.open(SRC).convert("RGB")
W, H = img.size
px = img.load()

alpha = Image.new("L", (W, H))
ap = alpha.load()
rgb = Image.new("RGB", (W, H))
cp = rgb.load()

for y in range(H):
    for x in range(W):
        r, g, b = px[x, y]
        lum = max(r, g, b)
        sat = lum - min(r, g, b)

        if sat >= SAT_BG:                    # coloured -> ink
            cover = 1.0
        elif lum >= LUM_BG:                  # light and neutral -> background
            cover = 0.0
        elif lum <= LUM_INK:                 # dark and neutral -> ink (the navy)
            cover = 1.0
        else:                                # neutral mid-tone -> edge blend
            cover = (LUM_BG - lum) / (LUM_BG - LUM_INK)

        if cover <= 0.06:
            ap[x, y] = 0
            cp[x, y] = (255, 255, 255)
            continue

        if cover >= 0.98:
            ap[x, y] = 255
            cp[x, y] = (r, g, b)
            continue

        # un-premultiply against the white background it was composited onto
        inv = 1.0 - cover
        cp[x, y] = tuple(
            max(0, min(255, int((c - 255 * inv) / cover))) for c in (r, g, b)
        )
        ap[x, y] = int(round(cover * 255))

# knock out isolated JPEG speckle without eating the anti-aliased rim
alpha = alpha.filter(ImageFilter.MedianFilter(3))

out = rgb.convert("RGBA")
out.putalpha(alpha)

# ---- split into horizontal bands of content -------------------------------
a = alpha.load()
rows = []
for y in range(H):
    rows.append(any(a[x, y] > 48 for x in range(0, W, 2)))

bands, start = [], None
for y, ink in enumerate(rows):
    if ink and start is None:
        start = y
    elif not ink and start is not None:
        if y - start > 12:
            bands.append((start, y))
        start = None
if start is not None:
    bands.append((start, H))
print("bands:", bands)

os.makedirs(OUT, exist_ok=True)

def save(band, name, pad=6):
    top, bottom = band
    crop = out.crop((0, max(0, top - pad), W, min(H, bottom + pad)))
    box = crop.getbbox()
    crop = crop.crop((max(0, box[0] - pad), 0, min(crop.width, box[2] + pad), crop.height))
    crop.save(os.path.join(OUT, name), "PNG", optimize=True)
    print(f"{name}: {crop.width}x{crop.height}  {os.path.getsize(os.path.join(OUT, name))//1024} KB")
    return crop

saved = [save(b, n) for b, n in zip(
    bands, ["seqontrol-symbol.png", "seqontrol-wordmark.png", "seqontrol-tagline.png"])]
