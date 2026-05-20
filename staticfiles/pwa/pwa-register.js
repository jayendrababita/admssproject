(function () {
  if (!window.isSecureContext || !('serviceWorker' in navigator)) {
    return;
  }

  function registerSW() {
    navigator.serviceWorker
      .register('/service-worker.js', { scope: '/' })
      .catch(function () {});
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', registerSW);
  } else {
    registerSW();
  }
})();
