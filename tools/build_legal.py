#!/usr/bin/env python3
"""Generate the trust pages: privacy, terms and security.

Chrome (head, header, footer) is lifted from an existing page so these never
drift from the rest of the site. Only the <main> differs.

FACTS THIS SCRIPT DOES NOT KNOW — fill them in before relying on these pages:
  · the legal entity name, registered address and company/VAT number
  · where product data is hosted (region) and the subprocessor list
  · retention periods for product data, if they differ from what is stated
Everything else here is either verifiable from the platform code or is a
commitment the site already makes elsewhere. These are solid drafts, not
lawyer-reviewed documents; have them reviewed before they carry weight.

Run: python tools/build_legal.py
"""
from __future__ import annotations

import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "contact.html")   # chrome donor

OPERATOR = 'JeffOps'
CONTACT = 'jeff@jeffops.com'

PAGES = {
    "vs-grc-platforms.html": dict(
        title="SeQontrol - vs GRC platforms - Where each one wins",
        desc="How SeQontrol compares with questionnaire-first GRC platforms on Microsoft 365 control "
             "evidence, and where those platforms are the better choice.",
        eyebrow="Comparison",
        h1="SeQontrol and the GRC platforms",
        lede="Vanta, Drata, Secureframe and their peers do something we deliberately do not. Here is "
             "the honest split, including the cases where you should pick them.",
        body="""
      <h2>What they are better at</h2>
      <p>Said first, because it is true. Automated GRC platforms have spent years on the parts of
        compliance that are workflow: policy management, employee onboarding and training records,
        vendor reviews, questionnaire handling, and — importantly — established relationships with
        auditors who already know their evidence format.</p>
      <p><strong>If your problem is "we need to run a SOC 2 programme and we have no process yet",
        buy one of those.</strong> We are not a substitute for it and pretending otherwise would waste
        your money.</p>

      <h2>What we are better at</h2>
      <p>Proving the technical controls, at control granularity, on a Microsoft 365 estate.</p>
      <p>A GRC platform generally establishes that a control exists by asking you, or by a shallow
        integration check. SeQontrol establishes it by scanning: external sharing containment,
        Conditional Access coverage, MFA enforcement including the exclusions, application permissions
        that are actually unused, email authentication posture. The finding and the evidence are the
        same record, and you can re-run it.</p>
      <p>The second difference is fleet economics. If you manage many client tenants, per-tenant GRC
        licensing prices the work out of existence. This platform was built provider-first.</p>

      <h2>They are often complementary</h2>
      <p>The common shape: a GRC platform runs the programme, and SeQontrol feeds it the technical
        control evidence it cannot produce itself. If that is your situation, say so on the first call
        and we will scope for it rather than argue for replacement.</p>

      <div class="note scope">
        <h2>What we will not claim</h2>
        <p class="mb0">We do not give you an audit opinion, an auditor relationship, or the process
          half of a compliance programme. <a href="limits.html">The full list of what we do not do</a>
          is published, and this is on it.</p>
      </div>
"""),

    "vs-secure-score.html": dict(
        title="SeQontrol - vs Secure Score - What native tooling misses",
        desc="How SeQontrol differs from Microsoft Secure Score and native Microsoft 365 reporting, "
             "and when the native tools are enough.",
        eyebrow="Comparison",
        h1="SeQontrol and Microsoft's native tooling",
        lede="Secure Score, Purview and SharePoint Advanced Management already ship with your "
             "licence. Here is what they cover, and the specific gaps that made this worth building.",
        body="""
      <h2>When native is enough</h2>
      <p>One tenant, one administrator, no external reporting obligation and no Copilot rollout
        pending: Secure Score plus the native reports will tell you most of what you need, and they
        cost nothing extra. <strong>Start there.</strong> A tool you already own and will actually
        check beats one you buy and ignore.</p>

      <h2>The four gaps</h2>
      <ul>
        <li><strong>One number, not a control.</strong> Secure Score gives a figure per tenant. It
          does not tell an auditor which control held, or produce evidence that it held over a
          period.</li>
        <li><strong>Per workload, per tenant.</strong> Sharing sits in one report, identity in
          another, mail flow in a third — and none of them span the clients a provider manages.</li>
        <li><strong>No outside-in view.</strong> Nothing native scans your public web and domain
          surface, which is where a good deal of exposure actually lives.</li>
        <li><strong>Reporting, not remediation, and no memory.</strong> Native reports show a state.
          They do not stage a fix with a grace window and an undo, and they do not keep a
          tamper-evident record of what changed and who approved it.</li>
      </ul>

      <h2>The honest overlap</h2>
      <p>Microsoft improves this surface constantly, and some of what SeQontrol does today will be
        native eventually. The parts we expect to keep mattering are the ones native tooling is
        structurally unlikely to build: cross-tenant fleet economics, and turning a security finding
        into portable compliance evidence.</p>
      <p>We license per estate, so if Microsoft ships something that replaces a piece of this, you
        are free to stop paying for that piece.</p>
"""),

    "exposure-report.html": dict(
        title="SeQontrol - Free report - What Copilot can reach",
        desc="A free, scoped scan of your Microsoft 365 tenant: what is shared externally, what is "
             "over-shared internally, and exactly what to revoke first.",
        eyebrow="Free assessment",
        h1="See what Copilot can reach in your tenant",
        lede="A scoped scan, a scored list of what is actually exposed, and a remediation order. "
             "Free, read-only, and useful whether or not you buy anything afterwards.",
        body="""
      <h2>What you get back</h2>
      <ul>
        <li><strong>Every external share, listed and scored</strong> — anonymous links, links that
          allow editing, guests who have not signed in for months, and the resources each can reach.</li>
        <li><strong>The internal over-exposure</strong> — organisation-wide links and company-wide
          groups such as "Everyone except external users". These are the patterns that make Copilot
          surface far more than anyone intended, and they are invisible in native reports.</li>
        <li><strong>Risky grants beyond files</strong> — over-permissioned OAuth applications, and
          mail forwarding to domains nobody in your organisation owns.</li>
        <li><strong>A remediation order</strong> — not a CSV of everything, but what to revoke first,
          ranked by sensitivity and blast radius, with the ones that are safe to automate marked.</li>
      </ul>

      <h2>What it costs, and what it does not</h2>
      <p>Nothing. No card, no trial that converts into a subscription, no contract. If the report
        tells you your estate is in good shape, that is a perfectly good outcome and we will say so.</p>
      <p><strong>The catch, stated plainly:</strong> we do this because a scored list of your own
        exposure is a better argument for the product than any page on this site. If it is not
        compelling, you will not buy, and that is fair.</p>

      <h2>What it touches</h2>
      <ul>
        <li><strong>Read-only, app-only.</strong> Application permissions through Microsoft Graph — not
          a user's session, no agent to install, no disruption to anybody working.</li>
        <li><strong>Metadata, not content.</strong> We read who can reach what. We do not read your
          documents or your mail.</li>
        <li><strong>Nothing is changed.</strong> Remediation needs a separate consent that this
          assessment does not ask for and does not use.</li>
        <li><strong>You can revoke it the moment the report lands</strong>, and the findings you have
          been given remain yours.</li>
      </ul>

      <h2>How it runs</h2>
      <ol>
        <li>You tell us the tenant and roughly how big it is.</li>
        <li>We agree the scope and a date before anything connects.</li>
        <li>An administrator grants read-only consent to one Entra application.</li>
        <li>The crawl runs. Large estates are swept in stages so nothing is throttled.</li>
        <li>You get the report, and a walkthrough of it if you want one.</li>
      </ol>

      <h2>Managing many tenants?</h2>
      <p>The provider version ranks your worst clients against each other, so the conversation you
        have with them is specific rather than general.
        <a href="for-msps.html">More on the provider model</a>.</p>

      <div class="note plain">
        <h2>Ask for the report</h2>
        <p>Mail <a href="mailto:{contact}?subject=Free%20exposure%20report">{contact}</a> with your
          tenant size, or use <a href="contact.html">the contact form</a> and pick
          <em>"A scoped assessment (Copilot oversharing)"</em>. A person replies — usually the same
          working day.</p>
        <p class="mb0"><a class="btn btn-primary" href="contact.html">Request the report</a></p>
      </div>
"""),

    "limits.html": dict(
        title="SeQontrol - Limits - What this does not do",
        desc="The planes that detect but cannot yet fix, where the Microsoft-first scope ends, and "
             "why readiness is not an audit opinion. Written down before you ask.",
        eyebrow="Straight answers",
        h1="What SeQontrol does not do",
        lede="Every limit worth knowing, in one place — including the ones a sales call would "
             "normally leave until month two.",
        body="""
      <p>Security software is bought on trust, and trust does not survive a discovered exaggeration.
        So here is the unflattering version, in one place, rather than scattered through the pages
        that are trying to persuade you.</p>

<div class="note honest">
        <h2>"Connect once" means the permission grant, not zero-touch</h2>
        <p class="mb0">One Entra app covers every product, so your admin consents once and enabling a product
          never asks for new permissions. It is not zero-touch: each product's connector still has to be switched
          on by an administrator, write-back is a separate opt-in, and Exchange admin, Power Platform, Azure and
          DNS each need their own one-time setup. The
          <a href="platform.html">platform page lists every step</a> rather than letting you find them during
          onboarding.</p>
      </div>

<div class="note honest">
        <h2>Some planes detect but do not yet fix</h2>
        <p class="mb0">Where a plane can be remediated app-only, it is. Where it cannot — Exchange, SharePoint
          site roles, Power Platform and delegated-admin relationships today — the product says so, with the
          precise reason, rather than guessing or quietly failing.</p>
      </div>

<div class="note honest">
        <h2>We are Microsoft-first</h2>
        <p class="mb0">Microsoft 365 and Entra are the deep estate. Box and Slack sharing planes ship today, and
          CompliancePortal covers Google Cloud and AWS through read-only connectors. Everything else is roadmap,
          and we will not pretend otherwise on a sales call.</p>
      </div>

<div class="note honest">
        <h2>Readiness is not an audit opinion</h2>
        <p class="mb0">CompliancePortal produces continuous evidence and readiness for the technical controls on
          the platforms we support. Your auditor still signs the opinion, and the controls that live in people and
          process are still yours to run.</p>
      </div>

      <h2>Why this page exists</h2>
      <p>Most vendors bury this and let you find out in month two. We would rather you knew before
        the first call, because every one of these limits is something you would eventually hit —
        and finding out late costs you more than it costs us.</p>
      <p>If one of them is a dealbreaker, tell us and we will say so plainly rather than sell around
        it. <a href="contact.html">Ask the awkward question</a>.</p>
"""),

    "about.html": dict(
        title="SeQontrol - About - Why this exists",
        desc="Who builds SeQontrol, why a Microsoft 365 security and compliance platform was worth "
             "building, and what we will and will not claim about it.",
        eyebrow="About",
        h1="Why this exists",
        lede="SeQontrol is built by {operator} — a small team, working on the Microsoft 365 estate, "
             "shipping in public.",
        body="""
      <h2>The problem that started it</h2>
      <p>Every Microsoft 365 tenant accumulates access. A link shared with a supplier in 2019, a group
        that quietly means "everyone", an app somebody consented to once. None of it mattered much
        while it stayed obscure. Copilot ended that: anything a user can technically reach is now
        something an assistant will happily summarise and cite.</p>
      <p>The tooling that existed answered the wrong shape of question. Native reports are per-workload
        and per-tenant. GRC platforms take your word for the technical controls and spend their effort
        on questionnaires. Nothing joined "what is exposed" to "prove it stayed fixed" — and nothing at
        all was built for somebody managing forty tenants rather than one.</p>

      <h2>The bet</h2>
      <p>That the platform matters more than any single scanner. One consented connection, one findings
        store, one audit trail — so a security finding becomes compliance evidence without a second
        integration, and so the tenth tenant costs no more thought than the first.</p>
      <p>And that security sits above compliance. A waived control turns a report green without
        changing anything real; we would rather show you the finding that is still there.
        <a href="index.html#principle">The full argument is on the home page.</a></p>

      <h2>Who</h2>
      <p>{operator} is Jeff Wouters — writing, speaking and consulting on the Microsoft platform at
        <a href="https://jeffops.com">jeffops.com</a>, and building SeQontrol. If you email us, the
        reply comes from a person who worked on the thing you are asking about.</p>

      <h2>What we will not do</h2>
      <ul>
        <li><strong>Claim customers we do not have.</strong> There are no logos on this site because
          there is nothing to show yet, and inventing them would be a strange way to start a
          relationship built on trusting us with tenant access.</li>
        <li><strong>Fabricate a pass.</strong> A control we cannot assess is reported as "not
          assessed", never as green.</li>
        <li><strong>Oversell the roadmap.</strong> What is shipped is labelled shipped, and what is
          not is labelled coming soon, on the page where you would otherwise assume otherwise.</li>
      </ul>

      <!-- TO ADD: a photo, and a line of background if you want one. A named,
           visible founder is the strongest trust signal available before there
           are customers to reference. -->

      <h2>Talk to us</h2>
      <p>Ask a hard question — <a href="contact.html">the contact page</a> or
        <a href="mailto:{contact}">{contact}</a>. If SeQontrol is not a fit for you, we would rather
        say so early than sell you a year of it.</p>
"""),

    "privacy.html": dict(
        title="SeQontrol - Privacy - What we collect and why",
        desc="What SeQontrol collects from this website and from a connected tenant, "
             "why, how long it is kept, and who to contact about it.",
        eyebrow="Privacy",
        h1="What we collect, and why",
        lede="Short, because there is not much of it. This covers the website; the second half "
             "covers what the product reads once a tenant is connected.",
        body="""
      <h2>This website</h2>
      <p>The site is static. It sets no cookies, runs no advertising or profiling scripts, and makes
        no third-party requests — no fonts, no CDN, no embedded video. Nothing about you is collected
        by visiting it.</p>
      <p>If you send the contact form, we receive what you typed: your name, email address, and
        whatever else you chose to add. We use it to reply to you and to keep track of the
        conversation. We do not sell it, share it for marketing, or add you to a list you did not ask
        for.</p>

      <h2>What the product reads</h2>
      <p>Once you connect a Microsoft 365 tenant, SeQontrol reads configuration and metadata through
        app-only Microsoft Graph permissions in order to produce findings. Concretely, that means
        things like sharing links, permission assignments, group memberships, application consents,
        Conditional Access policies and DNS records.</p>
      <p><strong>It is metadata about access, not the contents of your files.</strong> SeQontrol
        records that a document is shared with an external address; it does not read the document.</p>
      <p>Scanning is read-only. Anything that writes back to your tenant — revoking a permission,
        publishing a DNS record, restoring an approved configuration — requires a separate, explicit
        consent that is distinct from the read grant, and can be withdrawn without losing the
        findings and evidence you already hold.</p>

      <h2>How long it is kept</h2>
      <p>Findings and evidence are retained for the period your licence sets, because the value of
        compliance evidence is that it covers a period. The audit trail is hash-chained and
        append-only by design: entries are not edited or deleted, which is the property that makes it
        worth having.</p>
      <p>Contact-form correspondence is kept for as long as the conversation is useful, and deleted
        on request.</p>

      <h2>Your rights</h2>
      <p>You can ask what we hold about you, ask for it to be corrected, ask for it to be deleted, or
        object to it being processed. Email <a href="mailto:{contact}">{contact}</a> and you will get
        a reply from a person.</p>
      <p>Where SeQontrol processes data from your tenant, you are the controller and we act as
        processor on your instructions. A data processing agreement is available on request.</p>

      <h2>Changes</h2>
      <p>If this notice changes materially, the change is visible in the site's public commit
        history — the whole site is a public repository, which is a stronger guarantee than a
        "last updated" date we control.</p>
"""),

    "terms.html": dict(
        title="SeQontrol - Terms - The plain version",
        desc="The terms covering use of the SeQontrol website and, in outline, the service — "
             "written to be read rather than to be scrolled past.",
        eyebrow="Terms",
        h1="Terms, in language you can actually check",
        lede="These cover the website. A signed agreement governs the service itself; ask and we "
             "will send it before you commit to anything.",
        body="""
      <h2>The website</h2>
      <p>You may read, quote and link to anything here. The words, the brand and the artwork belong
        to {operator}. The site's source is public and its licence sits in the repository.</p>
      <p>Everything on this site describing the product is written to be accurate at the time of
        writing, including the parts that say what the product does <em>not</em> do. Where something
        is not yet available it is labelled "coming soon", and where a capability is limited the
        limit is stated. If you find something on this site that is wrong, tell us and we will fix
        it — that is a commitment we would rather be held to than a disclaimer.</p>

      <h2>The service</h2>
      <p>Use of the platform is governed by a written agreement, not by this page. That agreement
        covers availability, support, liability, processing terms and termination. We will send it
        before you are asked to commit, not after.</p>
      <p>Two things worth stating plainly here, because they shape everything else:</p>
      <ul>
        <li><strong>SeQontrol provides readiness and evidence, not an audit opinion.</strong> Your
          auditor signs the opinion. Nothing produced here is a certification.</li>
        <li><strong>Remediation writes to your tenant only where you have separately consented.</strong>
          It restores an approved state or removes an identified exposure; it does not run arbitrary
          automation.</li>
      </ul>

      <h2>No warranty of a secure estate</h2>
      <p>SeQontrol reports what it can observe through the connections you grant it. It does not
        claim to find everything, and a clean report is not a guarantee that you are not exposed —
        a control that cannot be assessed is reported as "not assessed" rather than as a pass,
        precisely so that the gap is visible to you.</p>

      <h2>Contact</h2>
      <p>Questions about these terms: <a href="mailto:{contact}">{contact}</a>.</p>
"""),

    "security.html": dict(
        title="SeQontrol - Security - What we do with your access",
        desc="The access SeQontrol asks for, what it does with it, how the audit trail works, "
             "and how to report a vulnerability.",
        eyebrow="Security",
        h1="What we do with the access you give us",
        lede="A new vendor asking to read your entire identity estate should expect hard questions. "
             "These are the answers, before you ask.",
        body="""
      <h2>The access we ask for</h2>
      <ul>
        <li><strong>App-only, and read-first.</strong> Scanning uses application permissions, not a
          user's session. There is no agent to install and no user-facing disruption.</li>
        <li><strong>One consent, scoped and documented.</strong> A single Entra application declares
          the permissions every product needs. Enabling a further product does not ask you for new
          permissions — though it does require an administrator to switch that product's connector
          on.</li>
        <li><strong>Write access is separate.</strong> Remediation requires its own explicit consent
          on top of the read grant. Withdrawing it stops all write paths and leaves your findings and
          evidence intact.</li>
        <li><strong>Metadata, not content.</strong> We read who can reach what. We do not read your
          documents or your mail.</li>
      </ul>

      <h2>How the platform is built</h2>
      <ul>
        <li><strong>Tenant isolation.</strong> Each tenant owns its own connectors, findings,
          governance records and history. There is no shared tenant data. Templates may seed a
          tenant, but instantiated records belong to that tenant.</li>
        <li><strong>Tamper-evident audit.</strong> The audit trail is hash-chained, so a record that
          was altered after the fact can be shown to have been altered. Support access through
          impersonation is recorded in it like anything else.</li>
        <li><strong>An approval gate for providers.</strong> Where a managed service provider
          operates inside your tenant, you can require that their actions are approved first.</li>
        <li><strong>Nothing is overwritten.</strong> Controls, desired states, findings, remediations,
          approvals and waivers preserve their history. Governance decisions overlay the facts; they
          never rewrite them.</li>
        <li><strong>No fabricated passes.</strong> A control that cannot be assessed — no exported
          logs, an unsupported plane, a missing permission — is reported as "not assessed", with the
          reason. It is never scored green by default.</li>
      </ul>

      <h2>This website</h2>
      <p>Static files, served over HTTPS with HSTS via the host. No cookies, no third-party scripts,
        no external requests of any kind. The source is public, so any claim on this page can be
        checked against the code that makes it.</p>

      <h2>Reporting a vulnerability</h2>
      <p>Email <a href="mailto:{contact}">{contact}</a>. Include enough detail to reproduce the
        issue. We will acknowledge within two working days and keep you informed until it is
        resolved. We will not take legal action against anyone acting in good faith to find and
        report a problem, and we are happy to credit you unless you would rather we did not.</p>
      <p>Machine-readable contact details are published at
        <a href=".well-known/security.txt">/.well-known/security.txt</a>.</p>

      <!-- TO FILL IN before this page carries real weight:
             · hosting region(s) for product data
             · subprocessor list (hosting, mail, error reporting)
             · retention defaults per data class
             · certifications held, if any (say none rather than implying)  -->
"""),
}


