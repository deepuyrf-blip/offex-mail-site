OFFEX AUDIO — CLOUDFLARE PAGES (NO HUGGING FACE DEPENDENCY)

What changed
------------
The site no longer uses a Hugging Face Space or the Gradio client. The
audio-processing dependency on hydui-ytvideo.hf.space has been removed
completely, along with all /hf/* proxying and the HF_TOKEN secret.

How the tools work now
----------------------
- Remove Silence  -> runs entirely in the browser (audio-engine.js, Web Audio API).
- Enhance Audio   -> runs entirely in the browser (noise gate + high-pass + normalise).
- Voice / BGM     -> server-side AI feature. Shown as "Not connected" unless a
                     processing backend is configured (see BACKEND_URL below).

Files served (Cloudflare Pages project: "audio", domain offexmail.online)
------------------------------------------------------------------------
index.html, _worker.js, styles.css, audio-engine.js, favicon.svg, robots.txt,
sitemap.xml, ads.txt, sw.js, promo.js, and the guide/legal .html pages.

Health indicator
----------------
_worker.js exposes GET /health which returns JSON, e.g.
  {"status":"ok","service":"offex-audio","time":"...","processor":false}
The page fetches /health with a 4.5s timeout and shows a green "Live" badge
when it responds, or "Not connected" when it does not. The check never blocks
the page and retries automatically every 25 seconds.

Optional server processor
-------------------------
To enable the server-side Voice / BGM tool later, set a plain-text Pages
variable named BACKEND_URL on the "audio" project, pointing at a service that
exposes /health and the separation endpoint. The worker then proxies /api/* to
it and /health reports "processor": true. No token is required by default, and
never hardcode secrets into the HTML or JS.
