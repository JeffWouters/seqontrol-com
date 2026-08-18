"""Rebuild the licensing page's "What each licence includes" section.

One tab per product; inside each, the technologies it covers and a capability
matrix. The ticks come from the seeded entitlement catalog (Billing's
CatalogSeeder), the technology lists from each product's own connectors and
business plan — not invented.

Markup ships with the tab strip hidden and every panel visible, so the content
survives with JavaScript off; site.js flips it into tabs.
"""
import io

PAGE = r"Z:\Websites\SeQontrol.com\licensing.html"

Y = '<span class="tick" aria-hidden="true">&check;</span><span class="sr-only">Included</span>'
N = '<span class="no" aria-hidden="true">&mdash;</span><span class="sr-only">Not included</span>'

LADDER = [("Visibility", "see it"), ("Governance", "govern it"), ("Automation", "act on it")]
BANDS = [("1 framework", "single regime"), ("3 frameworks", "the usual mix"), ("Unlimited", "every regime")]
ONE = [("Included", "one tier")]
# WebScan's ladder is not see -> govern -> act. It is scan -> keep -> keep
# automatically: the free rung runs everything and remembers nothing.
KEPT = [("Free", "on every tenant"), ("Monitoring", "per site"), ("Continuous", "per site")]


def rows(items, cols):
    out = []
    for item in items:
        if isinstance(item, str):
            out.append('              <tr class="group"><th colspan="%d" scope="colgroup">%s</th></tr>'
                       % (cols + 1, item))
            continue
        label, cells = item
        out.append('              <tr><th scope="row">%s</th>%s</tr>'
                   % (label, "".join("<td>%s</td>" % c for c in cells)))
    return "\n".join(out)


def table(cols, items):
    head = "".join('<th class="rung-head" scope="col">%s<small>%s</small></th>' % (n, s) for n, s in cols)
    return ('        <div class="table-wrap table-scroll" tabindex="0" role="group"'
            ' aria-label="Licence comparison">\n'
            '          <table class="matrix">\n'
            '            <thead>\n'
            '              <tr><th scope="col">Capability</th>%s</tr>\n'
            '            </thead>\n'
            '            <tbody>\n%s\n            </tbody>\n'
            '          </table>\n'
            '        </div>') % (head, rows(items, len(cols)))


def tech(groups):
    """groups: list of (label, [(name, supported_bool), ...])"""
    out = ['        <div class="tech">', '          <h4>Technologies covered</h4>']
    for label, items in groups:
        if label:
            out.append('          <span class="group-label">%s</span>' % label)
        tags = "".join(
            '<li class="tag %s">%s</li>' % ("on" if ok else "off", name) for name, ok in items)
        out.append('          <ul class="tags">%s</ul>' % tags)
    out.append('        </div>')
    return "\n".join(out)


# --------------------------------------------------------------- product data

