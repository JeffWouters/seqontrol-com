#!/usr/bin/env python3
"""Own the two product lists that appear on every page.

The products submenu and the footer's product column were copied into 27 files
by hand, at three different directory depths. Adding a product meant 54 edits
and one of them silently pointing at the wrong path — which is exactly what
happened the first time. One list here, rendered per page depth.

Availability is a property of the product, so the "Soon" tag on a coming-soon
entry is derived rather than remembered.

Run: python tools/build_nav.py
"""
from __future__ import annotations

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# order is deliberate: what is running, roughly by how often it is bought,
# then what is coming.
PRODUCTS = [
    ("sharecare.html",         "ShareCare",         "--t-sharecare",  False),
    ("securityportal.html",    "SecurityPortal",    "--t-security",   False),
    ("webscan.html",           "WebScan",           "--t-webscan",    False),
    ("complianceportal.html",  "CompliancePortal",  "--t-compliance", False),
    ("postureportal.html",     "PosturePortal",     "--t-posture",    False),
    ("mailtrust.html",         "MailTrust",         "--t-mailtrust",  False),
    ("dredd.html",             "Dredd",             "--t-dredd",      False),
]

# The footer's Company column carries the three free assessments — one per
# product a prospect can start with before talking to anyone. It was duplicated
# in the same 28 files as the product list, so it is owned here too.
COMPANY = [
    ("exposure-report.html", "Free exposure report"),
    ("spoofing-report.html", "Free spoofing check"),
    ("surface-report.html",  "Free surface scan"),
    ("guides/index.html",    "Guides"),
    ("about.html",           "About"),
    ("platform.html",        "Platform"),
    ("for-msps.html",        "For MSPs"),
    ("pricing.html",         "Pricing"),
    ("contact.html",         "Contact"),
]

SUBNAV = re.compile(r'( *)<ul class="subnav">.*?</ul>', re.S)
FOOTER = re.compile(r'( *)<h2>Products</h2>\n *<ul>.*?</ul>', re.S)
COMPANY_RE = re.compile(r'( *)<h2>Company</h2>\n *<ul>.*?</ul>', re.S)


def prefix(rel: str) -> str:
    """How a page at `rel` reaches products/."""
    d = os.path.dirname(rel)
    if d == "products":
        return ""
    return "../products/" if d else "products/"


def root(rel: str) -> str:
    """How a page at `rel` reaches the site root."""
    return "../" if os.path.dirname(rel) else ""


def company(pad: str, up: str) -> str:
    out = [f'{pad}<h2>Company</h2>', f'{pad}<ul>']
    for href, name in COMPANY:
        out.append(f'{pad}  <li><a href="{up}{href}">{name}</a></li>')
    out.append(f'{pad}</ul>')
    return "\n".join(out)


def subnav(pad: str, pre: str) -> str:
    out = [f'{pad}<ul class="subnav">']
    for href, name, tone, soon in PRODUCTS:
        tag = '<span class="soon-tag">Soon</span>' if soon else ""
        out.append(f'{pad}  <li><a href="{pre}{href}">'
                   f'<span class="dot" style="--tone: var({tone})"></span>{name}{tag}</a></li>')
    out.append(f'{pad}</ul>')
    return "\n".join(out)


def footer(pad: str, pre: str) -> str:
    out = [f'{pad}<h2>Products</h2>', f'{pad}<ul>']
    for href, name, _tone, _soon in PRODUCTS:
        out.append(f'{pad}  <li><a href="{pre}{href}">{name}</a></li>')
    out.append(f'{pad}</ul>')
    return "\n".join(out)


def main() -> None:
    changed = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith((".", "assets", "css", "js", "tools"))]
        for fn in sorted(filenames):
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            src = open(path, encoding="utf-8").read()
            pre = prefix(rel)

            up = root(rel)

            out = SUBNAV.sub(lambda m: subnav(m.group(1), pre), src)
            out = FOOTER.sub(lambda m: footer(m.group(1), pre), out)
            out = COMPANY_RE.sub(lambda m: company(m.group(1), up), out)

            if out != src:
                open(path, "w", encoding="utf-8", newline="\n").write(out)
                changed += 1
                print(f"  {rel}")
    print(f"nav rewritten in {changed} pages")


if __name__ == "__main__":
    main()
