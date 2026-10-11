#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offex Mail - AdSense readiness fix.
Runs from the repo root (CI: `python3 tools/adsense_fix.py`).

  Task 1  new AdSense publisher id everywhere + ads.txt
  Task 2  remove keywords meta, soften over-claiming titles / copy
  Task 3  homepage long-form content, blog/guides, service-page de-thinning
  Task 4  sitemap

Idempotent: every content injection is guarded by a marker.
"""
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PUB = os.path.join(ROOT, "public")

OLD_ID = "7802179098119853"
NEW_ID = "9424904813990636"
NEW_LINE = "google.com, pub-%s, DIRECT, f08c47fec0942fa0" % NEW_ID

report = []


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write(path, s):
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


def html_files():
    out = []
    for r, _d, fs in os.walk(PUB):
        for f in fs:
            if f.endswith(".html"):
                out.append(os.path.join(r, f))
    return sorted(out)


def all_text_files():
    """Every file that decodes as UTF-8 text (skips apk/png/ico/woff...)."""
    out = []
    for r, _d, fs in os.walk(PUB):
        for f in fs:
            p = os.path.join(r, f)
            try:
                with open(p, "rb") as fh:
                    fh.read().decode("utf-8")
            except Exception:
                continue
            out.append(p)
    return sorted(out)


def visible_words(s):
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&[a-z]+;|&#\d+;", " ", s)
    return len([w for w in s.split() if any(c.isalnum() for c in w)])


# --------------------------------------------------------------------------
# TASK 1 - publisher id
# --------------------------------------------------------------------------
def task1():
    changed = 0
    for p in all_text_files():
        s = read(p)
        if OLD_ID in s:
            write(p, s.replace(OLD_ID, NEW_ID))
            changed += 1
    # ads.txt exact line
    ads = os.path.join(PUB, "ads.txt")
    write(ads, (
        "# Offex Mail - ads.txt\n"
        "# Authorized Digital Sellers (Google AdSense).\n"
        "#\n"
        "# This is the seller line AdSense gives you for this site.\n"
        "# Do not edit it by hand; keep exactly one line per publisher id.\n"
        "\n"
        + NEW_LINE + "\n"
    ))
    report.append("TASK1: replaced old id in %d files; ads.txt rewritten." % changed)


# --------------------------------------------------------------------------
# TASK 2 - keywords meta + over-claiming copy
# --------------------------------------------------------------------------
KW_RE = re.compile(r'\s*<meta\s+name=["\']keywords["\'][^>]*>', re.I)

# parentheticals that carry an over-claim, incl. fullwidth parens (zh/ja)
CLAIM_RE = re.compile(
    r"\s*[（(][^（()）]*(?:100%|85%|يعمل|работает|funciona|funktion|fonctionnel|"
    r"काम कर|可用|使え|функцион|käyt|werkt)[^（()）]*[）)]"
)


def clean_head(s):
    s = KW_RE.sub("", s)

    # <title>: drop claim parenthetical + trailing brand suffix
    def fix_title(m):
        t = m.group(1)
        t = CLAIM_RE.sub("", t)
        t = re.sub(r"\s*\|\s*Offex Mail\s*$", "", t)
        t = re.sub(r"\s{2,}", " ", t).strip()
        return "<title>%s</title>" % t
    s = re.sub(r"<title>(.*?)</title>", fix_title, s, flags=re.S)

    # og:title / twitter:title: drop claim parenthetical only
    s = re.sub(
        r'(<meta\s+(?:property="og:title"|name="twitter:title")\s+content=")([^"]*)(")',
        lambda m: m.group(1) + CLAIM_RE.sub("", m.group(2)) + m.group(3), s)

    # meta description / og:description / twitter:description
    def fix_desc(m):
        d = m.group(2)
        d = d.replace(", 100% working disposable inbox for", " - a disposable inbox for")
        d = d.replace(", 85% working disposable inbox for", " - a disposable inbox for")
        d = re.sub(r"\s*\|\s*Offex Mail\s*$", "", d)
        d = re.sub(r"\s{2,}", " ", d).strip()
        return m.group(1) + d + m.group(3)
    s = re.sub(
        r'(<meta\s+(?:name="description"|property="og:description"|name="twitter:description")\s+content=")([^"]*)(")',
        fix_desc, s)

    # h1 over-claims
    s = s.replace("100% Working Free Disposable Email", "Free Disposable Email")
    s = s.replace("85% Working Free Disposable Email", "Free Disposable Email")
    s = s.replace("100% working Free Disposable Email", "Free Disposable Email")
    # localised h1
    s = s.replace(" — 100% काम करने वाला मुफ़्त डिस्पोज़ेबल ईमेल", " — मुफ़्त डिस्पोज़ेबल ईमेल")
    s = s.replace(" — Correo desechable gratis 100% funcional", " — Correo desechable gratis")
    s = s.replace(" — E-mail jetable gratuit 100% fonctionnel", " — E-mail jetable gratuit")
    s = s.replace(" — 100% funktionierende kostenlose Wegwerf-E-Mail", " — Kostenlose Wegwerf-E-Mail")
    s = s.replace(" — E-mail descartável grátis 100% funcional", " — E-mail descartável grátis")
    s = s.replace(", работает 100%", "")
    s = s.replace(" يعمل 100%", "")
    s = s.replace(" — 100% 可用的免费一次性邮箱", " — 免费一次性邮箱")
    s = s.replace(" — 100% 使える無料の使い捨てメール", " — 無料の使い捨てメール")

    # leftover claim wording in body copy / JSON-LD
    s = s.replace("100% free", "free").replace("100% Free", "Free")
    s = s.replace("Yes — free. No account, no payment, no limits.",
                  "Yes - it is free. No account, no payment and no hidden charges.")
    return s


def task2():
    n_kw = n_t = 0
    for p in html_files():
        s = read(p)
        before = s
        s = clean_head(s)
        if 'name="keywords"' in before:
            n_kw += 1
        if s != before:
            n_t += 1
            write(p, s)
    report.append("TASK2: removed keywords meta from %d pages; softened head/copy on %d pages."
                  % (n_kw, n_t))


# --------------------------------------------------------------------------
# TASK 2b - i18n.js softening
# --------------------------------------------------------------------------
I18N_REPL = [
    ("Temp Mail for ElevenLabs (11Labs) — 85% Working",
     "Temp Mail for ElevenLabs (11Labs) — Free Disposable Email"),
    ("<b>85% working</b> • free • instant • no signup",
     "<b>free</b> • instant • no signup"),
    ("Yes — 100% free. No account, no payment, no limits.",
     "Yes — it is free. No account, no payment, no hidden charges."),
    ("ElevenLabs (11Labs) ke liye Temp Mail — 85% Working",
     "ElevenLabs (11Labs) ke liye Temp Mail — free disposable email"),
    ("<b>85% working temp mail</b> • free • instant • no signup",
     "<b>free temp mail</b> • instant • no signup"),
    ("हाँ — 100% फ्री। कोई अकाउंट नहीं, कोई पेमेंट नहीं।",
     "हाँ — यह फ्री है। कोई अकाउंट नहीं, कोई पेमेंट नहीं।"),
    ("Correo temporal para ElevenLabs (11Labs) — 85% funcional",
     "Correo temporal para ElevenLabs (11Labs) — correo desechable gratis"),
    ("<b>85% funcional</b> • gratis • instantáneo • sin registro",
     "<b>gratis</b> • instantáneo • sin registro"),
    ("Sí — 100% gratis. Sin cuenta, sin pago, sin límites.",
     "Sí — es gratis. Sin cuenta, sin pago, sin límites."),
    ("Mail temporaire pour ElevenLabs (11Labs) — 85 % fonctionnel",
     "Mail temporaire pour ElevenLabs (11Labs) — e-mail jetable gratuit"),
    ("<b>85 % fonctionnel</b> • gratuit • instantané • sans inscription",
     "<b>gratuit</b> • instantané • sans inscription"),
    ("Oui — 100% gratuit. Sans compte, sans paiement, sans limite.",
     "Oui — c'est gratuit. Sans compte, sans paiement, sans limite."),
    ("Temp-Mail für ElevenLabs (11Labs) — 85 % funktionsfähig",
     "Temp-Mail für ElevenLabs (11Labs) — kostenlose Wegwerf-E-Mail"),
    ("<b>85 % funktionsfähig</b> • kostenlos • sofort • ohne Anmeldung",
     "<b>kostenlos</b> • sofort • ohne Anmeldung"),
    ("Ja — 100% kostenlos. Kein Konto, keine Zahlung, keine Limits.",
     "Ja — es ist kostenlos. Kein Konto, keine Zahlung, keine Limits."),
    ("E-mail temporário para ElevenLabs (11Labs) — 85% funcional",
     "E-mail temporário para ElevenLabs (11Labs) — e-mail descartável grátis"),
    ("<b>85% funcional</b> • grátis • instantâneo • sem cadastro",
     "<b>grátis</b> • instantâneo • sem cadastro"),
    ("Sim — 100% grátis. Sem conta, sem pagamento, sem limites.",
     "Sim — é grátis. Sem conta, sem pagamento, sem limites."),
    ("Временная почта для ElevenLabs (11Labs) — работает на 85%",
     "Временная почта для ElevenLabs (11Labs) — бесплатная одноразовая почта"),
    ("<b>работает на 85%</b> • бесплатно • мгновенно • без регистрации",
     "<b>бесплатно</b> • мгновенно • без регистрации"),
    ("Да — 100% бесплатно. Без аккаунта и оплаты.",
     "Да — это бесплатно. Без аккаунта и оплаты."),
    ("بريد مؤقت لـ ElevenLabs (11Labs) — يعمل 85%",
     "بريد مؤقت لـ ElevenLabs (11Labs) — بريد مجاني لمرة واحدة"),
    ("<b>يعمل 85%</b> • مجاني • فوري • بدون تسجيل",
     "<b>مجاني</b> • فوري • بدون تسجيل"),
    ("نعم — مجاني 100%. بلا حساب أو دفع أو حدود.",
     "نعم — مجاني. بلا حساب أو دفع أو حدود."),
    ("ElevenLabs (11Labs) 临时邮箱 — 85% 可用",
     "ElevenLabs (11Labs) 临时邮箱 — 免费一次性邮箱"),
    ("<b>85% 可用</b> • 免费 • 即时 • 无需注册",
     "<b>免费</b> • 即时 • 无需注册"),
    ("是的——100% 免费。无需账号、无需付费、无限制。",
     "是的——免费。无需账号、无需付费、无限制。"),
    ("ElevenLabs（11Labs）用の一時メール — 85% 使えます",
     "ElevenLabs（11Labs）用の一時メール — 無料の使い捨てメール"),
    ("<b>85% 使えます</b> • 無料 • 即時 • 登録不要",
     "<b>無料</b> • 即時 • 登録不要"),
    ('p_tag:"100% ', 'p_tag:"'),
    ('p_tag:"مجاني 100%"', 'p_tag:"مجاني"'),
]


def task2b():
    p = os.path.join(PUB, "i18n.js")
    s = read(p)
    for a, b in I18N_REPL:
        s = s.replace(a, b)
    write(p, s)
    report.append("TASK2b: softened i18n.js strings.")


# --------------------------------------------------------------------------
# TASK 2c - homepage <title> / description
# --------------------------------------------------------------------------
HOME_TITLE = "Offex Mail — Free Temporary Email & Disposable Inbox"
HOME_DESC = ("Offex Mail gives you a free, instant disposable email address to receive "
             "OTPs, verification links and sign-up mail — no signup, no password and "
             "nothing left behind in your real inbox.")


def task2c():
    p = os.path.join(PUB, "index.html")
    s = read(p)
    s = re.sub(r"<title>.*?</title>", "<title>%s</title>" % HOME_TITLE, s, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + HOME_DESC + m.group(2), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + HOME_DESC + m.group(2), s, count=1)
    s = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")',
               lambda m: m.group(1) + HOME_DESC + m.group(2), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
               lambda m: m.group(1) + HOME_TITLE + m.group(2), s, count=1)
    write(p, s)
    report.append("TASK2c: rewrote homepage title + description.")


# --------------------------------------------------------------------------
# TASK 2d - make sure every page carries the AdSense snippet; unique app title
# --------------------------------------------------------------------------
SNIPPET = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/'
           'adsbygoogle.js?client=ca-pub-%s" crossorigin="anonymous"></script>' % NEW_ID)


def task2d():
    added = []
    for p in html_files():
        s = read(p)
        if "adsbygoogle.js?client=ca-pub-" + NEW_ID in s:
            continue
        if "</head>" in s:
            s = s.replace("</head>", SNIPPET + "\n</head>", 1)
            write(p, s)
            added.append(os.path.relpath(p, PUB))
    ap = os.path.join(PUB, "app-privacy.html")
    if os.path.exists(ap):
        s = read(ap)
        s = s.replace("<title>Offex Mail - Privacy Policy</title>",
                      "<title>Offex Mail App — Privacy Policy</title>")
        write(ap, s)
    report.append("TASK2d: added AdSense snippet to %d page(s): %s" % (len(added), ", ".join(added)))


# --------------------------------------------------------------------------
# TASK 3a - homepage long-form content
# --------------------------------------------------------------------------
HOME_CONTENT = '''<!-- offex-learn-start -->
<style>
  .learn{padding:56px 0}
  .learn .wrap{max-width:900px}
  .learn h2{font-size:clamp(22px,3.4vw,32px);font-weight:900;letter-spacing:-.6px;margin:0 0 14px}
  .learn h3{font-size:18px;font-weight:800;margin:26px 0 8px}
  .learn p{color:var(--muted);font-size:15.5px;line-height:1.75;margin:0 0 14px}
  .learn ul,.learn ol{color:var(--muted);font-size:15.5px;line-height:1.75;padding-left:22px;margin:0 0 16px}
  .learn li{margin:6px 0}
  .learn a{color:var(--accent);font-weight:600;text-decoration:none}
  .learn a:hover{text-decoration:underline}
  .learn .gloss dt{font-weight:800;color:var(--text);margin-top:14px}
  .learn .gloss dd{margin:2px 0 0;color:var(--muted);font-size:15px;line-height:1.7}
  .learn .cards{display:grid;gap:12px;grid-template-columns:1fr;margin:12px 0 4px}
  @media(min-width:640px){.learn .cards{grid-template-columns:1fr 1fr}}
  .learn .cards a{display:block;border:1px solid var(--border);border-radius:16px;padding:16px 18px;background:var(--surface);color:inherit;text-decoration:none}
  .learn .cards a:hover{border-color:var(--border2);text-decoration:none}
  .learn .cards a b{display:block;font-size:15.5px;margin-bottom:4px;color:var(--text)}
  .learn .cards a small{color:var(--muted)}
  .learn .faq{margin-top:8px}
</style>

<section class="learn" id="learn">
 <div class="wrap">

  <h2>What is a temporary email address?</h2>
  <p>A temporary email address — also called a temp mail, disposable email, throwaway email or burner inbox — is a working email address you can use immediately and then throw away. It is not tied to your name, your phone number or an account you have to maintain. You open Offex Mail, an address is generated for you on the spot, and you can start receiving mail at it within seconds. When you are done you close the tab, and the inbox and everything in it disappears on its own.</p>
  <p>Every address here runs on Offex Mail's own domain, <strong>mytemp-mail.online</strong>, so what you get is a real, deliverable mailbox rather than something that merely looks like an email address. That matters more than it sounds: many websites quietly reject obvious throwaway domains, and a real domain that accepts mail passes those checks far more often.</p>

  <h3>How a disposable inbox works under the hood</h3>
  <p>A temp mail service is really a mail server with a catch-all rule. Instead of one mailbox per person, the server accepts mail for any address on its domain — <em>random-name@mytemp-mail.online</em>, <em>my-test@mytemp-mail.online</em> and so on — and routes it to the inbox you are viewing. The moment a message arrives the page is told about it and the message appears, usually within a couple of seconds. Nothing is installed and there is no password to remember, because there is no account to log into.</p>
  <p>When an inbox expires, its messages are deleted. That short lifetime is the whole point: a disposable address is meant to be useful for minutes, not years.</p>

  <h2>When should you use a temp mail?</h2>
  <p>A temporary inbox is the right tool whenever a site wants an email address but you do not want a lasting relationship with that site. Typical cases:</p>
  <ul>
   <li><strong>One-off signups and free trials.</strong> Try a service, a template pack or an AI tool without handing over the address your friends and bank use.</li>
   <li><strong>Gated downloads.</strong> When a PDF, cheat-sheet or webinar only unlocks after you "enter your email", a throwaway address gets you the file without the follow-up marketing.</li>
   <li><strong>Testing your own product.</strong> Developers use temp mail to walk through signup, confirmation and password-reset flows again and again without creating real accounts.</li>
   <li><strong>Coupons and first-order discounts.</strong> New-customer codes often work once per email, so a fresh address is handy for a legitimate second purchase.</li>
   <li><strong>Shared or public devices.</strong> If you would rather not type your real address into a computer you do not own, use a disposable one.</li>
  </ul>
  <p>It is just as important to know when <em>not</em> to use one: banking, payments and government services; accounts you will need to recover later or that hold data you care about; and anything you might turn into a paid, long-term subscription.</p>

  <h2>How to keep your real inbox safe</h2>
  <p>Your primary inbox is the master key to your online life — it is where password resets land. Every site you give it to is another place that can leak it, sell it or spam it. A few habits keep it clean:</p>
  <ul>
   <li><strong>Default to disposable.</strong> If you are not sure a site deserves your real address, it doesn't — use a temp mail first.</li>
   <li><strong>Separate your identities.</strong> Keep one address for people, one for shopping and services, and use temp mail for everything you are only trying.</li>
   <li><strong>Never reuse passwords.</strong> A throwaway inbox does not make a weak password safe; use a password manager.</li>
   <li><strong>Watch for breach alerts.</strong> If a site you used a temp address for is breached, nothing important is exposed.</li>
   <li><strong>Read before you click.</strong> A temp inbox shows every message, including phishing — treat unexpected "verify your account" mail with suspicion.</li>
  </ul>

  <h2>How to receive an OTP or verification code</h2>
  <p>Receiving a one-time passcode on a temporary address works the same way as on any mailbox:</p>
  <ol>
   <li>Open Offex Mail and create an inbox, or type a custom name you will recognise.</li>
   <li>Copy the address shown at the top of the page.</li>
   <li>Paste it into the site that is asking for your email, then submit the form so the code is sent.</li>
   <li>Watch the inbox — it refreshes automatically and plays a chime when new mail arrives.</li>
   <li>Open the message and either copy the code back into the site or tap the confirmation link.</li>
  </ol>
  <p>Most codes arrive within seconds. If one does not, ask the site to resend it, wait two full minutes, and double-check the address for a stray space. Some services refuse disposable domains outright, or require a phone number as well — in that case the temp address simply is not the right tool for that account.</p>

  <h2>Is temp mail safe to use?</h2>
  <p>For its intended job — one-time signups, trials, downloads and testing — a disposable inbox is a sensible privacy tool, not a risky one. It keeps your real address out of marketing lists and data-broker databases, and it leaves nothing behind. Two limits are worth stating plainly. First, a temp inbox is public in the sense that anyone who knows the address can read what arrives there, so never let sensitive mail, receipts or reset links for important accounts go to one. Second, because the inbox expires you cannot use it to recover an account later. Treat it as a burner and it will behave exactly as you expect.</p>

  <h2>Temp mail vs. a second email account</h2>
  <p>People often ask whether a spare Gmail account is not simply better. It depends on the job.</p>
  <ul>
   <li><strong>Setup:</strong> a temp address is ready in one click; a second account needs a phone number, a password and often a recovery email.</li>
   <li><strong>Cleanup:</strong> a temp inbox deletes itself; a spare account lives forever and slowly fills with spam you then have to manage.</li>
   <li><strong>Anonymity:</strong> a temp address asks for nothing about you; a second account is tied to your phone and device.</li>
   <li><strong>Durability:</strong> a second account is recoverable and permanent — exactly what you want for anything you will keep.</li>
  </ul>
  <p>The practical answer: use temp mail for anything you are only trying, and keep one permanent secondary address for the handful of services you actually keep using.</p>

  <h2>What Offex Mail does with your mail</h2>
  <p>Offex Mail is built to be boring about data. Messages live only inside the inbox you are looking at, and they are removed when that inbox expires. There is no account, so there is no profile to build; the address you use is not linked to your name, your device or your real email. We do not sell or share inbox contents, and we do not ask you for a phone number. The trade-off is the one described above: a disposable inbox is for short-lived mail, not for anything you will need to find again months from now.</p>

  <h2>Popular services you can verify with a temp mail</h2>
  <p>Disposable inboxes work for the signup step of most consumer apps and websites — social networks, streaming services, marketplaces, AI tools and developer platforms. We publish a short, human-written guide for each popular service, covering exactly what that site asks for during signup and the little gotchas that make a code go missing. Browse the full list on the <a href="/services">services page</a>, or start with a few favourites: <a href="/instagram">Instagram</a>, <a href="/discord">Discord</a>, <a href="/chatgpt">ChatGPT</a>, <a href="/github">GitHub</a> and <a href="/spotify">Spotify</a>.</p>

  <h2>Guides and how-tos</h2>
  <p>For a deeper read, our guides explain the ideas behind disposable email:</p>
  <div class="cards">
   <a href="/blog/sms-free-email-verification"><b>How to receive email verification without a phone</b><small>Which services still insist on SMS — and what to do about it.</small></a>
   <a href="/blog/protecting-your-primary-inbox"><b>Protecting your primary inbox from spam</b><small>A practical routine for keeping your real address clean.</small></a>
   <a href="/blog/how-disposable-inboxes-work"><b>How disposable inboxes work under the hood</b><small>Catch-all mail servers, routing and expiry, explained simply.</small></a>
   <a href="/blog/temp-mail-vs-second-email"><b>Temp mail vs a second email account</b><small>When a burner beats a spare Gmail — and when it does not.</small></a>
   <a href="/blog/temp-mail-safety-guide"><b>Is temp mail safe? A straight answer</b><small>What a disposable inbox protects, and what it cannot.</small></a>
   <a href="/blog/"><b>All guides</b><small>The Offex Mail blog index.</small></a>
  </div>

  <h2>Temp mail glossary</h2>
  <dl class="gloss">
   <dt>Temp mail</dt><dd>A free, short-lived email address used to receive mail without exposing your real inbox.</dd>
   <dt>Disposable inbox</dt><dd>The mailbox behind a temp address; it is deleted automatically once it expires.</dd>
   <dt>Throwaway / burner address</dt><dd>Informal names for the same idea — an address you intend to abandon.</dd>
   <dt>OTP</dt><dd>One-time password: the short code many sites send to confirm a signup or login.</dd>
   <dt>Verification link</dt><dd>A unique URL emailed to confirm that the address is real and reachable.</dd>
   <dt>Domain</dt><dd>The part after the @ sign. Offex Mail runs on its own domain, mytemp-mail.online.</dd>
   <dt>Catch-all</dt><dd>A mail-server rule that accepts messages for any address on the domain, which is what lets a temp service create addresses on demand.</dd>
   <dt>Expiry</dt><dd>The point at which an inbox and its messages are removed.</dd>
  </dl>

  <h2>More questions about temp mail</h2>
  <div class="faq">
   <details class="q reveal"><summary>Will a website know I used a temp address?</summary><div class="a">Sometimes. Some sites check against lists of known disposable domains and may block them, and a few ask for a phone number as well. When that happens, the address is not the right fit for that account.</div></details>
   <details class="q reveal"><summary>Can I send email from a temp address?</summary><div class="a">Offex Mail is built for receiving, which is exactly what signups and verification codes need. For two-way conversations, use a real mailbox.</div></details>
   <details class="q reveal"><summary>How long should I wait for a verification code?</summary><div class="a">Most arrive in seconds. If nothing shows after two minutes, request a new code and re-check the address you entered for a stray space or a wrong letter.</div></details>
   <details class="q reveal"><summary>Can I choose my own temp email name?</summary><div class="a">Yes. Type a custom name before you create the inbox; if it is free, you get it. Otherwise a random address is created for you.</div></details>
   <details class="q reveal"><summary>Do I need to install anything?</summary><div class="a">No. It works in any modern browser on desktop and mobile, and there is an optional Android app if you want new-mail alerts.</div></details>
   <details class="q reveal"><summary>Is there a limit on how many inboxes I can create?</summary><div class="a">You can create as many as you need for normal personal use. Please do not abuse the service.</div></details>
  </div>

 </div>
</section>
<!-- offex-learn-end -->'''


def task3a():
    p = os.path.join(PUB, "index.html")
    s = read(p)
    if "offex-learn-start" in s:
        report.append("TASK3a: homepage content already present, skipped.")
        return
    before = visible_words(s)
    s = s.replace("</main>", HOME_CONTENT + "\n</main>", 1)
    write(p, s)
    after = visible_words(s)
    report.append("TASK3a: homepage visible words %d -> %d (+%d)." % (before, after, after - before))


# --------------------------------------------------------------------------
# TASK 3b - de-thin the English service pages that lack a unique section
# --------------------------------------------------------------------------
SERVICE_EXTRA = {
 "adobe.html": (
  "What Adobe's signup actually asks for",
  "Creating an Adobe ID needs an email address and a password, and Adobe emails a verification code before the account becomes usable. The free Creative Cloud plan and the seven-day trials for apps such as Photoshop, Illustrator and Premiere Pro all sit behind that same signup, and Adobe tends to follow up with product and offer mail afterwards &mdash; a good reason to keep it off your main inbox.",
  "Adobe sometimes asks for a payment method when a trial begins, so read the trial terms carefully and remember that cancelling in time is your responsibility. If the code does not arrive, request it again and confirm the address you typed; Adobe quietly drops malformed addresses."),
 "airbnb.html": (
  "What Airbnb's signup actually asks for",
  "Airbnb asks for your email, your name and a date of birth to create a guest account, then sends a confirmation link. Hosting an apartment asks for much more &mdash; identity checks, a phone number and payout details &mdash; so a disposable address is only sensible for the browsing-and-booking side, not for a host profile you will be paid through.",
  "The usual snag is the confirmation link: Airbnb may open it inside the app rather than confirming in the browser, so if the link misbehaves, copy the code or paste the URL into a desktop browser. Booking confirmations and receipts should always go to an address you keep."),
 "aliexpress.html": (
  "What AliExpress's signup actually asks for",
  "AliExpress wants an email address to create a buyer account and sends a numeric verification code to confirm it. New-user coupons and welcome discounts are tied to that signup, which is why a fresh address is popular with shoppers testing the platform for the first time.",
  "The catch is the phone step: AliExpress frequently asks for a mobile number as well, and it may refuse to complete checkout without one. If your only goal is to browse or claim a first-order code, a temp address works; if you plan to buy and track orders, use an address you can reach later."),
 "apple.html": (
  "What an Apple ID signup actually asks for",
  "An Apple ID needs an email address, a password and, in most regions, a phone number for two-factor authentication. Apple emails a verification code to the address you enter, and it also uses that address for receipts, iCloud and the App Store.",
  "This is one account where a disposable inbox deserves caution. An Apple ID is hard to live without and even harder to recover once you lose the inbox behind it, so use a temp address only for a throwaway test sign-in. For a real device, use a permanent address."),
 "canva.html": (
  "What Canva's signup actually asks for",
  "Canva's signup is refreshingly light: an email address, a password, and a short verification step. You can also start with a Google, Facebook or Apple login, in which case Canva never asks for an email at all. The free tier is generous, which is why so many people try it before committing.",
  "Canva sends a confirmation link and a welcome mail with template suggestions. There is no phone requirement, so a temp address clears the signup easily. Just remember that anything you save lives in that Canva account, so migrate to a permanent address before you build a real project."),
 "chatgpt.html": (
  "What ChatGPT's signup actually asks for",
  "OpenAI's signup asks for an email address and a password, then sends a confirmation link to prove the address is real. In many regions OpenAI also asks for a phone number for verification, and it limits how many accounts one number can create.",
  "That phone step is the one to watch: if OpenAI demands a number, a temp address alone will not get you through, and you should not try to dodge the requirement. When the email step is all that is needed, a disposable inbox handles it cleanly &mdash; but treat the account as temporary and never store anything important in it."),
 "dropbox.html": (
  "What Dropbox's signup actually asks for",
  "Dropbox wants an email address and a password, and sends a verification link to confirm it. The free plan gives you a few gigabytes of storage, and Dropbox is quick to email tips, referral offers and upgrade prompts once you are in.",
  "The signup itself has no phone requirement, so a temp address works for a quick trial. Do keep in mind that anything you upload lives in that account: if you intend to store files you care about, use an address you control so you can always sign back in."),
 "ebay.html": (
  "What eBay's signup actually asks for",
  "eBay asks for an email address, a password and a username, then sends a confirmation code. Registering as a buyer is straightforward; selling adds identity verification and payout details that a disposable address cannot cover.",
  "eBay often requests a phone number during registration and may use it for security checks on later logins. For browsing and a one-off purchase a temp address is fine, but auction wins, refunds and disputes all depend on mail you can still read, so switch to a permanent address before you buy."),
 "github.html": (
  "What GitHub's signup actually asks for",
  "GitHub needs an email address, a password and a username, and sends a verification link. It then nudges you to enable two-factor authentication, which in practice means keeping access to the email you signed up with.",
  "Because a GitHub account often becomes a developer's public identity &mdash; repositories, issues and commit history &mdash; a disposable inbox is best reserved for throwaway test accounts. For anything you will actually push code to, use an address you control and turn on 2FA."),
 "gitlab.html": (
  "What GitLab's signup actually asks for",
  "GitLab asks for a name, a username and an email address, then emails a confirmation link before the account is active. Self-hosted and SaaS instances behave the same way, and GitLab frequently asks new users to set up two-factor authentication.",
  "The confirmation link is the only email GitLab strictly needs, so a temp address passes signup. As with any developer platform, though, your account is tied to that inbox for password resets and security alerts &mdash; use a permanent address for repositories you intend to keep."),
 "microsoft.html": (
  "What a Microsoft account signup actually asks for",
  "A Microsoft account needs an email address, a password and a date of birth, and Microsoft sends a verification code. Signing into Windows, Office, Xbox and OneDrive all route through this single account, which makes it more important than most.",
  "Microsoft usually asks for a phone number for two-factor authentication and account recovery. That combination &mdash; a phone requirement plus long-term importance &mdash; means a disposable inbox is only a good fit for a throwaway test account, never for the Microsoft account that unlocks your PC."),
 "notion.html": (
  "What Notion's signup actually asks for",
  "Notion asks for an email address and a password, or lets you continue with Google or Apple, then sends a short verification code. New workspaces start on the free personal plan and Notion emails onboarding tips and template suggestions.",
  "The signup has no phone step, so a temp address works for a quick look. Notion is a place people store notes and plans they want back, so if you decide to keep using it, move to an address you control before you fill the workspace with anything valuable."),
 "openai.html": (
  "What an OpenAI account signup actually asks for",
  "OpenAI's signup wants an email address and a password, followed by a confirmation link. It often requires a phone number as well, and the platform emails usage notices and billing receipts once you add a payment method.",
  "If OpenAI insists on a phone number, a temp address will not get you through on its own, and you should not try to work around that requirement. When only the email step is required, a disposable inbox clears it &mdash; but keep API keys and billing off an account whose inbox will vanish."),
 "paypal.html": (
  "Why PayPal is different",
  "PayPal is a financial account, and it should not be created with a disposable inbox. Money, refunds, disputes and identity checks all depend on mail you can read for years, and losing access to the address behind a PayPal account can lock you out of your own balance.",
  "If you only want to see how PayPal's signup form looks, a temp address can display it, but stop there &mdash; do not link a bank card, send or receive money, or treat the account as real. For any genuine PayPal use, sign up with a permanent email and protect it with two-factor authentication."),
 "playstation.html": (
  "What a PlayStation Network signup actually asks for",
  "A PSN account needs an email address, a password, a date of birth and a country, and Sony sends a verification link before the account is active. PSN ties together purchases, trophies and subscriptions, and it also sends security alerts to that address.",
  "Sony often nudges you towards two-factor authentication, and any digital purchases live in the account permanently. A temp address handles the signup, but a PSN account is a long-term thing &mdash; use an address you control if you intend to buy games or keep your progress."),
 "shopify.html": (
  "What a Shopify signup actually asks for",
  "Shopify asks for an email address, a password and a store name, then emails a confirmation. The free trial gives you a full storefront for a limited time, and Shopify follows up with setup tips, app suggestions and trial reminders.",
  "Running a store means customers, orders and payouts &mdash; none of which belong behind an inbox that disappears. A temp address is fine for exploring the admin and seeing whether the platform suits you, but move to a permanent address before you take a single real order."),
 "slack.html": (
  "What a Slack signup actually asks for",
  "Slack asks for an email address and sends a six-character confirmation code. You can create a new workspace or join an existing one, and Slack emails invitations, notifications and password-reset links to that address.",
  "The signup has no phone requirement, so a temp address works for trying the product or joining a throwaway workspace. A workspace that your team actually depends on, however, should sit behind an address the whole team can keep &mdash; Slack recovery runs through email."),
 "twitter.html": (
  "What Twitter / X's signup actually asks for",
  "Twitter (now X) asks for a name, an email or phone number, a date of birth and a password, then sends a confirmation code to the email you gave. It also emails login alerts and security notices to that address.",
  "X frequently asks for a phone number, especially if you create more than one account or trigger its spam checks. When the email step is enough, a temp address handles it &mdash; but a handle you intend to keep should use an address you can always recover."),
 "x.html": (
  "What X's signup actually asks for",
  "X (the platform formerly called Twitter) needs a name, an email or phone number, a date of birth and a password, and it emails a short confirmation code to verify the address. Login alerts and security notices also go to that inbox.",
  "Expect a phone-number prompt, particularly on a second account or after an unusual signup. If X lets you through on email alone, a disposable inbox does the job; if you plan to keep the handle, use an address you control so you can reset the password later."),
 "xbox.html": (
  "What an Xbox account signup actually asks for",
  "An Xbox account is a Microsoft account, so it needs an email address, a password and a date of birth, followed by a verification code. The same login covers Game Pass, cloud saves and any purchases you make on the console.",
  "Microsoft leans on phone-based two-factor authentication and account recovery, and a gamertag with purchases is hard to replace. A temp address is fine for a spare test profile, but your main Xbox identity should live on an address you will still have next year."),
 "zoom.html": (
  "What Zoom's signup actually asks for",
  "Zoom asks for an email address, a name and a password, or lets you sign in with Google or Facebook, then emails a confirmation. Free accounts can host meetings up to a set time limit, and Zoom emails recaps, recordings and product news.",
  "There is no phone requirement for a basic account, so a temp address clears signup. Meetings themselves do not depend on your email, but password resets and billing do &mdash; use an address you control if you host meetings you care about."),
}


def task3b():
    done = []
    for fname, (h2, p1, p2) in SERVICE_EXTRA.items():
        p = os.path.join(PUB, fname)
        if not os.path.exists(p):
            continue
        s = read(p)
        if "offex-extra-en" in s:
            continue
        block = ('<!-- offex-extra-en -->\n  <section class="card">\n'
                 '    <h2>%s</h2>\n    <p>%s</p>\n    <p>%s</p>\n  </section>\n' % (h2, p1, p2))
        s = s.replace("</main>", block + "\n</main>", 1)
        write(p, s)
        done.append(fname)
    report.append("TASK3b: added a unique section to %d English service pages: %s"
                  % (len(done), ", ".join(done)))


# --------------------------------------------------------------------------
# TASK 3c - blog / guides
# --------------------------------------------------------------------------
BLOG_HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ | Offex Mail</title>
<meta name="description" content="__DESC__">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://mytemp-mail.online/blog/__SLUG__">
<link rel="icon" href="/favicon.ico" sizes="any">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Offex Mail">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="https://mytemp-mail.online/blog/__SLUG__">
<meta name="twitter:card" content="summary">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-__PUB__" crossorigin="anonymous"></script>
<style>
:root{--accent:#6d4dff;--ink:#1a1730;--muted:#5b5776;--bg:#f6f4ff;--card:#fff;--line:#e8e4ff}
*{box-sizing:border-box}
body{margin:0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.7;-webkit-font-smoothing:antialiased;overflow-wrap:break-word}
a{color:var(--accent)}
header.site{display:flex;align-items:center;justify-content:space-between;gap:12px;max-width:820px;margin:0 auto;padding:16px}
.brand{font-weight:800;text-decoration:none;color:var(--ink)}
.brand span{color:var(--accent)}
.nav a{color:var(--muted);text-decoration:none;font-size:.9rem;margin-left:14px}
.wrap{max-width:820px;margin:0 auto;padding:8px 16px 56px}
.hero{background:linear-gradient(135deg,#6d4dff,#9b6dff);color:#fff;border-radius:18px;padding:30px 22px;margin-bottom:22px}
.hero h1{margin:0;font-size:1.6rem;line-height:1.3;letter-spacing:-.02em}
.hero .meta{opacity:.9;font-size:.85rem;margin-top:8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;box-shadow:0 6px 24px rgba(80,60,180,.07)}
h2{font-size:1.25rem;margin:1.5em 0 .5em}
h3{font-size:1.05rem;margin:1.2em 0 .35em}
p{margin:.7em 0}
ul,ol{padding-left:1.25em}
li{margin:.4em 0}
.cta{display:inline-block;background:linear-gradient(135deg,#6d4dff,#9b6dff);color:#fff;text-decoration:none;font-weight:700;padding:13px 24px;border-radius:12px;margin:8px 0}
.related{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
.related a{font-size:.9rem;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:6px 12px;background:#fff}
footer{max-width:820px;margin:0 auto;padding:20px 16px 44px;color:var(--muted);font-size:.85rem;text-align:center}
footer a{text-decoration:none}
</style>
</head>
<body>
<header class="site"><a class="brand" href="/">Offex <span>Mail</span></a><nav class="nav"><a href="/blog/">Guides</a><a href="/">Open tool</a></nav></header>
<main class="wrap">
  <section class="hero"><h1>__H1__</h1><div class="meta">__META__</div></section>
  <article class="card">
__BODY__
    <p style="text-align:center;margin-top:22px"><a class="cta" href="/">Create a free inbox &rarr;</a></p>
  </article>
  <section class="card" style="margin-top:18px">
    <h2>More guides</h2>
    <ul class="related">__RELATED__</ul>
  </section>
</main>
<footer><p>Offex Mail &mdash; free temporary email &amp; disposable inbox. <a href="/">mytemp-mail.online</a></p>
<p><a href="/about">About</a> &middot; <a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a> &middot; <a href="/contact">Contact</a></p></footer>
<script src="/app-promo.js" defer></script>
</body>
</html>
'''

BLOG_ARTICLES = [
 ("sms-free-email-verification",
  "How to Receive Email Verification Without a Phone",
  "How to receive email verification without a phone, which services still insist on SMS, and what to do when a site asks for a number you would rather not give.",
  "Receiving verification without a phone number",
  "Updated for 2026 &middot; 4 min read",
  """<p>Almost every signup form today asks for one of two things: an email address or a phone number. Email is easy to keep private &mdash; you can hand over a disposable address and walk away. A phone number is not. It is tied to your identity, it follows you between services, and it is the one thing you cannot simply throw away after a signup. So a fair question is whether you can verify an account by email alone, and what to do when a site insists on SMS.</p>
