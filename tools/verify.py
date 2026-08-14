#!/usr/bin/env python3
"""Pre-deploy checks for SeQontrol.com. Exits non-zero on any failure.

Four groups, all of which have caught a real regression at least once:

  links     every internal href/src resolves to a file that exists
  markup    tags balance, no duplicate ids, no malformed attributes
  a11y      lang, single h1, no skipped heading levels, alt text, labels,
            landmarks, th scope, keyboard-reachable scroll boxes
  content   the editorial rules the site is committed to — no prices, no
            customer references, no CIS framework names, no re-consent overclaim

Run: python tools/verify.py
"""
from __future__ import annotations

import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = sorted(
    os.path.join(dp, f)
    for dp, _, fns in os.walk(ROOT)
    for f in fns
    if f.endswith(".html") and ".git" not in dp
)

failures: list[str] = []


def fail(page: str, msg: str) -> None:
    failures.append(f"{os.path.relpath(page, ROOT)}: {msg}")


# --------------------------------------------------------------------- links

def check_links(page: str, src: str) -> None:
    for url in re.findall(r'(?:href|src)="([^"]+)"', src):
        if url.startswith(("http://", "https://", "mailto:", "//", "#", "data:")):
            continue
        target = os.path.join(os.path.dirname(page), url.split("#")[0])
        if not os.path.exists(target):
            fail(page, f"broken link -> {url}")


# -------------------------------------------------------------------- markup

PAIRED = ("div", "table", "section", "article", "ul", "ol", "li", "button", "nav",
          "th", "td", "tr", "thead", "tbody", "aside", "form", "main", "header",
          "footer", "p", "span", "a", "h1", "h2", "h3", "h4")


def check_markup(page: str, src: str) -> None:
    for tag in PAIRED:
        opened = len(re.findall(rf"<{tag}[ >]", src))
        closed = len(re.findall(rf"</{tag}>", src))
        if opened != closed:
            fail(page, f"<{tag}> unbalanced: {opened} open, {closed} close")

    # the class of bug a naive regex edit introduces: an attribute injected into
    # a tag name, e.g. <thead> becoming <th scope="col"ead>. Note alt="" is
    # legitimate (decorative images) and must not trip this.
    for bad in ('scope="col"ead', '<th scope="col"e', 'scope="col"scope'):
        if bad in src:
            fail(page, f"malformed markup: {bad!r}")
    if re.search(r'<[a-z]+[^>]*"[a-z]+>', src):
        fail(page, "attribute value runs into a tag name")


# ---------------------------------------------------------------------- a11y

class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[int] = []
        self.ids: list[str] = []
        self.labels: set[str] = set()
        self.fields: list[tuple[str, str | None, bool]] = []
        self.img_no_alt = 0
        self.landmarks: set[str] = set()
        self.th = 0
        self.th_scoped = 0
        self.scroll = 0
        self.scroll_reachable = 0
        self.link_text: list[str] = []
        self._in_a = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        if tag == "img" and "alt" not in a:
            self.img_no_alt += 1
        if tag == "a" and a.get("href"):
            self._in_a = True
        if tag == "label" and a.get("for"):
            self.labels.add(a["for"])
        if tag in ("input", "select", "textarea"):
            self.fields.append(
                (tag, a.get("id"), bool(a.get("aria-label") or a.get("aria-labelledby"))))
        if tag in ("main", "header", "footer", "nav", "aside"):
            self.landmarks.add(tag)
        if tag == "th":
            self.th += 1
            self.th_scoped += bool(a.get("scope"))
        if tag == "div" and "table-scroll" in a.get("class", ""):
            self.scroll += 1
            self.scroll_reachable += a.get("tabindex") is not None

    def handle_data(self, data):
        if self._in_a and data.strip():
            self.link_text.append(data.strip())
            self._in_a = False


def check_a11y(page: str, src: str) -> None:
    p = Page()
    p.feed(src)

    if "<html lang=" not in src:
        fail(page, "no lang on <html>")
    if src.count("<title>") != 1:
        fail(page, "expected exactly one <title>")

    if p.headings.count(1) != 1:
        fail(page, f"expected exactly one h1, found {p.headings.count(1)}")
    prev = 0
    for level in p.headings:
        if prev and level > prev + 1:
            fail(page, f"heading order jumps h{prev} -> h{level}")
        prev = level

    dupes = sorted({i for i in p.ids if p.ids.count(i) > 1})
    if dupes:
        fail(page, f"duplicate ids: {dupes}")
    if p.img_no_alt:
        fail(page, f"{p.img_no_alt} <img> without alt")
    for tag, fid, aria in p.fields:
        if not aria and (not fid or fid not in p.labels):
            fail(page, f"unlabelled <{tag}> id={fid}")
    for landmark in ("main", "header", "footer", "nav"):
        if landmark not in p.landmarks:
            fail(page, f"missing <{landmark}> landmark")
    if p.th and p.th_scoped < p.th:
        fail(page, f"{p.th - p.th_scoped} <th> without scope")
    if p.scroll != p.scroll_reachable:
        fail(page, f"{p.scroll - p.scroll_reachable} scroll box(es) not keyboard reachable")
    vague = [t for t in p.link_text if t.lower() in
             ("here", "click here", "read more", "more", "link", "this")]
    if vague:
        fail(page, f"vague link text: {vague}")


# ------------------------------------------------------------------- content

# Each rule is a decision made deliberately; see README "Content rules".
CONTENT_RULES = [
    (r"\bCIS\b|CIS-[A-Z]", "CIS framework reference (site names other frameworks only)"),
    (r"\$\s?\d", "a price (the site carries no figures)"),
    (r"\b\d+\s?%\s?(off|discount)", "a discount percentage"),
    (r"testimonial|customer logo|reference customer|pre-revenue|no customers",
     "a customer reference or a statement about their absence"),
    (r"consents once, not once per product|never means going back through onboarding"
     r"|without re-onboarding|no second consent",
     "the consent overclaim (consent is per connector — see README)"),
]


def check_content(page: str, src: str) -> None:
    text = re.sub(r"<[^>]+>", " ", src)
    for pattern, why in CONTENT_RULES:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            fail(page, f"content rule: {why} — found {m.group(0)!r}")


# --------------------------------------------------------------------- main

def main() -> int:
    if not PAGES:
        print("no pages found", file=sys.stderr)
        return 1

    for page in PAGES:
        with open(page, encoding="utf-8") as fh:
            src = fh.read()
        check_links(page, src)
        check_markup(page, src)
        check_a11y(page, src)
        check_content(page, src)

    print(f"checked {len(PAGES)} pages")
    if failures:
        print(f"\n{len(failures)} failure(s):\n")
        for f in failures:
            print(f"  {f}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
