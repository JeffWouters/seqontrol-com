#!/usr/bin/env python3
"""Cut the raw screenshots into the assets the pages actually use.

A full dashboard shrunk into a column is texture, not evidence: nothing in it
can be read. These crops keep one idea each, at a size where the words survive.

The three-row checks composite is deliberate — the rows that matter (a failure
with a control tag, an unassessed check, a pass) are scattered down a long list,
so they are stacked into one image rather than asking anyone to hunt.

Run: python tools/crop_screenshots.py
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw

SHOTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "assets", "Screenshots")
GAP_BG = (11, 15, 23)


def load(prod, name):
    return Image.open(os.path.join(SHOTS, prod, name + ".png")).convert("RGBA")


def save(im, prod, name):
    p = os.path.join(SHOTS, prod, name + ".png")
    im.save(p, "PNG", optimize=True)
    print(f"{name:<34} {im.width}x{im.height}  {os.path.getsize(p)//1024} KB")


def crop(prod, src, box, out, erase=()):
    im = load(prod, src).crop(box)
    if erase:
        d = ImageDraw.Draw(im)
        bg = im.convert("RGB").getpixel(erase[0])
        for r in erase[1:]:
            d.rectangle(r, fill=bg + (255,))
    save(im, prod, out)


def splice(im, keep_left, cut_to):
    """Cut an empty vertical strip out of a wide panel so it reflows narrow.

    A card that stretches the full page width cannot be cropped without slicing
    through its own right border. Removing the dead space in its middle keeps
    the border and drops the emptiness.
    """
    right = im.crop((cut_to, 0, im.width, im.height))
    out = Image.new("RGBA", (keep_left + right.width, im.height))
    out.paste(im.crop((0, 0, keep_left, im.height)), (0, 0))
    out.paste(right, (keep_left, 0))
    return out


def compose(prod, src, parts, out, pad=14):
    """Stack panels taken from one screenshot onto a single background."""
    im = load(prod, src)
    bg = im.convert("RGB").getpixel((700, 300))
    tiles = []
    for box, splice_at in parts:
        tile = im.crop(box)
        if splice_at:
            tile = splice(tile, *splice_at)
        tiles.append(tile)
    w = max(t.width for t in tiles)
    h = sum(t.height for t in tiles) + pad * (len(tiles) - 1)
    canvas = Image.new("RGBA", (w, h), bg + (255,))
    y = 0
    for t in tiles:
        canvas.paste(t, (0, y), t)
        y += t.height + pad
    save(canvas, prod, out)


def stack(prod, src, bands, out, gap=10):
    """Composite several horizontal bands of one image into a single asset."""
    im = load(prod, src)
    parts = [im.crop((0, a, im.width, b)) for a, b in bands]
    w = max(p.width for p in parts)
    h = sum(p.height for p in parts) + gap * (len(parts) - 1)
    canvas = Image.new("RGBA", (w, h), GAP_BG + (255,))
    y = 0
    for p in parts:
        canvas.paste(p, (0, y), p)
        y += p.height + gap
    save(canvas, prod, out)


if __name__ == "__main__":
    # Hero: product name, "needs attention", the exposure score. The wide card is
    # spliced rather than cropped so its right border survives, and the tile of
    # raw counters beside the ring is dropped — at this tenant's size those
    # numbers argue against the product.
    compose("ShareCare", "ShareCare01",
            [((0, 6, 300, 54), None),            # product name
             ((0, 145, 969, 300), (500, 940)),   # needs attention
             ((0, 308, 434, 578), None)],        # exposure score
            "hero-attention")

    # The scan modal argues that unreadable planes are never scored as clean, and
    # the per-plane results carry that on their own. The running total beside the
    # progress text is a fact about the demo tenant, not about the product, so it
    # goes: nothing that supports the claim is touched.
    crop("ShareCare", "ShareCare02", (0, 0, 907, 636), "scan-detail",
         erase=[(700, 112), (341, 100, 420, 126)])

    # The ladder is the product's whole arc and lives as a thin strip inside a
    # 1536px-tall screenshot.
    crop("SecurityPortal", "SecurityPortal01", (18, 196, 1186, 320), "ladder-strip")

    # The rung-rule panel from this same screenshot is already cut as
    # posture-rung-detail.png and carries the principle section on the home page.

    # Category rows, with the unassessed count sitting next to the failures.
    crop("SecurityPortal", "SecurityPortal01", (6, 1008, 1202, 1522), "category-rows")

    # One fail with a control reference, one unassessed, one pass.
    stack("SecurityPortal", "SecurityPortal03",
          [(325, 415), (915, 995), (1205, 1285)], "checks-three-rows")