<h2>Why sites ask for a phone number at all</h2>
<p>Phone numbers are a cheap way to slow down abuse. A disposable email address costs nothing to create, but a working phone number is harder to mass-produce, so services use it to limit fake accounts, spam and fraud. That logic is reasonable &mdash; and it is also why a number requirement usually cannot be waved away by clever tricks.</p>
<h2>When email alone is enough</h2>
<p>Plenty of services still confirm you by email and nothing else. A temporary inbox handles those perfectly: you create an address, paste it into the form, and read the confirmation code that lands seconds later. Consumer apps, newsletters, marketplaces, trial accounts and most developer tools fall into this group. If the form asks only for an email, a disposable address is the cleanest way to keep your real inbox out of it.</p>
<h2>When a phone number is genuinely required</h2>
<p>Other services treat the number as part of the account itself &mdash; banking, payments, messaging apps and a growing list of social platforms. When a service asks for a number for two-factor authentication or identity checks, that is a security feature, not a hurdle to sidestep. Trying to work around it, for example with public online SMS receivers, is unreliable and often against the service's terms, and it can leave you locked out of an account you cannot recover.</p>
<h2>What to do instead</h2>
<ul>
<li><strong>Use a number you control.</strong> If the account matters, give it your real number and turn on two-factor authentication. That is the trade the service is asking for, and it protects you as much as it protects them.</li>
<li><strong>Keep the account temporary.</strong> If you only need to look inside a product, use email verification and treat the account as disposable &mdash; do not put anything valuable in it.</li>
<li><strong>Separate the two.</strong> Use a disposable email for the signup and reserve your number for the few services that truly need it.</li>
</ul>
<h2>How a temp mail fits in</h2>
<p>The realistic picture is that email verification and phone verification solve different problems. A temporary email address is the right tool when a site only needs to prove that an address is real and reachable. It is the wrong tool when a site is deliberately using your phone as part of the account's security. Knowing which situation you are in saves a lot of frustration &mdash; and it keeps you on the right side of the services you use.</p>
<h2>A quick checklist before you sign up</h2>
<p>When a signup form appears, run through three questions in order. First, what is the form actually asking for &mdash; an email, a phone, or both? Second, do you need the account to survive longer than a day? Third, would you be upset to lose access to it? If the form only wants an email and the account is disposable, a temp mail is the fast, clean choice. If it wants a phone or the account matters, stop and use real details.</p>
<ul>
<li><strong>Email-only, throwaway:</strong> temp mail.</li>
<li><strong>Email-only, keep it:</strong> a real address you control.</li>
<li><strong>Phone required:</strong> your own number, no shortcuts.</li>
</ul>
<p>Most frustration with verification comes from mixing these up &mdash; giving a permanent address to a site you will never use again, or giving a burner to an account you will want back next month. Sorting the situation into one of the three buckets first makes the rest of the signup straightforward.</p>"""),

 ("protecting-your-primary-inbox",
  "Protecting Your Primary Inbox from Spam",
  "A practical routine for keeping your main email address clean, out of data-broker lists and away from the sites that sell it.",
  "Protecting your primary inbox from spam",
  "Updated for 2026 &middot; 5 min read",
  """<p>Your primary inbox is the most valuable account you own. It is where password resets land, where receipts arrive and where people you actually know reach you. That also makes it the most attractive target: every website you hand it to is another place that can leak it, sell it or flood it with marketing. The good news is that keeping it clean is mostly a matter of habits, not software.</p>
