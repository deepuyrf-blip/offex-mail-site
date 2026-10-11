#!/usr/bin/env python3
"""
Offex Mail — apply the fixes found by tools/audit_site.py.

Idempotent: re-running it after a successful pass changes nothing.

Fixes
  1 titles        shorten >65-char titles (decoded length)
  2 descriptions  shorten >165, lengthen <70 (CJK), fix missing / over-claim
  3 hreflang      add the 10-language + x-default cluster to English pages
                  that really have variants
  4 links         repoint links to removed service pages (youtube/gmail/
                  google/whatsapp/telegram) at real pages
  5 misc          repair the stray, un-linked "Create a free inbox ->" text
  6 basics        add app-privacy to the sitemap and link it from the homepage
"""
import argparse
import html as htmllib
import os
import re

BASE = "https://mytemp-mail.online"
LANGS = ["en", "hi", "es", "fr", "de", "pt", "ru", "ar", "zh", "ja"]
LANG_DIRS = set(LANGS) - {"en"}
CJK = {"zh", "ja"}

# short replacement tails for over-long titles (decoded text)
SHORT_TAIL = {
    "Kostenlose Wegwerf-E-Mail für die Anmeldung": "Wegwerf-E-Mail",
    "Correo desechable gratis para registrarte": "Correo desechable gratis",
    "E-mail jetable gratuit pour l'inscription": "E-mail jetable gratuit",
    "E-mail descartável grátis para cadastro": "E-mail descartável grátis",
    "Бесплатная одноразовая почта для регистрации": "Одноразовая почта",
    "साइनअप के लिए मुफ़्त डिस्पोज़ेबल ईमेल": "मुफ़्त डिस्पोज़ेबल ईमेल",
}

# removed service -> ordered replacement candidates (all exist in every language)
REPL = {
    "google": ["microsoft", "apple", "dropbox", "notion"],
    "gmail": ["dropbox", "microsoft", "notion", "apple"],
    "whatsapp": ["discord", "slack", "twitter", "steam"],
    "telegram": ["slack", "discord", "twitter", "steam"],
    "youtube": ["netflix", "spotify", "steam", "twitter"],
}
DISPLAY = {
    "google": "Google", "gmail": "Gmail", "whatsapp": "WhatsApp",
    "telegram": "Telegram", "youtube": "YouTube",
    "microsoft": "Microsoft", "apple": "Apple", "dropbox": "Dropbox",
    "notion": "Notion", "discord": "Discord", "slack": "Slack",
    "twitter": "Twitter", "steam": "Steam", "netflix": "Netflix",
    "spotify": "Spotify",
    # shared (all-language) services
    "adobe": "Adobe", "airbnb": "Airbnb", "aliexpress": "AliExpress",
    "amazon": "Amazon", "canva": "Canva", "chatgpt": "ChatGPT",
    "ebay": "eBay", "facebook": "Facebook", "flipkart": "Flipkart",
    "github": "GitHub", "gitlab": "GitLab", "instagram": "Instagram",
    "linkedin": "LinkedIn", "netflix": "Netflix", "openai": "OpenAI",
    "paypal": "PayPal", "pinterest": "Pinterest", "playstation": "PlayStation",
    "reddit": "Reddit", "shopify": "Shopify", "snapchat": "Snapchat",
    "tiktok": "TikTok", "twitter": "Twitter", "uber": "Uber", "x": "X",
    "xbox": "Xbox", "zoom": "Zoom",
    # English-only services (used to fill index tiles without duplicates)
    "airtel": "Airtel", "cred": "CRED", "epic-games": "Epic Games",
    "google-pay": "Google Pay", "groww": "Groww", "irctc": "IRCTC",
    "jio": "Jio", "meesho": "Meesho", "minecraft": "Minecraft",
    "myntra": "Myntra", "ola": "Ola", "openai-chatgpt": "OpenAI / ChatGPT",
    "paytm": "Paytm", "phonepe": "PhonePe", "razorpay": "Razorpay",
    "roblox": "Roblox", "swiggy": "Swiggy", "twitter-x": "Twitter / X",
    "zerodha": "Zerodha", "zomato": "Zomato",
}
ZH_TAIL = " 免费、即时、安全，即开即用，保护你的真实邮箱。"

log = []


def note(msg):
    log.append(msg)


