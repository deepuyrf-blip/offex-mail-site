# ============================================================================
#  gna_5.py  -  Offex Audio, generator 5 of 6  (bundled assets)
# ============================================================================
#  v1.1: the app no longer ships a fake local UI shell. The WebView loads the
#  REAL website (https://offexmail.online), so the only bundled asset is a tiny
#  offline fallback page shown if the site cannot be reached. It contains NO
#  fake job logic - it only offers a Retry that reloads the live site.
# ============================================================================
import os

DST = "android-audio/app/src/main/assets"

OFFLINE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Offex Audio</title>
<style>
  :root { color-scheme: dark; }
  html, body { margin: 0; height: 100%; }
  body {
    background: #05060D; color: #EEF1FB;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    display: flex; align-items: center; justify-content: center; padding: 24px;
  }
  .card {
    max-width: 420px; width: 100%; text-align: center;
    background: #0A0C18; border: 1px solid #1B2140; border-radius: 22px;
    padding: 32px 24px;
  }
  .dot {
    width: 56px; height: 56px; margin: 0 auto 18px; border-radius: 50%;
    background: linear-gradient(135deg, #6366F1, #D946EF);
    display: flex; align-items: center; justify-content: center; font-size: 26px;
  }
  h1 { font-size: 20px; margin: 0 0 8px; }
  p { color: #9AA3C0; font-size: 14px; line-height: 1.5; margin: 0 0 22px; }
  button {
    appearance: none; border: 0; border-radius: 14px; cursor: pointer;
    padding: 14px 22px; font-size: 15px; font-weight: 700; color: #FFFFFF;
    background: linear-gradient(135deg, #6366F1, #D946EF); width: 100%;
  }
</style>
</head>
<body>
  <div class="card">
    <div class="dot">&#9835;</div>
    <h1>You are offline</h1>
    <p>Offex Audio could not reach the live audio site. Check your connection and try again.</p>
    <button onclick="location.replace('https://offexmail.online/')">Retry</button>
  </div>
</body>
</html>
"""

os.makedirs(DST, exist_ok=True)
path = os.path.join(DST, "offline.html")
with open(path, "w", encoding="utf-8") as f:
    f.write(OFFLINE)
print("GNA5: assets/offline.html (%d bytes)" % os.path.getsize(path))

# The WebView now loads the real site, so no bundled UI shell / vendored Gradio
# client is shipped. If a stale copy from a previous run is present, drop it.
for stale in ("offex_audio_ui.html", "audio-engine.js", "gradio_client.js"):
    sp = os.path.join(DST, stale)
    if os.path.exists(sp):
        os.remove(sp)
        print("GNA5: removed stale asset %s" % stale)

print("GNA5: done (real site is loaded from the network; only offline.html bundled)")