<h2>Understand where the spam comes from</h2>
<p>Most unwanted mail is not random. It arrives because your address was shared, sold or scraped somewhere along the way. Once an address is on a list, it gets copied between lists, and there is no way to remove it. That is why prevention beats cleanup: the fewer places that hold your real address, the less there is to leak.</p>
<h2>Use a disposable address by default</h2>
<p>The single most effective habit is to stop giving your real address to sites you do not fully trust. A temporary inbox lets you complete a signup, read the one confirmation email and move on, leaving nothing behind for a marketer to find. If you later decide a service deserves to stay in touch, you can always switch to a permanent address deliberately.</p>
<h2>Split your addresses by purpose</h2>
<p>Even with a temp mail in the mix, it helps to think in tiers. Keep one address for people and important accounts, one for shopping and everyday services, and use disposable inboxes for everything you are only trying. When one tier starts to fill with noise, you can retire it without disturbing the others.</p>
<h2>Habits that keep the noise down</h2>
<ul>
<li><strong>Unsubscribe, do not just delete.</strong> Legitimate senders honour unsubscribe links; deleting alone changes nothing.</li>
<li><strong>Never reuse passwords.</strong> Spam is annoying; a leaked password that works elsewhere is dangerous. Use a password manager.</li>
<li><strong>Turn on two-factor authentication</strong> for the accounts that matter most, so a leaked address is not enough on its own.</li>
<li><strong>Do not click "verify your account"</strong> in unexpected mail. Phishing copies the look of real notifications, so check the sender before you act.</li>
<li><strong>Watch breach notifications.</strong> If a site you used a temp address for is breached, your real inbox is untouched.</li>
</ul>
<h2>A simple routine</h2>
<p>Before you type your address anywhere, ask one question: do I want a lasting relationship with this site? If the answer is no, use a temporary inbox. If the answer is yes, give it your permanent address and take a minute to enable two-factor authentication. That one habit, repeated, will keep your primary inbox close to empty &mdash; and keep the mail that matters easy to find.</p>
<h2>What to do when the spam has already arrived</h2>
<p>If your inbox is already noisy, start with the biggest senders rather than the newest messages. Bulk senders &mdash; retailers, newsletters and app notifications &mdash; are almost always the bulk of the volume, and each one you unsubscribe from cuts a steady stream. Use the sender's own unsubscribe link where it is offered; for the genuinely unsolicited, mark the message as spam so your provider learns the pattern.</p>
<p>Then, quietly, move the sites you do not trust onto a fresh disposable address the next time they ask. You do not have to delete the old account; simply stop giving it your real address. Within a month or two the flow of new junk slows to a trickle, and the mail that remains is the mail you actually want.</p>"""),

 ("how-disposable-inboxes-work",
  "How Disposable Inboxes Work Under the Hood",
  "Catch-all mail servers, routing, expiry and the small technical decisions that make a temporary email service instant and self-cleaning.",
  "How disposable inboxes work under the hood",
  "Updated for 2026 &middot; 5 min read",
  """<p>To use a temp mail service you do not need to know anything about how it works. But understanding the machinery behind it explains a lot: why addresses appear instantly, why there is no password, and why the messages vanish on their own. Here is the short version, without the jargon.</p>
