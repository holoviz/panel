// panel.holoviz.org used to be one unversioned Sphinx site, and its nbsite and
// `panel convert --pwa` service workers were registered at / and /pyodide/. Those serve
// every request cache-first and fail on the redirects into /en/docs/, so returning
// visitors would be stuck on the old site. Browsers re-fetch this script on navigation;
// this version deletes the old caches, unregisters itself and reloads its pages.
self.addEventListener('install', () => self.skipWaiting())

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys()
    await Promise.all(names.filter((name) => name.startsWith('Panel')).map((name) => caches.delete(name)))
    await self.registration.unregister()
    const pages = await self.clients.matchAll({type: 'window'})
    pages.forEach((page) => page.navigate(page.url))
  })())
})
