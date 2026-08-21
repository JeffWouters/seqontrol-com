"""Build the on-dark variants, the small sizes, the icons and an OG card.

The supplied artwork is drawn for a light page: the wordmark and the shield are
navy (#1a1b4b), which all but disappears on the site background (#0b0f17). The
purple is fine. So the on-dark variants keep the purple exactly and lift only
the navy to a light slate, preserving anti-aliasing by interpolating between the
two brand colours rather than thresholding.

Run: python tools/make_logo_variants.py

RUN THIS BEFORE make_icons.py. Both scripts write favicon-32.png,
apple-touch-icon.png and icon-512.png and disagree about what belongs in them:
this one centres the on-dark symbol, make_icons emits a white shield on a dark
tile. Whichever runs last wins. make_icons is the treatment the site actually
links, so it must run second — which also means the three icons written here are
overwritten in the normal flow and exist only for a run of this script alone.

It only runs when invoked directly. At import scope, `import make_logo_variants`
regenerated every logo variant as a side effect — and being last alphabetically,
it silently reverted make_icons' output in the process.
"""
from __future__ import annotations

import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
# A working comparison, not a site asset, so it is deliberately written outside the repo.
PREVIEW = os.environ.get("SEQONTROL_PREVIEW_DIR", r"Z:\tmp")

BG = (11, 15, 23)
PURPLE = (108, 82, 217)
NAVY = (26, 27, 75)
LIGHT = (229, 231, 235)      # site --text


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def on_dark(src, dst):
    im = Image.open(os.path.join(OUT, src)).convert("RGBA")
    w, h = im.size
    p = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = p[x, y]
            if a == 0:
                continue
            dn, dp = dist((r, g, b), NAVY), dist((r, g, b), PURPLE)
            t = dn / (dn + dp) if (dn + dp) else 1.0   # 1 = purple, 0 = navy
            p[x, y] = (
                int(LIGHT[0] + (PURPLE[0] - LIGHT[0]) * t),
                int(LIGHT[1] + (PURPLE[1] - LIGHT[1]) * t),
                int(LIGHT[2] + (PURPLE[2] - LIGHT[2]) * t),
                a,
            )
    im.save(os.path.join(OUT, dst), "PNG", optimize=True)
    print(f"{dst}: {w}x{h}  {os.path.getsize(os.path.join(OUT, dst))//1024} KB")
    return im


def resize(im, name, size, box=True):
    s = im.copy()
    s.thumbnail((size, size * 4 if box else size), Image.LANCZOS)
    s.save(os.path.join(OUT, name), "PNG", optimize=True)
    print(f"{name}: {s.width}x{s.height}  {os.path.getsize(os.path.join(OUT, name))//1024} KB")


def og_card(sym_d, word_d, tag_d):
    card = Image.new("RGB", (1200, 630), BG)
    s = sym_d.copy(); s.thumbnail((250, 250), Image.LANCZOS)
    w = word_d.copy(); w.thumbnail((520, 520), Image.LANCZOS)
    t = tag_d.copy(); t.thumbnail((430, 430), Image.LANCZOS)
    card.paste(s, ((1200 - s.width) // 2, 92), s)
    card.paste(w, ((1200 - w.width) // 2, 92 + s.height + 34), w)
    card.paste(t, ((1200 - t.width) // 2, 92 + s.height + 34 + w.height + 22), t)
    card.save(os.path.join(OUT, "og-card.png"), "PNG", optimize=True)
    print(f"og-card.png: 1200x630  {os.path.getsize(os.path.join(OUT, 'og-card.png'))//1024} KB")


def preview(sym_d, word_d):
    """Both treatments side by side, for eyeballing."""
    prev = Image.new("RGB", (1180, 760), BG)
    o_s = Image.open(os.path.join(OUT, "seqontrol-symbol.png")).convert("RGBA")
    o_w = Image.open(os.path.join(OUT, "seqontrol-wordmark.png")).convert("RGBA")
    for col, (ss, ww) in enumerate(((o_s, o_w), (sym_d, word_d))):
        a = ss.copy(); a.thumbnail((300, 300), Image.LANCZOS)
        b = ww.copy(); b.thumbnail((460, 460), Image.LANCZOS)
        cx = 300 + col * 590
        prev.paste(a, (cx - a.width // 2, 90), a)
        prev.paste(b, (cx - b.width // 2, 90 + a.height + 50), b)
    os.makedirs(PREVIEW, exist_ok=True)
    prev.save(os.path.join(PREVIEW, "preview-compare.png"))
    print("comparison written")


def main() -> None:
    for needed in ("seqontrol-symbol.png", "seqontrol-wordmark.png", "seqontrol-tagline.png"):
        if not os.path.exists(os.path.join(OUT, needed)):
            raise SystemExit(f"make_logo_variants: {needed} is missing — run tools/extract_logo.py first")

    sym_d = on_dark("seqontrol-symbol.png", "seqontrol-symbol-on-dark.png")
    word_d = on_dark("seqontrol-wordmark.png", "seqontrol-wordmark-on-dark.png")
    tag_d = on_dark("seqontrol-tagline.png", "seqontrol-tagline-on-dark.png")

    # header/footer sized copies so a 34px slot does not pull a 644px image
    for size in (64, 128):
        resize(sym_d, f"seqontrol-symbol-on-dark-{size}.png", size)
    resize(word_d, "seqontrol-wordmark-on-dark-320.png", 320)
    resize(tag_d, "seqontrol-tagline-on-dark-320.png", 320)

    # icons: square canvas, symbol centred, keeps transparency. Overwritten by make_icons.py in
    # the normal flow — see the module docstring.
    for size, name in ((32, "favicon-32.png"), (180, "apple-touch-icon.png"), (512, "icon-512.png")):
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        s = sym_d.copy()
        s.thumbnail((int(size * 0.92), int(size * 0.92)), Image.LANCZOS)
        canvas.paste(s, ((size - s.width) // 2, (size - s.height) // 2), s)
        canvas.save(os.path.join(OUT, name), "PNG", optimize=True)
        print(f"{name}: {size}x{size}  {os.path.getsize(os.path.join(OUT, name))//1024} KB")

    og_card(sym_d, word_d, tag_d)
    preview(sym_d, word_d)


if __name__ == "__main__":
    main()