<h2>The catch-all idea</h2>
<p>An ordinary mail server has one mailbox per person. A temp mail server does the opposite: it accepts mail addressed to <em>any</em> name on its domain and holds it in a shared pool. That rule is called a catch-all. It is what lets a service invent an address such as <em>random-name@mytemp-mail.online</em> the moment you click a button, without anyone having to create a real mailbox first.</p>
<h2>Routing the mail to the right place</h2>
<p>When someone sends a message to one of those addresses, the server needs to know which visitor should see it. It does that by keying each message to the specific address it was sent to. Your browser, meanwhile, is watching just that one address. As soon as a matching message arrives, the page is notified and the mail appears &mdash; usually within a couple of seconds. There is no account and no login because the address itself is the key: whoever is viewing it can read it.</p>
<h2>Why there is no password</h2>
<p>A password exists to prove you own a mailbox. A disposable inbox is deliberately the opposite: it is meant to be easy to open and easy to abandon. Because the address is short-lived and holds nothing sensitive by design, a login would add friction without adding much security. The trade-off is the one you should keep in mind &mdash; anyone who knows the address can read what arrives there, so a temp inbox is not the place for private mail.</p>
<h2>Expiry and cleanup</h2>
<p>The final piece is the timer. Each inbox is given a limited life. When it expires, its messages are deleted, which is what keeps the service from turning into an endless archive of everyone's throwaway mail. That cleanup is also why you cannot use a disposable inbox to recover an account later: by the time you need the reset link, the inbox that received it is long gone.</p>
<h2>What this means for you</h2>
<p>Once you see a temp mail as a catch-all pool with a timer, its behaviour stops being mysterious. It is fast because nothing has to be provisioned. It is passwordless because the address is the credential. And it forgets on purpose, because remembering is exactly what a disposable inbox is designed not to do.</p>
<h2>Why some messages take a little longer</h2>
<p>Most mail lands within seconds, but a few messages lag, and it helps to know why. Sender-side queues are the usual cause: a busy service may batch its outgoing mail and send it a minute or two late, which has nothing to do with the inbox. Spam filtering is another factor &mdash; a message that looks automated may be held briefly before it is delivered. And a handful of senders retry on their own schedule, so a code that seemed lost can appear a couple of minutes later.</p>
<p>If nothing arrives at all, the likeliest explanations are a mistyped address or a service that refuses disposable domains. Both are quick to check: compare the address you entered with the one on screen, and if they match, try a different address or a different service. Understanding these three causes &mdash; queues, filters and refusals &mdash; turns a confusing delay into a routine troubleshooting step.</p>"""),

 ("temp-mail-vs-second-email",
  "Temp Mail vs a Second Email Account",
  "A second Gmail account and a disposable inbox solve overlapping problems. Here is how to choose between them.",
  "Temp mail vs a second email account",
  "Updated for 2026 &middot; 4 min read",
  """<p>When your main inbox gets too noisy, there are two obvious fixes: create a spare email account, or start using a disposable inbox. Both keep your primary address clean, but they are built for different jobs, and choosing the wrong one usually means extra work later.</p>
