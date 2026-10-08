// Offex Audio service worker.
//
// This is a self-unregistering stub. The previous worker cached pages/assets and
// showed a push notification; both are retired. On activate this worker deletes
// every Cache Storage bucket this origin owns and then unregisters itself, so
// already-installed workers on users' devices go away and stop serving stale
// copies of app-ui.html / index.html.
//
// It deliberately installs NO fetch handler, so it never intercepts requests.

self.addEventListener('install', function () {
  // Activate immediately instead of waiting for existing tabs to close.
  self.skipWaiting();
});

self.addEventListener('activate', function (event) {
  event.waitUntil((async function () {
    try {
      var keys = await caches.keys();
      await Promise.all(keys.map(function (key) { return caches.delete(key); }));
    } catch (err) { /* Cache Storage unavailable - nothing to clear */ }
    try {
      await self.registration.unregister();
    } catch (err) { /* already gone */ }
  })());
});
