// Monetag push service worker removed. This stub unregisters itself so old
// subscribers stop receiving notifications from the retired network.
self.addEventListener('install', function(){ self.skipWaiting(); });
self.addEventListener('activate', function(e){ e.waitUntil(self.registration.unregister()); });
