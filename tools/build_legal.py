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

# A page with form=<button label> gets the request form inlined. It lives here
# rather than being pasted into the HTML, because this script regenerates those
# files — anything added to the output by hand is wiped on the next run.
FORM = '''
      <!-- FORM ENDPOINT: paste the URL into BOTH action and data-endpoint.
           With it set the form posts normally and works without JavaScript;
           left empty it falls back to composing a mailto, which can fail
           silently on webmail — see README. -->
      <form id="contact-form" method="post" action="" data-endpoint="" novalidate>
        <input type="hidden" id="cf-topic" name="topic" value="{topic}">
        <div class="field">
          <label for="cf-name">Name</label>
          <input id="cf-name" name="name" type="text" autocomplete="name" required>
        </div>
        <div class="field">
          <label for="cf-email">Work email</label>
          <input id="cf-email" name="email" type="email" autocomplete="email" required>
          <p class="hint">So we can reply. Nothing else is done with it.</p>
        </div>
        <div class="field">
          <label for="cf-org">Organisation</label>
          <input id="cf-org" name="org" type="text" autocomplete="organization">
        </div>
        <div class="field">
          <label for="cf-estate">{estate_label}</label>
          <input id="cf-estate" name="estate" type="text" placeholder="{estate_hint}">
        </div>
        <div class="field">
          <label for="cf-message">Anything we should know?</label>
          <textarea id="cf-message" name="message" rows="4"></textarea>
        </div>
        <button class="btn btn-primary" type="submit" id="cf-submit">{button}</button>
        <p class="hint" id="cf-status" role="status" aria-live="polite"></p>
        <p class="hint">Or email <a href="mailto:{contact}">{contact}</a> directly.</p>
      </form>

      <div class="note plain" id="cf-fallback" hidden>
        <h2>If your mail client did not open</h2>
        <p>Some browsers and webmail setups cannot hand off to a mail app. Nothing is lost — copy
          the message below and send it to <a href="mailto:{contact}">{contact}</a>.</p>
        <label class="sr-only" for="cf-copy">Your message, ready to copy</label>
        <textarea id="cf-copy" rows="9" readonly
                  style="width:100%;font-family:var(--mono);font-size:.85rem"></textarea>
        <p class="mb0"><button class="btn btn-ghost" type="button" id="cf-copy-btn">Copy message</button></p>
      </div>

      <div class="note plain" id="cf-thanks" hidden>
        <h2>Request sent</h2>
        <p class="mb0">It landed. You will get a reply from a person, usually the same working day.</p>
      </div>
'''

FORM_SCRIPT = '''<script>
/* Same behaviour as the contact page: post when an endpoint is configured,
   otherwise compose a mailto and surface the text so a failed handoff is
   recoverable rather than silent. */
(function () {
  'use strict';
  var form = document.getElementById('contact-form');
  if (!form) return;
  var status = document.getElementById('cf-status');
  var thanks = document.getElementById('cf-thanks');
  var fallback = document.getElementById('cf-fallback');
  var submit = document.getElementById('cf-submit');
  var endpoint = (form.getAttribute('data-endpoint') || '').trim();

  function say(m) { status.textContent = m; }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = form.elements.name.value.trim();
    if (!name) { say('A name helps.'); form.elements.name.focus(); return; }
    var email = form.elements.email.value.trim();
    if (!email || email.indexOf('@') < 1) {
      say('We need an email address to reply to.'); form.elements.email.focus(); return;
    }

    var body = [
      'Name: ' + name,
      'Email: ' + email,
      'Organisation: ' + (form.elements.org.value.trim() || '—'),
      'Request: ' + form.elements.topic.value,
      'Estate: ' + (form.elements.estate.value.trim() || '—'),
      '', form.elements.message.value.trim()
    ].join('\\n');

    if (endpoint) {
      submit.disabled = true; say('Sending…');
      fetch(endpoint, { method: 'POST', headers: { 'Accept': 'application/json' },
                        body: new FormData(form) })
        .then(function (r) { if (!r.ok) throw new Error(r.status);
          form.hidden = true; thanks.hidden = false;
          thanks.setAttribute('tabindex', '-1'); thanks.focus(); })
        .catch(function () { submit.disabled = false;
          say('That did not send. Try again, or email us — your message is still in the form.'); });
      return;
    }

    window.location.href = 'mailto:{contact}'
      + '?subject=' + encodeURIComponent('SeQontrol — ' + form.elements.topic.value)
      + '&body=' + encodeURIComponent(body);
    say('Opening your mail client…');
    document.getElementById('cf-copy').value =
      'To: {contact}\\nSubject: SeQontrol — ' + form.elements.topic.value + '\\n\\n' + body;
    window.setTimeout(function () { fallback.hidden = false; }, 1200);
  });

  var copyBtn = document.getElementById('cf-copy-btn');
  if (copyBtn) copyBtn.addEventListener('click', function () {
    var box = document.getElementById('cf-copy');
    box.select();
    var done = function () { copyBtn.textContent = 'Copied'; };
    if (navigator.clipboard) navigator.clipboard.writeText(box.value).then(done, function () {});
    else { document.execCommand('copy'); done(); }
  });
})();
</script>
'''

