#!/usr/bin/env python3
"""Build the per-framework coverage section on the CompliancePortal page.

The numbers are read out of the compliance framework packs, not estimated:
each pack declares its controls with `Automatable: true|false`, which the
domain defines as "expected to have a test/selector; otherwise it is
manual-attestation-only". That is exactly the split a buyer needs — what can be
proved by inspecting configuration, and what still needs a human to attest.

Frameworks are grouped into families because 24 tabs is not a tab set. Every
framework still gets its own row with its own numbers.

CIS packs are excluded deliberately (site-wide rule, see README).

Regenerate the counts with tools/framework_stats.py against the platform repo;
they are pasted here so the site builds without the platform checkout.

Run: python tools/build_frameworks.py
"""
from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "products", "complianceportal.html")
START, END = "<!-- frameworks:start -->", "<!-- frameworks:end -->"

# (family key, tab label, blurb, [(framework, controls, automatable), ...])
FAMILIES = [
    ("governance", "Security and governance",
     "The general-purpose control sets most buyers are assessed against first.",
     [("SOC 2 (2017 Trust Services Criteria)", 61, 20),
      ("ISO/IEC 27001:2022", 93, 42),
      ("ISO/IEC 27002:2022", 93, 42),
      ("NIST CSF 2.0", 106, 16),
      ("CSA STAR (Cloud Controls Matrix)", 197, 39)]),

    ("privacy", "Privacy and data protection",
     "Privacy regimes are mostly process, lawful basis and record-keeping — which is why the "
     "automatable share here is the smallest on the site, and why we say so rather than implying "
     "a product can make you GDPR-compliant.",
     [("GDPR", 91, 2),
      ("ISO/IEC 27701", 49, 2)]),

    ("sector", "Sector regulation",
     "Where the regime is written for a specific industry and the technical controls are explicit.",
     [("PCI DSS 4.0", 313, 87),
      ("HIPAA Security Rule", 97, 11),
      ("NEN 7510 (Dutch healthcare)", 93, 42),
      ("NEN 7513 (Dutch healthcare logging)", 3, 3)]),

    ("regimes", "EU and national regimes",
     "Obligations set by law or by a national scheme, usually stated as outcomes rather than "
     "configuration — so the automatable share is low by nature.",
     [("NIS 2", 44, 7),
      ("DORA", 29, 4),
      ("Essential Eight (ACSC)", 24, 12),
      ("Cyber Essentials", 4, 4)]),

    ("government", "Government and defence",
     "Large baselines with deep technical detail. FedRAMP uses NIST SP 800-53 Rev 5 control "
     "identifiers; 800-53 is not carried as a separate pack.",
     [("FedRAMP (Rev 5 baselines)", 410, 72),
      ("CMMC 2.0", 126, 72),
      ("DISA STIG", 226, 17)]),

    ("technical", "Technical baselines",
     "Configuration and threat catalogues rather than certification schemes. They are here because "
     "findings map onto them, not because anyone audits you against ATT&CK.",
     [("MITRE ATT&CK", 691, 23),
      ("OWASP", 278, 6),
      ("CISA SCuBA (Microsoft 365)", 104, 25),
      ("ISO/IEC 27017 (cloud)", 101, 49),
      ("Microsoft Cloud Security Benchmark", 86, 21)]),

    ("first-party", "Our own",
     "A first-party set covering the things the standard frameworks under-specify for a Microsoft "
     "365 estate. Every control in it is automatable — it was written against what the platform "
     "can actually observe.",
     [("JeffOps Beyond", 12, 12)]),
]

TONE = "var(--t-compliance)"


def rows(items):
    out = []
    for name, total, auto in items:
        manual = total - auto
        pct = round(auto * 100 / total) if total else 0
        out.append(
            f'              <tr><th scope="row">{name}</th>'
            f"<td>{total}</td><td>{auto} <span class=\"dim\">({pct}%)</span></td>"
            f"<td>{manual}</td></tr>")
    return "\n".join(out)


def build() -> str:
    tabs, panels = [], []
    for i, (key, label, blurb, items) in enumerate(FAMILIES):
        tabs.append(
            f'          <button type="button" role="tab" id="tab-{key}"'
            f' aria-controls="panel-{key}" aria-selected="{"true" if i == 0 else "false"}"'
            f' tabindex="{"0" if i == 0 else "-1"}" style="--tone: {TONE}">{label}</button>')

        total = sum(t for _, t, _ in items)
        auto = sum(a for _, _, a in items)
        panels.append(f"""      <div class="product-licence" role="tabpanel" id="panel-{key}"
           aria-labelledby="tab-{key}" tabindex="0" style="--tone: {TONE}">
        <header>
          <h3>{label}</h3>
          <p class="counted">{len(items)} framework{"s" if len(items) != 1 else ""} &middot;
            {total} controls &middot; {auto} provable from configuration</p>
        </header>
        <p class="after" style="margin-top:0">{blurb}</p>
        <div class="table-wrap table-scroll" tabindex="0" role="group" aria-label="{label} coverage">
          <table class="matrix">
            <thead>
              <tr>
                <th scope="col">Framework</th>
                <th scope="col">Controls</th>
                <th scope="col">Provable from<br>configuration</th>
                <th scope="col">Needs<br>attestation</th>
              </tr>
            </thead>
            <tbody>
{rows(items)}
            </tbody>
          </table>
        </div>
      </div>""")

    grand_total = sum(t for _, _, _, items in FAMILIES for _, t, _ in items)
    grand_auto = sum(a for _, _, _, items in FAMILIES for _, _, a in items)
    count = sum(len(items) for _, _, _, items in FAMILIES)

    return f"""{START}
  <section id="coverage">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Coverage</span>
        <h2>What we can prove, framework by framework</h2>
        <p>{count} frameworks, {grand_total:,} controls between them. <strong>{grand_auto:,} of those
          are provable by inspecting configuration</strong> — the rest need a human to attest, and no
          amount of scanning changes that.</p>
        <p>Publishing the split is the point. A control that cannot be automated is not a gap we are
          hiding; it is the part of your programme that was always going to be yours.</p>
      </div>

      <div data-tabs class="tabs-v">
        <div class="tablist" role="tablist" aria-label="Framework families">
{chr(10).join(tabs)}
        </div>
{chr(10).join(panels)}
      </div>

      <div class="note scope">
        <h3>How to read these numbers</h3>
        <p><strong>&ldquo;Provable from configuration&rdquo;</strong> means the control is assessed by
          inspecting a connected platform, rather than by someone signing a statement. It is a property
          of the control, not a promise that every one of them is implemented today — coverage of that
          set is high but not complete, and the product reports per-control status rather than a
          headline percentage.</p>
        <p class="mb0"><strong>A low share is not a weakness in the framework or in us.</strong> GDPR
          sits at 2 of 91 because GDPR is mostly lawful basis, records and process. Reporting it as
          anything else would be the fabricated automation we refuse to ship.</p>
      </div>
    </div>
  </section>

{END}
"""


def main() -> None:
    src = io.open(PAGE, encoding="utf-8").read()
    section = build()
    if START in src and END in src:
        head, rest = src.split(START, 1)
        _, tail = rest.split(END, 1)
        src = head + section.rstrip("\n") + tail
    else:
        anchor = '  <section class="cta">'
        assert anchor in src
        src = src.replace(anchor, section + anchor, 1)
    io.open(PAGE, "w", encoding="utf-8").write(src)
    print(f"framework section written: {len(FAMILIES)} families, "
          f"{sum(len(i) for _, _, _, i in FAMILIES)} frameworks")


if __name__ == "__main__":
    main()
