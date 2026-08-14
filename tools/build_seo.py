#!/usr/bin/env python3
"""Apply per-page SEO metadata: titles, descriptions, canonicals, Open Graph,
Twitter cards and JSON-LD. Also regenerates sitemap.xml.

Titles and descriptions are hand-written per page and live here rather than
being derived from the copy — generated ones read like generated ones. Titles
are kept under 60 characters and descriptions between 110 and 160 so neither is
truncated in a result listing.

Run: python tools/build_seo.py
"""
from __future__ import annotations

import datetime
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://seqontrol.com"

# page -> (title, description, breadcrumb label or None)
META = {
    "index.html": (
        "SeQontrol - Microsoft 365 - Secure, Compliant, Confident",
        "One platform for Microsoft 365 security, compliance and configuration governance. "
        "Seven products on one Entra app, across every tenant you manage.",
        None),
    "platform.html": (
        "SeQontrol - Platform - Connect once, secure &amp; prove it all",
        "One tenancy model, one Entra app, one findings store and a tamper-evident audit trail "
        "— the layer every SeQontrol product is built on.",
        "Platform"),
    "licensing.html": (
        "SeQontrol - Licensing - Visibility, Governance, Automation",
        "Three licence flavours: Visibility, Governance and Automation. See what each one unlocks "
        "per product, and why scanning itself is never metered.",
        "Licensing"),
    "for-msps.html": (
        "SeQontrol - For MSPs - Every client or tenant, one screen",
        "Built provider-first: one console across every client tenant, pooled capacity, fleet "
        "benchmarking, and partner margin built into the plan.",
        "For MSPs"),
    "contact.html": (
        "SeQontrol - Contact - Talk to the people who built it",
        "Book a walkthrough, request a scoped assessment, or get a quote against your actual "
        "estate. You get a reply from the people who built it.",
        "Contact"),
    "about.html": (
        "SeQontrol - About - Why this exists",
        "Who builds SeQontrol, why a Microsoft 365 security and compliance platform was worth "
        "building, and what we will and will not claim about it.",
        "About"),
    "privacy.html": (
        "SeQontrol - Privacy - What we collect and why",
        "What SeQontrol collects from this website and from a connected tenant, why, how long it "
        "is kept, and who to contact about it.",
        "Privacy"),
    "terms.html": (
        "SeQontrol - Terms - The plain version",
        "The terms covering use of the SeQontrol website and, in outline, the service — written to "
        "be read rather than to be scrolled past.",
        "Terms"),
    "security.html": (
        "SeQontrol - Security - What we do with your access",
        "The access SeQontrol asks for, what it does with it, how the audit trail works, and how "
        "to report a vulnerability.",
        "Security"),
    "products/index.html": (
        "SeQontrol - Products - Each stands alone, all connect",
        "Seven products on one platform: ShareCare, SecurityPortal, CompliancePortal, "
        "PosturePortal, MailTrust, Dredd and ConditionalAccessPortal.",
        "Products"),
    "products/sharecare.html": (
        "SeQontrol - ShareCare - Who can reach what, and why",
        "See what Microsoft 365 over-shares, externally and to Copilot, across every tenant you "
        "manage — then remediate it safely, with a grace window and undo.",
        "ShareCare"),
    "products/securityportal.html": (
        "SeQontrol - SecurityPortal - Estate and public surface",
        "Continuous Microsoft 365 and Entra security posture, plus your external web and domain "
        "surface, with every finding tagged as control evidence.",
        "SecurityPortal"),
    "products/complianceportal.html": (
        "SeQontrol - CompliancePortal - Many frameworks, one crosswalk",
        "Turn the scans you already run into framework-mapped, audit-ready evidence for the "
        "technical controls on the platforms SeQontrol connects to.",
        "CompliancePortal"),
    "products/postureportal.html": (
        "SeQontrol - PosturePortal - The answer, not the raw scan",
        "The read-only board that aggregates findings, risk and coverage from every SeQontrol "
        "product into one per-tenant and fleet-wide view. Coming soon.",
        "PosturePortal"),
    "products/mailtrust.html": (
        "SeQontrol - MailTrust - SPF, DKIM, DMARC and more, enforced",
        "Take every domain from DMARC monitoring to safe enforcement: real sender inventory, a "
        "staged rollout, and the DNS records written in-product.",
        "MailTrust"),
    "products/dredd.html": (
        "SeQontrol - Dredd - Revert it, or ratify it",
        "Hold your approved Entra configuration as a versioned baseline, catch every unapproved "
        "change, and force the decision: revert it, or ratify it. Coming soon.",
        "Dredd"),
}

# ---------------------------------------------------------------- analytics
# Paste a single analytics snippet here and re-run to inject it into every
# page. Left empty, the site makes no third-party requests at all — which is
# the current state and a deliberate one.
#
# The site cannot be optimised while it is unmeasured, so this is meant to be
# filled in. Use something cookieless (Plausible, Fathom, GoatCounter) so the
# privacy notice stays short and no consent banner is needed. Example:
#
#   ANALYTICS = '<script defer data-domain="seqontrol.com" ' #               'src="https://plausible.io/js/script.js"></script>'
#
# If you add a script here, update privacy.html — it currently states that no
# third-party analytics run.
ANALYTICS = ""

