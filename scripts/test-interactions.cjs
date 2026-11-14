// Behavioral checks for progressive enhancement; no browser automation.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const code = fs.readFileSync(path.join(__dirname, '../dist/site.js'), 'utf8');

function fixture(isMobile = false) {
  const document = { activeElement: null, handlers: {}, addEventListener(type, fn) { this.handlers[type] = fn; } };
  function element(options = {}) {
    return Object.assign({
      hidden: false, attrs: {}, handlers: {}, dataset: {}, textContent: '',
      addEventListener(type, fn) { this.handlers[type] = fn; },
      setAttribute(key, value) { this.attrs[key] = value; },
      getAttribute(key) { return this.attrs[key] ?? null; },
      focus() { document.activeElement = this; },
    }, options);
  }
  const categories = ['brand', 'web', 'experiment'];
  const projects = categories.map(category => element({ dataset: { category } }));
  const buttons = ['all', ...categories].map(filter => element({ dataset: { filter }, textContent: filter }));
  const filters = element({ hidden: true, querySelectorAll: () => buttons });
  const status = element();
  const toggle = element({ hidden: true, attrs: { 'aria-expanded': 'false' } });
  const destination = element();
  const link = element({ attrs: { href: '#work' } });
  link.closest = () => link;
  const nav = element({ contains: item => item === link, querySelector: () => link });
  const nodes = { '.filters': filters, '#filter-status': status, '.menu-toggle': toggle, '#site-nav': nav, '#work': destination };
  document.querySelector = selector => nodes[selector] || null;
  document.querySelectorAll = () => projects;
  const media = { matches: isMobile, addEventListener(type, fn) { this.onChange = fn; } };
  const window = { matchMedia: () => media };
  vm.runInNewContext(code, { document, window });
  return { document, projects, buttons, filters, status, toggle, nav, link, destination, media };
}

let tests = 0;
function test(name, fn) {
  fn();
  tests += 1;
  console.log(`PASS ${name}`);
}
test('desktop navigation remains visible, mobile toggle remains hidden', () => {
  const f = fixture();
  assert.equal(f.nav.hidden, false);
  assert.equal(f.toggle.hidden, true);
});
test('each filter selects its category, updates pressed state and announces count', () => {
  const f = fixture();
  assert.equal(f.filters.hidden, false);
  for (const button of f.buttons.slice(1)) {
    button.handlers.click();
    assert.equal(f.projects.filter(project => !project.hidden).length, 1);
    assert.equal(f.projects.find(project => !project.hidden).dataset.category, button.dataset.filter);
    assert.equal(f.buttons.filter(item => item.attrs['aria-pressed'] === 'true').length, 1);
    assert.equal(button.attrs['aria-pressed'], 'true');
    assert.match(f.status.textContent, /1件/);
  }
});
test('all restores projects after repeated filter changes', () => {
  const f = fixture();
  f.buttons[2].handlers.click();
  f.buttons[3].handlers.click();
  f.buttons[0].handlers.click();
  assert.ok(f.projects.every(project => !project.hidden));
  assert.match(f.status.textContent, /3件/);
});
test('mobile menu starts collapsed and can toggle both ways', () => {
  const f = fixture(true);
  assert.equal(f.toggle.hidden, false);
  assert.equal(f.nav.hidden, true);
  f.toggle.handlers.click();
  assert.equal(f.nav.hidden, false);
  assert.equal(f.toggle.attrs['aria-expanded'], 'true');
  f.toggle.handlers.click();
  assert.equal(f.nav.hidden, true);
  assert.equal(f.toggle.attrs['aria-expanded'], 'false');
});
test('Escape closes mobile menu and returns focus', () => {
  const f = fixture(true);
  f.toggle.handlers.click();
  f.link.focus();
  f.document.handlers.keydown({ key: 'Escape' });
  assert.equal(f.nav.hidden, true);
  assert.equal(f.document.activeElement, f.toggle);
});
test('mobile link moves focus to its destination before the nav is hidden', () => {
  const f = fixture(true);
  f.toggle.handlers.click();
  f.link.focus();
  f.nav.handlers.click({ target: f.link });
  assert.equal(f.nav.hidden, true);
  assert.equal(f.document.activeElement, f.destination);
  assert.equal(f.destination.attrs.tabindex, '-1');
});
test('responsive breakpoint does not strand focus on hidden navigation', () => {
  const f = fixture();
  f.link.focus();
  f.media.matches = true;
  f.media.onChange();
  assert.equal(f.document.activeElement, f.toggle);
  assert.equal(f.nav.hidden, true);
  f.media.matches = false;
  f.media.onChange();
  assert.equal(f.document.activeElement, f.link);
  assert.equal(f.nav.hidden, false);
  assert.equal(f.toggle.hidden, true);
});
test('missing enhancement hooks do not break the document', () => {
  const document = { querySelector: () => null, querySelectorAll: () => [] };
  assert.doesNotThrow(() => vm.runInNewContext(code, { document, window: {} }));
});
console.log(`${tests} interaction checks passed (DOM stubs; no visual browser test).`);
