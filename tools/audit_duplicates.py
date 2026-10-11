#!/usr/bin/env python3
"""
Offex Mail — duplicate / near-duplicate content audit.

Walks every HTML page under public/, extracts the visible text, and reports:

  1. shingle-based (6-gram Jaccard) similarity between pages *within the same
     language*, flagging pairs above a threshold (default 0.85);
  2. per-language stats: page count, average pairwise similarity, worst pairs;
  3. thin pages (visible word count below --min-words, default 400);
  4. duplicate <title> and duplicate <meta name="description"> across pages;
  5. repeated identical long sentences (>= 40 words) appearing on more than
     one page.

Usage:
    python tools/audit_duplicates.py                 # concise report
    python tools/audit_duplicates.py --json out.json # also dump machine JSON
    python tools/audit_duplicates.py --threshold .80 --min-words 350
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"

LANGS = ["en", "hi", "es", "fr", "de", "pt", "ru", "ar", "zh", "ja"]

# ----------------------------------------------------------------------------
# text extraction
# ----------------------------------------------------------------------------
_RE_SCRIPT = re.compile(r"<(script|style|noscript)\b[^>]*>.*?</\1>", re.I | re.S)
_RE_COMMENT = re.compile(r"<!--.*?-->", re.S)
_RE_TAG = re.compile(r"<[^>]+>")
_RE_WS = re.compile(r"\s+")
_RE_TITLE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
_RE_DESC = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', re.I | re.S
)
_RE_DESC_ALT = re.compile(
    r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', re.I | re.S
)


def strip_html(raw: str) -> str:
    """Return visible text only."""
    txt = _RE_SCRIPT.sub(" ", raw)
    txt = _RE_COMMENT.sub(" ", txt)
    # drop head-only blocks that are not visible
    txt = _RE_TAG.sub(" ", txt)
    txt = html.unescape(txt)
    txt = txt.replace("\u00a0", " ")
    return _RE_WS.sub(" ", txt).strip()


# CJK scripts are written without spaces, so a whole clause would collapse into
# a single token. Split each CJK ideograph / kana / hangul syllable into its own
# token so shingling still works for zh and ja.
_RE_CJK = re.compile(
    r"([\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af])"
)


def words(text: str) -> list[str]:
    text = text.lower()
    text = _RE_CJK.sub(r" \1 ", text)
    return re.findall(r"[^\W\d_]+|\d+", text, flags=re.UNICODE)


def ngrams(tokens: list[str], n: int = 6) -> set[tuple]:
    if len(tokens) < n:
        return set()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / (len(a) + len(b) - inter)


def lang_of(rel: str) -> str:
    parts = rel.split("/")
    if parts[0] in LANGS and parts[0] != "en":
        return parts[0]
    return "en"


def meta_of(raw: str) -> tuple[str, str]:
    m = _RE_TITLE.search(raw)
    title = _RE_WS.sub(" ", html.unescape(m.group(1))).strip() if m else ""
    d = _RE_DESC.search(raw) or _RE_DESC_ALT.search(raw)
    desc = _RE_WS.sub(" ", html.unescape(d.group(1))).strip() if d else ""
    return title, desc


# ----------------------------------------------------------------------------
# collect pages
# ----------------------------------------------------------------------------
def collect():
    pages = {}
    for p in sorted(PUBLIC.rglob("*.html")):
        rel = p.relative_to(PUBLIC).as_posix()
        raw = p.read_text(encoding="utf-8", errors="ignore")
        text = strip_html(raw)
        toks = words(text)
        title, desc = meta_of(raw)
        pages[rel] = {
            "rel": rel,
            "lang": lang_of(rel),
            "text": text,
            "tokens": toks,
            "wc": len(toks),
            "shingles": ngrams(toks, 6),
            "title": title,
            "desc": desc,
        }
    return pages


def sentences_40w(pages):
    """Map a normalized 40+ word sentence -> set of pages it appears on."""
    seen = defaultdict(set)
    for rel, pg in pages.items():
        for sent in re.split(r"[.!?\n]+", pg["text"]):
            w = words(sent)
            if len(w) >= 40:
                key = " ".join(w)
                seen[key].add(rel)
    return {k: v for k, v in seen.items() if len(v) > 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.85)
    ap.add_argument("--min-words", type=int, default=400)
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    pages = collect()
    by_lang = defaultdict(list)
    for pg in pages.values():
        by_lang[pg["lang"]].append(pg)

    print("=" * 78)
    print("OFFEX MAIL — DUPLICATE / NEAR-DUPLICATE CONTENT AUDIT")
    print("=" * 78)
    print(f"Pages scanned : {len(pages)}")
    print(f"Threshold     : Jaccard(6-gram) > {args.threshold}")
    print(f"Thin threshold: < {args.min_words} visible words")
    print()

    results = {"pages": len(pages), "threshold": args.threshold,
               "min_words": args.min_words, "languages": {}, "pairs": [],
               "thin": [], "dup_titles": {}, "dup_descs": {},
               "repeated_sentences": []}

    all_pairs = []
    for lang in LANGS:
        group = by_lang.get(lang, [])
        if not group:
            continue
        sims = []
        worst = []
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                s = jaccard(a["shingles"], b["shingles"])
                sims.append(s)
                worst.append((s, a["rel"], b["rel"]))
                if s > args.threshold:
                    all_pairs.append((lang, s, a["rel"], b["rel"]))
        avg = sum(sims) / len(sims) if sims else 0.0
        worst.sort(reverse=True)
        results["languages"][lang] = {
            "pages": len(group),
            "avg_similarity": round(avg, 4),
            "max_similarity": round(worst[0][0], 4) if worst else 0.0,
            "worst_pairs": [{"sim": round(s, 4), "a": a, "b": b}
                            for s, a, b in worst[:5]],
        }
        mx = worst[0][0] if worst else 0.0
        print(f"--- {lang} : {len(group)} pages | avg pairwise similarity "
              f"{avg:.3f} | max {mx:.3f}")

    print()
    print(f"NEAR-DUPLICATE PAIRS (>{args.threshold}): {len(all_pairs)}")
    all_pairs.sort(key=lambda x: -x[1])
    for lang, s, a, b in all_pairs[:60]:
        print(f"  [{lang}] {s:.3f}  {a}  <->  {b}")
    results["pairs"] = [{"lang": l, "sim": round(s, 4), "a": a, "b": b}
                        for l, s, a, b in all_pairs]

    # thin pages
    print()
    thin = sorted((pg["wc"], pg["rel"]) for pg in pages.values()
                  if pg["wc"] < args.min_words)
    print(f"THIN PAGES (<{args.min_words} words): {len(thin)}")
    for wc, rel in thin:
        print(f"  {wc:5d}  {rel}")
    results["thin"] = [{"wc": wc, "rel": rel} for wc, rel in thin]

    # duplicate titles / descriptions
    def dups(field):
        m = defaultdict(list)
        for pg in pages.values():
            if pg[field]:
                m[pg[field]].append(pg["rel"])
        return {k: v for k, v in m.items() if len(v) > 1}

    dt = dups("title")
    dd = dups("desc")
    print()
    print(f"DUPLICATE TITLES: {len(dt)} groups")
    for k, v in list(dt.items())[:25]:
        print(f"  x{len(v)}: {k[:70]}  -> {', '.join(v[:6])}")
    print()
    print(f"DUPLICATE META DESCRIPTIONS: {len(dd)} groups")
    for k, v in list(dd.items())[:25]:
        print(f"  x{len(v)}: {k[:70]}  -> {', '.join(v[:6])}")
    results["dup_titles"] = {k: v for k, v in dt.items()}
    results["dup_descs"] = {k: v for k, v in dd.items()}

    # repeated long sentences
    rep = sentences_40w(pages)
    print()
    print(f"REPEATED 40+ WORD SENTENCES (on >1 page): {len(rep)}")
    for k, v in list(rep.items())[:30]:
        print(f"  x{len(v)}: {' '.join(k.split()[:12])}...  -> {', '.join(sorted(v)[:5])}")
    results["repeated_sentences"] = [
        {"pages": sorted(v), "text": k[:200]} for k, v in rep.items()
    ]

    if args.json:
        Path(args.json).write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print(f"\nJSON written to {args.json}")

    return results


if __name__ == "__main__":
    main()