PRODUCTS = [
    dict(
        key="sharecare", name="ShareCare", tone="--t-sharecare", status=None,
        counted="Counted per Microsoft 365 user &middot; 25-user minimum &middot; $2 / $3.50 / $5 per user, per month",
        tech=[("Microsoft 365", [("SharePoint", 1), ("OneDrive", 1), ("Teams", 1),
                                 ("Entra ID app consents", 1), ("Exchange Online forwarding", 1),
                                 ("Power Platform", 1), ("Power BI", 1)]),
              ("Beyond Microsoft 365", [("Box", 1), ("Slack Connect", 1), ("Google Workspace — roadmap", 0)])],
        cols=LADDER,
        rows=["Price",
              ("Per Microsoft 365 user, per month", ["$2", "$3.50", "$5"]),
              ("At 100 users, per month", ["$200", "$350", "$500"]),
              "Cadence",
              ("On-demand scan, whenever you want one", [Y, Y, Y]),
              ("Scheduled scan cadence", ["Daily", "Every 6 hours", "Hourly"]),
              "Inventory and detection",
              ("Sharing and permission inventory across every connected plane", [Y, Y, Y]),
              ("Risk scoring by sensitivity, exposure and blast radius", [Y, Y, Y]),
              ("Findings history and reports", [Y, Y, Y]),
              ("Fleet view across managed tenants", [Y, Y, Y]),
              ("Oversharing detection — org-wide links and company-wide groups", [N, Y, Y]),
              ("Advanced detections — anonymous links, dormant guests, over-permissioned apps", [N, Y, Y]),
              "Governance",
              ("Policies", [N, Y, Y]),
              ("Owner-delegated access reviews and recertification", [N, Y, Y]),
              ("Approvals", [N, Y, Y]),
              ("Waivers and risk acceptance, with mandatory expiry", [N, Y, Y]),
              ("Evidence packs", [N, Y, Y]),
              "Write access",
              ("Automated remediation write-back, with grace window and undo", [N, N, Y])],
        note=("<strong>Estate size is a quote-time band, not a meter.</strong> The invoice stays on seats, but "
              "at quote time we ask roughly how large the SharePoint and OneDrive estate is — storage volume and "
              "site count. Almost every tenant sits in the standard band. A tenant whose estate is far larger "
              "than its seat count suggests — the 40-user firm with twelve terabytes — is banded accordingly, so "
              "it is priced for what it actually costs to crawl rather than discovering that later. Nothing about "
              "this is metered, gated or counted after the fact."),
        after=("Counted on users rather than on shares or resources — metering the resource count would punish "
               "the messiest estates, which are exactly the ones that need it most, and it could not be quoted "
               "before a discovery scan. Write-back is live for OneDrive permissions and sharing links; Exchange "
               "forwarding, SharePoint site roles, Power Platform and delegated-admin relationships are detected "
               "but not yet revoked app-only."),
    ),
    dict(
        key="securityportal", name="SecurityPortal", tone="--t-security", status=None,
        counted="Counted per user — or included with any ShareCare tier",
        tech=[("Microsoft 365 and Entra", [("Conditional Access", 1), ("MFA enforcement", 1),
                                           ("Entra ID app permissions", 1), ("Sign-in risk signals", 1),
                                           ("Log Analytics (KQL checks)", 1)])],
        cols=ONE,
        rows=[("On-demand scan, whenever you want one", [Y]),
              ("Scheduled scan cadence — daily", [Y]),
              ("Microsoft 365 and Entra posture — Conditional Access, MFA, app permissions", [Y]),
              ("Log-analytics checks, where activity logs are exported", [Y]),
              ("Posture ladder, advanced only by scan evidence", [Y]),
              ("Control-reference tags on every finding", [Y]),
              ("Findings history and reports", [Y]),
              ("Fleet-wide across managed tenants", [Y]),
              ("Write access to your tenant", [N])],
        after=("One tier, not a ladder: SecurityPortal is scan-only, so there is no write access to sell on a "
               "higher rung. Remediation lives in the products built to write safely. The log-analytics checks "
               "need the tenant to export activity logs; without that export they report &ldquo;not "
               "assessed&rdquo; rather than a pass. The public web and domain surface is "
               "<a href=\"products/webscan.html\">WebScan</a>, licensed separately and free to run."),
    ),
    dict(
        key="webscan", name="WebScan", tone="--t-webscan", status=None,
        counted="Free on every tenant &middot; $4 / $8 per monitored site, per month &middot; five-site minimum",
        tech=[("Discovery", [("Subdomain and asset discovery", 1),
                             ("Certificate transparency monitoring", 1)]),
              ("Transport", [("TLS versions and cipher suites", 1), ("Certificate chain and expiry", 1),
                             ("Client handshake simulation", 1), ("HSTS", 1),
                             ("IPv6 and protocol readiness", 1)]),
              ("HTTP", [("Security headers", 1), ("Cookie flags", 1), ("Redirect chain", 1)]),
              ("DNS", [("CAA", 1), ("DNSSEC", 1), ("Nameserver and record hygiene", 1)]),
              ("Content and infrastructure", [("Exposed paths and files", 1),
                                              ("Open ports and exposed services", 1),
                                              ("security.txt (RFC 9116)", 1),
                                              ("Server and technology disclosure", 1)])],
        cols=KEPT,
        rows=["Price",
              ("Per monitored site, per month", ["$0", "$4", "$8"]),
              ("At the five-site minimum", ["$0", "$20", "$40"]),
              "The scan itself",
              ("On-demand scan, whenever you want one", [Y, Y, Y]),
              ("The complete check set — nothing withheld from the free tier", [Y, Y, Y]),
              ("Scan a site you have not onboarded", [N, Y, Y]),
              ("Subdomain and asset discovery", [Y, Y, Y]),
              ("Certificate transparency lookup", [Y, Y, Y]),
              ("Certificate expiry, checked on every scan", [Y, Y, Y]),
              ("Graded score with the four result states kept apart", [Y, Y, Y]),
              ("Standard and RFC references on every check", [Y, Y, Y]),
              ("Why it matters, and the fix, on every failure", [Y, Y, Y]),
              ("Sites you may scan", ["1", "Unlimited", "Unlimited"]),
              ("On-demand scans per day", ["3", "Unlimited", "Unlimited"]),
              "What happens afterwards",
              ("Results kept once you close the page", [N, Y, Y]),
              ("Scan history and trend over time", [N, Y, Y]),
              ("Findings, waivers and an audit trail", [N, Y, Y]),
              ("Control-reference tags, feeding CompliancePortal as evidence", [N, Y, Y]),
              ("Fleet view across sites and managed tenants", [N, Y, Y]),
              "Watched on a clock, between scans",
              ("Certificate expiry warned before it lapses, not after", [N, Y, Y]),
              ("Certificate transparency monitoring — alerting on new issuance", [N, Y, Y]),
              ("Alerting when discovery turns up a new asset", [N, Y, Y]),
              ("Alerting when a passing check regresses", [N, Y, Y]),
              "Running without you",
              ("Scheduled scans", ["&mdash;", "Monthly", "A cadence you set"]),
              "Minimums",
              ("Monthly minimum for a WebScan-only tenant", ["&mdash;", "$25", "$25"]),
              "Write access",
              ("Write access to your DNS or web server", [N, N, N])],
        note=("<strong>The free tier has a ceiling, and it is a small one.</strong> One site, three scans a day. "
              "That is deliberate and it is about abuse rather than margin: an uncapped scanner pointed at domains "
              "the caller does not own is reconnaissance run from our addresses, and it ends with our egress "
              "ranges on somebody's blocklist. The ceiling is what lets the tier stay genuinely free rather than "
              "becoming a trial with an expiry date. Register your own site, check it as often as a working day "
              "needs, and pay only when you want more than one or want it remembered.<br><br>"
              "<strong>Two paid rungs, and the difference is how often, not how much.</strong> Monitoring is where "
              "a site becomes a thing we remember — history, findings, waivers, an audit trail, and the daily "
              "watches that warn you about a certificate before it lapses rather than after. It scans monthly, "
              "because retained history is worth very little if nothing generates it. Continuous is the same "
              "product on a cadence you choose.<br><br>"
              "<strong>Not called Automation, deliberately.</strong> On every other product here that word "
              "means the rung that writes to your tenant, and it is a separate consent for that reason. "
              "WebScan never writes anywhere — so borrowing the word would have made a safety promise mean "
              "two different things on one page.<br><br>"
              "<strong>The free tier is the whole scanner, and that is deliberate.</strong> Nothing is held back "
              "to make the paid version look better — the free tier runs every check and shows every result. "
              "What it does not do is remember. There is no history, no schedule, no evidence and no audit "
              "trail, because nothing is written down when the scan finishes. That is also what makes it free "
              "to give away: a free scan is a short-lived function with no storage behind it, it is on demand "
              "only so nothing can schedule itself into a bill, and its cost ends when the scan does."),
        after=("Counted per site rather than per domain, because a site is what gets scanned: one domain can "
               "front several, and each is its own configuration to grade. The five-site minimum is there "
               "because a single-site licence does not cover the platform underneath it — MailTrust counts "
               "domains, which is a different question about the same names. Nothing caps how many sites you "
               "may add; the count is trued up, never a hard stop. WebScan never writes anywhere — DNS "
               "write-back belongs to MailTrust, which also owns SPF, DKIM and DMARC; those are mail "
               "authentication rather than web surface and are not duplicated here."),
    ),
    dict(
        key="complianceportal", name="CompliancePortal", tone="--t-compliance", status=None,
        counted="Counted per tenant &middot; banded by frameworks in scope",
        tech=[("Microsoft", [("Entra ID", 1), ("Exchange Online", 1), ("SharePoint", 1), ("Teams", 1),
                             ("Intune", 1), ("Azure", 1), ("Purview", 1), ("Power Platform", 1), ("Power BI", 1)]),
              ("Other clouds", [("Google Cloud", 1), ("Amazon Web Services", 1)]),
              ("Engineering", [("GitHub", 1), ("Azure DevOps", 1)]),
              # 24 in the catalog; a representative spread is listed rather than all of them.
              # The full per-framework coverage lives on the CompliancePortal page.
              ("Frameworks — 24 in the catalog", [
                  ("SOC 2", 1), ("ISO 27001", 1), ("ISO 27002", 1), ("ISO 27017", 1),
                  ("ISO 27701", 1), ("NIST CSF", 1), ("PCI DSS", 1), ("HIPAA", 1),
                  ("GDPR", 1), ("NIS 2", 1), ("DORA", 1), ("FedRAMP", 1), ("CMMC", 1),
                  ("CSA STAR", 1), ("Essential Eight", 1), ("Cyber Essentials", 1),
                  ("NEN 7510", 1), ("MITRE ATT&amp;CK", 1), ("OWASP", 1),
                  ("A first-party set", 1)])],
        cols=BANDS,
        rows=["In every band",
              ("On-demand assessment, whenever you want one", [Y, Y, Y]),
              ("Scheduled assessment cadence — daily", [Y, Y, Y]),
              ("Framework and benchmark catalog", [Y, Y, Y]),
              ("Multi-framework crosswalk — one piece of evidence, many controls", [Y, Y, Y]),
              ("Automated control probes across the connected planes", [Y, Y, Y]),
              ("Google Cloud and AWS coverage via read-only connectors", [Y, Y, Y]),
              ("Evidence reuse from SecurityPortal, ShareCare and MailTrust", [Y, Y, Y]),
              ("Assessment workflow and immutable snapshot trail", [Y, Y, Y]),
              ("Evidence repository and provided-by-client requests", [Y, Y, Y]),
              ("Time-boxed auditor access", [Y, Y, Y]),
              ("Control ownership and remediation tasks", [Y, Y, Y]),
              "Scales with the band",
              ("Frameworks in scope", ["1", "3", "Unlimited"]),
              ("Evidence retention", ["12 months", "36 months", "84 months"]),
              ("Attestation and sign-off, with four-eyes and expiry", [N, Y, Y]),
              ("Automated evidence capture", [N, N, Y])],
        after=("Depth here is not see → govern → act. It is <strong>how many frameworks are in scope, how long "
               "the evidence is kept, and how much of it is captured automatically.</strong> The scope still "
               "holds: this proves the technical controls on the platforms SeQontrol connects to, not a "
               "whole-company compliance programme."),
    ),
    dict(
        key="postureportal", name="PosturePortal", tone="--t-posture", status=None,
        counted="Bundled — it comes with SecurityPortal or any ShareCare tier",
        tech=[("Reads from", [("ShareCare", 1), ("SecurityPortal", 1), ("WebScan", 1),
                              ("CompliancePortal", 1), ("MailTrust", 1), ("Dredd", 1),
                              ("Connector health", 1)])],
        cols=ONE,
        rows=[("Cross-product findings aggregation", [Y]),
              ("Posture scores, top risks and trends", [Y]),
              ("Connector health and coverage visibility", [Y]),
              ("Saved views and annotations", [Y]),
              ("Fleet overview across managed tenants", [Y]),
              ("Write access to your tenant", [N])],
        after=("PosturePortal connects to nothing itself — it reads the shared findings store, which is why it "
               "costs nothing extra to run and why it is bundled rather than sold as a separate line. An "
               "aggregation layer is only worth having once two or more products feed it."),
    ),
    dict(
        key="mailtrust", name="MailTrust", tone="--t-mailtrust", status=None,
        counted="Counted per domain",
        tech=[("Standards", [("SPF", 1), ("DKIM", 1), ("DMARC", 1), ("BIMI", 1), ("MTA-STS", 1)]),
              ("DNS write-back", [("Azure DNS", 1), ("DNSimple", 1), ("Other providers — guided steps", 0)])],
        cols=LADDER,
        rows=["Cadence",
              ("On-demand scan, whenever you want one", [Y, Y, Y]),
              ("Scheduled scan cadence", ["Daily", "Every 6 hours", "Hourly"]),
              "Assessment",
              ("SPF, DKIM, DMARC, BIMI and MTA-STS posture", [Y, Y, Y]),
              ("DMARC aggregate report ingestion and sender analysis", [Y, Y, Y]),
              ("Findings history and reports", [Y, Y, Y]),
              ("Unlimited domains on every rung", [Y, Y, Y]),
              "Governance",
              ("Guided staged rollout toward enforcement", [N, Y, Y]),
              ("Deliverability and authentication alerting", [N, Y, Y]),
              ("Multi-domain fleet view", [N, Y, Y]),
              "Write access",
              ("DNS write-back for supported providers", [N, N, Y])],
        note=("<strong>Report volume carries an allowance.</strong> Ingesting, parsing and storing DMARC "
              "aggregate reports is a real cost that scales with how much mail a domain sends, not with how many "
              "domains you have — so each domain includes an allowance sized to normal sending volume, and "
              "unusually high-volume domains buy additional blocks. Same test as the deliverability allowance: a "
              "genuine external cost, optional, and bursty. Posture, findings and reports stay uncapped."),
        after=("No rung caps how many domains you may add — the count is a commercial measurement, trued up on "
               "the next invoice, never a hard stop. Ingesting DMARC reports needs a mailbox to receive them; "
               "that is part of onboarding."),
    ),
    dict(
        key="dredd", name="Dredd", tone="--t-dredd", status=None,
        counted="Counted per monitored configuration scope",
        tech=[("Control planes", [("Microsoft Entra ID", 1), ("Microsoft 365 tenant config — designed", 0),
                                  ("Intune — designed", 0)])],
        cols=None,
        rows=None,
        after=None,
        note=("<strong>Dredd runs; its licence shape is still being set.</strong> The product is built and the "
              "governance, remediation and bulk-heal paths are live — what is not settled is the unit it should "
              "be counted on. It is the metric we understand least, and rather than guess a shape and reprice "
              "it six months later, it is being set against real configuration scopes first. Ask and you will "
              "get a number. The full capability set is on the "
              "<a href=\"products/dredd.html\">Dredd page</a>."),
    ),
]

