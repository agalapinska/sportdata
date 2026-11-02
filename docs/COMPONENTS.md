# Komponenty i konwencje (Sport Data)

Stack: czysty HTML + CSS + JS. Strony źródłowe w `src/pages/*.html`, budowane przez `python3 tools/build.py [nazwa]`
do katalogu głównego (NIE edytuj wygenerowanych `*.html` w katalogu głównym). Nawigacja i stopka są w `src/partials/`.

## Plik strony – szablon
```html
<!--page
{"title": "Nasze realizacje – Sport Data",
 "description": "…",
 "nav": "realizacje",              // oferta | produkty | realizacje | blog | pomoc | "" (aktywny link)
 "cta": "Poznaj ofertę",           // etykieta jasnego przycisku w nawigacji
 "css": ["css/pages/realizacje.css"],
 "head": []}                       // opcjonalnie np. <link rel="preload" …> dla zdjęcia LCP
-->
<main id="main">
  <div class="container page-top">
    <nav class="breadcrumbs" aria-label="Okruszki">
      <ol>
        <li><a href="realizacje.html">Realizacje</a></li>
        <li><span aria-current="page">Targi Kielce</span></li>
      </ol>
    </nav>
  </div>
  <section class="section"> <div class="container"> … </div> </section>
</main>
```

## Tokeny (css/styles.css :root)
Kolory: `--orange-900 #5f3200`, `--orange-700 #ed7c00` (brand), `--orange-600`, `--orange-500`, `--orange-100 #fdead5`, `--orange-50 #fff6ed`,
`--gray-900 #050505`, `--gray-800 #161616`, `--gray-600 #373737`, `--gray-500 #484848`, `--gray-400 #696969`, `--gray-200 #cdcdcd`,
`--gray-100 #e6e6e6`, `--gray-50 #f7f7f7`, `--light-grey #f4f4f4`, `--gray-700 #262626`, `--orange-800 #be6300`, tło strony `--page-bg #fbfbfb`, tekst `--black #161616`.
Fonty: tylko Roboto (300/400/500/700) – `--font-alt` wskazuje też na Roboto (SD Brand system). Layout: `.container` (max 1312 + gutter 20→64px), `.section` (padding 56→80px).
Promień `--radius 8px`. Breakpointy: 560 / 768 / 900 / 1024 / 1200 px (mobile-first, `min-width`).

## Gotowe klasy
| Klasa | Zastosowanie |
|---|---|
| `.h-display`, `.h-page` (48), `.h-sub` (40), `.h-section` (40, ciemniejszy) | nagłówki |
| `.text-lead`, `.text-body-lg`, `.text-lead-sm` | akapity wprowadzające |
| `.section-head` (+`--narrow`), `.page-intro`, `.split` | nagłówek sekcji / 2 kolumny tytuł+opis |
| `.btn .btn--primary .btn--md .btn--glow` + `<img src="assets/icons/arrow-white.svg">` | pomarańczowy przycisk „Zobacz wszystkie …” |
| `.btn .btn--secondary .btn--lg` | biały przycisk |
| `.btn--dark` (+`.btn--sm`) | czarny przycisk w formularzach (pełna szerokość) |
| `.btn-line` + `arrow-orange.svg` | „Zobacz wszystkie realizacje ↗” (podkreślony) |
| `.link-arrow` + `arrow-orange.svg` | „Przejdź do wpisu ↗” |
| `.tags` + `.tag` (szary), `.tags--brand` (pomarańczowy) | tagi (`<ul class="tags"><li><a class="tag">`) |
| `.section-action` (+`<hr class="divider">`) | linia + przycisk na końcu sekcji |
| `.posts` / `.post…` | karty bloga (zob. index.html, sekcja BLOG) |
| `.carousel` / `.review…` | karuzela opinii (zob. index.html, sekcja OPINIE – kopiuj 1:1) |
| `.faq__list` | lista pytań FAQ |
| `.breadcrumbs`, `.page-top` | okruszki pod nawigacją |
| `.accordion` + `details.accordion__item[open]` > `summary` + `.accordion__body` | sekcje rozwijane |
| `.quote-card` (+`--hover` i `data-quote`) | karta „Zamów wycenę / Zapytaj o ofertę” rozwijana w formularz |
| `.form`, `.field`, `.field__label`, `.field__input`, `.field--check`, `.form__status`, `form[data-form]` | formularze |
| `.prose` | treść z CMS (h2–h6, p, ul/ol, blockquote, figure+figcaption) |
| `.visually-hidden`, `.br-md`, `.br-lg` | dostępność / łamania tylko na szerszych ekranach |

