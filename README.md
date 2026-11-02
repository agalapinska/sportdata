# Sport Data – strona internetowa

Statyczna, responsywna implementacja serwisu Sport Data (12 stron) z projektu Figma `WEB_SD`.
Bez frameworków i kroku budowania – czysty HTML + CSS + JS.

## Uruchomienie
Otwórz `index.html` w przeglądarce albo uruchom lokalny serwer:

```bash
npx serve .
```

## Struktura
```
src/pages/*.html    – źródła stron (blok metadanych <!--page {...}--> + <main>)
src/partials/       – wspólna nawigacja (header.html) i stopka (footer.html)
tools/build.py      – składa strony do katalogu głównego:  python3 tools/build.py [nazwa ...]
tools/img.py        – optymalizacja zdjęć do WebP (kilka szerokości, opcjonalny kadr)
*.html              – WYGENEROWANE strony (nie edytować ręcznie)
css/styles.css      – tokeny z Figmy (:root), layout mobile-first, wspólne komponenty
css/pages/*.css     – style poszczególnych podstron
js/main.js          – menu mobilne, karuzela opinii, „sierotki”, rozwijana karta wyceny, formularze
assets/img, icons   – zdjęcia WebP (srcset/sizes) i SVG z Figmy
docs/COMPONENTS.md  – katalog komponentów i konwencji
```

Po zmianie czegokolwiek w `src/` uruchom `python3 tools/build.py`.

## Responsywność
- Breakpointy: 560 / 768 / 900 / 1024 / 1200 px; projekt desktopowy 1440 px (kontener 1312 px).
- Nawigacja: pełne menu od 1200 px, poniżej panel z przyciskiem „hamburger” (Esc / klik poza panelem zamyka).
- Kolaż w hero skaluje się proporcjonalnie (aspect-ratio 552 × 532).
- Siatki: cechy 1 → 2 → 4 kol., produkty auto-fill → 4 kol., blog 1 → 2 → 3 kol., FAQ 1 → 2 kol.
- Ręczne łamania wierszy z projektu (`<br class="br-md|br-lg">`) działają tylko na szerszych ekranach.
- Obrazy: `srcset` + `sizes`, `loading="lazy"`, wymiary w atrybutach (brak przesunięć układu – CLS).

## Uwagi z komentarzy w Figmie
- **Sierotki** – `js/main.js` globalnie wstawia twardą spację po krótkich słowach („z, i, w, do, od, bo, więc…”).
  W CMS warto robić to też po stronie serwera (np. filtr treści).
- **Tagi produktów** linkują do `realizacje.html?tag=…` (filtr realizacji po tagu), a tagi w realizacjach do `produkty.html?produkt=…`.
- **Opinie** – karta jest linkiem do opinii w Google (do uzupełnienia `href`); jeśli brak danych autora, wiersz autora jest pomijany.
- Podstrony (`oferta.html`, `produkty.html`, `realizacje.html`, `blog.html`, `pomoc.html`, `kontakt.html`, `polityka-prywatnosci.html`) są podlinkowane, ale jeszcze nie zaimplementowane.
- Do dodania wg adnotacji w nawigacji: wyszukiwarka, przełącznik języka, rozwijane mega-menu.

## Strony
| Plik | Ramka w Figmie |
|---|---|
| index.html | home (367:1111) |
| oferta.html | produkty (383:4212) – sekcje #urzadzenia, #parking, #oprogramowanie, #indywidualne |
| produkt.html | produkt (367:2140) |
| usluga.html | usługa (912:1741) |
| realizacje.html | realizacje (739:3077) – filtr `?tag=` |
| realizacja.html | realizacja (367:2449) |
| blog.html | blog (394:14486) |
| wpis.html | wpis blogowy (367:3083) |
| o-nas.html | o nas (767:1094) – link w stopce |
| polityka-prywatnosci.html | Polityka prywatności (367:2935) |
| pomoc.html | Centrum pomocy (767:1386) |
| kontakt.html | kontakt (400:15223) |

## Do uzupełnienia przed publikacją (CMS / backend)
- Treści-zaślepki z Figmy (lorem ipsum, „Project name here”, „Variant”, „Subscribe to receive…”), szare pola zdjęć.
- Wysyłka formularzy (`js/main.js`, TODO), adres wideo na „O nas”, mapa (iframe po decyzji o zgodach cookies).
- Linki do opinii Google, profili społecznościowych i logo UE; paginacja bloga (`?strona=`) i filtr tagów po stronie serwera.
