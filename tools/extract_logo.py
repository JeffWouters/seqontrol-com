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

Run: python tools/extract_logo.py

This rewrites committed artwork, so it only runs when invoked directly. It used
to do all of this at import scope, which meant `import extract_logo` — to read a
constant, or in a script that walks tools/ — silently regenerated the logo PNGs.
That is not hypothetical: it happened while testing that the tools still load,
and rewrote sixteen tracked binaries in one go.

SRC is genuinely outside the repository: it is the supplied artwork, not a site
asset, and is not tracked here. Override it with SEQONTROL_LOGO_SRC.
"""
from __future__ import annotations

import os

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
SRC = os.environ.get("SEQONTROL_LOGO_SRC", r"Z:\tmp\seqontrol-src.jpg")

LUM_BG = 232      # at/above this luminance a neutral pixel is pure background
LUM_INK = 168     # at/below this it is pure ink
SAT_BG = 26       # channel spread below which a pixel counts as neutral

BANDS = ["seqontrol-symbol.png", "seqontrol-wordmark.png", "seqontrol-tagline.png"]


def separate(img: "Image.Image") -> "Image.Image":
    """Recover ink colour and coverage from the flattened JPEG."""
    w, h = img.size
    px = img.load()
    alpha = Image.new("L", (w, h))
    ap = alpha.load()
    rgb = Image.new("RGB", (w, h))
    cp = rgb.load()

    for y in range(h):
        for x in range(w):
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
    return out


def find_bands(out: "Image.Image") -> list[tuple[int, int]]:
    """The horizontal bands of content: symbol, wordmark, tagline."""
    w, h = out.size
    a = out.getchannel("A").load()
    rows = [any(a[x, y] > 48 for x in range(0, w, 2)) for y in range(h)]

    bands, start = [], None
    for y, ink in enumerate(rows):
        if ink and start is None:
            start = y
        elif not ink and start is not None:
            if y - start > 12:
                bands.append((start, y))
            start = None
    if start is not None:
        bands.append((start, h))
    return bands


def save(out: "Image.Image", band: tuple[int, int], name: str, pad: int = 6) -> "Image.Image":
    top, bottom = band
    w, h = out.size
    crop = out.crop((0, max(0, top - pad), w, min(h, bottom + pad)))
    box = crop.getbbox()
    crop = crop.crop((max(0, box[0] - pad), 0, min(crop.width, box[2] + pad), crop.height))
    path = os.path.join(OUT, name)
    crop.save(path, "PNG", optimize=True)
    print(f"{name}: {crop.width}x{crop.height}  {os.path.getsize(path)//1024} KB")
    return crop


def main() -> None:
    if not os.path.exists(SRC):
        raise SystemExit(
            f"extract_logo: source artwork not found at {SRC}. It is not tracked in this repo — "
            "point SEQONTROL_LOGO_SRC at the supplied logo JPEG."
        )
    img = Image.open(SRC).convert("RGB")
    out = separate(img)
    bands = find_bands(out)
    print("bands:", bands)

    os.makedirs(OUT, exist_ok=True)
    for band, name in zip(bands, BANDS):
        save(out, band, name)


if __name__ == "__main__":
    main()
