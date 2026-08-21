#!/usr/bin/env python3
"""Derive WebP twins of the published screenshots and wrap their <img> tags in <picture>.

WHY WEBP, AND WHY LOSSLESS. These are UI screenshots: flat fills, hard edges, small text. That is the
content type WebP's lossless mode is best at and the one lossy modes are worst at - quality 82 saved
48% while softening the very text the screenshot exists to show, and quality 90 saved only 34%.
Lossless saves 69% (362 KB -> 111 KB across the site) and is pixel-identical to the PNG. There is no
tradeoff to weigh here, which is unusual enough to write down so nobody "optimises" it to lossy later.

WHY THE WORK LIST COMES FROM GIT AND NOT FROM A GLOB. This is the important part of this file.
assets/Screenshots holds raw captures that are deliberately NOT published - .gitignore keeps them out
because they still carry the real third-party domain the redaction exists to remove. Those ignore
rules match *.png. A derived ShareCare01.webp matches none of them, so a filesystem glob would
convert an ignored capture, git would see a brand-new unignored file, and the next `git add -A` would
publish exactly what the redaction was for. Deriving the work list from `git ls-files` means this
tool can only ever touch files that are already published. The .gitignore carries matching webp rules
as a second line of defence, but this is the one that matters.

Run: python tools/build_images.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

try:
    from PIL import Image
except ImportError:                                              # pragma: no cover
    sys.exit("build_images: Pillow is required (pip install Pillow)")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = "assets/Screenshots"

# Matches a screenshot <img>, with or without the <picture> wrapper this tool adds. Capturing the
# wrapper too is what makes a second run a no-op instead of a nesting doll: the whole thing is
# rewritten from the <img> every time, so the output depends on the image, not on how often this ran.
PICTURE_RE = re.compile(
    r'(?:<picture>\s*<source[^>]*>\s*)?'
    r'(<img\b[^>]*?src="([^"]*' + SHOTS.split("/")[-1] + r'/[^"]*\.png)"[^>]*?>)'
    r'(?:\s*</picture>)?',
    re.S,
)


def published_screenshots() -> list[str]:
    """Every screenshot git is actually tracking. See the module docstring for why this is not a glob."""
    out = subprocess.run(["git", "ls-files", SHOTS], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split()
    return [p for p in out if p.lower().endswith(".png")]


def convert(rel: str) -> tuple[int, int, bool]:
    """PNG -> lossless WebP beside it. Returns (png bytes, webp bytes, whether it was rewritten)."""
    png = os.path.join(ROOT, rel)
    webp = os.path.splitext(png)[0] + ".webp"
    fresh = os.path.exists(webp) and os.path.getmtime(webp) >= os.path.getmtime(png)
    if not fresh:
        # RGBA keeps any transparency the crop carried; method=6 is the slowest, smallest setting,
        # which is free here because this runs on a handful of files by hand, not per request.
        Image.open(png).convert("RGBA").save(webp, "WEBP", lossless=True, method=6)
    return os.path.getsize(png), os.path.getsize(webp), not fresh


def rewrite(src: str) -> str:
    """Wrap screenshot <img> tags in <picture> so browsers take the WebP and old ones keep the PNG."""
    def one(m: re.Match) -> str:
        img, png_src = m.group(1), m.group(2)
        if not os.path.exists(os.path.join(ROOT, png_src.replace("../", ""))):
            return m.group(0)
        webp_src = os.path.splitext(png_src)[0] + ".webp"
        return (f'<picture><source srcset="{webp_src}" type="image/webp">{img}</picture>')
    return PICTURE_RE.sub(one, src)


def main() -> None:
    shots = published_screenshots()
    if not shots:
        sys.exit("build_images: git reports no tracked screenshots - refusing to guess from disk")

    png_total = webp_total = 0
    made = 0
    for rel in shots:
        p, w, did = convert(rel)
        png_total += p
        webp_total += w
        made += did
    print(f"  {len(shots)} screenshots, {made} (re)encoded")
    print(f"  {png_total/1024:.1f} KB png -> {webp_total/1024:.1f} KB webp "
          f"({100 * (1 - webp_total / png_total):.0f}% smaller, lossless)")

    changed = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith((".", "assets", "css", "js", "tools"))]
        for fn in sorted(filenames):
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            out = rewrite(src)
            if out != src:
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(out)
                changed += 1
                print(f"  {os.path.relpath(path, ROOT)}")
    print(f"<picture> wrappers written in {changed} pages")


if __name__ == "__main__":
    main()
