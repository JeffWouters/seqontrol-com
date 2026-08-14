# SeQontrol.com

Static marketing site for the SeQontrol platform. Hand-written HTML/CSS/JS — no build step, no
package manager, no external network requests at runtime (no CDN, no fonts, no analytics).

Open `index.html` in a browser, or serve the folder:

```powershell
python -m http.server 8080
```

## Layout

```
index.html          Home — pitch, products, platform, licensing preview, MSP, honesty section
platform.html       The shared platform layer + the trust/security answers
licensing.html      License flavours, metering rules, and a per-product capability matrix (no prices)
for-msps.html       Provider model, commercials, land-and-expand motion
contact.html        Contact + a form that composes a mailto (no backend, nothing submitted)
products/
  index.html        Product overview + at-a-glance comparison table
  sharecare.html    ShareCare
  securityportal.html
  complianceportal.html
  postureportal.html
  mailtrust.html
  dredd.html
css/styles.css      Single stylesheet
js/site.js          Mobile nav, current-page marker, footer year, tabs
assets/             Logo extractions, on-dark variants, icons, OG card
favicon.ico         Multi-resolution icon at the root, where browsers look for it
tools/
  verify.py         Pre-deploy checks — run by CI on every push
  build_licensing.py  Regenerates the per-product licence tabs and matrices
  extract_logo.py     Re-keys the supplied logo JPEG into transparent PNGs
  make_logo_variants.py  On-dark variants, sized copies, OG card
  make_icons.py       favicon.ico and the PNG icon set
.github/workflows/deploy.yml   Verify, then publish to GitHub Pages
CNAME, .nojekyll, robots.txt, sitemap.xml
```

## Hosting — GitHub Pages

The repository root *is* the site: no build step, so the whole checkout is published as-is.
`.github/workflows/deploy.yml` runs `tools/verify.py` first and only deploys if it passes — pull
requests are verified but never published.

### One-time setup

> **The repository must be public unless you pay for GitHub.** GitHub Pages on a *private* repository
> requires Pro, Team or Enterprise. On the free plan, enabling Pages on a private repo fails with
> `HTTP 422: Your current plan does not support GitHub Pages for this repository`, and the deploy job
> dies at `configure-pages`. Repository visibility and *site* visibility are separate things: a public
> repo means the source is readable, which for a hand-written marketing site is mostly the same content
> the site already serves — but **read the "What goes public" note below before flipping it.**

```bash
git init -b main
git add .
git commit -m "SeQontrol.com: initial site"
gh repo create seqontrol-com --public --source=. --remote=origin --push
```

The workflow sets `enablement: true` on `configure-pages`, so Pages is switched on automatically by the
first successful run — no visit to Settings needed. To do it by hand instead:
**Settings → Pages → Build and deployment → Source: GitHub Actions.**

### What goes public

A public repository publishes **this README** alongside the site, and this file is candid by design: it
records the ShareCare catalog mismatch, that scan cadence is sold but not yet enforced, and pointers to
internal pricing material. None of that is secret, but none of it is written for customers either.
Before making the repository public, either trim the "Things to change before it goes live" section and
the internal cross-references, or keep the repo private and pay for Pages.

### Custom domain

`CNAME` contains `seqontrol.com`, which is also what `sitemap.xml`, `robots.txt` and the `og:image` URL
assume. Point the domain at GitHub:

Eight apex records — four A and four AAAA — plus one CNAME for `www`. Each value below is literal and
complete; enter them exactly as written, one record per row.

| Record | Name | Value |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |
| CNAME | `www` | `<owner>.github.io` |

The AAAA values differ only in the fourth group (`8000`, `8001`, `8002`, `8003`); `::` is IPv6's own
notation for a run of zero groups and is part of the address, not an abbreviation of mine.

**Check these against GitHub's current documentation before you commit them.** They are GitHub's
published Pages addresses and have been stable for years, but hosting IPs are not a promise, and a stale
A record is a site that silently stops resolving. Search GitHub Docs for "Managing a custom domain for
your GitHub Pages site".