# ------------------------------------------------------------------ rendering

tabs, panels = [], []
for i, p in enumerate(PRODUCTS):
    # The badge belongs on the panel heading, not the tab. A tab label is a
    # navigation target and should stay short; the availability caveat is part
    # of what the panel says about the product, and it is repeated in the
    # "Counted on" line and the notes below it anyway.
    badge = (' <span class="status soon">%s</span>' % p["status"]) if p["status"] else ""
    tabs.append(
        '          <button type="button" role="tab" id="tab-%s" aria-controls="panel-%s"'
        ' aria-selected="%s" tabindex="%s" style="--tone: var(%s)">%s</button>'
        % (p["key"], p["key"], "true" if i == 0 else "false", "0" if i == 0 else "-1",
           p["tone"], p["name"]))

    body = [tech(p["tech"])]
    if p["cols"]:
        body.append(table(p["cols"], p["rows"]))
    if p.get("note"):
        body.append('        <div class="note plain" style="margin-top:0">\n'
                    '          <p class="mb0">%s</p>\n        </div>' % p["note"])
    if p.get("after"):
        body.append('        <p class="after">%s</p>' % p["after"])

    panels.append(
        '      <div class="product-licence" role="tabpanel" id="panel-%s" aria-labelledby="tab-%s"'
        ' tabindex="0" style="--tone: var(%s)">\n'
        '        <header>\n'
        '          <h3>%s%s</h3>\n'
        '          <p class="counted">%s</p>\n'
        '        </header>\n%s\n      </div>'
        % (p["key"], p["key"], p["tone"], p["name"], badge, p["counted"], "\n".join(body)))

