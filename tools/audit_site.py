#!/usr/bin/env python3
"""
Offex Mail — end-to-end QA / SEO / AdSense audit for the whole public/ tree.

Usage:
    python3 tools/audit_site.py [--root public] [--json out.json]

Checks (14 groups):
  1 titles  2 meta descriptions  3 headings  4 content depth  5 duplicate content
  6 canonicals  7 hreflang  8 internal links  9 images  10 structured data
  11 AdSense compliance  12 basics (robots/sitemap/orphans)  13 spelling  14 misc

The script is dependency-free (stdlib only) so it runs in CI.
It prints a human-readable report and exits non-zero when hard errors exist.
"""
import argparse
import json
import os
import posixpath
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urlparse

BASE = "https://mytemp-mail.online"
LANGS = ["en", "hi", "es", "fr", "de", "pt", "ru", "ar", "zh", "ja"]
LANG_DIRS = set(LANGS) - {"en"}
CJK = {"zh", "ja"}
PUB_ID = "ca-pub-9424904813990636"
ADS_TXT_LINE = "google.com, pub-9424904813990636, DIRECT, f08c47fec0942fa0"
OVERCLAIM = ["100%", "guaranteed", "guarantee", "hack", "bypass", "unlimited"]
PLACEHOLDERS = ["lorem ipsum", "lorem", "todo", "tbd", "xxx", "your-domain",
                "example.com", "placeholder", "changeme", "foo bar", "dummy text"]
# common English misspellings worth flagging in visible copy
COMMON_TYPOS = [
    "recieve", "recieved", "seperate", "seperated", "occured", "occuring",
    "accomodate", "definately", "publically", "adress", "wich", "teh",
    "availabe", "sucessful", "successfull", "enviroment", "existance",
    "neccessary", "untill", "wierd", "grammer", "goverment", "guarentee",
    "maintainance", "occassion", "recomend", "recomended", "refered",
    "responsibilty", "tommorow", "truely", "usefull", "behaviour ", "alot ",
]

# ----------------------------------------------------------------------------
# HTML parsing
# ----------------------------------------------------------------------------


