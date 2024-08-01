const appName = '{{ name }}'
const appCacheName = '{{ name }}-{{ uuid }}';

const preCacheFiles = [{{ pre_cache }}];

self.addEventListener('install', (e) => {
  console.log('[Service Worker] Install');
  self.skipWaiting();
  e.waitUntil((async () => {
    const cacheNames = await caches.keys();
    for (const cacheName of cacheNames) {
      if (cacheName.startsWith(appName) && cacheName !== appCacheName) {
        console.log(`[Service Worker] Delete old cache ${cacheName}`);
        caches.delete(cacheName);
      }
    }
    const cache = await caches.open(appCacheName);
    console.log('[Service Worker] Caching ');
    preCacheFiles.forEach(async (cacheFile) => {
      const request = new Request(cacheFile);
      const response = await fetch(request);
      if (response.ok || response.type == 'opaque') {
        cache.put(request, response);
      }
    })
  })());
});

self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating');
  return self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') {
    return
  }
  e.respondWith((async () => {
    const cache = await caches.open(appCacheName);
    let response = await cache.match(e.request);
    console.log(`[Service Worker] Fetching resource: ${e.request.url}`);
    if (response) {
      return response;
    }
    response = await fetch(e.request);
    if (!response.ok && !(response.type == 'opaque')) {
      throw Error('[Service Worker] Fetching resource failed with response: ' + response.status);
    }
    console.log(`[Service Worker] Caching new resource: ${e.request.url}`);
    cache.put(e.request, response.clone());
    return response;
  })());
});
