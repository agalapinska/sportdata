/* Sport Data – interakcje strony głównej */
(() => {
  'use strict';

  /* ------------------------------------------------------------------
   * 1. "Sierotki" – globalne przenoszenie krótkich słów do nowej linii.
   *    Po jedno-/dwuliterowych słowach i spójnikach wstawiamy twardą
   *    spację (U+00A0), więc słowo nigdy nie zostaje na końcu wiersza.
   *    Działa na całą treść, także tę wczytaną później z CMS.
   * ------------------------------------------------------------------ */
  const ORPHANS = ['a', 'i', 'o', 'u', 'w', 'z', 'np.', 'do', 'od', 'na', 'po', 'za', 'ze', 'we', 'bo', 'by', 'że', 'to', 'oraz', 'lub', 'czy', 'nie', 'jak', 'aż', 'tj.', 'tzw.', 'więc', 'przez', 'dla', 'pod', 'nad', 'bez'];
  const escaped = ORPHANS.map((w) => w.replace(/\./g, '\\.')).join('|');
  const orphanRe = new RegExp(`(^|[\\s\\u00A0(„"“])(${escaped}) (?=\\S)`, 'giu');
  const SKIP = new Set(['SCRIPT', 'STYLE', 'TEXTAREA', 'CODE', 'PRE', 'INPUT']);

  const fixOrphans = (root) => {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: (node) =>
        !node.parentElement || SKIP.has(node.parentElement.tagName) || !/\s/.test(node.nodeValue)
          ? NodeFilter.FILTER_REJECT
          : NodeFilter.FILTER_ACCEPT,
    });
    let node;
    while ((node = walker.nextNode())) {
      // dwa przebiegi, by obsłużyć sekwencje typu "i w ..."
      const next = node.nodeValue.replace(orphanRe, '$1$2 ').replace(orphanRe, '$1$2 ');
      if (next !== node.nodeValue) node.nodeValue = next;
    }
  };
  fixOrphans(document.body);

  /* ------------------------------------------------------------------
   * 2. Nawigacja – menu mobilne + zmniejszanie paska po przewinięciu
   * ------------------------------------------------------------------ */
  const navbar = document.querySelector('.navbar');
  const toggle = navbar?.querySelector('.navbar__toggle');
  const menu = navbar?.querySelector('.navbar__menu');
  const desktopMq = window.matchMedia('(min-width: 1200px)');

  const setMenu = (open) => {
    if (!navbar || !toggle) return;
    navbar.classList.toggle('is-open', open);
    document.body.classList.toggle('menu-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Zamknij menu' : 'Otwórz menu');
  };

  toggle?.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  menu?.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navbar?.classList.contains('is-open')) { setMenu(false); toggle.focus(); }
  });
  document.addEventListener('click', (e) => {
    if (navbar?.classList.contains('is-open') && !navbar.contains(e.target)) setMenu(false);
  });
  desktopMq.addEventListener('change', (e) => { if (e.matches) setMenu(false); });

  // Wysokość paska -> zmienna CSS (scroll-padding dla kotwic)
  const syncNavHeight = () => navbar && document.documentElement.style.setProperty('--nav-h', `${navbar.offsetHeight}px`);
  if (navbar && 'ResizeObserver' in window) new ResizeObserver(syncNavHeight).observe(navbar);

  // Klasa po przewinięciu (sentinel zamiast nasłuchu scroll)
  if (navbar && 'IntersectionObserver' in window) {
    const sentinel = document.createElement('div');
    sentinel.setAttribute('aria-hidden', 'true');
    sentinel.style.cssText = 'position:absolute;top:0;left:0;width:1px;height:40px;pointer-events:none;';
    document.body.prepend(sentinel);
    new IntersectionObserver(([entry]) => navbar.classList.toggle('is-scrolled', !entry.isIntersecting)).observe(sentinel);
  }

  /* ------------------------------------------------------------------
   * 3. Karuzela opinii – natywny scroll-snap + strzałki + kropki
   * ------------------------------------------------------------------ */
  document.querySelectorAll('[data-carousel]').forEach((carousel) => {
    const track = carousel.querySelector('[data-carousel-track]');
    const prev = carousel.querySelector('[data-carousel-prev]');
    const next = carousel.querySelector('[data-carousel-next]');
    const dotsWrap = carousel.querySelector('[data-carousel-dots]');
    const slides = [...track.children];
    let dots = [];

    const step = () => {
      const [a, b] = slides;
      return b ? b.offsetLeft - a.offsetLeft : track.clientWidth;
    };
    const pageCount = () => {
      const visible = Math.max(1, Math.round(track.clientWidth / step()));
      return Math.max(1, slides.length - visible + 1);
    };
    const current = () => Math.round(track.scrollLeft / step());
    const goTo = (i) => track.scrollTo({ left: i * step() });

    const buildDots = () => {
      const count = pageCount();
      dotsWrap.hidden = count < 2;
      carousel.classList.toggle('is-static', count < 2);
      if (dots.length === count) return;
      dotsWrap.replaceChildren();
      dots = Array.from({ length: count }, (_, i) => {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'carousel__dot';
        dot.setAttribute('aria-label', `Slajd ${i + 1} z ${count}`);
        dot.addEventListener('click', () => goTo(i));
        dotsWrap.append(dot);
        return dot;
      });
    };

    const update = () => {
      const max = track.scrollWidth - track.clientWidth - 2;
      const idx = Math.min(current(), dots.length - 1);
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max;
      dots.forEach((d, i) => d.setAttribute('aria-current', String(i === idx)));
    };

    prev.addEventListener('click', () => goTo(Math.max(0, current() - 1)));
    next.addEventListener('click', () => goTo(Math.min(pageCount() - 1, current() + 1)));
    track.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); next.click(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); prev.click(); }
    });

    let raf = 0;
    track.addEventListener('scroll', () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(update); }, { passive: true });
    const refresh = () => { buildDots(); update(); };
    if ('ResizeObserver' in window) new ResizeObserver(refresh).observe(track);
    refresh();
  });
  /* ------------------------------------------------------------------
   * 4. Karta „Zamów wycenę / Zapytaj o ofertę” – rozwijanie formularza
   *    (desktop: hover/focus w CSS; dotyk i klawiatura: klik w przycisk)
   * ------------------------------------------------------------------ */
  document.querySelectorAll('[data-quote]').forEach((card) => {
    const cta = card.querySelector('.quote-card__cta');
    const firstField = card.querySelector('input, textarea');
    cta?.addEventListener('click', () => {
      card.classList.add('is-open');
      cta.setAttribute('aria-expanded', 'true');
      firstField?.focus({ preventScroll: true });
    });
  });

  /* ------------------------------------------------------------------
   * 5. Formularze – walidacja HTML5 + komunikat (wysyłka do podpięcia w CMS)
   * ------------------------------------------------------------------ */
  document.querySelectorAll('form[data-form]').forEach((form) => {
    const status = form.querySelector('.form__status');
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      // TODO: podpiąć endpoint (np. fetch(form.action, { method: 'POST', body: new FormData(form) }))
      if (status) status.textContent = 'Dziękujemy! Wiadomość została przygotowana do wysłania.';
      form.reset();
    });
  });
})();
