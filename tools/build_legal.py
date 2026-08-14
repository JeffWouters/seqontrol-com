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