PAGES = {
    "pricing.html": dict(
        title="SeQontrol - Pricing - What sets your number",
        desc="How SeQontrol is priced: what each product counts, what makes a quote go up or down, and "
             "how to get a real number against your own estate.",
        eyebrow="Pricing",
        h1="What sets your number",
        lede="ShareCare is listed in full. Everything else is quoted, and this page says which is "
             "which — plus every factor that moves the number, so you can size it before you ask.",
        form=dict(topic="Pricing for my estate",
                  button="Get a real number",
                  estate_label="Your estate",
                  estate_hint="e.g. 150 users, 2 domains — or 60 managed tenants"),
        body="""
      <h2 id="figures">ShareCare, WebScan and MailTrust, in figures</h2>
      <p>This page carried no numbers for a while, for a stated reason: the model was settled but the levels
        were not, and publishing a figure we expected to move is the kind of thing this site refuses to do.
        The levels are now set, so here they are.</p>
      <div class="table-wrap table-scroll" tabindex="0">
        <table class="matrix">
          <thead>
            <tr>
              <th scope="col">Per Microsoft 365 user, per month</th>
              <th class="rung-head" scope="col">Visibility<small>see it</small></th>
              <th class="rung-head" scope="col">Governance<small>govern it</small></th>
              <th class="rung-head" scope="col">Automation<small>act on it</small></th>
            </tr>
          </thead>
          <tbody>
            <tr><th scope="row">List</th><td>$2</td><td>$3.50</td><td>$5</td></tr>
            <tr><th scope="row">100 users</th><td>$200</td><td>$350</td><td>$500</td></tr>
            <tr><th scope="row">500 users, less 10 per cent</th><td>$900</td><td>$1,575</td><td>$2,250</td></tr>
            <tr><th scope="row">2,000 users, less 20 per cent</th><td>$3,200</td><td>$5,600</td><td>$8,000</td></tr>
          </tbody>
        </table>
      </div>
      <p class="small dim">Volume: less 10 per cent above 100 users, less 20 per cent above 500, less 30 per
        cent above 2,000. A year costs twelve months — see <a href="#never">what never moves it</a>.</p>

      <div class="note plain">
        <h3>The floor, before you do the multiplication</h3>
        <p class="mb0">A <strong>monthly platform minimum of $99</strong> applies to the total. It covers the
          tenancy, auth, audit trail, findings store, reporting and scheduling that every product runs on, and
          it is charged as greater-of rather than added on top. Where it bites: on Visibility up to 49 users,
          on Governance up to 28, and on Automation never — the 25-user minimum already clears it there. A
          30-user tenant on Visibility computes $60 and pays $99. Better to hear that here than at quote
          time.</p>
      </div>

      <h3 style="margin-top:2.6rem">WebScan — per monitored site, per month</h3>
      <p>Priced the other way round from everything else here. The scan is free on every tenant, forever,
        with no site count attached to it. What is counted is the sites you asked us to keep.</p>
      <div class="table-wrap table-scroll" tabindex="0">
        <table class="matrix">
          <thead>
            <tr>
              <th scope="col">Per monitored site, per month</th>
              <th class="rung-head" scope="col">Free<small>on every tenant</small></th>
              <th class="rung-head" scope="col">Monitoring<small>keep it</small></th>
              <th class="rung-head" scope="col">Continuous<small>on your cadence</small></th>
            </tr>
          </thead>
          <tbody>
            <tr><th scope="row">List</th><td>$0</td><td>$4</td><td>$8</td></tr>
            <tr><th scope="row">5 sites, the minimum</th><td>$0</td><td>$20</td><td>$40</td></tr>
            <tr><th scope="row">25 sites</th><td>$0</td><td>$100</td><td>$200</td></tr>
          </tbody>
        </table>
      </div>
      <p class="small dim">Five-site minimum on either paid rung. Scanning is never counted — only sites you
        chose to keep, once per billing period each, however often they are scanned.</p>

      <div class="note plain">
        <h3>A WebScan-only tenant does not pay the $99</h3>
        <p class="mb0">It pays <strong>$25 a month</strong> instead. A tenant that arrived through a free scan
          is one we would not otherwise have, and quoting $99 against $20 of monitoring converts nobody — the
          floor would eat the funnel it sits downstream of. Add any second product and the $99 applies from
          that point.</p>
      </div>

      <h3 style="margin-top:2.6rem">MailTrust — per domain, per month</h3>
      <div class="table-wrap table-scroll" tabindex="0">
        <table class="matrix">
          <thead>
            <tr>
              <th scope="col">Per domain, per month</th>
              <th class="rung-head" scope="col">Visibility<small>see it</small></th>
              <th class="rung-head" scope="col">Governance<small>govern it</small></th>
              <th class="rung-head" scope="col">Automation<small>act on it</small></th>
            </tr>
          </thead>
          <tbody>
            <tr><th scope="row">Sending domain</th><td>$15</td><td>$30</td><td>$40</td></tr>
            <tr><th scope="row">Parked domain</th><td>$3</td><td>$3</td><td>$3</td></tr>
            <tr><th scope="row">3 sending, 40 parked</th><td>$120</td><td>$165</td><td>$195</td></tr>
          </tbody>
        </table>
      </div>
      <p class="small dim">Five parked domains included with every sending domain — the example above prices
        the remaining 25.</p>

      <div class="note plain">
        <h3>Why a parked domain costs $3 and not $15</h3>
        <p>Most organisations own far more domains than they send from: acquisitions, retired brands,
          defensive and typo registrations. Those are exactly the ones worth spoofing — no real mail flows,
          so nothing breaks and nobody notices.</p>
        <p class="mb0">Charging full rate for them makes the rational decision <em>protect fewer domains</em>,
          which is the behaviour this product exists to prevent. A parked domain needs a policy, a null MX and
          a daily check that nobody quietly changed them, and it sends us almost no report volume — so it is
          priced for what it is. The classification is measured, not asserted: a domain is parked when it has
          produced no DMARC report volume and no DKIM signing for a full period, and it reclassifies itself
          the moment you start sending from it.</p>
      </div>

      <div class="note honest">
        <h3>What Automation writes, and where it does not</h3>
        <p class="mb0">DNS write-back is live for <strong>Azure DNS and DNSimple</strong>. Anywhere else,
          Automation gives you a staged rollout and the exact records to apply yourself — guidance, not
          automation. That is why the rung is $40 rather than the $50 the capability would be worth if it
          wrote everywhere. Cloudflare and Route 53 are next, and the price moves when they ship, not before.
          Better to read that here than to discover it after buying the top rung.</p>
      </div>

      <p>SecurityPortal, CompliancePortal, PosturePortal, Dredd and ConditionalAccessPortal are quoted rather
        than listed. Not evasion — those levels genuinely are still being set against real estates, and we
        would rather say so than publish a number we expect to move. Ask, and you get one back, usually the
        same working day.</p>

      <h2>What each product counts</h2>
      <div class="table-wrap table-scroll" tabindex="0">
        <table>
          <thead><tr><th scope="col">Product</th><th scope="col">Priced on</th></tr></thead>
          <tbody>
            <tr><th scope="row">ShareCare</th><td>Microsoft 365 users, with a 25-user minimum</td></tr>
            <tr><th scope="row">SecurityPortal</th><td>Users — or included with any ShareCare tier</td></tr>
            <tr><th scope="row">CompliancePortal</th><td>Per tenant, banded by how many frameworks are in scope</td></tr>
            <tr><th scope="row">WebScan</th><td>Free on every tenant; Monitoring and Continuous per monitored site, five-site minimum</td></tr>
            <tr><th scope="row">MailTrust</th><td>Per sending domain; parked domains at a lower rate, five included with each</td></tr>
            <tr><th scope="row">PosturePortal</th><td>Bundled, never a separate line</td></tr>
          </tbody>
        </table>
      </div>

      <p>WebScan is the exception to that floor, and it goes the other way — see
        <a href="#figures">its figures above</a>.</p>

      <h2>What moves the number</h2>
      <ul>
        <li><strong>Which rung you buy.</strong> Visibility, Governance or Automation — see
          <a href="licensing.html">what each licence includes</a>.</li>
        <li><strong>How big the estate is</strong>, in the unit that product counts.</li>
        <li><strong>How many products.</strong> Taking the suite costs meaningfully less than the parts.</li>
        <li><strong>Whether you are a provider.</strong> Pooled capacity across managed tenants, with a
          per-tenant floor applied as greater-of rather than added on top.</li>
      </ul>

      <h2 id="never">What never moves it</h2>
      <p>How often you scan, how many findings you have, how much you remediate, or how much evidence you
        export. None of those are metered, deliberately — charging for them would teach you to look less
        often, which is the one behaviour this product exists to prevent.</p>
      <p><strong>Nor does how you pay.</strong> A year costs twelve months. Annual and monthly are a
        cash-flow decision, not a lever: there is no discount for committing and no penalty for not. If you
        would rather pay yearly because it is one invoice instead of twelve, do that — it will not change
        the number, and nobody here will pretend it should.</p>
      <p><a href="products/webscan.html">WebScan</a> takes that further: every tenant scans one site three
        times a day at no cost, indefinitely. The licence buys more sites and what happens <em>after</em> the
        scan — the history, the schedule, the audit trail and the evidence. A scan you do not keep cannot
        prove anything, and the one you do keep is the one we charge for.</p>

      <h2 id="request">Get a number</h2>
      <p>Tell us the size of the estate. You will get a real figure back, not a discovery call.</p>
"""),

    "spoofing-report.html": dict(
        title="SeQontrol - Free report - Who is sending as you",
        desc="A free check of your domain's email authentication: SPF, DKIM, DMARC, BIMI and MTA-STS, "
             "plus every source currently sending mail as you.",
        eyebrow="Free assessment",
        h1="Find out who is sending email as your domain",
        lede="A free check of SPF, DKIM, DMARC, BIMI and MTA-STS — and, once reports are flowing, a list "
             "of every source sending mail as you. No tenant access required.",
        form=dict(topic="Free spoofing / DMARC check",
                  button="Check my domain",
                  estate_label="Domain",
                  estate_hint="yourcompany.com — or several, comma separated"),
        body="""
      <h2>What you get back</h2>
      <ul>
        <li><strong>Your posture, record by record</strong> — what SPF actually authorises, whether DKIM is
          signing, what your DMARC policy does today, and whether MTA-STS and BIMI are in play.</li>
        <li><strong>Whether you can be spoofed right now</strong>, stated plainly rather than as a score.
          Most domains sit at <code>p=none</code>, which monitors and blocks nothing.</li>
        <li><strong>Every sender using your domain</strong> — from real DMARC aggregate reports once
          collection is running. Legitimate services you had forgotten about, and anyone else.</li>
        <li><strong>A staged path to enforcement</strong> that will not drop the mail your business depends
          on, which is the actual reason most DMARC projects stall at monitoring.</li>
      </ul>

      <h2>The easiest one to start with</h2>
      <p>It needs no access to your tenant. Email authentication is published in public DNS, so the first
        pass costs you nothing but the domain name. The sender inventory needs a mailbox to receive DMARC
        reports — we will tell you exactly how to point them at it.</p>

      <h2>Why now</h2>
      <p>Major mailbox providers now require DMARC for bulk senders, inbox brand indicators require
        enforcement, and business email compromise remains among the most expensive attacks in circulation.
        Reaching <code>p=reject</code> is the proven defence; doing it without breaking legitimate mail is
        the hard part, and it is what this is designed around.</p>

      <h2>If you want it continuously</h2>
      <p>That is <a href="products/mailtrust.html">MailTrust</a> — across one domain or every domain your
        clients own, writing the DNS records itself for supported providers rather than handing you a
        ticket for another team.</p>

      <h2 id="request">Check my domain</h2>
      <p>Send the domain name. A person replies, usually the same working day.</p>
"""),

    "surface-report.html": dict(
        title="SeQontrol - Free scan - Your public surface, graded",
        desc="A free grade of your public web surface: TLS, HTTP headers, cookies, DNS, content and "
             "infrastructure, each failure with the standard it breaks and the fix.",
        eyebrow="Free assessment",
        h1="Find out what your attacker sees first",
        lede="A free grade of your public surface — TLS, HTTP headers, cookies, DNS, content and "
             "infrastructure — with the standard behind every failure and the fix next to it. No tenant, "
             "no consent, no onboarding.",
        form=dict(topic="Free public surface scan",
                  button="Scan my site",
                  estate_label="Site",
                  estate_hint="https://yourcompany.com — or several, comma separated"),
        body="""
      <h2>The one you can start with today</h2>
      <p>Every other assessment on this site needs an administrator to consent to something. This one does
        not. WebScan reads what any anonymous visitor can read, so there is nothing to install, nothing to
        approve, and no reason to involve anyone before you know whether there is a problem.</p>
      <p>Send a URL. You get the grade back, usually the same working day.</p>

      <h2>What you get back</h2>
      <ul>
        <li><strong>A grade, and the four counts behind it</strong> — passed, failed, not assessed and not
          applicable, kept apart so a low score can be read rather than argued with.</li>
        <li><strong>Every failure with the standard it breaks.</strong> Not "the scanner says so" but the
          RFC number, which is what turns a finding into a change request somebody approves.</li>
        <li><strong>Why it matters, then the fix</strong>, on each one — in the words you would use to
          justify the work to whoever has to schedule it.</li>
        <li><strong>The hosts you did not send us.</strong> Discovery looks for the subdomains and assets
          attached to the name you gave, which is usually where the surprise is.</li>
        <li><strong>What could not be assessed</strong>, said out loud. A check we could not run is never
          quietly counted as a pass.</li>
      </ul>

      <h2>And it stays free</h2>
      <p>This is not a sample of a paid product. <a href="products/webscan.html">WebScan</a>'s free tier
        runs the complete check set and shows every result, on your own site, three scans a day, for as long
        as you keep the tenant and with no expiry date on it. Nothing is held back from the check set — the
        cap is on reach, not on depth, and it exists so an uncapped scanner cannot be pointed at domains
        nobody owns.</p>
      <p>What the free tier does not do is <em>remember</em>. Nothing is written down when the scan
        finishes — so there is no history, no trend, no schedule, no alert when a passing check regresses,
        and no evidence to hand an auditor. That is the whole of what the licence buys, and it is also why
        the free tier can be free: a free scan is a short-lived function with no storage behind it.</p>

      <div class="note honest">
        <h2>What this is not</h2>
        <p class="mb0">Not a penetration test. It grades configuration against published standards; as it
          stands it does not attempt exploitation and cannot see anything behind a login. It requests pages
          and reads DNS the way any visitor does — no fuzzing, no load, and it never writes anywhere. Active
          testing and authenticated scanning are on the
          <a href="products/webscan.html#roadmap">WebScan roadmap</a>; the free scan will stay
          unauthenticated and non-intrusive either way, so it is always safe to point at anything you
          own.</p>
      </div>

      <h2 id="request">Scan my site</h2>
      <p>Send a URL. No tenant, no consent, no call first.</p>
"""),

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
          surface, which is where a good deal of exposure actually lives — that is
          <a href="products/webscan.html">WebScan</a>, and running it costs nothing.</li>
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
        form=dict(topic="Free exposure report",
                  button="Request my exposure report",
                  estate_label="Tenant size",
                  estate_hint="e.g. 150 users, ~4 TB in SharePoint"),
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
        <li>An administrator grants read-only consent to the Entra application for the product being
          assessed — scoped to that product, and nothing else.</li>
        <li>The crawl runs. Large estates are swept in stages so nothing is throttled.</li>
        <li>You get the report, and a walkthrough of it if you want one.</li>
      </ol>

      <h2>Managing many tenants?</h2>
      <p>The provider version ranks your worst clients against each other, so the conversation you
        have with them is specific rather than general.
        <a href="for-msps.html">More on the provider model</a>.</p>

      <h2 id="request">Ask for the report</h2>
      <p>Tell us the tenant size and we will come back with a scope and a date. A person replies,
        usually the same working day.</p>
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
        <h2>Every product asks for its own consent</h2>
        <p class="mb0">There is no single grant that switches the platform on. Each product has its own Entra
          application and its own admin consent, scoped to that product's permissions — so adding a product
          means going back to an administrator, not flipping a switch. The upside is real: nothing inherits
          permissions it has no use for, and revoking one product revokes exactly one. But if you were told
          this was a one-consent platform, it is not, and you would have found out during onboarding. On top
          of that, write-back is a separate opt-in again, and Exchange admin, Power Platform, Azure and DNS
          each need their own one-time setup. The
          <a href="platform.html">platform page lists every step</a>.</p>
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
      <p>That the platform matters more than any single scanner. One findings store, one audit trail, one
        console — so a security finding becomes compliance evidence without a second integration, and so the
        tenth tenant costs no more thought than the first. Each product still asks for its own consent; what
        the platform saves you is everything after that.</p>
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
        <li><strong>Consent is per product, scoped and documented.</strong> Each product has its own
          Entra application, declaring only the permissions that product needs. Enabling a further product
          means a further admin consent — so nothing inherits permissions it has no use for, and revoking
          one product revokes exactly one.</li>
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

    # An offer page carries its own form, so the ask sits where the intent is
    # rather than one click away on the contact page.
    if spec.get("form"):
        body += FORM.format(
            contact=CONTACT,
            topic=spec["form"]["topic"],
            button=spec["form"]["button"],
            estate_label=spec["form"]["estate_label"],
            estate_hint=spec["form"]["estate_hint"],
        )

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
        + '<script src="js/site.js"></script>\n'
        + (FORM_SCRIPT.replace("{contact}", CONTACT) if spec.get("form") else "")
        + '</body>\n</html>\n'
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
