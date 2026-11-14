(() => {
  'use strict';
  // Details/summary and navigation links remain usable without JavaScript.
  const filters = document.querySelector('.filters');
  const projects = [...document.querySelectorAll('.project')];
  const status = document.querySelector('#filter-status');
  if (filters && projects.length && status) {
    filters.hidden = false;
    const buttons = [...filters.querySelectorAll('button[data-filter]')];
    buttons.forEach(button => {
      button.addEventListener('click', () => {
        const category = button.dataset.filter;
        let count = 0;
        projects.forEach(project => {
          project.hidden = category !== 'all' && project.dataset.category !== category;
          if (!project.hidden) count += 1;
        });
        buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
        status.textContent = `${button.textContent}：${count}件の作品を表示しています。`;
      });
    });
  }

  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');
  if (!toggle || !nav || !window.matchMedia) return;
  const mobile = window.matchMedia('(max-width: 767px)');
  function setMenu(open) {
    toggle.setAttribute('aria-expanded', String(open));
    nav.hidden = mobile.matches && !open;
  }
  function syncLayout() {
    const focusInNav = nav.contains(document.activeElement);
    const focusOnToggle = document.activeElement === toggle;
    toggle.hidden = !mobile.matches;
    setMenu(false);
    if (mobile.matches && focusInNav) toggle.focus();
    if (!mobile.matches && focusOnToggle) nav.querySelector('a')?.focus();
  }
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', event => {
    if (!mobile.matches || !event.target.closest('a')) return;
    const link = event.target.closest('a');
    const destination = document.querySelector(link.getAttribute('href'));
    setMenu(false);
    if (destination) {
      destination.setAttribute('tabindex', '-1');
      destination.focus({ preventScroll: true });
    }
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && mobile.matches && toggle.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      toggle.focus();
    }
  });
  if (mobile.addEventListener) mobile.addEventListener('change', syncLayout);
  else mobile.addListener(syncLayout);
  syncLayout();
})();