# ---------------------------------------------------------------------------
def shorten_title(dec):
    if 15 <= len(dec) <= 65:
        return dec
    t = dec
    for suf in (" | Offex Mail", " — Offex Mail", " - Offex Mail"):
        if t.endswith(suf):
            t = t[: -len(suf)]
            break
    if len(t) > 65:
        m = re.match(r"^(.*?)\s+[—–]\s+(.*)$", t)
        if m:
            head, tail = m.group(1), m.group(2)
            if tail in SHORT_TAIL:
                cand = head + " — " + SHORT_TAIL[tail]
            else:
                cand = head
            if 15 <= len(cand) <= 65:
                t = cand
    if len(t) > 65:
        t = t[:65].rsplit(" ", 1)[0].rstrip(" —-")
    return t


def _term(s):
    if s and s[-1] not in ".!?。！？…।":
        s += "."
    return s


def shorten_desc(dec, maxlen=165, minlen=70):
    if len(dec) <= maxlen:
        return dec
    parts = re.split(r"(?<=[.!?。۔।])\s+", dec)
    cands = []
    if len(parts) >= 2:
        cands.append(" ".join(parts))
        cands.append(" ".join([parts[0], parts[-1]]))
        if len(parts) >= 3:
            cands.append(" ".join(parts[:2]))
            cands.append(" ".join([parts[0], parts[-2]]))
        cands.append(parts[0])
    ok = [c for c in cands if minlen <= len(c) <= maxlen]
    if ok:
        return max(ok, key=len)
    cut = dec[:maxlen]
    for sep in ("— ", "– ", "; ", ", ", ". ", "! ", "? "):
        j = cut.rfind(sep)
        if j >= minlen:
            return _term(cut[:j].rstrip(" ,;،—-").strip())
    j = cut.rfind(" ")
    return _term((cut[:j] if j >= minlen else cut).strip())


# ---------------------------------------------------------------------------
def fix_head_titles_descs(path, rel, s):
    # --- <title>
    def repl_title(m):
        raw = m.group(2)
        dec = htmllib.unescape(raw)
        new = shorten_title(dec)
        if new != dec:
            note(f"TITLE {rel}: {len(dec)}->{len(new)} :: {new}")
            return m.group(1) + htmllib.escape(new, quote=False) + m.group(3)
        return m.group(0)
    s = re.sub(r"(<title[^>]*>)(.*?)(</title>)", repl_title, s, count=1, flags=re.S | re.I)

    # --- og:title / twitter:title (keep consistent with <title>)
    def repl_metatitle(m):
        raw = m.group(2)
        dec = htmllib.unescape(raw)
        new = shorten_title(dec)
        if new != dec:
            return m.group(1) + htmllib.escape(new, quote=True) + m.group(3)
        return m.group(0)
    for attr in ("og:title", "twitter:title"):
        pat = re.compile(
            r'(<meta[^>]*(?:property|name)="' + attr + r'"[^>]*content=")(.*?)(")',
            re.S)
        def mk(pat):
            def f(m):
                raw = m.group(2)
                dec = htmllib.unescape(raw)
                new = shorten_title(dec)
                if new != dec:
                    return m.group(1) + htmllib.escape(new, quote=True) + m.group(3)
                return m.group(0)
            return f
        s = pat.sub(mk(pat), s)

    # --- meta description (and og/twitter description kept in sync)
    def desc_transform(dec):
        if rel.endswith("app-privacy.html") and not dec:
            return dec
        # over-claim reword
        dec2 = dec.replace("starts with a hack", "starts with a malicious attack")
        new = shorten_desc(dec2)
        if rel.split("/")[0] in CJK and len(new) < 70:
            new = new + ZH_TAIL
        return new

    pat = re.compile(r'(<meta\s+name="description"\s+content=")(.*?)(")', re.S | re.I)
    def repl_desc(m):
        raw = m.group(2)
        dec = htmllib.unescape(raw)
        new = desc_transform(dec)
        if new != dec:
            note(f"DESC {rel}: {len(dec)}->{len(new)}")
            return m.group(1) + htmllib.escape(new, quote=True) + m.group(3)
        return m.group(0)
    s = pat.sub(repl_desc, s)
    return s


