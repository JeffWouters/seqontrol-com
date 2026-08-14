/* SeQontrol site chrome. No dependencies, no network calls.
   Three jobs: the mobile nav, the current-page nav marker, and the footer year. */
(function () {
  'use strict';

  // --- mobile nav -----------------------------------------------------------
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');

  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });

    // Close on Escape so keyboard users are not trapped behind the panel.
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && links.classList.contains('open')) {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  // --- current page ---------------------------------------------------------
  // Marks the nav entry for the page you are on. Product pages live one level
  // down, so compare the last path segment and treat /products/* as "Products".
  var path = window.location.pathname.replace(/\/+$/, '');
  var file = path.substring(path.lastIndexOf('/') + 1) || 'index.html';
  var inProducts = /\/products(\/|$)/.test(path);

  Array.prototype.forEach.call(document.querySelectorAll('.nav-links a'), function (a) {
    if (a.classList.contains('btn')) return;
    var href = a.getAttribute('href') || '';
    var target = href.substring(href.lastIndexOf('/') + 1);
    var isProductsLink = href.indexOf('products/') !== -1;

    if ((inProducts && isProductsLink) || (!inProducts && target === file && !isProductsLink)) {
      a.setAttribute('aria-current', 'page');
    }
  });

  // --- footer year ----------------------------------------------------------
  Array.prototype.forEach.call(document.querySelectorAll('[data-year]'), function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  // --- tabs -----------------------------------------------------------------
  // Progressive: the markup ships with every panel visible and the tab strip
  // hidden by CSS. Only once this runs does the container get
  // [data-tabs-ready], which reveals the strip and lets us collapse the panels.
  // No script, no loss of content.
  Array.prototype.forEach.call(document.querySelectorAll('[data-tabs]'), function (root) {
    var tabs = [].slice.call(root.querySelectorAll('[role="tab"]'));
    var panels = [].slice.call(root.querySelectorAll('[role="tabpanel"]'));
    if (!tabs.length || tabs.length !== panels.length) return;

    function select(index, moveFocus) {
      tabs.forEach(function (tab, i) {
        var on = i === index;
        tab.setAttribute('aria-selected', String(on));
        tab.setAttribute('tabindex', on ? '0' : '-1');
        panels[i].hidden = !on;
      });
      if (moveFocus) tabs[index].focus();
    }

    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { select(i); });
      tab.addEventListener('keydown', function (e) {
        var next = null;
        if (e.key === 'ArrowRight') next = (i + 1) % tabs.length;
        else if (e.key === 'ArrowLeft') next = (i - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') next = 0;
        else if (e.key === 'End') next = tabs.length - 1;
        if (next === null) return;
        e.preventDefault();
        select(next, true);
      });
    });

    root.setAttribute('data-tabs-ready', '');

    // Deep links: /licensing.html#mailtrust opens that product's tab.
    var wanted = window.location.hash.replace('#', '');
    var start = 0;
    panels.forEach(function (panel, i) {
      if (panel.id === 'panel-' + wanted) start = i;
    });
    select(start);
  });
})();
