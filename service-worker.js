self.addEventListener('install', function(e) {
  console.log('Service Worker installed');
  e.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', function(e) {
  console.log('Service Worker activated');
  return self.clients.claim();
});