# ---------------------------------------------------------------------------
def add_hreflang(path, rel, s):
    """Add the hreflang cluster to an English page that has real variants."""
    if re.search(r'rel="alternate"\s+hreflang', s):
        return s, False
    if rel == "index.html":
        base = None
    elif "/" not in rel and rel.endswith(".html"):
        base = rel[:-5]
    else:
        return s, False
    block = []
    for lang in LANGS:
        if lang == "en":
            url = BASE + ("/" if base is None else "/" + base)
        else:
            url = BASE + "/" + lang + ("/" if base is None else "/" + base)
        block.append(f'<link rel="alternate" hreflang="{lang}" href="{url}">')
    block.append(f'<link rel="alternate" hreflang="x-default" href="'
                 f'{BASE + ("/" if base is None else "/" + base)}">')
    ins = "\n".join(block)
    m = re.search(r'<link\s+rel="canonical"[^>]*>', s)
    if not m:
        return s, False
    s = s[: m.end()] + "\n" + ins + s[m.end():]
    note(f"HREFLANG {rel}: added 11 alternates")
    return s, True


# ---------------------------------------------------------------------------
def fix_links(path, rel, s, en_services, shared_services):
    top = rel.split("/")[0]
    lang = top if top in LANG_DIRS else "en"
    # gather existing service slugs linked on this page
    present = set()
    for m in re.finditer(r'href="(?:https://mytemp-mail\.online)?/(?:[a-z]{2}/)?([a-z0-9-]+)"', s):
        present.add(m.group(1))
    changed = 0

    def choose(removed):
        pool = en_services if lang == "en" else shared_services
        for c in pool:
            if c not in present and c not in REPL:
                present.add(c)
                return c
        for c in REPL[removed]:
            if c not in present:
                present.add(c)
                return c
        present.add(REPL[removed][0])
        return REPL[removed][0]

    # language pages: absolute hrefs
    def repl_abs(m):
        nonlocal changed
        pre, removed, rest, inner = m.group(1), m.group(2), m.group(3), m.group(4)
        if removed not in REPL:
            return m.group(0)
        new = choose(removed)
        inner2 = re.sub(re.escape(DISPLAY[removed]), DISPLAY[new], inner, flags=re.I)
        changed += 1
        return f'{pre}{new}{rest}{inner2}</a>'
    s = re.sub(r'(<a href="https://mytemp-mail\.online/' + lang +
               r'/)(google|gmail|whatsapp|telegram|youtube)("[^>]*>)(.*?)</a>',
               repl_abs, s, flags=re.S)

    # english index tiles: root-relative
    def repl_idx(m):
        nonlocal changed
        removed = m.group(2)
        if removed not in REPL:
            return m.group(0)
        new = choose(removed)
        inner2 = re.sub(re.escape(DISPLAY[removed]), DISPLAY[new], m.group(4), flags=re.I)
        changed += 1
        return f'{m.group(1)}{new}{m.group(3)}{inner2}</a>'
    if lang == "en":
        s = re.sub(r'(<a[^>]*href="/)(google|gmail|whatsapp|telegram|youtube)("[^>]*>)(.*?)</a>',
                   repl_idx, s, flags=re.S)

        # stale labels pointing at the hub: <a href="/services">Temp mail for X</a>
        label2slug = {v: k for k, v in DISPLAY.items()}
        def repl_hub(m):
            nonlocal changed
            removed = label2slug.get(m.group(1))
            if removed not in REPL:
                return m.group(0)
            new = choose(removed)
            changed += 1
            return f'<a href="/{new}">Temp mail for {DISPLAY[new]}</a>'
        s = re.sub(r'<a href="/services">Temp mail for (Google|Gmail|YouTube|WhatsApp|Telegram)</a>',
                   repl_hub, s)

    if changed:
        note(f"LINKS {rel}: repointed {changed} removed-service link(s)")
    return s


# ---------------------------------------------------------------------------
def fix_stray_cta(path, rel, s):
    pat = re.compile(r'</ol>\s*\n\s*Create a free inbox →')
    if pat.search(s):
        s = pat.sub('</ol>\n    <div class="cta-wrap"><a class="cta" '
                    'href="https://mytemp-mail.online/">Create a free inbox →</a></div>', s)
        note(f"CTA {rel}: wrapped stray 'Create a free inbox →' in a real link")
    return s


# grammar/article slips produced by the page template
TYPO_FIXES = [
    ("is a Indian", "is an Indian"),
    ("is a AI", "is an AI"),
    ("is a Apple", "is an Apple"),
    ("is a Xbox", "is an Xbox"),
    ("is a investment", "is an investment"),
    ("is a online", "is an online"),
    # English FAQ phrasing only (avoid touching e.g. Spanish "para OpenAI")
    ("create a AliExpress", "create an AliExpress"),
    ("create a OpenAI", "create an OpenAI"),
]


