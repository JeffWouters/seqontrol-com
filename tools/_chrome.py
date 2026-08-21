#!/usr/bin/env python3
"""The page shell every generator wraps its content in.

WHY THIS IS SHARED RATHER THAN COPIED. build_legal.py and build_guides.py each held an identical
`chrome()`: same donor page, same three index() calls, same return shape. That is not incidental
repetition — it is one piece of knowledge about the SHAPE of contact.html, written down twice.

The three markers below are load-bearing and brittle by nature: `<title>`, `</head>`, `<main`,
`<footer class="site-footer">` and `<script src=`. Move any of them in the donor and the split goes
wrong. With two copies, the next person fixes the one that failed loudly and leaves the other to fail
quietly on the next run — which is the specific failure mode this file removes.

The donor is contact.html because it is hand-written, small, and carries the full chrome: header,
nav, footer, script tag. Nothing generates it, so it cannot be rewritten out from under this.
"""
from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "contact.html")


def chrome() -> tuple[str, str, str]:
    """Split the donor into (head_open, after_head, footer).

    `head_open` runs up to <title> so a caller supplies its own title and metadata; `after_head`
    carries </head> through to <main>, which is the header and nav; `footer` is the site footer up
    to the script tag the caller re-adds. Deliberately three strings rather than a template: the
    chrome is markup nobody should be re-typing, and a template would invite editing it here.
    """
    src = io.open(SOURCE, encoding="utf-8").read()
    for marker in ("<title>", "</head>", "<main", '<footer class="site-footer">', "<script src="):
        if marker not in src:
            raise SystemExit(
                f"_chrome: {os.path.basename(SOURCE)} no longer contains {marker!r}. The donor's shape "
                "changed and every generated page would be built wrong — fix the marker here rather "
                "than letting each generator guess."
            )
    return (src[:src.index("<title>")],
            src[src.index("</head>"):src.index("<main")],
            src[src.index('<footer class="site-footer">'):src.index("<script src=")])