def chrome() -> tuple[str, str]:
    src = io.open(SOURCE, encoding="utf-8").read()
    head_open = src[:src.index("<title>")]
    after_head = src[src.index("</head>"):src.index("<main")]
    footer = src[src.index('<footer class="site-footer">'):src.index("<script src=")]
    return head_open, after_head, footer


def build(name: str, spec: dict) -> None:
    head_open, after_head, footer = chrome()
    body = spec["body"].format(contact=CONTACT, operator=OPERATOR)
    html = (
        head_open
        + f"<title>{spec['title']}</title>\n"
        + f'<meta name="description" content="{spec["desc"]}">\n'
        + '<link rel="stylesheet" href="css/styles.css">\n'
        + after_head
        + "<main id=\"main\">\n\n"
        + '  <section class="hero">\n    <div class="wrap wrap-narrow">\n'
        + f'      <span class="eyebrow">{spec["eyebrow"]}</span>\n'
        + f'      <h1>{spec["h1"]}</h1>\n'
        + f'      <p class="lede">{spec["lede"]}</p>\n'
        + "    </div>\n  </section>\n\n"
        + '  <section>\n    <div class="wrap wrap-narrow">\n'
        + body
        + "    </div>\n  </section>\n\n</main>\n\n"
        + footer
        + '<script src="js/site.js"></script>\n</body>\n</html>\n'
    )
    path = os.path.join(ROOT, name)
    io.open(path, "w", encoding="utf-8").write(html)
    print("wrote", name)


SECURITY_TXT = f"""Contact: mailto:{CONTACT}
Expires: 2027-08-14T00:00:00.000Z
Preferred-Languages: en, nl
Canonical: https://seqontrol.com/.well-known/security.txt
Policy: https://seqontrol.com/security.html
"""

if __name__ == "__main__":
    for name, spec in PAGES.items():
        build(name, spec)
    d = os.path.join(ROOT, ".well-known")
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "security.txt"), "w", encoding="utf-8").write(SECURITY_TXT)
    print("wrote .well-known/security.txt")
