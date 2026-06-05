/**
 * Use native sidebar scroll instead of AdminLTE overlayScrollbars
 * (overlayScrollbars often blocks touch scroll on phones).
 * Also hides AdminLTE fixed brand strip on real mobile browsers.
 */
(function ($) {
  'use strict';

  var MOBILE_MAX = 991.98;

  function isMobileViewport() {
    return window.innerWidth <= MOBILE_MAX;
  }

  function fixMobileBrandStrip() {
    if (!isMobileViewport()) {
      return;
    }

    var body = document.body;
    var isOpen = body.classList.contains('sidebar-open');
    var brandLink = document.querySelector('.main-sidebar .brand-link');
    var sidebar = document.querySelector('.main-sidebar');

    if (brandLink) {
      if (isOpen) {
        brandLink.style.removeProperty('display');
        brandLink.style.setProperty('width', '250px', 'important');
        brandLink.style.setProperty('visibility', 'visible', 'important');
        brandLink.style.setProperty('opacity', '1', 'important');
        brandLink.style.setProperty('left', '0', 'important');
      } else {
        brandLink.style.setProperty('display', 'none', 'important');
        brandLink.style.setProperty('width', '0', 'important');
        brandLink.style.setProperty('visibility', 'hidden', 'important');
        brandLink.style.setProperty('opacity', '0', 'important');
        brandLink.style.setProperty('left', '-9999px', 'important');
      }
    }

    ['.content-wrapper', '.main-footer', '.main-header'].forEach(function (selector) {
      var el = document.querySelector(selector);
      if (el) {
        el.style.setProperty('margin-left', '0', 'important');
      }
    });

    if (sidebar && !isOpen) {
      sidebar.style.setProperty('margin-left', '-250px', 'important');
      sidebar.style.setProperty('width', '250px', 'important');
    } else if (sidebar && isOpen) {
      sidebar.style.setProperty('margin-left', '0', 'important');
    }
  }

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
    fixMobileBrandStrip();
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
