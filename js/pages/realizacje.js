/* Sport Data – Nasze realizacje: filtrowanie listy po ?tag=<slug> (progressive enhancement) */
(() => {
  'use strict';
  const filter = document.querySelector('[data-tag-filter]');
  const list = document.querySelector('[data-tag-list]');
  if (!filter || !list) return;

  const raw = new URLSearchParams(window.location.search).get('tag');
  const tag = (raw || '').trim().toLowerCase();
  if (!tag) return;

  // Etykieta: slug zamieniony na tekst („hala-targowa” → „hala targowa”)
  filter.querySelector('[data-tag-label]').textContent = tag.replace(/-/g, ' ');

  let visible = 0;
  [...list.children].forEach((item) => {
    const tags = (item.dataset.tags || '').toLowerCase().split(/\s+/);
    const match = tags.includes(tag);
    item.hidden = !match;
    if (match) visible += 1;
  });

  filter.querySelector('[data-tag-empty]').hidden = visible > 0;
  filter.hidden = false;
})();