Then tick **Enforce HTTPS** in Settings → Pages once the certificate is issued (can take a few minutes
to an hour). If your DNS provider supports ALIAS/ANAME at the apex, use that instead of the A and AAAA
records — one record that follows GitHub's changes beats eight that do not.

**Not using a custom domain?** Delete `CNAME`, and update the absolute URLs in `sitemap.xml`,
`robots.txt` and the `og:image` meta tag to your Pages URL. Every internal link in the site is
*relative* (no leading `/` anywhere — `tools/verify.py` would flag one), so a project site served from
`https://<owner>.github.io/<repo>/` works without further changes. Those three absolute URLs are the
only place the domain is hard-coded.

### Notes

- `.nojekyll` stops GitHub running the content through Jekyll. Nothing here starts with an underscore
  today, but the file costs nothing and removes a whole class of surprise.
- `tools/` and `.github/` are uploaded with the site. They are a few KB, are never executed by Pages,
  and keeping them in the artifact means the deployed tree matches the repository exactly.
- The site makes no external requests at runtime, so there is no CDN, font host or analytics endpoint
  to allow-list, and nothing to break when a third party changes.

## Brand and theme

- **SeQontrol** is the platform/product brand. **JeffOps** is the company behind it — the footer and
  copy say so ("Built by JeffOps", "SeQontrol is a JeffOps platform"). Every one of those mentions links
  to `https://jeffops.com` and is coloured in JeffOps' own cyan `#00d9ff` (its `--cyan` token), not the
  SeQontrol purple — the two brands stay visually distinct. The rule matches on the href
  (`a[href^="https://jeffops.com"]`), so a new mention is styled automatically; there is no class to
  remember. Reserve that cyan for JeffOps links and nothing else.
- **The accent is the SeQontrol purple, not the platform shell's blue.** `#6b4de2` is sampled straight
  from the logo artwork (the most common fully-opaque violet in the symbol). The *neutrals* still come
  from the shell's `theme.css` dark variant, so the site and the product UI share a substrate:

  | Token | Value | Role |
  |---|---|---|
  | `--bg` | `#0b0f17` | page background |
  | `--surface` | `#0f172a` | cards, panels |
  | `--border` | `#334155` | borders |
  | `--text` | `#e5e7eb` | body text |
  | `--muted` | `#94a3b8` | secondary text |
  | `--brand` | `#6b4de2` | **the logo purple** — solid fills, primary buttons |
  | `--brand-dark` | `#7658e6` | hover (lifted, not darkened — the page is dark) |
  | `--brand-deep` | `#5b40c9` | pressed / heavier borders |
  | `--accent` | `#a78bfa` | links, eyebrows, labels |
  | `--accent-soft` | `#c4b5fd` | link hover, inline code |
  | `--focus` | `#a78bfa` | focus ring |
  | `--ok` / `--warn` / `--danger` | `#4ade80` / `#fbbf24` / `#f87171` | status |
  | `--jeffops` | `#00d9ff` | **JeffOps' brand cyan** — links back to the parent company only |

  **Why two purples.** White on `--brand` is 5.55:1, so it carries buttons. But `--brand` *as text* on
  `--bg` is only 3.46:1 — below AA — so links and labels use the lighter `--accent` at 7.05:1. Do not
  swap one for the other. `--brand-dark` is a deliberate 4.87:1 with white; going brighter for hover
  drops it under 4.5.

- **Dark only.** There is deliberately no light theme and no `prefers-color-scheme` block.
- Product accent tones live in `:root` as `--t-sharecare`, `--t-security`, `--t-compliance`,
  `--t-posture`, `--t-mailtrust`, `--t-dredd`, `--t-soon`. A card picks one with
  `style="--tone: var(--t-dredd)"`. `--t-compliance` was moved from `#a78bfa` to `#c084fc` when the
  brand went purple — it had become the exact same violet as `--accent`.

## Logo assets

The supplied logo arrived flattened to JPEG, so the original alpha was gone and the transparency
checkerboard (30px cells) was baked in as real pixels. `tools/extract_logo.py` re-keys it:

- Measuring the file settles the ambiguity — the interior of the magnifying glass alternates
  241/252 down its centre, i.e. the checkerboard shows *through* it. The lens is a hole, not a white
  fill, and so are the letter counters. Keying is therefore colour-based (light + neutral = background);
  a flood fill from the border would have wrongly kept those areas opaque.
- Edge pixels are un-premultiplied — the true ink colour is recovered from its blend with the white
  background — so there is no pale halo on a dark page.

| Asset | What it is |
|---|---|
| `seqontrol-symbol.png` | Faithful extraction of the cloud + shield + magnifier, original colours |
| `seqontrol-wordmark.png` | Faithful extraction of "SeQontrol" |
| `seqontrol-tagline.png` | Faithful extraction of "Secure. Compliant. Confident." |
| `*-on-dark.png` | Site variants — see below |
| `seqontrol-symbol-on-dark-{64,128}.png`, `seqontrol-wordmark-on-dark-320.png`, `seqontrol-tagline-on-dark-320.png` | Sized copies, so a 32px slot does not pull a 644px image |
| `../favicon.ico` | Multi-resolution icon (16→256) at the site root, where browsers look for it |
| `favicon-32.png`, `apple-touch-icon.png`, `icon-512.png` | The same treatment as PNG |
| `og-card.png` | 1200×630 social card, lockup on `--bg` |

**Why the on-dark variants exist.** The delivered artwork is drawn for a light page: the wordmark and
the shield are navy `#1a1b4b`, which is all but invisible on `--bg` `#0b0f17`. The variants keep the
purple exactly as supplied and lift only the navy to `--text` `#e5e7eb`, interpolating between the two
brand colours so anti-aliasing survives. **The site uses the on-dark variants everywhere**; the faithful
extractions are kept as the source of truth for print, light backgrounds and hand-off.

If you would rather the site carried the artwork unaltered, swap the `-on-dark` filenames back to the
plain ones in the header/footer — the wordmark will be very hard to read.

**The icons match the site lockup: white shield, purple cloud, ring, magnifier and check**, on a
transparent background. The delivered artwork paints the shield navy because it is drawn for a white
page; the icons lift it to pure white the same way the header lockup does, and leave every purple pixel
untouched (interpolating between the two brand colours, so the anti-aliased rim stays clean).

The catch is the mirror of the old one: a white shield disappears on a **light** tab strip. So the navy
original is emitted as `favicon-32-light.png` and linked behind `media="(prefers-color-scheme: light)"`.
Browsers honouring that swap to it; everything else falls back to `favicon.ico`, which is the white-shield
version. Do not "simplify" by deleting one of the two links — that is what the pair is for.

`apple-touch-icon.png` is opaque on a **dark** tile (`#0b0f17`): iOS ignores alpha and composites
home-screen icons onto black, and a white shield needs a dark ground anyway. Regenerate everything with
`tools/make_icons.py`.

## Accessibility

Audited and fixed; re-check with `tools/verify.py`, which parses every page and fails on missing
`lang`, multiple or missing `h1`, skipped heading levels, duplicate ids, images without `alt`,
unlabelled form fields, missing landmarks, `th` without `scope`, unreachable scroll containers and
vague link text. It currently reports clean across all 12 pages — **keep it that way when editing.**

What that involved, and why, so it does not get undone:

- **Contrast.** Every text token clears WCAG AA (4.5:1) against all four surfaces it can sit on; the
  lowest is `--dim` at 4.79:1. `--dim` was `#6b7490`, which measured 3.71–4.22:1 and carried hints,
  captions and the footer line — all small text. It was lifted at the same hue to `#7c87a3`. White on
  `--brand` is 5.55:1 and on `--brand-dark` 4.87:1, which is why hover lifts only that far.
  `::placeholder` is set explicitly because the browser default fails here.
