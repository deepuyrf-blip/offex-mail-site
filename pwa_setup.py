import json
import os
import sys

from PIL import Image, ImageDraw

PURPLE = (109, 77, 255, 255)
WHITE = (255, 255, 255, 255)
OUT = "public"
ICONS = os.path.join(OUT, "icons")
os.makedirs(ICONS, exist_ok=True)


def make_icon(size, maskable=False):
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if maskable:
        d.rectangle([0, 0, S, S], fill=PURPLE)
        scale = 0.60
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.24), fill=PURPLE)
        scale = 0.70

    def X(v):
        return S / 2 + (v - 50) * S * scale / 100

    def Y(v):
        return S / 2 + (v - 50) * S * scale / 100

    w = max(2, int(S * 0.055))
    d.rectangle([X(22), Y(34), X(78), Y(66)], outline=WHITE, width=w)
    d.line([(X(24), Y(37)), (X(50), Y(57)), (X(76), Y(37))], fill=WHITE, width=w, joint="curve")
    return img.resize((size, size), Image.LANCZOS)


for s in (192, 512):
    make_icon(s).save(os.path.join(ICONS, "icon-%d.png" % s))
make_icon(512, maskable=True).save(os.path.join(ICONS, "icon-maskable-512.png"))
make_icon(180).save(os.path.join(ICONS, "apple-touch-icon.png"))
print("icons written:", sorted(os.listdir(ICONS)))


manifest = {
    "name": "Offex Temp Mail - Instant Disposable Inbox",
    "short_name": "Offex Mail",
    "description": "Free temp mail. Get a disposable inbox instantly for OTPs, verification links and test emails.",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#0f1117",
    "theme_color": "#6d4dff",
    "icons": [
        {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
open(os.path.join(OUT, "manifest.webmanifest"), "w", encoding="utf-8").write(
    json.dumps(manifest, indent=2, ensure_ascii=False)
)
print("manifest written")


sw = r'''// Offex Mail PWA service worker - app-shell cache.
// API calls (api.mytemp-mail.online) are never cached.
const CACHE = "offex-pwa-v1";
const SHELL = [
  "/", "/index.html", "/i18n.js", "/manifest.webmanifest",
  "/icons/icon-192.png", "/icons/icon-512.png", "/favicon.svg",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api")) return;

  const isHtml = req.mode === "navigate" || url.pathname === "/" || url.pathname.endsWith(".html");
  if (isHtml) {
    e.respondWith(
      fetch(req)
        .then((r) => {
          const cp = r.clone();
          caches.open(CACHE).then((c) => c.put(req, cp));
          return r;
        })
        .catch(() => caches.match(req).then((m) => m || caches.match("/")))
    );
    return;
  }

  e.respondWith(
    caches.match(req).then(
      (m) =>
        m ||
        fetch(req).then((r) => {
          if (r.ok) {
            const cp = r.clone();
            caches.open(CACHE).then((c) => c.put(req, cp));
          }
          return r;
        })
    )
  );
});
'''
open(os.path.join(OUT, "sw.js"), "w", encoding="utf-8").write(sw)
print("sw.js written")


p = os.path.join(OUT, "index.html")
s = open(p, encoding="utf-8").read()

head = '''</head>'''
head_add = '''<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#6d4dff">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Offex Mail">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
</head>'''
if s.count(head) != 1:
    print("head anchor FAIL", s.count(head))
    sys.exit(2)
s = s.replace(head, head_add, 1)

old_api = 'return fetch(API_BASE + "/api" + path, Object.assign({ headers:{ "content-type":"application/json" } }, opts||{}))'
new_api = ('var _h = Object.assign({ "content-type":"application/json" }, (opts && opts.headers) || {});\n'
           '    if((((opts||{}).method)||"GET").toUpperCase()==="POST" && path==="/inbox"){ try{ var _el=document.querySelector(\'[name="cf-turnstile-response"]\'); if(_el && _el.value) _h["x-turnstile-token"]=_el.value; }catch(e){} }\n'
           '    opts = Object.assign({}, opts, { headers: _h });\n'
           '    return fetch(API_BASE + "/api" + path, opts)')
if s.count(old_api) != 1:
    print("api anchor FAIL", s.count(old_api))
    sys.exit(2)
s = s.replace(old_api, new_api, 1)

body_add = '''<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
<div class="cf-turnstile" data-sitekey="0x4AAAAAAFN9iQll6bXoy2tA" data-size="invisible" data-theme="dark"></div>
<button id="pwaInstall" style="display:none;position:fixed;left:50%;transform:translateX(-50%);bottom:18px;z-index:9998;padding:12px 22px;border:0;border-radius:999px;background:#6d4dff;color:#fff;font-weight:700;font-size:14px;cursor:pointer;box-shadow:0 8px 24px rgba(109,77,255,.45)">📲 Install app</button>
<script>
(function(){
  if("serviceWorker" in navigator){ window.addEventListener("load", function(){ navigator.serviceWorker.register("/sw.js").catch(function(){}); }); }
  var deferred = null, btn = document.getElementById("pwaInstall");
  window.addEventListener("beforeinstallprompt", function(e){ e.preventDefault(); deferred = e; if(btn) btn.style.display = "block"; });
  if(btn){ btn.onclick = function(){ if(!deferred) return; deferred.prompt(); deferred.userChoice.then(function(){ deferred = null; btn.style.display = "none"; }); }; }
  window.addEventListener("appinstalled", function(){ if(btn) btn.style.display = "none"; });
})();
</script>
</body>'''
if s.count("</body>") != 1:
    print("body close anchor FAIL", s.count("</body>"))
    sys.exit(2)
s = s.replace("</body>", body_add, 1)

open(p, "w", encoding="utf-8").write(s)
print("index.html patched, size:", len(s))
