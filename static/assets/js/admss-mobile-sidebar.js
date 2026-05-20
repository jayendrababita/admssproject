/**
 * Use native sidebar scroll instead of AdminLTE overlayScrollbars
 * (overlayScrollbars often blocks touch scroll on phones).
 */
(function ($) {
  'use strict';

  function destroySidebarOverlayScrollbars() {
    if (typeof $.fn.overlayScrollbars === 'undefined') {
      return;
    }

    $('.main-sidebar .sidebar').each(function () {
      var $el = $(this);
      try {
        if ($el.hasClass('os-host')) {
          $el.overlayScrollbars('destroy');
        }
      } catch (e) {
        /* ignore */
      }
    });
  }

  function enableNativeSidebarScroll() {
    destroySidebarOverlayScrollbars();

    $('.main-sidebar .sidebar').each(function () {
      this.style.overflowY = 'auto';
      this.style.overflowX = 'hidden';
      this.style.webkitOverflowScrolling = 'touch';
    });
  }

  function runFix() {
    enableNativeSidebarScroll();
  }

  function scheduleFixes() {
    runFix();
    setTimeout(runFix, 100);
    setTimeout(runFix, 400);
    setTimeout(runFix, 1200);
  }

  $(scheduleFixes);
  $(window).on('load resize', scheduleFixes);
  $(document).on(
    'expanded.lte.pushmenu collapsed.lte.pushmenu shown.lte.pushmenu',
    scheduleFixes
  );
  $(document).on('click', '[data-widget="pushmenu"]', function () {
    setTimeout(scheduleFixes, 50);
    setTimeout(scheduleFixes, 300);
  });

  /* AdminLTE Layout re-applies overlayScrollbars after resize */
  if (window.MutationObserver) {
    var observer = new MutationObserver(function (mutations) {
      for (var i = 0; i < mutations.length; i++) {
        var m = mutations[i];
        if (m.type === 'attributes' && m.attributeName === 'class') {
          var t = m.target;
          if (t && t.classList && t.classList.contains('os-host')) {
            scheduleFixes();
            return;
          }
        }
      }
    });
    $(function () {
      $('.main-sidebar .sidebar').each(function () {
        observer.observe(this, { attributes: true, attributeFilter: ['class'] });
      });
    });
  }
})(window.jQuery);
