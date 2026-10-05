// Offex Mail PWA service worker - app-shell cache.
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
