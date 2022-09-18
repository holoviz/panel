const appName = 'panel-convert-{{ uuid }}';

const preCacheFiles = [{{ pre_cache }}];

self.addEventListener('install', (e) => {
  console.log('[Service Worker] Install');
  e.waitUntil((async () => {
    const cache = await caches.open(appName);
    console.log('[Service Worker] Caching ');
    await cache.addAll(preCacheFiles);
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.forEach((cache, cacheName) => {
      if (cacheName.startsWith('panel-converted') && cacheName !== appName) {
        return caches.delete(cacheName);
      }
    })
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith((async () => {
    const cache = await caches.open(appName);
    const response = await cache.match(e.request);
    console.log(`[Service Worker] Fetching resource: ${e.request.url}`);
    if (response) { return response; }
    const response = await fetch(e.request);
    const cache = await caches.open(cacheName);
    console.log(`[Service Worker] Caching new resource: ${e.request.url}`);
    cache.put(e.request, response.clone());
    return response;
  })());
});