class PageParser(HTMLParser):
    """Collect tags/text we need for the audit."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.metas = []          # list of dict(attrs)
        self.links = []          # list of dict(attrs)
        self.hrefs = []          # every <a href>
        self.imgs = []           # list of dict(attrs)
        self.headings = []       # (level, text)
        self.jsonld = []         # raw strings
        self.scripts = []        # list of dict(attrs)
        self._in = None
        self._buf = []
        self._hidden_stack = []  # track style display:none / hidden
        self._texts = {"all": [], "chrome": []}  # chrome = header/nav/footer/aside
        self._chrome_depth = 0
        self._depth = 0
        self._capture = None

    # -- helpers
    def _text(self):
        return "".join(self._buf)

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v if v is not None else "") for k, v in attrs}
        self._depth += 1
        if tag in ("header", "nav", "footer", "aside"):
            self._chrome_depth += 1
        if tag == "script":
            self.scripts.append(a)
            if a.get("type", "").strip().lower() == "application/ld+json":
                self._capture = ("jsonld", a)
                self._buf = []
            else:
                self._capture = ("script", a)
                self._buf = []
        elif tag == "style":
            self._capture = ("style", a)
            self._buf = []
        elif tag == "title":
            self._capture = ("title", a)
            self._buf = []
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "a":
            if a.get("href"):
                self.hrefs.append(a["href"])
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._capture = ("h", tag)
            self._buf = []

    def handle_startendtag(self, tag, attrs):
        a = {k.lower(): (v if v is not None else "") for k, v in attrs}
        if tag == "img":
            self.imgs.append(a)
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.links.append(a)

    def handle_endtag(self, tag):
        if tag in ("header", "nav", "footer", "aside") and self._chrome_depth > 0:
            self._chrome_depth -= 1
        if self._capture and self._capture[1] is not None:
            kind, val = self._capture
            if kind == "h" and tag == val:
                self.headings.append((int(val[1]), self._text().strip()))
                self._capture = None
            elif kind == "title" and tag == "title":
                self.title = self._text().strip()
                self._capture = None
            elif kind == "jsonld" and tag == "script":
                self.jsonld.append(self._text())
                self._capture = None
            elif kind in ("script", "style") and tag == kind:
                self._capture = None
        self._depth = max(0, self._depth - 1)

    def handle_data(self, data):
        if self._capture and self._capture[0] in ("script", "style", "jsonld"):
            self._buf.append(data)
            return
        if self._capture:
            self._buf.append(data)
        t = data.strip()
        if t:
            self._texts["all"].append(data)
            if self._chrome_depth > 0:
                self._texts["chrome"].append(data)

    def text(self, which="all"):
        return " ".join(self._texts[which])


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


# ----------------------------------------------------------------------------
# Route / URL helpers
# ----------------------------------------------------------------------------

def url_for(relpath):
    """Map a path relative to public/ to its clean absolute URL path."""
    p = relpath.replace(os.sep, "/")
    if p == "index.html":
        return "/"
    if p.endswith("/index.html"):
        return "/" + p[: -len("index.html")]
    if p.endswith(".html"):
        return "/" + p[:-5]
    return "/" + p


def route_to_file(root, route):
    """Resolve a URL path (e.g. /ar/amazon) to a file under root, or None."""
    p = route.lstrip("/")
    p = posixpath.normpath(p) if p else ""
    if p in ("", "."):
        p = ""
    candidates = []
    if p == "" or p.endswith("/"):
        candidates.append(posixpath.join(p, "index.html"))
    else:
        candidates.append(p)                       # exact file
        candidates.append(p + ".html")             # clean url
        candidates.append(posixpath.join(p, "index.html"))  # dir index
    for c in candidates:
        full = os.path.join(root, c)
        if os.path.isfile(full):
            return c
    return None


def resolve_href(root, href, from_rel):
    """Return ('internal', relpath) / ('external', url) / ('special', scheme)
    / ('missing', route) for a single href."""
    h = href.strip()
    if not h or h.startswith("#"):
        return ("special", "anchor")
    low = h.lower()
    if low.startswith(("mailto:", "tel:", "javascript:", "data:", "sms:")):
        return ("special", low.split(":", 1)[0])
    if h.startswith("//"):
        return ("external", h)
    if low.startswith("http://") or low.startswith("https://"):
        host = urlparse(h).netloc.lower()
        if host.endswith("mytemp-mail.online"):
            route = urlparse(h).path or "/"
            f = route_to_file(root, route)
            return ("internal", f) if f else ("missing", route)
        return ("external", h)
    # relative or root-relative
    clean = h.split("#")[0].split("?")[0]
    if clean.startswith("/"):
        route = clean
    else:
        base = posixpath.dirname(from_rel)
        route = "/" + posixpath.normpath(posixpath.join(base, clean))
    f = route_to_file(root, route)
    return ("internal", f) if f else ("missing", route)


def lang_of(relpath):
    top = relpath.split("/")[0]
    return top if top in LANG_DIRS else "en"


# ----------------------------------------------------------------------------
# Audit
# ----------------------------------------------------------------------------

class Audit:
    def __init__(self, root):
        self.root = root
        self.files = []          # relpaths
        self.pages = {}          # relpath -> parsed dict
        self.problems = defaultdict(list)   # key -> list of strings
        self.info = {}
        self._scan()

    def add(self, key, msg):
        self.problems[key].append(msg)

    def _scan(self):
        for dirpath, _dirs, names in os.walk(self.root):
            for n in names:
                if n.endswith(".html"):
                    full = os.path.join(dirpath, n)
                    rel = os.path.relpath(full, self.root).replace(os.sep, "/")
                    self.files.append(rel)
        self.files.sort()
        for rel in self.files:
            full = os.path.join(self.root, rel)
            s = read(full)
            p = PageParser()
            p.feed(s)
            self.pages[rel] = {"html": s, "parsed": p, "url": url_for(rel),
                               "lang": lang_of(rel), "size": len(s)}

    # -- 1 titles -----------------------------------------------------------
    def check_titles(self):
        seen = {}
        for rel, d in self.pages.items():
            p = d["parsed"]
            title = p.title
            if title is None:
                self.add("titles", f"{rel}: MISSING <title>")
                continue
            if len(p.links) and False:
                pass
            # count title tags
            n = len(re.findall(r"<title[ >]", d["html"], re.I))
            if n != 1:
                self.add("titles", f"{rel}: {n} <title> tags (need exactly 1)")
            t = title.strip()
            if not (15 <= len(t) <= 65):
                self.add("titles", f"{rel}: title length {len(t)} not in 15-65 :: {t!r}")
            low = t.lower()
            for w in OVERCLAIM:
                if w in low:
                    self.add("titles", f"{rel}: over-claim word {w!r} in title :: {t!r}")
            # duplicated text inside the title
            segs = [s.strip() for s in re.split(r"[—|·–]| - ", t) if s.strip()]
            norm = [s.lower() for s in segs]
            if len(norm) != len(set(norm)) and len(norm) > 1:
                self.add("titles", f"{rel}: repeated segment in title :: {t!r}")
            key = t.lower()
            if key in seen:
                self.add("titles", f"{rel}: title DUPLICATE of {seen[key]} :: {t!r}")
            else:
                seen[key] = rel
        self.info["titles_unique"] = len(seen)

    # -- 2 meta descriptions ------------------------------------------------
    def check_descriptions(self):
        seen = {}
        for rel, d in self.pages.items():
            p = d["parsed"]
            desc = None
            for m in p.metas:
                if m.get("name", "").lower() == "description":
                    desc = m.get("content", "")
            if desc is None:
                self.add("descriptions", f"{rel}: MISSING meta description")
                continue
            if desc == "":
                self.add("descriptions", f"{rel}: EMPTY meta description")
                continue
            L = len(desc)
            if not (70 <= L <= 165):
                self.add("descriptions", f"{rel}: description length {L} not in 70-165")
            low = desc.lower()
            for w in OVERCLAIM:
                if w in low:
                    self.add("descriptions", f"{rel}: over-claim word {w!r} in description")
            key = desc.lower()
            if key in seen:
                self.add("descriptions", f"{rel}: description DUPLICATE of {seen[key]}")
            else:
                seen[key] = rel

    # -- 3 headings ---------------------------------------------------------
    def check_headings(self):
        for rel, d in self.pages.items():
            hs = d["parsed"].headings
            h1 = [h for h in hs if h[0] == 1]
            if len(h1) == 0:
                self.add("headings", f"{rel}: no <h1>")
            elif len(h1) > 1:
                self.add("headings", f"{rel}: {len(h1)} <h1> tags (need exactly 1)")
            for lvl, txt in hs:
                if txt == "":
                    self.add("headings", f"{rel}: empty <h{lvl}>")
            prev = None
            for lvl, txt in hs:
                if prev is not None and lvl > prev + 1:
                    self.add("headings", f"{rel}: skipped level h{prev} -> h{lvl} :: {txt[:50]!r}")
                prev = lvl

    # -- 4 content depth ----------------------------------------------------
    def check_content(self):
        self.info["word_counts"] = {}
        for rel, d in self.pages.items():
            p = d["parsed"]
            text = p.text("all")
            chrome = p.text("chrome")
            # Unicode-aware word count so Arabic / Devanagari / Cyrillic etc.
            # are counted as words, not as zero.
            words = len(re.findall(r"\w+", text))
            body = len(re.findall(r"\w+", text.replace(chrome, " ")))
            lang = d["lang"]
            if lang in CJK:
                cj = len(re.findall(r"[\u4e00-\u9fff\u3040-\u30ff]", text))
                self.info["word_counts"][rel] = {"chars_cjk": cj, "words": words}
                if cj < 400:
                    self.add("content", f"{rel}: CJK char count {cj} < 400 (thin)")
            else:
                self.info["word_counts"][rel] = {"words": words, "body_words": body}
                if words < 400:
                    self.add("content", f"{rel}: word count {words} < 400 (thin)")
                if words >= 400 and body < 0.45 * words:
                    self.add("content", f"{rel}: only {body} body words of {words} (mostly chrome)")

    # -- 5 duplicate content (6-gram Jaccard within a language) -------------
    def check_duplicates(self, threshold=0.80):
        def shingles(rel):
            text = self.pages[rel]["parsed"].text("all").lower()
            toks = re.findall(r"[a-z0-9']+", text)
            return set(tuple(toks[i:i + 6]) for i in range(len(toks) - 5))

        by_lang = defaultdict(list)
        for rel in self.files:
            by_lang[self.pages[rel]["lang"]].append(rel)
        self.info["dup_pairs"] = []
        for lang, rels in by_lang.items():
            sh = {r: shingles(r) for r in rels}
            for i in range(len(rels)):
                for j in range(i + 1, len(rels)):
                    a, b = sh[rels[i]], sh[rels[j]]
                    if not a or not b:
                        continue
                    inter = len(a & b)
                    union = len(a | b)
                    if union and inter / union > threshold:
                        jac = inter / union
                        self.info["dup_pairs"].append((rels[i], rels[j], round(jac, 3)))
                        self.add("duplicates",
                                 f"{rels[i]} ~ {rels[j]} :: Jaccard {jac:.3f} > {threshold}")

    # -- 6 canonicals -------------------------------------------------------
    def check_canonicals(self):
        for rel, d in self.pages.items():
            cans = [l.get("href", "") for l in d["parsed"].links
                    if l.get("rel", "").lower() == "canonical"]
            if not cans:
                self.add("canonicals", f"{rel}: MISSING canonical")
                continue
            if len(cans) > 1:
                self.add("canonicals", f"{rel}: {len(cans)} canonical tags")
            want = BASE + d["url"]
            got = cans[0]
            if got != want:
                self.add("canonicals", f"{rel}: canonical {got!r} != self {want!r}")
                # does it point at a real page?
                route = urlparse(got).path
                if urlparse(got).netloc and not urlparse(got).netloc.endswith("mytemp-mail.online"):
                    self.add("canonicals", f"{rel}: canonical host not mytemp-mail.online")
                elif route_to_file(self.root, route) is None:
                    self.add("canonicals", f"{rel}: canonical points at NON-EXISTENT {route}")

    # -- 7 hreflang ---------------------------------------------------------
    def _variant_langs(self, rel):
        """Set of languages in which this page's basename actually exists.

        A page participates in an hreflang cluster only when the same
        basename exists in more than one language (including English)."""
        parts = rel.split("/")
        base = parts[-1][:-5] if parts[-1].endswith(".html") else parts[-1]
        if rel == "index.html":
            base = "index"
        if parts[0] == "blog":
            return set()
        if base in ("about", "contact", "services", "privacy", "terms",
                    "disclaimer", "app-privacy"):
            return set()
        present = set()
        if os.path.isfile(os.path.join(self.root, base + ".html")):
            present.add("en")
        for l in LANG_DIRS:
            if os.path.isfile(os.path.join(self.root, l, base + ".html")):
                present.add(l)
        return present

    def check_hreflang(self):
        for rel, d in self.pages.items():
            alts = {}
            for l in d["parsed"].links:
                if l.get("rel", "").lower() == "alternate" and l.get("hreflang"):
                    alts[l["hreflang"].lower()] = l.get("href", "")
            present = self._variant_langs(rel)
            if len(present) <= 1:
                # no language variants -> hreflang must not be present
                if alts:
                    self.add("hreflang", f"{rel}: has hreflang but no language variants")
                continue
            want = set(present) | {"x-default"}
            missing = want - set(alts)
            extra = set(alts) - want
            if missing:
                self.add("hreflang", f"{rel}: missing hreflang {sorted(missing)}")
            if extra:
                self.add("hreflang", f"{rel}: unexpected hreflang {sorted(extra)}")
            for lang, href in alts.items():
                if not href:
                    self.add("hreflang", f"{rel}: empty hreflang {lang}")
                    continue
                route = urlparse(href).path or "/"
                if route_to_file(self.root, route) is None:
                    self.add("hreflang", f"{rel}: hreflang {lang} -> NON-EXISTENT {route}")

    # -- 8 internal links ---------------------------------------------------
    def check_links(self):
        self.info["broken_links"] = []
        for rel, d in self.pages.items():
            for href in d["parsed"].hrefs:
                kind, val = resolve_href(self.root, href, rel)
                if kind == "missing":
                    self.info["broken_links"].append((rel, href, val))
                    self.add("links", f"{rel}: broken link {href!r} (route {val})")

    # -- 9 images -----------------------------------------------------------
    def check_images(self):
        for rel, d in self.pages.items():
            for im in d["parsed"].imgs:
                src = im.get("src", "")
                if not src:
                    self.add("images", f"{rel}: <img> without src")
                    continue
                if "alt" not in im:
                    self.add("images", f"{rel}: <img src={src!r}> missing alt")
                elif im["alt"].strip() == "":
                    self.add("images", f"{rel}: <img src={src!r}> empty alt")
                for attr in ("width", "height"):
                    if not im.get(attr, "").strip():
                        self.add("images", f"{rel}: <img src={src!r}> missing {attr}")
                low = src.lower()
                if low.startswith("http://") or low.startswith("https://") or low.startswith("//"):
                    host = urlparse(src).netloc.lower()
                    if not host.endswith("mytemp-mail.online"):
                        self.add("images", f"{rel}: EXTERNAL image hotlink {src!r}")
                elif low.startswith("data:"):
                    pass
                else:
                    clean = src.split("?")[0].split("#")[0]
                    if clean.startswith("/"):
                        route = clean
                    else:
                        route = "/" + posixpath.normpath(
                            posixpath.join(posixpath.dirname(rel), clean))
                    if route_to_file(self.root, route) is None:
                        self.add("images", f"{rel}: broken image src {src!r}")

    # -- 10 structured data -------------------------------------------------
    def check_structured(self):
        req = {
            "FAQPage": ["mainEntity"],
            "WebApplication": ["name", "url"],
            "Organization": ["name", "url"],
            "WebSite": ["name", "url"],
            "BreadcrumbList": ["itemListElement"],
            "Article": ["headline"],
            "HowTo": ["name", "step"],
        }
        for rel, d in self.pages.items():
            for raw in d["parsed"].jsonld:
                try:
                    obj = json.loads(raw)
                except Exception as e:
                    self.add("structured", f"{rel}: JSON-LD does not parse :: {e}")
                    continue
                low = raw.lower()
                for ph in PLACEHOLDERS:
                    if ph in low:
                        self.add("structured", f"{rel}: JSON-LD placeholder text {ph!r}")
                items = obj if isinstance(obj, list) else [obj]
                for it in items:
                    if not isinstance(it, dict):
                        self.add("structured", f"{rel}: JSON-LD item not an object")
                        continue
                    t = it.get("@type", "")
                    for f in req.get(t, []):
                        if f not in it or it[f] in ("", None, [], {}):
                            self.add("structured", f"{rel}: {t} missing required field {f!r}")
                    if t == "FAQPage":
                        me = it.get("mainEntity", [])
                        for q in me:
                            if not isinstance(q, dict) or "name" not in q:
                                self.add("structured", f"{rel}: FAQ question missing name")
                            ans = (q or {}).get("acceptedAnswer", {})
                            if not isinstance(ans, dict) or not ans.get("text"):
                                self.add("structured", f"{rel}: FAQ answer missing text")

    # -- 11 AdSense ---------------------------------------------------------
    def check_adsense(self):
        for rel, d in self.pages.items():
            html = d["html"]
            # ignore HTML comments (e.g. "Monetag removed ... popunder ..." notes)
            scan = re.sub(r"<!--.*?-->", "", html, flags=re.S)
            n = len(re.findall(r"pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js", html))
            if n != 1:
                self.add("adsense", f"{rel}: {n} AdSense loader scripts (need exactly 1)")
            if PUB_ID not in html:
                self.add("adsense", f"{rel}: correct pub id {PUB_ID} not found")
            # keyword meta
            if re.search(r'<meta[^>]+name=["\']keywords["\']', html, re.I):
                self.add("adsense", f"{rel}: keyword meta present (should be removed)")
            # auto popups / interstitials
            for pat in (r"window\.open\(", r"popunder", r"profitableratecpmnetwork",
                        r"highperformanceformat", r"onclick=[\"']window\.location"):
                if re.search(pat, scan, re.I):
                    self.add("adsense", f"{rel}: possible popup/redirect pattern {pat!r}")
            # hidden text via inline style
            for m in re.finditer(r"<[^>]+style=[\"'][^\"']*display\s*:\s*none[^\"']*[\"'][^>]*>([^<]{20,})",
                                 scan, re.I):
                txt = m.group(1).strip()
                if txt and not re.search(r"^(select|option|svg|path)", txt):
                    self.add("adsense", f"{rel}: possible hidden text :: {txt[:60]!r}")
        # ads.txt
        adstxt = os.path.join(self.root, "ads.txt")
        if not os.path.isfile(adstxt):
            self.add("adsense", "ads.txt MISSING")
        else:
            lines = [l.strip() for l in read(adstxt).splitlines()
                     if l.strip() and not l.strip().startswith("#")]
            if lines != [ADS_TXT_LINE]:
                self.add("adsense", f"ads.txt lines unexpected: {lines}")
        # tool works (index has inbox creation code)
        idx = self.pages.get("index.html")
        if idx:
            for marker in ("detectOtp", "fetch("):
                if marker not in idx["html"]:
                    self.add("adsense", f"index.html missing tool marker {marker!r}")

    # -- 12 basics ----------------------------------------------------------
    def check_basics(self):
        rb = os.path.join(self.root, "robots.txt")
        if not os.path.isfile(rb):
            self.add("basics", "robots.txt MISSING")
        else:
            t = read(rb)
            if "Disallow: /" in t and "Allow: /" not in t:
                self.add("basics", "robots.txt disallows crawling")
            if "sitemap" not in t.lower():
                self.add("basics", "robots.txt has no Sitemap line")
        sm = os.path.join(self.root, "sitemap.xml")
        if not os.path.isfile(sm):
            self.add("basics", "sitemap.xml MISSING")
        else:
            t = read(sm)
            locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", t)
            self.info["sitemap_locs"] = len(locs)
            sm_routes = set()
            for loc in locs:
                route = urlparse(loc).path or "/"
                sm_routes.add(route)
                if urlparse(loc).netloc and not urlparse(loc).netloc.endswith("mytemp-mail.online"):
                    self.add("basics", f"sitemap.xml foreign host {loc}")
                if route_to_file(self.root, route) is None:
                    self.add("basics", f"sitemap.xml stale/non-existent URL {loc}")
            # every page should be in the sitemap
            for rel in self.files:
                if url_for(rel) not in sm_routes:
                    self.add("basics", f"sitemap.xml missing page {url_for(rel)} ({rel})")
        # orphans: reachable from homepage
        reach = self._reachable()
        self.info["orphans"] = []
        for rel in self.files:
            if rel == "index.html":
                continue
            if url_for(rel) not in reach and rel not in reach:
                self.info["orphans"].append(rel)
                self.add("basics", f"orphan page (not reachable from homepage): {rel}")

    def _reachable(self):
        seen = set()
        stack = ["index.html"]
        while stack:
            rel = stack.pop()
            if rel in seen or rel not in self.pages:
                continue
            seen.add(rel)
            for href in self.pages[rel]["parsed"].hrefs:
                kind, val = resolve_href(self.root, href, rel)
                if kind == "internal" and val and val.endswith(".html"):
                    stack.append(val)
        return seen

    # -- 13 spelling --------------------------------------------------------
    def check_spelling(self, sample=None):
        import random
        if sample is None:
            others = [f for f in self.files if f != "index.html"]
            random.seed(7)
            sample = ["index.html"] + random.sample(others, 5)
        for rel in sample:
            d = self.pages.get(rel)
            if not d:
                continue
            text = d["parsed"].text("all").lower()
            for typo in COMMON_TYPOS:
                if re.search(r"\b" + re.escape(typo.strip()) + r"\b", text):
                    self.add("spelling", f"{rel}: possible typo {typo.strip()!r}")

    # -- 14 misc ------------------------------------------------------------
    def check_misc(self):
        for rel, d in self.pages.items():
            html = d["html"]
            if re.search(r"<meta[^>]+name=[\"']keywords[\"']", html, re.I):
                pass  # covered in adsense
            if "http://mytemp-mail.online" in html:
                self.add("misc", f"{rel}: insecure http:// link to own domain")
            if "offexmail.online" in html and "mytemp-mail.online" not in html:
                self.add("misc", f"{rel}: references wrong domain")
        # stray bare CTA text (a known artifact pattern)
        for rel, d in self.pages.items():
            if re.search(r"</ol>\s*\n?\s*Create a free inbox →", d["html"]):
                self.add("misc", f"{rel}: stray un-linked 'Create a free inbox →' after </ol>")

    # -- run all ------------------------------------------------------------
    def run(self, spelling_sample=None):
        self.check_titles()
        self.check_descriptions()
        self.check_headings()
        self.check_content()
        self.check_duplicates()
        self.check_canonicals()
        self.check_hreflang()
        self.check_links()
        self.check_images()
        self.check_structured()
        self.check_adsense()
        self.check_basics()
        self.check_spelling(spelling_sample)
        self.check_misc()
        return self.problems


ORDER = ["titles", "descriptions", "headings", "content", "duplicates",
         "canonicals", "hreflang", "links", "images", "structured",
         "adsense", "basics", "spelling", "misc"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", "public"))
    ap.add_argument("--json", default="")
    ap.add_argument("--max-show", type=int, default=40)
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    a = Audit(root)
    a.run()
    print(f"Offex Mail audit — root={root}")
    print(f"pages scanned: {len(a.files)}")
    total = 0
    for key in ORDER:
        probs = a.problems.get(key, [])
        total += len(probs)
        print(f"\n=== [{key}] {len(probs)} problem(s) ===")
        for msg in probs[: args.max_show]:
            print("  -", msg)
        if len(probs) > args.max_show:
            print(f"  ... and {len(probs) - args.max_show} more")
    print(f"\nTOTAL problems: {total}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"problems": dict(a.problems), "info": a.info,
                       "pages": len(a.files)}, fh, indent=1, default=str)
        print("wrote", args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
