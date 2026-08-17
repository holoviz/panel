if ('serviceWorker' in navigator) {
  const url_root = document.getElementsByTagName('html')[0].getAttribute('data-content_root')
  navigator.serviceWorker.register(`${url_root}PyodideServiceWorker.js`).then(reg => {
    reg.onupdatefound = () => {
      const installingWorker = reg.installing;
      installingWorker.onstatechange = () => {
        if (installingWorker.state === 'installed' &&
            navigator.serviceWorker.controller) {
          // Reload page if service worker is replaced
          location.reload();
        }
      }
    }
  })
}