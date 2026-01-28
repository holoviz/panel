const appName = 'Panel Pyodide App'
const appCacheName = 'Panel Pyodide App-e06a0f2e3ece45afa7f2b9047479a4b8';

const preCacheFiles = ['images/favicon.ico', 'images/icon-vector.svg', 'images/icon-32x32.png', 'images/icon-192x192.png', 'images/icon-512x512.png', 'images/apple-touch-icon.png', 'images/index_background.png'];

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