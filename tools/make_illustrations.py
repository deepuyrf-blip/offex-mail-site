#!/usr/bin/env python3
"""
Generate the additional self-hosted inline SVG illustrations used across the
Offex Mail site (homepage, language hubs, guides and service pages).

Each illustration is a standalone .svg file written to public/images/. They share
one palette and a common "soft card" look so the design stays consistent:

    accent  #6d4dff / #9b6dff   teal #0ea5b7   ink #1a1730   bg #f1edff

Run: python tools/make_illustrations.py
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "public" / "images"

DEFS = (
    '<defs>'
    '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#6d4dff"/><stop offset="1" stop-color="#9b6dff"/>'
    '</linearGradient>'
    '<linearGradient id="gc" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#6d4dff"/><stop offset="1" stop-color="#0ea5b7"/>'
    '</linearGradient>'
    '</defs>'
)


def wrap(w, h, label, body):
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{label}">{DEFS}'
        f'<rect width="{w}" height="{h}" rx="22" fill="#f1edff"/>{body}</svg>'
    )


def card(x, y, w, h, r=14, fill="#ffffff", stroke="#e3dffb"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def line(x, y, w, h=10, r=5, fill="#e3ddff"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'


def check(cx, cy, s=1.0, color="#0f9d63"):
    return (f'<circle cx="{cx}" cy="{cy}" r="{22*s:.0f}" fill="{color}"/>'
            f'<path d="M{cx-11*s:.0f} {cy} l{8*s:.0f} {9*s:.0f} l{15*s:.0f} -{18*s:.0f}" '
            f'fill="none" stroke="#fff" stroke-width="{5*s:.0f}" stroke-linecap="round" stroke-linejoin="round"/>')


# ---------------------------------------------------------------------------
def comparison_columns():
    b = card(40, 40, 250, 320)
    b += '<rect x="40" y="40" width="250" height="46" rx="14" fill="url(#g)"/>'
    b += '<rect x="40" y="70" width="250" height="16" fill="url(#g)"/>'
    b += line(66, 112, 150, 12) + line(66, 140, 190, 10, fill="#efeaff")
    b += line(66, 162, 170, 10, fill="#efeaff") + line(66, 184, 200, 10, fill="#efeaff")
    b += line(66, 206, 140, 10, fill="#efeaff")
    b += card(350, 40, 250, 320)
    b += '<rect x="350" y="40" width="250" height="46" rx="14" fill="url(#gc)"/>'
    b += '<rect x="350" y="70" width="250" height="16" fill="url(#gc)"/>'
    b += line(376, 112, 150, 12) + line(376, 140, 190, 10, fill="#d8f2f5")
    b += line(376, 162, 170, 10, fill="#d8f2f5") + line(376, 184, 200, 10, fill="#d8f2f5")
    b += line(376, 206, 140, 10, fill="#d8f2f5")
    b += check(300, 200, 0.8, "#6d4dff")
    return wrap(640, 400, "Side-by-side comparison of a throwaway inbox and a permanent second email account", b)


def otp_arrives():
    b = card(90, 60, 460, 280, 18)
    b += '<rect x="90" y="60" width="460" height="44" rx="18" fill="url(#g)"/>'
    b += '<rect x="90" y="86" width="460" height="18" fill="url(#g)"/>'
    b += '<circle cx="118" cy="82" r="6" fill="#fff" opacity=".7"/>'
    b += line(130, 130, 300, 12) + line(130, 158, 380, 10, fill="#efeaff")
    b += '<rect x="130" y="196" width="60" height="66" rx="10" fill="#f3f0ff" stroke="#6d4dff" stroke-width="2"/>'
    b += '<rect x="200" y="196" width="60" height="66" rx="10" fill="#f3f0ff" stroke="#6d4dff" stroke-width="2"/>'
    b += '<rect x="270" y="196" width="60" height="66" rx="10" fill="#f3f0ff" stroke="#6d4dff" stroke-width="2"/>'
    b += '<rect x="340" y="196" width="60" height="66" rx="10" fill="#f3f0ff" stroke="#6d4dff" stroke-width="2"/>'
    b += '<text x="160" y="238" font-family="monospace" font-size="30" font-weight="700" fill="#6d4dff" text-anchor="middle">7</text>'
    b += '<text x="230" y="238" font-family="monospace" font-size="30" font-weight="700" fill="#6d4dff" text-anchor="middle">4</text>'
    b += '<text x="300" y="238" font-family="monospace" font-size="30" font-weight="700" fill="#6d4dff" text-anchor="middle">1</text>'
    b += '<text x="370" y="238" font-family="monospace" font-size="30" font-weight="700" fill="#6d4dff" text-anchor="middle">9</text>'
    b += check(500, 120, 0.9)
    return wrap(640, 400, "A one-time passcode arriving as a message in the temporary inbox", b)


def inbox_timeline():
    b = '<line x1="90" y1="200" x2="550" y2="200" stroke="#d9d2ff" stroke-width="6" stroke-linecap="round"/>'
    for i, (x, c) in enumerate([(120, "#6d4dff"), (280, "#8b6dff"), (440, "#0ea5b7")]):
        b += f'<circle cx="{x}" cy="200" r="20" fill="{c}"/>'
        b += f'<circle cx="{x}" cy="200" r="8" fill="#fff"/>'
    b += line(70, 118, 100, 12) + line(70, 140, 130, 9, fill="#efeaff")
    b += line(230, 118, 100, 12) + line(230, 140, 130, 9, fill="#efeaff")
    b += line(390, 118, 100, 12) + line(390, 140, 130, 9, fill="#efeaff")
    b += line(70, 250, 110, 10, fill="#efeaff") + line(230, 250, 110, 10, fill="#efeaff")
    b += line(390, 250, 130, 10, fill="#efeaff")
    b += '<text x="120" y="300" font-family="sans-serif" font-size="16" fill="#5b5776" text-anchor="middle">create</text>'
    b += '<text x="280" y="300" font-family="sans-serif" font-size="16" fill="#5b5776" text-anchor="middle">receive</text>'
    b += '<text x="440" y="300" font-family="sans-serif" font-size="16" fill="#5b5776" text-anchor="middle">expire</text>'
    return wrap(640, 400, "Timeline showing a temporary inbox being created, receiving mail and then expiring", b)


def spam_sources():
    b = '<circle cx="320" cy="110" r="46" fill="url(#g)"/>'
    b += '<text x="320" y="118" font-family="sans-serif" font-size="20" fill="#fff" text-anchor="middle">you</text>'
    for i, x in enumerate([120, 240, 400, 520]):
        b += f'<line x1="320" y1="156" x2="{x}" y2="250" stroke="#c9bcff" stroke-width="3" stroke-dasharray="6 6"/>'
        b += card(x - 55, 250, 110, 96, 12)
        b += line(x - 38, 274, 76, 10) + line(x - 38, 296, 60, 8, fill="#efeaff")
        b += line(x - 38, 314, 70, 8, fill="#efeaff")
    return wrap(640, 400, "One email address branching out to many sites that may resell or leak it", b)


def domain_reputation():
    b = card(60, 70, 240, 260, 16)
    b += '<rect x="60" y="70" width="240" height="44" rx="16" fill="#e7f8ee"/>'
    b += check(180, 92, 0.7, "#0f9d63")
    b += line(84, 140, 150, 12) + line(84, 168, 180, 10, fill="#efeaff")
    b += line(84, 192, 140, 10, fill="#efeaff")
    b += '<text x="180" y="300" font-family="sans-serif" font-size="15" fill="#0f9d63" text-anchor="middle">accepted</text>'
    b += card(340, 70, 240, 260, 16)
    b += '<rect x="340" y="70" width="240" height="44" rx="16" fill="#ffe6ec"/>'
    b += '<path d="M468 82 l14 14 M482 82 l-14 14" stroke="#df3d5c" stroke-width="4" stroke-linecap="round"/>'
    b += line(364, 140, 150, 12) + line(364, 168, 180, 10, fill="#f3e0e6")
    b += line(364, 192, 140, 10, fill="#f3e0e6")
    b += '<text x="460" y="300" font-family="sans-serif" font-size="15" fill="#df3d5c" text-anchor="middle">rejected</text>'
    return wrap(640, 400, "A real domain that is accepted next to a known throwaway domain that is rejected", b)


def desktop_mobile():
    b = card(60, 70, 380, 250, 16)
    b += '<rect x="60" y="70" width="380" height="40" rx="16" fill="url(#g)"/>'
    b += '<rect x="60" y="92" width="380" height="18" fill="url(#g)"/>'
    b += line(88, 140, 200, 12) + line(88, 166, 300, 10, fill="#efeaff")
    b += line(88, 190, 260, 10, fill="#efeaff") + line(88, 214, 300, 10, fill="#efeaff")
    b += card(420, 96, 150, 268, 20)
    b += '<rect x="440" y="118" width="110" height="14" rx="7" fill="#efeaff"/>'
    b += '<rect x="440" y="146" width="110" height="90" rx="10" fill="#f3f0ff" stroke="#d9d2ff" stroke-width="2"/>'
    b += line(452, 160, 80, 8, fill="#e3ddff") + line(452, 178, 60, 8, fill="#e3ddff")
    b += '<circle cx="495" cy="330" r="12" fill="none" stroke="#9b6dff" stroke-width="3"/>'
    b += '<circle cx="320" cy="330" r="8" fill="#6d4dff"/>'
    return wrap(640, 400, "The same temporary inbox open on a desktop browser and a phone", b)


def secure_form():
    b = card(140, 70, 360, 270, 18)
    b += line(170, 104, 220, 14)
    b += '<rect x="170" y="140" width="300" height="42" rx="10" fill="#f4f3fb" stroke="#d9d2ff" stroke-width="2"/>'
    b += line(188, 156, 150, 10, fill="#c9bcff")
    b += '<rect x="170" y="196" width="300" height="42" rx="10" fill="#f4f3fb" stroke="#d9d2ff" stroke-width="2"/>'
    b += line(188, 212, 110, 10, fill="#c9bcff")
    b += '<rect x="170" y="258" width="150" height="46" rx="12" fill="url(#g)"/>'
    b += line(192, 276, 106, 10, fill="#ffffff", fill_opacity=".9") if False else '<rect x="192" y="276" width="106" height="10" rx="5" fill="#ffffff" opacity=".9"/>'
    b += '<path d="M470 150 l0 -26 a26 26 0 0 1 52 0 l0 26" fill="none" stroke="#6d4dff" stroke-width="6"/>'
    b += '<rect x="458" y="150" width="76" height="60" rx="12" fill="url(#g)"/>'
    b += '<circle cx="496" cy="178" r="8" fill="#fff"/>'
    return wrap(640, 400, "A sign-up form being filled with a temporary address under a padlock", b)


def cleanup_checklist():
    b = card(120, 60, 400, 290, 18)
    b += line(150, 92, 200, 14)
    for i, y in enumerate([140, 186, 232, 278]):
        b += f'<rect x="150" y="{y-16}" width="26" height="26" rx="7" fill="#e7f8ee" stroke="#0f9d63" stroke-width="2"/>'
        b += f'<path d="M156 {y-3} l6 7 l11 -13" fill="none" stroke="#0f9d63" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        b += line(192, y - 8, 280 - i * 20, 12, fill="#efeaff")
    return wrap(640, 400, "A checklist of habits that keep a real inbox free of spam", b)


def phishing_alert():
    b = card(150, 70, 340, 260, 18)
    b += '<path d="M320 78 L400 190 L240 190 Z" fill="#fff4d6" stroke="#e0a100" stroke-width="3" stroke-linejoin="round"/>'
    b += '<text x="320" y="176" font-family="sans-serif" font-size="60" font-weight="800" fill="#e0a100" text-anchor="middle">!</text>'
    b += line(190, 226, 240, 12) + line(190, 252, 260, 10, fill="#efeaff")
    b += line(190, 276, 200, 10, fill="#efeaff")
    b += '<text x="320" y="320" font-family="sans-serif" font-size="15" fill="#5b5776" text-anchor="middle">verify sender before you click</text>'
    return wrap(640, 400, "Warning triangle over a suspicious verification email", b)


def verification_3ways():
    labels = ["link", "code", "button"]
    b = ""
    for i, x in enumerate([70, 250, 430]):
        b += card(x, 110, 140, 180, 16)
        b += f'<rect x="{x}" y="110" width="140" height="34" rx="16" fill="url(#g)"/>'
        b += f'<rect x="{x}" y="128" width="140" height="16" fill="url(#g)"/>'
        b += line(x + 20, 168, 100, 10) + line(x + 20, 190, 80, 8, fill="#efeaff")
        b += line(x + 20, 210, 90, 8, fill="#efeaff")
        b += f'<text x="{x+70}" y="300" font-family="sans-serif" font-size="16" fill="#5b5776" text-anchor="middle">{labels[i]}</text>'
    return wrap(640, 400, "Three ways sites verify email: a link, a one-time code and a confirm button", b)


def dev_testing():
    b = card(70, 80, 300, 250, 16)
    b += '<rect x="70" y="80" width="300" height="40" rx="16" fill="#1a1730"/>'
    b += '<rect x="70" y="102" width="300" height="18" fill="#1a1730"/>'
    b += '<circle cx="94" cy="100" r="5" fill="#6d4dff"/><circle cx="112" cy="100" r="5" fill="#9b6dff"/><circle cx="130" cy="100" r="5" fill="#0ea5b7"/>'
    for i, y in enumerate([150, 178, 206, 234]):
        b += line(94, y, 150 - (i % 2) * 40, 10, fill="#4a4570")
    b += card(400, 120, 180, 170, 16)
    b += '<text x="490" y="176" font-family="monospace" font-size="26" font-weight="700" fill="#6d4dff" text-anchor="middle">200 OK</text>'
    b += line(430, 200, 120, 10) + line(430, 224, 90, 8, fill="#efeaff")
    b += line(430, 246, 110, 8, fill="#efeaff")
    return wrap(640, 400, "A developer console running automated sign-up and verification tests", b)


def data_broker():
    b = '<circle cx="150" cy="120" r="40" fill="url(#g)"/>'
    b += '<text x="150" y="128" font-family="sans-serif" font-size="18" fill="#fff" text-anchor="middle">you</text>'
    b += '<path d="M200 140 q120 -40 240 20" fill="none" stroke="#c9bcff" stroke-width="4" stroke-dasharray="7 7"/>'
    b += card(400, 90, 190, 120, 16)
    b += line(424, 118, 140, 12) + line(424, 144, 100, 9, fill="#efeaff")
    b += line(424, 166, 120, 9, fill="#efeaff")
    b += '<text x="495" y="196" font-family="sans-serif" font-size="14" fill="#5b5776" text-anchor="middle">data broker</text>'
    b += '<circle cx="150" cy="290" r="34" fill="#efeaff"/>'
    b += '<text x="150" y="298" font-family="sans-serif" font-size="15" fill="#6d4dff" text-anchor="middle">temp</text>'
    b += '<path d="M198 290 h60" stroke="#0f9d63" stroke-width="5" stroke-linecap="round"/>'
    b += '<path d="M250 282 l10 8 l-10 8" fill="none" stroke="#0f9d63" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
    b += '<text x="300" y="298" font-family="sans-serif" font-size="14" fill="#0f9d63">nothing to sell</text>'
    return wrap(640, 400, "A throwaway address keeping a real inbox out of data-broker lists", b)


def digital_footprint():
    b = ""
    for i, (x, y, r) in enumerate([(200, 150, 34), (260, 200, 26), (170, 230, 22),
                                   (300, 150, 20), (240, 120, 16), (330, 230, 28)]):
        b += f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#c9bcff" stroke-width="3"/>'
    b += '<circle cx="250" cy="185" r="18" fill="url(#g)"/>'
    b += card(400, 100, 190, 200, 16)
    b += line(424, 132, 140, 12) + line(424, 158, 100, 9, fill="#efeaff")
    b += line(424, 182, 120, 9, fill="#efeaff") + line(424, 206, 90, 9, fill="#efeaff")
    b += check(495, 262, 0.9)
    return wrap(640, 400, "A shrinking digital footprint when sign-ups use a disposable address", b)


ILLUSTRATIONS = {
    "comparison-columns.svg": comparison_columns,
    "otp-arrives.svg": otp_arrives,
    "inbox-timeline.svg": inbox_timeline,
    "spam-sources.svg": spam_sources,
    "domain-reputation.svg": domain_reputation,
    "desktop-mobile.svg": desktop_mobile,
    "secure-form.svg": secure_form,
    "cleanup-checklist.svg": cleanup_checklist,
    "phishing-alert.svg": phishing_alert,
    "verification-3ways.svg": verification_3ways,
    "dev-testing.svg": dev_testing,
    "data-broker.svg": data_broker,
    "digital-footprint.svg": digital_footprint,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in ILLUSTRATIONS.items():
        (OUT / name).write_text(fn(), encoding="utf-8")
        print("wrote", name)
    print(f"{len(ILLUSTRATIONS)} illustrations")


if __name__ == "__main__":
    main()
