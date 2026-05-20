/**
 * On phones/tablets: remove overlayScrollbars from sidebar so native touch scroll works.
 */
(function ($) {
  'use strict';

  function isMobileLayout() {
    return window.matchMedia('(max-width: 991.98px)').matches;
  }

  function destroySidebarOverlayScrollbars() {
    if (!isMobileLayout() || typeof $.fn.overlayScrollbars === 'undefined') {
      return;
    }

    var $sidebar = $('.main-sidebar .sidebar');
    $sidebar.each(function () {
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

  function runFix() {
    destroySidebarOverlayScrollbars();
  }

  $(runFix);
  $(window).on('load', function () {
    runFix();
    setTimeout(runFix, 300);
    setTimeout(runFix, 1000);
  });
  $(window).on('resize', runFix);
  $(document).on('expanded.lte.pushmenu collapsed.lte.pushmenu', runFix);
})(window.jQuery);
