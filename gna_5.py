# ============================================================================
#  gna_5.py  -  Offex Audio, generator 5 of 6  (bundled web assets)
# ============================================================================
#  Copies the self-contained UI shell into app/src/main/assets/:
#    * offex_audio_ui.html  - the whole UI (CSS + SVG + JS inline)
#    * audio-engine.js      - the in-browser fallback engine (Remove Silence /
#                             Enhance work even when the backend is offline)
#    * gradio_client.js     - a vendored, ESM->classic build of @gradio/client
#                             so the page has NO external CDN dependency
#  Sources live in audioapp/assets/. A missing source is a hard failure.
# ============================================================================
import os, shutil

SRC = "audioapp/assets"
DST = "android-audio/app/src/main/assets"

FILES = ["offex_audio_ui.html", "audio-engine.js", "gradio_client.js"]

os.makedirs(DST, exist_ok=True)
missing = []
for name in FILES:
    s = os.path.join(SRC, name)
    if not os.path.exists(s):
        missing.append(name)
        continue
    shutil.copyfile(s, os.path.join(DST, name))
    print("GNA5: assets/%s (%d bytes)" % (name, os.path.getsize(os.path.join(DST, name))))

if missing:
    raise SystemExit("GNA5: MISSING asset source(s) in %s: %s" % (SRC, ", ".join(missing)))

# Guard: the UI shell must not reference an external CDN for its own code.
html = open(os.path.join(DST, "offex_audio_ui.html"), encoding="utf-8").read()
for bad in ("cdn.jsdelivr.net", "unpkg.com", "fonts.googleapis.com", "cdnjs.cloudflare.com"):
    if bad in html:
        raise SystemExit("GNA5: UI shell must not depend on external CDN (%s)" % bad)
print("GNA5: UI shell has no external CDN dependencies")
