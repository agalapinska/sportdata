/* Produkt: galeria (zamiana miniatury ze zdjęciem głównym) + przełącznik wersji kolorystycznych */
(() => {
  'use strict';

  document.querySelectorAll('[data-gallery]').forEach((gallery) => {
    const main = gallery.querySelector('[data-gallery-main]');
    if (!main) return;
    gallery.addEventListener('click', (e) => {
      const thumb = e.target.closest('.gallery__thumb');
      if (!thumb) return;
      const thumbImg = thumb.querySelector('img');
      // Bieżące zdjęcie główne trafia do miniatury, a wybrane – na miejsce główne
      const prev = {
        full: main.getAttribute('src'),
        srcset: main.getAttribute('srcset') || '',
        alt: main.getAttribute('alt') || '',
      };
      main.src = thumb.dataset.full;
      if (thumb.dataset.fullSrcset) {
        main.srcset = thumb.dataset.fullSrcset;
        main.sizes = '(min-width: 1440px) 520px, (min-width: 1024px) 36vw, (min-width: 560px) 80vw, 92vw';
      } else {
        main.removeAttribute('srcset');
      }
      main.alt = thumb.dataset.alt || '';

      thumb.dataset.full = prev.full;
      thumb.dataset.fullSrcset = prev.srcset;
      thumb.dataset.alt = prev.alt;
      thumbImg.removeAttribute('srcset');
      thumbImg.src = prev.full;
      thumb.setAttribute('aria-label', `Pokaż zdjęcie: ${prev.alt}`);
    });
  });

  document.querySelectorAll('[data-variants]').forEach((group) => {
    const buttons = [...group.querySelectorAll('button')];
    group.addEventListener('click', (e) => {
      const btn = e.target.closest('button');
      if (!btn || btn.disabled) return;
      buttons.forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
    });
  });
})();