SECTION = """  <!-- ---------------------------------------------------------- per product -->
  <section>
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Product by product</span>
        <h2>What each licence includes</h2>
        <p>The technologies each product covers, the unit it counts, and exactly which capabilities each flavour
          unlocks. Every rung contains the one before it, so the ticks accumulate left to right.</p>
      </div>

      <div data-tabs class="tabs-v">
        <div class="tablist" role="tablist" aria-label="Products">
{tabs}
        </div>
{panels}
      </div>

      <article class="product-licence" style="margin-top:3.2rem">
        <header>
          <h3>Terms that apply to the total</h3>
          <p class="counted">Not separate line items</p>
        </header>
        <div class="table-wrap table-scroll" tabindex="0">
          <table>
            <thead><tr><th scope="col">Term</th><th scope="col">What it does</th></tr></thead>
            <tbody>
              <tr><td>Platform minimum</td><td>$99 a month on the total, as greater-of rather than added on top — covers tenancy, auth, audit, findings, reporting and scheduling</td></tr>
              <tr><td>Volume</td><td>Less 10 per cent above 100 users, less 20 per cent above 500, less 30 per cent above 2,000</td></tr>
              <tr><td>Suite discount</td><td>Taking all products costs meaningfully less than the sum of the parts</td></tr>
              <tr><td>Annual or monthly</td><td>A payment term, not a discount — a year costs twelve months</td></tr>
              <tr><td>Provider pooling</td><td>Users and domains pool across managed tenants, with a per-tenant floor applied as greater-of</td></tr>
            </tbody>
          </table>
        </div>
      </article>

      <div class="note plain">
        <p class="mb0"><strong>Evidence retention is a real lever, and we treat it as one.</strong> Twelve months as
          standard, three years on Governance, seven years at the top compliance band. It costs us storage and it
          distorts none of your behaviour — unlike every activity-based metric.</p>
      </div>
    </div>
  </section>

"""

s = io.open(PAGE, encoding="utf-8").read()
start = s.index("  <!-- ---------------------------------------------------------- per product -->")
end = s.index('  <section class="cta">')
new = SECTION.format(tabs="\n".join(tabs), panels="\n".join(panels))
io.open(PAGE, "w", encoding="utf-8").write(s[:start] + new + s[end:])
print("tabs:", len(tabs), "| panels:", len(panels), "| matrices:", new.count('class="matrix"'))