PRODUCT_CATEGORY = "SecurityApplication"

ORG = """{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://seqontrol.com/#organization",
  "name": "SeQontrol",
  "url": "https://seqontrol.com/",
  "logo": "https://seqontrol.com/assets/seqontrol-symbol.png",
  "description": "A multi-tenant platform for Microsoft 365 security, compliance and configuration governance.",
  "parentOrganization": { "@type": "Organization", "name": "JeffOps", "url": "https://jeffops.com/" },
  "sameAs": ["https://jeffops.com/"]
}"""

WEBSITE = """{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://seqontrol.com/#website",
  "url": "https://seqontrol.com/",
  "name": "SeQontrol",
  "inLanguage": "en",
  "publisher": { "@id": "https://seqontrol.com/#organization" }
}"""


def canonical_for(rel: str) -> str:
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return f"{SITE}/{rel[:-len('index.html')]}"
    return f"{SITE}/{rel}"


def software_ld(name: str, desc: str, url: str) -> str:
    return f"""{{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "{name}",
  "url": "{url}",
  "applicationCategory": "{PRODUCT_CATEGORY}",
  "applicationSubCategory": "Microsoft 365 security and compliance",
  "operatingSystem": "Web-based",
  "description": "{desc}",
  "isPartOf": {{ "@type": "SoftwareApplication", "name": "SeQontrol", "url": "https://seqontrol.com/" }},
  "publisher": {{ "@id": "https://seqontrol.com/#organization" }}
}}"""


def breadcrumb_ld(label: str, url: str, in_products: bool) -> str:
    items = [('Home', SITE + '/')]
    if in_products and label != "Products":
        items.append(("Products", f"{SITE}/products/"))
    items.append((label, url))
    listing = ",\n    ".join(
        f'{{ "@type": "ListItem", "position": {i}, "name": "{n}", "item": "{u}" }}'
        for i, (n, u) in enumerate(items, 1))
    return f"""{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {listing}
  ]
}}"""


def strip_existing(src: str) -> str:
    """Remove the metadata this script owns, so it can be re-run idempotently."""
    src = re.sub(r'\n?<link rel="canonical"[^>]*>', "", src)
    src = re.sub(r'\n?<meta property="og:[^"]*"[^>]*>', "", src)
    src = re.sub(r'\n?<meta name="twitter:[^"]*"[^>]*>', "", src)
    src = re.sub(r'\n?<script type="application/ld\+json">[\s\S]*?</script>', "", src)
    return src


def apply(rel: str) -> None:
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    src = io.open(path, encoding="utf-8").read()
    title, desc, crumb = META[rel]
    url = canonical_for(rel)
    in_products = rel.startswith("products/")
    prefix = "../" if in_products else ""

    src = strip_existing(src)
    src = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", src, count=1, flags=re.S)
    src = re.sub(r'<meta name="description" content="[^"]*">',
                 f'<meta name="description" content="{desc}">', src, count=1)

    blocks = [
        f'<link rel="canonical" href="{url}">',
        f'<meta property="og:type" content="{"website" if rel == "index.html" else "article"}">',
        f'<meta property="og:site_name" content="SeQontrol">',
        f'<meta property="og:locale" content="en">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{SITE}/assets/og-card.png">',
        f'<meta property="og:image:width" content="1200">',
        f'<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="SeQontrol — secure, compliant, confident">',
        f'<meta name="twitter:card" content="summary_large_image">',
    ]

    if ANALYTICS:
        blocks.append(ANALYTICS)

    ld = []
    if rel == "index.html":
        ld += [ORG, WEBSITE]
    if in_products and rel != "products/index.html":
        ld.append(software_ld(crumb, desc, url))
    if crumb:
        ld.append(breadcrumb_ld(crumb, url, in_products))
    for block in ld:
        blocks.append('<script type="application/ld+json">\n' + block + "\n</script>")

    marker = f'<link rel="stylesheet" href="{prefix}css/styles.css">'
    assert marker in src, rel
    src = src.replace(marker, "\n".join(blocks) + "\n" + marker, 1)
    io.open(path, "w", encoding="utf-8").write(src)


def sitemap() -> None:
    today = datetime.date.today().isoformat()
    rows = []
    for rel, (_, _, _) in META.items():
        url = canonical_for(rel)
        priority = "1.0" if rel == "index.html" else (
            "0.9" if rel in ("products/index.html", "licensing.html") else "0.8")
        rows.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{today}</lastmod>\n"
                    f"    <changefreq>monthly</changefreq>\n    <priority>{priority}</priority>\n  </url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    io.open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(xml)


if __name__ == "__main__":
    for rel in META:
        apply(rel)
    sitemap()
    print(f"metadata applied to {len(META)} pages; sitemap regenerated")