### Karta „Zapytaj o ofertę” rozwijana (Figma 438:3114 → 438:3123, „po najechaniu komponent się rozwija”)
```html
<aside class="quote-card quote-card--hover" data-quote aria-labelledby="q-title">
  <h2 class="quote-card__title" id="q-title">Zapytaj o ofertę</h2>
  <p class="quote-card__text">…</p>
  <button class="btn btn--dark btn--sm quote-card__cta" type="button" aria-expanded="false" aria-controls="q-form">Napisz do nas</button>
  <div class="quote-card__panel">
    <form class="form" id="q-form" data-form action="#" method="post" novalidate>
      <label class="field"><span class="field__label">Mail na który mamy odpisać</span>
        <input class="field__input" type="email" name="email" autocomplete="email" required></label>
      <label class="field"><span class="field__label">Treść Twojej wiadomości</span>
        <textarea class="field__input" name="message" placeholder="Kliknij, żeby napisać ..." required></textarea></label>
      <label class="field--check"><input type="checkbox" name="consent" required> <span>Akceptuję <a href="polityka-prywatnosci.html">politykę prywatności</a></span></label>
      <button class="btn btn--dark" type="submit">Napisz do nas</button>
      <p class="form__status" role="status" aria-live="polite"></p>
    </form>
  </div>
</aside>
```

## Zasady
- Mobile-first, bez poziomego przewijania od 320 px; siatki przez `grid` + `repeat(auto-fill, minmax(min(100%, Xpx), 1fr))` lub breakpointy.
- Zdjęcia: `tools/img.py` → WebP w `assets/img/<strona>/`, `srcset` + `sizes`, `width`/`height`, `loading="lazy"` (poza LCP).
- Kadry z Figmy (procentowe `left/top/w/h` obrazka) przelicz na `--crop`; warstwy nałożone – użyj górnej.
- Linki: oferta.html, produkt-<slug>.html, usluga-<slug>.html, realizacje.html, realizacja-<slug>.html (generowane: tools/generate.py), blog.html, wpis.html, pomoc.html,
  centrum-pomocy.html, kontakt.html, o-nas.html, polityka-prywatnosci.html, tagi: `realizacje.html?tag=<slug>`.
- Tekst po polsku tak jak w Figmie (łącznie z lorem ipsum). Adnotacje z Figmy → zachowanie w kodzie lub komentarz `<!-- CMS: … -->`.

## Zasady marki (SD: Brand system – źródło prawdy)
- Nagłówki Roboto **Medium 500**, letter-spacing −2% (H4 −1,5%); skala web: H2 56/64, H3 40/48, H4 32/36 (mobile 36/44, 28/32, 24/28).
- Tekst: Roboto 400, +2% (`body`); przyciski Roboto 500 18/20 lub 20/24, +4%; etykiety i tagi 0%.
- Pomarańcz #ED7C00 tylko jako akcent (słowo-klucz w nagłówku, ikony, przyciski, podkreślenia). **Nie** jako kolor zwykłego tekstu/linków na jasnym tle (kontrast 2,72:1) – linki `.link-arrow` są ciemne z pomarańczowym podkreśleniem; tekst na przycisku pomarańczowym = #161616.
- Brak czystej czerni (#161616) i czystej bieli w tle strony (#FBFBFB); ciemne sekcje #262626.
- Promień zaokrągleń maks. 8 px; cienie bardzo miękkie.
- Copy: forma „Ty/Twój/Ci” (wielką literą), strona czynna, fakty zamiast ogólników. Nazwy: „Sport Data”, „TicketAPI”, „SmartPhoto”.
