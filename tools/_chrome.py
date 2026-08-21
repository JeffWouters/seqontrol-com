#!/usr/bin/env python3
"""The page shell every generator wraps its content in.

WHY THIS IS SHARED RATHER THAN COPIED. build_legal.py and build_guides.py each held an identical
`chrome()`: same donor page, same three index() calls, same return shape. That is not incidental
repetition — it is one piece of knowledge about the SHAPE of contact.html, written down twice.

The three markers below are load-bearing and brittle by nature: `<title>`, `</head>`, `<main`,
`<footer class="site-footer">` and `<script src=`. Move any of them in the donor and the split goes
wrong. With two copies, the next person fixes the one that failed loudly and leaves the other to fail
quietly on the next run — which is the specific failure mode this file removes.

The donor is contact.html because it is authored by hand, is small, and carries the full chrome:
header, nav, footer, script tag.

It is NOT, however, untouched by the pipeline, and an earlier version of this docstring claimed it
was - which was wrong in the direction that makes the coupling look safer than it is. build_nav.py
rewrites its nav, skip link, footer columns and data-contact; build_seo.py rewrites its title,
description, CSP, canonical and Open Graph tags. Those are precisely the slices chrome() takes, so
this module reads a file that two other generators are actively rewriting. That is the coupling.

The invariant that keeps it working: build_seo.META must continue to include contact.html. A page
outside META goes through apply_csp_only() instead, which injects the CSP straight after <head> -
so contact.html would start carrying a policy tag inside the head_open slice, and every generated
page would inherit a second one. It is also why generators must run in the documented order:
chrome() reads whatever contact.html happens to hold at that moment.
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
