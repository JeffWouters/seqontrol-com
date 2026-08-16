#!/usr/bin/env python3
"""Replace the real third-party domain in the web-scan screenshots.

The web scan shots were taken against a live external site and show its
failing checks — weak TLS, no CAA records, no security.txt. Publishing a named
third party's security weaknesses on our own marketing site would be both a bad
look and unfair to them, so the domain is replaced with example.com.

Nothing else in the image is touched: the scores, the failures and the fixes
are exactly as the product produced them.

Writes *-redacted.png alongside the originals; the site references those.

Run: python tools/redact_screenshots.py
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont

SHOTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "assets", "Screenshots", "WebScan")
SURFACE = (15, 23, 42, 255)      # sampled from the screenshots themselves
TEXT = (229, 231, 235, 255)


def font(size: int):
    for path in (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf",
                 r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def redact(name: str, box, text: str, size: int, colour):
    src = os.path.join(SHOTS, name + ".png")
    im = Image.open(src).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle(box, fill=SURFACE)
    d.text((box[0], box[1]), text, font=font(size), fill=colour)
    out = os.path.join(SHOTS, name + "-redacted.png")
    im.save(out, "PNG", optimize=True)
    print(f"{name}-redacted.png  {im.width}x{im.height}  {os.path.getsize(out)//1024} KB")


if __name__ == "__main__":
    # the scan-result modal: domain as the panel title
    redact("WebScan02", (8, 6, 260, 34), "example.com", 22, TEXT)