def fix_typos(path, rel, s):
    for bad, good in TYPO_FIXES:
        if bad in s:
            n = s.count(bad)
            s = s.replace(bad, good)
            note(f"TYPO {rel}: {bad!r} -> {good!r} ({n}x)")
    return s


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", "public"))
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    files = []
    for dp, _d, ns in os.walk(root):
        for n in ns:
            if n.endswith(".html"):
                rel = os.path.relpath(os.path.join(dp, n), root).replace(os.sep, "/")
                files.append(rel)
    files.sort()

    # English pages that legitimately have variants (basename present in all langs)
    en_root = {f[:-5] for f in files if "/" not in f}
    shared = {b for b in en_root
              if all(os.path.isfile(os.path.join(root, l, b + ".html")) for l in LANG_DIRS)}
    NON_SVC = {"index", "about", "contact", "services", "privacy", "terms",
               "disclaimer", "app-privacy"}
    en_services = sorted(b for b in en_root if b not in NON_SVC)
    shared_services = sorted(b for b in shared if b not in NON_SVC)

    changed_files = []
    for rel in files:
        full = os.path.join(root, rel)
        with open(full, encoding="utf-8") as fh:
            s = orig = fh.read()
        s = fix_head_titles_descs(full, rel, s)
        s = fix_links(full, rel, s, en_services, shared_services)
        s = fix_stray_cta(full, rel, s)
        s = fix_typos(full, rel, s)
        # hreflang for index + shared English service pages
        if rel == "index.html" or ("/" not in rel and rel[:-5] in shared):
            s, _ = add_hreflang(full, rel, s)
        if s != orig:
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(s)
            changed_files.append(rel)

    # --- app-privacy: add a meta description
    ap_path = os.path.join(root, "app-privacy.html")
    s = open(ap_path, encoding="utf-8").read()
    if '<meta name="description"' not in s:
        desc = ("Offex Mail Android app privacy policy: what the app collects, how "
                "temporary inbox data is handled, the permissions it asks for and how "
                "to contact us.")
        s = s.replace('<link rel="canonical" href="https://mytemp-mail.online/app-privacy">',
                      '<link rel="canonical" href="https://mytemp-mail.online/app-privacy">\n'
                      f'<meta name="description" content="{desc}">')
        open(ap_path, "w", encoding="utf-8").write(s)
        changed_files.append("app-privacy.html")
        note(f"DESC app-privacy.html: added ({len(desc)} chars)")

    # --- sitemap: add app-privacy
    sm_path = os.path.join(root, "sitemap.xml")
    sm = open(sm_path, encoding="utf-8").read()
    if "/app-privacy</loc>" not in sm:
        line = ('<url><loc>https://mytemp-mail.online/app-privacy</loc>'
                '<changefreq>yearly</changefreq><priority>0.3</priority></url>\n')
        anchor = '<url><loc>https://mytemp-mail.online/amazon</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n'
        if anchor in sm:
            sm = sm.replace(anchor, anchor + line, 1)
        else:
            sm = sm.replace("</urlset>", line + "</urlset>")
        open(sm_path, "w", encoding="utf-8").write(sm)
        changed_files.append("sitemap.xml")
        note("SITEMAP: added /app-privacy")

    # --- homepage footer: link app-privacy so it is not an orphan
    idx_path = os.path.join(root, "index.html")
    s = open(idx_path, encoding="utf-8").read()
    if 'href="/app-privacy"' not in s:
        old = '<a href="/disclaimer">Disclaimer</a></p>'
        new = '<a href="/disclaimer">Disclaimer</a> · <a href="/app-privacy">App privacy</a></p>'
        if old in s:
            s = s.replace(old, new, 1)
            open(idx_path, "w", encoding="utf-8").write(s)
            if "index.html" not in changed_files:
                changed_files.append("index.html")
            note("FOOTER index.html: linked /app-privacy")

    # --- soften the "85% working" banner claim in the no-JS base markup
    s = open(idx_path, encoding="utf-8").read()
    if "85% working temp mail" in s or "85% Working" in s:
        s = s.replace("85% working temp mail", "temp mail")
        s = s.replace("ElevenLabs (11Labs) ke liye Temp Mail — 85% Working",
                      "ElevenLabs (11Labs) ke liye Temp Mail — free &amp; instant")
        open(idx_path, "w", encoding="utf-8").write(s)
        if "index.html" not in changed_files:
            changed_files.append("index.html")
        note("MISC index.html: removed '85% working' claim from base markup")

    print("\n".join(log))
    print(f"\n{len(changed_files)} file(s) changed")


if __name__ == "__main__":
    main()