- **Heading order.** No level is skipped anywhere. Callout and aside headings are `h3`, footer column
  headings are `h2` (they follow the page's last section heading, so `h4` would skip), and the hero's
  step panel has a visually hidden `h2` so its steps can be `h3`. Callout headings are styled by
  container (`.note h2, .note h3`) rather than by element, so the level can follow document structure
  without changing how anything looks — **do not restyle these by element.**
- **Landmarks.** `header` / `nav[aria-label="Main"]` / `main` / `footer` on every page, plus `aside`
  where there is a complementary column.
- **Tables.** Column headers carry `scope="col"`, matrix row labels are `th scope="row"`, and group
  rows are `th scope="colgroup"`. `thead th` and `tbody th` are styled separately so row headers do not
  inherit the uppercase column-header treatment.
- **Scrollable regions.** Every `.table-scroll` has `tabindex="0"` — without it a keyboard user cannot
  scroll a wide table at all. The generated matrices also carry `role="group"` and a label.
- **Tabs** implement the full pattern: roles, `aria-selected`, roving `tabindex`, arrow/Home/End keys,
  and panels that stay reachable. They degrade to stacked content without JavaScript.
- **Ticks and dashes** are `aria-hidden` glyphs paired with `.sr-only` "Included" / "Not included", so
  the matrices are not read as a grid of meaningless symbols.
- **Motion** is disabled under `prefers-reduced-motion`. **Focus** is never removed; the ring is
  `--focus` at 6.32:1.

## Content rules baked into the copy

- **Be exact about consent and onboarding.** The site previously claimed "the customer consents once, not
  once per product, and adding a product never means going back through onboarding". Verified against the
  code, that overclaimed. What is true: **one Entra app** for the whole platform, declaring the union of
  every product's Graph permissions, so the admin consents once and **enabling a product never asks for new
  permissions**. What is not: consent is recorded per connector, and connectors are per (tenant, product) —
  so enabling a product still needs an administrator to activate its connector. It is a cheap trip (Entra
  already holds the grant, no new prompt) but it is a step, it needs Manage authorization, and the product
  does not run until it happens. The adjacent planes do **not** ride the Graph consent: Exchange admin needs
  a certificate and its own role, Power Platform a pre-registered service principal, Azure/Log Analytics a
  workspace and reader role, DNS its own OAuth2 flow per provider. Write-back is a second consent round trip.
  Only ShareCare, SecurityPortal, CompliancePortal and Dredd are Graph connector products. `platform.html`
  carries the full step-by-step table; do not compress it back into "connect once".
- **Security stands above compliance.** The key principle, stated in full in the `#principle` section on
  the home page (directly under the hero), reinforced in the CompliancePortal scope area and on the
  platform trust list. The argument: a compliance control can be waived, which turns the report green
  without changing the estate — so the security finding is treated as the fact and compliance as an
  interpretation laid over it. A waived finding stays visible and scored, and its exception expires.
  Do not let later copy imply compliance is the goal or that a green report equals a secure estate.
- **The three portals are grouped, with no bundle name.** The group headline is the agreed phrase:
  *"Three products. One platform. Zero compromise."* — used on `index.html` and `products/index.html`.
- **CompliancePortal scope.** Every mention says it covers the *technical implementation* of controls on
  the platforms SeQontrol supports — not a whole-company compliance programme, and not an audit opinion.
  The full carve-out (policies, HR process, physical security, vendor management, anything on an
  unsupported platform) is a prominent box near the top of `products/complianceportal.html`.
- **No CIS framework references anywhere**, per instruction. Named frameworks are limited to SOC 2,
  ISO 27001, NIST CSF / 800-53, PCI-DSS, HIPAA, GDPR, NIS 2 and Essential Eight, plus "a first-party
  framework of our own". Google Cloud and AWS coverage is described as read-only connectors without
  naming a benchmark.
- **No customer references of any kind.** No logos, testimonials, counts, revenue or traction claims —
  and no statements about their *absence* either. Where trust needs building, the site does it with
  concrete product limits (which planes are read-only, what Dredd has not shipped, Microsoft-first
  scope) rather than by discussing the customer base. Keep it that way when editing.
- **No prices anywhere.** No figures, no discount percentages, no worked bills. `licensing.html`
  describes the flavours, what each unlocks, the metering principles, and **what each product counts**
  (users / domains / tenants / configuration scope) — the commercial terms (platform minimum, suite
  discount, annual commit, per-tenant floor as greater-of) are named without numbers. Everything is
  quoted against the buyer's actual estate.
- **The licensing matrices are a commitment, so keep them true to the catalog.** The per-product tables
  in `licensing.html` were built from the seeded entitlement catalog (Billing's `CatalogSeeder.cs`), not
  invented: ShareCare and MailTrust ride the Visibility/Governance/Automation ladder, CompliancePortal
  is banded by frameworks in scope with retention and attestation moving between bands, and
  SecurityPortal has a single tier because it is scan-only. Rebuild them with `python tools/build_licensing.py`
  rather than hand-editing 100-odd cells. One row states the *intended* ladder rather than the seeded
  one — see the ShareCare caveat below.
- **The "What each licence includes" section is a tab set**, one tab per product, each carrying the
  technologies covered, the metering unit, and the capability matrix. It is **progressive**: the markup
  ships with the tab strip hidden by CSS and every panel visible, and `site.js` adds `data-tabs-ready`
  to flip it into tabs. With JavaScript off the whole thing renders stacked and nothing is lost — do not
  "tidy" this by hiding panels in CSS. Tabs are keyboard-driven (arrows, Home/End) and deep-linkable:
  `licensing.html#mailtrust` opens that product.
- **Technology lists are per product** and use `.tag.on` for supported, `.tag.off` (dashed) for roadmap
  or manual-only — e.g. ShareCare's Google Workspace, MailTrust's unsupported DNS providers. Keep the
  roadmap items visibly distinct rather than dropping them; that distinction is the honesty.
- **Availability.** Available now: ShareCare, SecurityPortal, CompliancePortal, MailTrust.
  **Coming soon:** PosturePortal, Dredd, ConditionalAccessPortal. The first two keep full pages carrying
  a "Coming soon" badge in the hero, the aside status, the product cards, the comparison table and every
  cross-page mention; their CTAs ask to be contacted when the product lands rather than offering a trial
  or assessment. CAP has no page.
- **Roadmap is labelled as roadmap.** Read-only planes, the Dredd snapshot-baselining gap and the
  scan-only nature of SecurityPortal are stated on their product pages.

## Things to change before it goes live

1. **Contact address.** Every mailto points at `jeff@jeffops.com`. Swap it for a product address
   (e.g. `hello@seqontrol.com`) if you want the product identity separate from the personal one.
2. **ShareCare's Automation rung.** The site — including the licensing matrix — describes the intended
   ladder, with remediation write-back at Automation. In the seeded catalog today
   `sharecare.autoremediate` is bundled into *Governance*, so Automation currently grants an identical
   set. This is the one cell in the matrices that does not match the catalog. Reconcile the catalog (move
   the flag up) or move that tick down to Governance.
3. **Scan cadence is sold but not yet enforced.** The licensing page now gates *scheduled* scan frequency
   by rung (daily / every 6 hours / hourly), with on-demand scans unlimited on every rung. **No
   entitlement gates the scheduler today.** Shipping this copy before the gate exists is precisely the
   "checkbox an operator can sell that nothing could honour" failure `CatalogSeeder.cs` warns about — so
   either add the gate first or pull those rows. Suggested shape: a numeric
   `<code>.schedule.min_interval_minutes` feature (1440 / 360 / 60) read by each product's scheduler,
   with the on-demand path exempt by design. Rationale is recorded in `Z:\repos\pricing.md`
   ("Margin protection — four decisions").
4. **Availability dates.** "Coming soon" carries no date anywhere. Add one if you have one.
4. **A real form endpoint**, if you want submissions rather than a mailto hand-off.
5. **Open Graph image** — `og:title`/`og:description` are set on the home page; no image is referenced.
6. **CNAME / deploy** — not included. Add whatever your host needs.

The commercial model behind the copy is `Z:\repos\pricing.md`; the license flavours and feature
groupings were cross-checked against `CatalogSeeder.cs` in the Billing service.