<h2>The case for a second account</h2>
<p>A spare Gmail or Outlook account is permanent, recoverable and familiar. It can hold a recovery phone number, it works for services you sign into regularly, and it will still be there in five years. If a site is one you will keep using &mdash; a bank, a job portal, a subscription you pay for &mdash; a real secondary address is the right home for it. The cost is setup: a phone number, a password, and another inbox slowly filling with the same kind of noise you were trying to escape.</p>
<h2>The case for temp mail</h2>
<p>A disposable inbox is the opposite trade. It needs no phone number and no password, it is ready in a second, and it disappears when you are done. For a one-off signup, a gated download or a trial you may never use again, that is exactly right. What it cannot do is persist: once the inbox expires, the account behind it becomes unrecoverable, which is a feature for a throwaway signup and a problem for anything you care about.</p>
<h2>Side by side</h2>
<ul>
<li><strong>Setup:</strong> temp mail is instant; a second account needs a phone, password and often a recovery email.</li>
<li><strong>Lifespan:</strong> a temp inbox expires by design; a second account lasts indefinitely.</li>
<li><strong>Recovery:</strong> a second account can be recovered; a temp inbox cannot.</li>
<li><strong>Privacy:</strong> a temp address asks nothing about you; a second account is tied to your phone and device.</li>
<li><strong>Cleanup:</strong> a temp inbox deletes itself; a second account accumulates spam forever.</li>
</ul>
<h2>The practical split</h2>
<p>Most people end up wanting both. Keep a permanent secondary address for the handful of services you genuinely rely on, and reach for a temporary inbox every time you are asked for an email by a site you are only curious about. The rule of thumb is simple: if you would be upset to lose access tomorrow, use a real address; if you would shrug, use a temp one.</p>
<h2>Where email aliases fit</h2>
<p>There is a third option worth knowing about: an alias. Some mail providers let you create forwarding addresses that all deliver to your real inbox under a unique name, so you can tell which site sold your address and switch an alias off when it starts attracting spam. An alias is more durable than a temp inbox but more private than your main address, which makes it a good middle tier for services you use occasionally but do not want to lose.</p>
<p>So the honest hierarchy has three rungs: a temp inbox for one-off signups you will abandon, an alias for the services you use now and then, and a permanent address for the accounts that matter most. Choosing the right rung takes a second and saves a lot of tidying up later.</p>"""),

 ("temp-mail-safety-guide",
  "Is Temp Mail Safe? A Straight Answer",
  "What a disposable inbox protects you from, what it cannot protect, and the handful of rules that keep temp mail genuinely safe to use.",
  "Is temp mail safe? A straight answer",
  "Updated for 2026 &middot; 4 min read",
  """<p>People ask whether temp mail is safe, and the honest answer is that it depends entirely on what you use it for. A disposable inbox is a well-understood tool with clear strengths and equally clear limits. Understand both and it is a safe, useful part of everyday privacy; ignore the limits and it can cause real trouble.</p>
