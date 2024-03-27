if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register(DOCUMENTATION_OPTIONS.URL_ROOT + 'PyodideServiceWorker.js').then(reg => {
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