<h2>What a temp inbox protects</h2>
<p>Its main job is to keep your real address out of places that do not need it. Every site you give your permanent email to can leak it, sell it or add it to a marketing list. A throwaway address absorbs that risk instead: if it ends up on a spam list, nothing of yours is exposed. It also keeps your inbox free of the confirmation mail, welcome sequences and follow-ups that a one-off signup produces.</p>
<h2>What it cannot protect</h2>
<p>The important caveat is that a temp inbox is not private in the way your personal mail is. Anyone who knows the address can read what arrives there, so it is not the place for bank statements, personal messages or anything you would not want a stranger to see. And because the inbox expires, it cannot be used to recover an account later &mdash; a reset link sent to a temp address is useless once the inbox is gone.</p>
<h2>Five rules that keep it safe</h2>
<ul>
<li><strong>Use it for low-stakes signups.</strong> Trials, downloads, newsletters and test accounts are ideal.</li>
<li><strong>Never use it for money or identity.</strong> No banking, payments, government services or tax portals.</li>
<li><strong>Do not rely on it for accounts you will keep.</strong> If you might need to reset a password, use a real address.</li>
<li><strong>Do not reuse passwords.</strong> A temp inbox does not make a weak password safe; use a password manager regardless.</li>
<li><strong>Expect some sites to block it.</strong> A few services reject known disposable domains or demand a phone number, and that is their right.</li>
</ul>
<h2>The bottom line</h2>
<p>Used as intended &mdash; a burner for the many small signups of everyday life &mdash; temp mail is safe and genuinely useful. Used as a substitute for a real account, it is the wrong tool and will eventually cost you access. Keep the two roles separate and you get the privacy benefits without the surprises.</p>
<h2>How to tell whether a site blocks temp mail</h2>
<p>Some services refuse disposable addresses on purpose, and it is worth recognising the signs early. The clearest is a form that rejects the address the moment you submit it, usually with a vague message about an invalid email. A subtler sign is silence: the signup appears to succeed, but no confirmation mail ever arrives even after a resend. A third is an unexpected demand for a phone number partway through the flow, which some platforms use as a fallback check.</p>
<p>None of these are failures on your side, and none are worth fighting. The right response is simply to pick a different tool for that account &mdash; a real address if you need it, or nothing at all if you were only curious. A disposable inbox is designed to make the many small signups of life easier; it is not meant to win an argument with a service that has decided it wants something more.</p>"""),
]


def task3c():
    bdir = os.path.join(PUB, "blog")
    os.makedirs(bdir, exist_ok=True)
    slugs = [a[0] for a in BLOG_ARTICLES]
    titles = {a[0]: a[1] for a in BLOG_ARTICLES}
    made = 0
    for slug, title, desc, h1, meta, body in BLOG_ARTICLES:
        related = "".join(
            '<li><a href="/blog/%s">%s</a></li>' % (s, titles[s])
            for s in slugs if s != slug)
        related += '<li><a href="/">Free temp mail tool</a></li>'
        page = (BLOG_HEAD
                .replace("__PUB__", NEW_ID)
                .replace("__TITLE__", title)
                .replace("__DESC__", desc)
                .replace("__SLUG__", slug)
                .replace("__H1__", h1)
                .replace("__META__", meta)
                .replace("__BODY__", body)
                .replace("__RELATED__", related))
        write(os.path.join(bdir, slug + ".html"), page)
        made += 1
    # blog index
    cards = "".join(
        '<li><a href="/blog/%s">%s</a></li>' % (a[0], a[1]) for a in BLOG_ARTICLES)
    idx = (BLOG_HEAD
           .replace("__PUB__", NEW_ID)
           .replace("__TITLE__", "Guides & How-tos")
           .replace("__DESC__", "Practical guides to temporary email: verification without a phone, protecting your inbox from spam, and how disposable inboxes work.")
           .replace("__SLUG__", "")
           .replace("__H1__", "Guides &amp; how-tos")
           .replace("__META__", "Offex Mail &middot; guides")
           .replace("__BODY__", "<p>Short, practical reads about temporary email and keeping your real inbox clean.</p><ul class=\"related\">%s</ul>" % cards)
           .replace("__RELATED__", cards))
    write(os.path.join(bdir, "index.html"), idx)
    report.append("TASK3c: wrote %d blog articles + /blog/ index." % made)


# --------------------------------------------------------------------------
# TASK 4 - sitemap
# --------------------------------------------------------------------------
def task4():
    p = os.path.join(PUB, "sitemap.xml")
    s = read(p)
    if "/blog/" in s:
        report.append("TASK4: sitemap already contains blog URLs.")
        return
    add = "".join(
        "<url><loc>https://mytemp-mail.online/blog/%s</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n"
        % a[0] for a in BLOG_ARTICLES)
    add += "<url><loc>https://mytemp-mail.online/blog/</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>\n"
    s = s.replace("</urlset>", add + "</urlset>", 1)
    write(p, s)
    report.append("TASK4: added %d blog URLs to sitemap.xml." % (len(BLOG_ARTICLES) + 1))


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    task1()
    task2()
    task2b()
    task2c()
    task2d()
    task3a()
    task3b()
    task3c()
    task4()
    for line in report:
        print(line)


if __name__ == "__main__":
    main()
