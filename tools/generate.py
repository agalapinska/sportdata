#!/usr/bin/env python3
"""Generuje strony źródłowe (src/pages/*.html) z danych w data/*.json.

Wejście:  data/produkty.json  (kategorie + produkty)
          data/realizacje.json
          data/uslugi.json
Wyjście:  src/pages/produkt-<slug>.html, usluga-<slug>.html, realizacja-<slug>.html,
          src/pages/oferta.html (całość) oraz lista w src/pages/realizacje.html
          (wstęp, filtr i opinie zostają bez zmian).

Uruchom:  python3 tools/generate.py && python3 tools/build.py
Tylko biblioteka standardowa. Wszystkie dane są escapowane (html.escape).
"""
import json, re, struct
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PAGES = ROOT / "src" / "pages"
IMG = ROOT / "assets" / "img"

MARK = "<!-- WYGENEROWANE przez tools/generate.py z data/*.json – nie edytuj ręcznie -->"
ARROW = '<img src="assets/icons/arrow-orange.svg" width="20" height="20" alt="">'
ARROW_W = '<img src="assets/icons/arrow-dark.svg" width="20" height="20" alt="">'
CHEVRON = '<img src="assets/icons/chevron-right-24.svg" width="24" height="24" alt="">'
QUOTE_TEXT = "Zostaw adres e-mail i opisz potrzeby – przygotujemy wycenę."

SIZES_CARD = "(min-width: 1440px) 304px, (min-width: 1200px) 22vw, (min-width: 900px) 30vw, (min-width: 560px) 46vw, 92vw"
SIZES_SELFPOS = "(min-width: 1440px) 169px, (min-width: 1200px) 12vw, (min-width: 900px) 17vw, (min-width: 560px) 26vw, 52vw"
SIZES_GALLERY = "(min-width: 1440px) 520px, (min-width: 1024px) 36vw, (min-width: 560px) 80vw, 92vw"
SIZES_GALLERY_SINGLE = "(min-width: 1440px) 616px, (min-width: 1024px) 44vw, 92vw"
SIZES_SHOWCASE = "(min-width: 1440px) 616px, (min-width: 900px) 44vw, 92vw"
SIZES_CASES_GRID = "(min-width: 1440px) 405px, (min-width: 1024px) 30vw, (min-width: 700px) 46vw, 92vw"
SIZES_CASE_PRODUCT = "(min-width: 1440px) 304px, (min-width: 900px) 22vw, 46vw"
SIZES_REALIZATION = "(min-width: 1024px) 880px, 92vw"
SIZES_COMPACT = "(min-width: 1440px) 632px, (min-width: 768px) 46vw, 92vw"


def e(s):
    return escape(str(s), quote=True)


# ---------------------------------------------------------------- obrazy
def webp_size(path):
    """(szerokość, wysokość) pliku WebP – bez zewnętrznych bibliotek."""
    d = path.read_bytes()[:40]
    kind = d[12:16]
    if kind == b"VP8X":
        return 1 + int.from_bytes(d[24:27], "little"), 1 + int.from_bytes(d[27:30], "little")
    if kind == b"VP8 ":
        w, h = struct.unpack("<HH", d[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if kind == b"VP8L":
        b = int.from_bytes(d[21:25], "little")
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    raise ValueError(f"Nieobsługiwany WebP: {path}")


def resolve_base(key):
    """Klucz obrazu → (katalog, nazwa bazowa) w assets/img."""
    if key.startswith("oferta/"):
        return IMG / "oferta", key.split("/", 1)[1]
    if key.startswith("produkt/"):
        return IMG / "produkt", key.split("/", 1)[1]
    if key.startswith("home/"):
        return IMG, key.split("/", 1)[1]
    return IMG, key


def image(key):
    """Zwraca {src, srcset, w, h, widths} na podstawie plików na dysku albo None."""
    if not key:
        return None
    folder, name = resolve_base(key)
    variants = []
    for f in folder.glob(f"{name}-*.webp"):
        m = re.fullmatch(re.escape(name) + r"-(\d+)\.webp", f.name)
        if m:
            variants.append((int(m.group(1)), f))
    rel = lambda f: f.relative_to(ROOT).as_posix()
    if variants:
        variants.sort()
        # src: wariant ~640 px (lub największy poniżej 1100 px)
        mid = [v for v in variants if v[0] <= 1100] or variants
        src = mid[-1][1]
        w, h = webp_size(variants[-1][1])
        return {"src": rel(src), "srcset": ", ".join(f"{rel(f)} {n}w" for n, f in variants),
                "w": w, "h": h, "smallest": rel(variants[0][1])}
    single = folder / f"{name}.webp"
    if single.exists():
        w, h = webp_size(single)
        return {"src": rel(single), "srcset": "", "w": w, "h": h, "smallest": rel(single)}
    raise SystemExit(f"Brak pliku obrazu dla klucza „{key}” ({folder}/{name}[-N].webp)")


def img_tag(im, sizes, w=None, h=None, alt="", lazy=True, extra=""):
    attrs = f'src="{e(im["src"])}"'
    if im["srcset"]:
        attrs += f' srcset="{e(im["srcset"])}" sizes="{sizes}"'
    attrs += f' width="{w or im["w"]}" height="{h or im["h"]}" alt="{e(alt)}"'
    attrs += ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return f"<img {attrs}{extra}>"


def logo_tag(logo, alt):
    im = image(logo)
    return (f'<img class="logo-panel__img" src="{e(im["src"])}" width="{im["w"]}" height="{im["h"]}" '
            f'alt="{e(alt)}" loading="lazy">')


# ---------------------------------------------------------------- dane
produkty = json.loads((DATA / "produkty.json").read_text())
CATS = produkty["categories"]
CAT = {c["slug"]: c for c in CATS}
PRODUCTS = produkty["products"]
PROD = {p["slug"]: p for p in PRODUCTS}
REAL = json.loads((DATA / "realizacje.json").read_text())
SERV = json.loads((DATA / "uslugi.json").read_text())

errors = []
for p in PRODUCTS:
    if p["category"] not in CAT:
        errors.append(f"produkt {p['slug']}: nieznana kategoria {p['category']}")
for r in REAL:
    for s in r.get("products", []):
        if s not in PROD:
            errors.append(f"realizacja {r['slug']}: nieznany produkt {s}")
if errors:
    raise SystemExit("\n".join(errors))


def product_url(slug):
    return f"produkt-{slug}.html"


def real_url(slug):
    return f"realizacja-{slug}.html"


def service_url(slug):
    return f"usluga-{slug}.html"


def tag_label(slug):
    return slug.replace("-", " ").capitalize()


def lead_of(p):
    return p.get("lead") or CAT[p["category"]]["lead"]


def write_page(name, meta, body):
    meta_json = json.dumps(meta, ensure_ascii=False, indent=None)
    out = f"<!--page\n{meta_json}\n-->\n{MARK}\n{body.strip()}\n"
    (PAGES / name).write_text(out)
    return name


# ---------------------------------------------------------------- komponenty
def breadcrumbs(items):
    lis = []
    for label, href in items[:-1]:
        lis.append(f'          <li><a href="{href}">{e(label)}</a></li>')
    lis.append(f'          <li><span aria-current="page">{e(items[-1][0])}</span></li>')
    return ("    <div class=\"container page-top\">\n"
            "      <nav class=\"breadcrumbs\" aria-label=\"Okruszki\">\n        <ol>\n"
            + "\n".join(lis) + "\n        </ol>\n      </nav>\n    </div>\n")


def quote_card(title, cta, hidden_name, hidden_value, indent="            "):
    i = indent
    return f"""{i}<aside class="quote-card quote-card--hover" data-quote aria-labelledby="q-title">
{i}  <h2 class="quote-card__title" id="q-title">{title}</h2>
{i}  <p class="quote-card__text">{QUOTE_TEXT}</p>
{i}  <button class="btn btn--dark btn--sm quote-card__cta" type="button" aria-expanded="false" aria-controls="q-form">{cta}</button>
{i}  <div class="quote-card__panel">
{i}    <form class="form" id="q-form" data-form action="#" method="post" novalidate>
{i}      <input type="hidden" name="{hidden_name}" value="{e(hidden_value)}">
{i}      <label class="field"><span class="field__label">Mail na który mamy odpisać</span>
{i}        <input class="field__input" type="email" name="email" autocomplete="email" required></label>
{i}      <label class="field"><span class="field__label">Treść Twojej wiadomości</span>
{i}        <textarea class="field__input" name="message" placeholder="Kliknij, żeby napisać ..." required></textarea></label>
{i}      <label class="field--check"><input type="checkbox" name="consent" required> <span>Akceptuję <a href="polityka-prywatnosci.html">politykę prywatności</a></span></label>
{i}      <button class="btn btn--dark" type="submit">{cta}</button>
{i}      <p class="form__status" role="status" aria-live="polite"></p>
{i}    </form>
{i}  </div>
{i}</aside>
"""


def product_card(p, indent="          "):
    """Karta produktu (oferta / „Inne z tej kategorii”)."""
    i = indent
    url = product_url(p["slug"])
    im = image(p.get("image"))
    if im is None:
        media = f'{i}  <a class="product__media ph" href="{url}" tabindex="-1" aria-hidden="true"></a>\n'
    else:
        mod = ""
        sizes, w, h = SIZES_CARD, 304, 304
        if p.get("image") == "oferta/palmtop":
            mod = " product__media--light"
        elif p.get("image") == "oferta/selfpos":
            mod = " product__media--selfpos"
            sizes, w, h = SIZES_SELFPOS, 169, 300
        media = (f'{i}  <a class="product__media{mod}" href="{url}" tabindex="-1" aria-hidden="true">\n'
                 f'{i}    {img_tag(im, sizes, w, h)}\n{i}  </a>\n')
    name = e(p["name"])
    return (f'{i}<li class="product">\n{media}'
            f'{i}  <h3 class="product__title"><a href="{url}">{name}</a></h3>\n'
            f'{i}  <p class="product__text">{e(p["type"])}</p>\n'
            f'{i}  <a class="link-arrow" href="{url}">Przejdź do produktu<span class="visually-hidden">: {name}</span>\n'
            f'{i}    {ARROW}\n{i}  </a>\n{i}</li>\n')


def tag_links(tags, indent):
    return "".join(f'{indent}<li><a class="tag" href="realizacje.html?tag={e(t)}">{e(tag_label(t))}</a></li>\n'
                   for t in tags)


def media_inner(r, sizes, w, h, lazy=True):
    """Zawartość pola zdjęcia realizacji: zdjęcie, logo albo nic (szary placeholder)."""
    if r.get("image"):
        return img_tag(image(r["image"]), sizes, w, h, lazy=lazy)
    if r.get("logo"):
        return logo_tag(r["logo"], "")
    return ""


def showcase_row(r, indent="          "):
    """Wiersz realizacji z oferty / strony produktu (Portfolio / 15)."""
    i = indent
    url = real_url(r["slug"])
    inner = media_inner(r, SIZES_SHOWCASE, 616, 384)
    cls = "showcase__media" + (" logo-panel" if (not r.get("image") and r.get("logo")) else "") + \
          ("" if inner else " ph")
    media = (f'{i}  <a class="{cls}" href="{url}" tabindex="-1" aria-hidden="true">'
             + (f"\n{i}    {inner}\n{i}  " if inner else "") + "</a>\n")
    name = e(r["name"])
    tags = ""
    if r.get("tags"):
        tags = f'{i}    <ul class="tags" aria-label="Tagi">\n{tag_links(r["tags"], i + "      ")}{i}    </ul>\n'
    return (f'{i}<li class="showcase__row case-card">\n{media}'
            f'{i}  <div class="showcase__body">\n'
            f'{i}    <h3 class="case-card__title"><a href="{url}">{name}</a></h3>\n'
            f'{i}    <p class="case-card__text">{e(r["lead"])}</p>\n{tags}'
            f'{i}    <a class="view-link" href="{url}">Zobacz realizację<span class="visually-hidden">: {name}</span>\n'
            f'{i}      {CHEVRON}\n{i}    </a>\n{i}  </div>\n{i}</li>\n')


def case_card(r, indent="          "):
    """Karta realizacji w siatce 3-kolumnowej (strona usługi)."""
    i = indent
    url = real_url(r["slug"])
    inner = media_inner(r, SIZES_CASES_GRID, 405, 384)
    cls = "case-card__media" + (" logo-panel" if (not r.get("image") and r.get("logo")) else "") + \
          ("" if inner else " ph")
    media = (f'{i}  <a class="{cls}" href="{url}" tabindex="-1" aria-hidden="true">'
             + (f"\n{i}    {inner}\n{i}  " if inner else "") + "</a>\n")
    name = e(r["name"])
    tags = ""
    if r.get("tags"):
        tags = f'{i}  <ul class="tags" aria-label="Tagi">\n{tag_links(r["tags"], i + "    ")}{i}  </ul>\n'
    return (f'{i}<li class="case-card">\n{media}'
            f'{i}  <h3 class="case-card__title"><a href="{url}">{name}</a></h3>\n'
            f'{i}  <p class="case-card__text">{e(r["lead"])}</p>\n{tags}'
            f'{i}  <a class="view-link" href="{url}">Zobacz realizację<span class="visually-hidden">: {name}</span>\n'
            f'{i}    {CHEVRON}\n{i}  </a>\n{i}</li>\n')


def service_card(s, indent="          ", heading="h3"):
    i = indent
    url = service_url(s["slug"])
    name = e(s["name"])
    return (f'{i}<li class="service">\n'
            f'{i}  <{heading} class="service__title">{name}</{heading}>\n'
            f'{i}  <p class="service__text">{e(s["lead"])}</p>\n'
            f'{i}  <a class="link-arrow" href="{url}">Przejdź do usługi<span class="visually-hidden">: {name}</span>\n'
            f'{i}    {ARROW}\n{i}  </a>\n{i}</li>\n')


def product_tags(r, limit=6, indent="              "):
    """Tagi produktów realizacji: linki do produktów + (gdy brak) produkty archiwalne bez linku."""
    i = indent
    items = [f'{i}  <li><a class="tag" href="{product_url(s)}">{e(PROD[s]["name"])}</a></li>\n'
             for s in r.get("products", [])[:limit]]
    if len(items) < limit:
        items += [f'{i}  <li><span class="tag">{e(n)}</span></li>\n'
                  for n in r.get("legacy", [])[:limit - len(items)]]
    if not items:
        return ""
    return f'{i}<ul class="tags realization__tags" aria-label="Produkty użyte w realizacji">\n{"".join(items)}{i}</ul>\n'


def realization_meta(r, cls="realization__meta", indent="              "):
    i = indent
    rows = [("Klient", r["name"]), ("Miasto", r["city"])]
    if r.get("status"):
        rows.append(("Status", r["status"]))
    body = "".join(f"{i}  <div><dt>{k}</dt><dd>{e(v)}</dd></div>\n" for k, v in rows)
    return f'{i}<dl class="{cls}">\n{body}{i}</dl>\n'


def realization_article(r, idx_prefix, compact=False, first=False, indent="            "):
    """Karta realizacji (lista realizacje.html i „Inne realizacje”)."""
    i = indent
    url = real_url(r["slug"])
    name = e(r["name"])
    hid = f'{idx_prefix}-{r["slug"]}-title'
    sizes, w, h = (SIZES_COMPACT, 632, 280) if compact else (SIZES_REALIZATION, 880, 280)
    inner = media_inner(r, sizes, w, h, lazy=not first)
    cls = "realization__media" + (" logo-panel" if (not r.get("image") and r.get("logo")) else "")
    media = (f'{i}  <a class="{cls}" href="{url}" tabindex="-1" aria-hidden="true">'
             + (f"\n{i}    {inner}\n{i}  " if inner else "") + "</a>\n")
    htag = "h3" if compact else "h2"
    if compact:
        meta = (f'{i}  <div class="realization__row">\n'
                + realization_meta(r, "realization__meta realization__meta--inline", i + "    ")
                + f'{i}  </div>\n')
    else:
        meta = realization_meta(r, indent=i + "  ")
    cls_art = "realization realization--compact" if compact else "realization"
    return (f'{i}<article class="{cls_art}" aria-labelledby="{hid}">\n{media}'
            f'{i}  <{htag} class="visually-hidden" id="{hid}">Realizacja: {name}</{htag}>\n'
            f'{meta}{product_tags(r, 6, i + "  ")}'
            f'{i}  <a class="link-arrow" href="{url}">Przeczytaj o realizacji<span class="visually-hidden">: {name}</span>\n'
            f'{i}    {ARROW}\n{i}  </a>\n{i}</article>\n')


def head_preload(im, sizes):
    if not im:
        return []
    if im["srcset"]:
        return [f'<link rel="preload" as="image" href="{im["src"]}" imagesrcset="{im["srcset"]}" imagesizes="{sizes}">']
    return [f'<link rel="preload" as="image" href="{im["src"]}">']


# ---------------------------------------------------------------- PRODUKT
VARIANTS = """            <div class="variants">
              <p class="variants__label" id="variants-label">Dostępne wersje kolorystyczne</p>
              <div class="variants__list" role="group" aria-labelledby="variants-label" data-variants>
                <button class="variant" type="button" aria-pressed="true">Domyślna</button>
                <button class="variant" type="button" aria-pressed="false">Personalizowana</button>
                <button class="variant" type="button" aria-pressed="false" disabled>Stal</button>
              </div>
            </div>
"""


def spec_html(p):
    rows = [("Typ", e(p["type"]))]
    makers = p.get("makers") or []
    if makers:
        rows.append(("Producent" if len(makers) == 1 else "Dostępni producenci", e(", ".join(makers))))
    if p.get("mount"):
        rows.append(("Montaż", e(re.sub(r"^Montaż\s+", "", p["mount"]).capitalize())))
    for key, label in (("features", "Cechy"), ("notes", "Integracje")):
        if p.get(key):
            lis = "".join(f"<li>{e(x)}</li>" for x in p[key])
            rows.append((label, f"<ul>{lis}</ul>"))
    body = "".join(f"                    <div><dt>{k}</dt><dd>{v}</dd></div>\n" for k, v in rows)
    return f'                  <dl class="spec">\n{body}                  </dl>\n'


def gallery_html(p):
    hero = image(p.get("hero"))
    img = image(p.get("image"))
    name = p["name"]
    if hero and img:
        main_im, thumb_im = hero, img
    else:
        main_im, thumb_im = hero or img, None
    if not main_im:
        return ('        <div class="gallery gallery--single">\n'
                f'          <figure class="gallery__main ph" role="img" aria-label="Zdjęcie produktu {e(name)} – wkrótce"></figure>\n'
                '        </div>\n'), None, False
    sizes = SIZES_GALLERY if thumb_im else SIZES_GALLERY_SINGLE
    main = img_tag(main_im, sizes, alt=name, lazy=False, extra=" data-gallery-main" if thumb_im else "")
    if not thumb_im:
        return ('        <div class="gallery gallery--single">\n'
                f'          <figure class="gallery__main">\n            {main}\n          </figure>\n'
                '        </div>\n'), (main_im, sizes), False
    alt2 = f"{name} – zdjęcie produktu"
    thumb = (f'            <li>\n'
             f'              <button class="gallery__thumb" type="button" aria-label="Pokaż zdjęcie: {e(alt2)}"\n'
             f'                      data-full="{e(thumb_im["src"])}"\n'
             + (f'                      data-full-srcset="{e(thumb_im["srcset"])}"\n' if thumb_im["srcset"] else "")
             + f'                      data-alt="{e(alt2)}">\n'
             f'                <img src="{e(thumb_im["smallest"])}" width="80" height="100" alt="" loading="lazy">\n'
             f'              </button>\n            </li>\n')
    return ('        <!-- Galeria: zdjęcie główne + miniatura (js/pages/produkt.js zamienia zdjęcia) -->\n'
            '        <div class="gallery" data-gallery>\n'
            f'          <figure class="gallery__main">\n            {main}\n          </figure>\n'
            f'          <ul class="gallery__thumbs" aria-label="Zdjęcia produktu">\n{thumb}          </ul>\n'
            '        </div>\n'), (main_im, sizes), True


def build_product(p):
    cat = CAT[p["category"]]
    name = p["name"]
    gallery, main, has_thumbs = gallery_html(p)
    has_variants = p["slug"] == "czytnik-modulo6-lite"
    lead = lead_of(p)

    acc = []
    acc.append(("Zastosowanie", f"                  <p>{e(cat['lead'])}</p>\n"))
    acc.append(("Specyfikacja", spec_html(p)))
    accordion = "".join(
        f'            <details class="accordion__item" open>\n'
        f'              <summary>{t}</summary>\n'
        f'              <div class="accordion__body">\n{b}              </div>\n'
        f'            </details>\n' for t, b in acc)

    body = breadcrumbs([("Produkty", "oferta.html#urzadzenia"),
                        (cat["name"], f"oferta.html#{cat['slug']}"), (name, None)])
    body += f"""
    <!-- ============ PRODUKT ============ -->
    <section class="section" aria-labelledby="product-title">
      <div class="container pdp">
{gallery}
        <div class="pdp__info">
          <div class="pdp__desc">
            <h1 class="pdp__title" id="product-title">{e(name)}</h1>
            <p class="pdp__lead">{e(lead)}</p>
{VARIANTS if has_variants else ""}
{quote_card("Zamów wycenę", "Zamów", "product", name)}          </div>

          <div class="accordion pdp__accordion">
{accordion}          </div>
        </div>
      </div>
    </section>
"""
    reals = [r for r in REAL if p["slug"] in r.get("products", [])]
    if reals:
        rows = "".join(showcase_row(r) for r in reals)
        body += f"""
    <!-- ============ PRODUKT W REALIZACJI ============ -->
    <section class="section" aria-labelledby="realizacje-title">
      <div class="container">
        <header class="section-head offer-head">
          <h2 class="h-page" id="realizacje-title">Zobacz produkt w realizacji</h2>
        </header>
        <ul class="showcase">
{rows}        </ul>
        <a class="btn-line btn-line--lg" href="realizacje.html">Zobacz wszystkie realizacje
          {ARROW}
        </a>
      </div>
    </section>
"""
    same = [x for x in PRODUCTS if x["category"] == p["category"]]
    k = same.index(p)
    others = (same[k + 1:] + same[:k])[:4]
    if others:
        cards = "".join(product_card(x) for x in others)
        body += f"""
    <!-- ============ INNE Z TEJ KATEGORII ============ -->
    <section class="section" aria-labelledby="inne-title">
      <div class="container">
        <header class="section-head offer-head">
          <h2 class="h-page" id="inne-title">Inne z tej kategorii</h2>
          <p class="text-body-lg">{e(cat["lead"])}</p>
        </header>
        <ul class="products__grid catalog" aria-label="Inne produkty z tej kategorii">
{cards}        </ul>
        <div class="section-cta">
          <a class="btn btn--primary btn--md btn--glow btn--roboto" href="oferta.html#{cat['slug']}">Zobacz całą kategorię
            {ARROW_W}
          </a>
        </div>
      </div>
    </section>
"""
    meta = {"title": f"{name} – Sport Data", "description": lead, "nav": "produkty",
            "css": ["css/pages/oferta.css"]}
    if has_thumbs or has_variants:
        meta["js"] = ["js/pages/produkt.js"]
    if main:
        meta["head"] = head_preload(*main)
        meta["og_image"] = main[0]["src"]
    return write_page(f"produkt-{p['slug']}.html", meta, f'<main id="main">\n{body}  </main>')


# ---------------------------------------------------------------- USŁUGA
def build_service(s):
    others = [x for x in SERV if x is not s]
    others.sort(key=lambda x: x["group"] != s["group"])  # najpierw ta sama grupa
    others = others[:4]
    cards = "".join(service_card(x) for x in others)
    showcase_reals = [r for r in REAL if r.get("image") or r.get("logo")][:3]
    cases = "".join(case_card(r) for r in showcase_reals)
    body = breadcrumbs([("Oferta", "oferta.html"), ("Usługi", "oferta.html#uslugi"), (s["name"], None)])
    body += f"""
    <!-- ============ USŁUGA ============ -->
    <section class="section" aria-labelledby="service-title">
      <div class="container svc">
        <div class="svc__main">
          <h1 class="pdp__title" id="service-title">{e(s["name"])}</h1>
          <p class="pdp__lead">{e(s["lead"])}</p>
        </div>

        <div class="svc__aside">
{quote_card("Zamów wycenę", "Zamów", "service", s["name"], "          ")}        </div>
      </div>
    </section>

    <!-- ============ INNE USŁUGI ============ -->
    <section class="section" aria-labelledby="pomoc-title">
      <div class="container">
        <header class="section-head offer-head">
          <h2 class="h-page" id="pomoc-title">W czym jeszcze możemy pomóc?</h2>
        </header>
        <ul class="services">
{cards}        </ul>
        <a class="btn btn--primary btn--md btn--glow btn--roboto" href="oferta.html#uslugi">Zobacz wszystkie usługi
          {ARROW_W}
        </a>
      </div>
    </section>

    <!-- ============ REALIZACJE ============ -->
    <section class="section" aria-labelledby="praktyka-title">
      <div class="container">
        <header class="section-head offer-head">
          <h2 class="h-page" id="praktyka-title">Zobacz nasze realizacje</h2>
        </header>
        <ul class="cases-grid">
{cases}        </ul>
        <a class="btn-line btn-line--lg" href="realizacje.html">Zobacz wszystkie realizacje
          {ARROW}
        </a>
      </div>
    </section>
"""
    meta = {"title": f"{s['name']} – Sport Data", "description": s["lead"], "nav": "oferta",
            "css": ["css/pages/oferta.css"]}
    return write_page(f"usluga-{s['slug']}.html", meta, f'<main id="main">\n{body}  </main>')


# ---------------------------------------------------------------- REALIZACJA
def build_realization(r):
    name = r["name"]
    meta = {"title": f"{name} – realizacja Sport Data", "description": r["lead"], "nav": "realizacje",
            "cta": "Poznaj ofertę", "css": ["css/pages/realizacje.css"]}
    hero = ""
    if r.get("image"):
        im = image(r["image"])
        meta["og_image"] = im["src"]
        meta["head"] = head_preload(im, "100vw")
        hero = (f'      <div class="case-hero__media">\n'
                f'        {img_tag(im, "100vw", 1440, 600, alt=f"Realizacja Sport Data – {name}", lazy=False)}\n'
                f'      </div>\n')
    elif r.get("logo"):
        logo = logo_tag(r["logo"], name).replace(' loading="lazy"', "")
        hero = (f'      <div class="container">\n'
                f'        <div class="case-logo logo-panel">\n'
                f'          {logo}\n'
                f'        </div>\n      </div>\n')
    tags = ""
    if r.get("tags"):
        tags = (f'            <ul class="tags realization__tags" aria-label="Tagi realizacji">\n'
                f'{tag_links(r["tags"], "              ")}            </ul>\n')
    meta_rows = [("Klient", r["name"]), ("Miasto", r["city"])]
    if r.get("status"):
        meta_rows.append(("Status", r["status"]))
    dl = "".join(f"            <div><dt>{k}</dt><dd>{e(v)}</dd></div>\n" for k, v in meta_rows)
    scope = ""
    if r.get("scope"):
        lis = "".join(f"              <li>{e(x)}</li>\n" for x in r["scope"])
        scope = f"            <h2>Zakres prac</h2>\n            <ul>\n{lis}            </ul>\n"

    body = breadcrumbs([("Realizacje", "realizacje.html"), (name, None)])
    body += f"""
    <article class="case-study" aria-labelledby="case-title">

      <!-- ============ NAGŁÓWEK REALIZACJI ============ -->
      <header class="case-hero{' case-hero--logo' if (r.get('logo') and not r.get('image')) else ''}">
{hero}        <div class="container case-hero__body">
          <div class="case-hero__intro">
            <h1 class="case-hero__title" id="case-title">{e(name)}</h1>
{tags}          </div>
          <dl class="case-meta">
{dl}          </dl>
        </div>
      </header>

      <!-- ============ TREŚĆ + KARTA „ZAPYTAJ O OFERTĘ” ============ -->
      <div class="section case-body">
        <div class="container case-body__inner">
          <div class="prose case-prose">
            <p class="lead">{e(r["lead"])}</p>
{scope}          </div>

          <div class="case-body__aside">
{quote_card("Zapytaj o ofertę", "Napisz do nas", "source", f"Realizacja: {name}")}          </div>
        </div>
      </div>
"""
    items = []
    for s in r.get("products", []):
        p = PROD[s]
        url = product_url(s)
        im = image(p.get("image"))
        if im:
            media = (f'              <a class="case-product__media" href="{url}" tabindex="-1" aria-hidden="true">\n'
                     f'                {img_tag(im, SIZES_CASE_PRODUCT, 304, 304)}\n              </a>\n')
        else:
            media = f'              <a class="case-product__media placeholder" href="{url}" tabindex="-1" aria-hidden="true"></a>\n'
        items.append(f'            <li class="case-product">\n{media}'
                     f'              <h3 class="case-product__name"><a href="{url}">{e(p["name"])}</a></h3>\n'
                     f'              <p class="case-product__variant">{e(p["type"])}</p>\n            </li>\n')
    for n in r.get("legacy", []):
        items.append(f'            <li class="case-product case-product--legacy">\n'
                     f'              <div class="case-product__media placeholder" aria-hidden="true"></div>\n'
                     f'              <h3 class="case-product__name">{e(n)}</h3>\n            </li>\n')
    if items:
        body += f"""
      <!-- ============ PRODUKTY UŻYTE W REALIZACJI ============ -->
      <section class="section case-products" aria-labelledby="products-title">
        <div class="container">
          <header class="section-head case-products__head">
            <h2 class="h-page" id="products-title">Produkty użyte w realizacji</h2>
          </header>
          <ul class="case-products__grid">
{"".join(items)}          </ul>
        </div>
      </section>
"""
    body += "    </article>\n"
    k = REAL.index(r)
    others = [REAL[(k + 1) % len(REAL)], REAL[(k + 2) % len(REAL)]]
    lis = "".join(f"          <li>\n{realization_article(o, 'o', compact=True, indent='            ')}          </li>\n"
                  for o in others)
    body += f"""
    <!-- ============ INNE REALIZACJE ============ -->
    <section class="section other-cases" aria-labelledby="other-title">
      <div class="container">
        <header class="section-head">
          <h2 class="blog__heading" id="other-title">Inne realizacje</h2>
          <p class="blog__sub">Znajdziesz tu inspiracje, wiedzę i praktyczne wskazówki.</p>
        </header>

        <ul class="other-cases__list">
{lis}        </ul>

        <div class="section-action section-action--blog">
          <hr class="divider divider--light">
          <a class="btn btn--primary btn--md btn--glow btn--roboto" href="realizacje.html">Zobacz wszystkie realizacje
            {ARROW_W}
          </a>
        </div>
      </div>
    </section>
"""
    return write_page(f"realizacja-{r['slug']}.html", meta, f'<main id="main">\n{body}  </main>')


# ---------------------------------------------------------------- LISTA REALIZACJI
def build_realizacje_list():
    path = PAGES / "realizacje.html"
    raw = path.read_text()
    lis = []
    for n, r in enumerate(REAL):
        lis.append(f'          <li id="{e(r["slug"])}" data-tags="{e(" ".join(r.get("tags", [])))}">\n'
                   + realization_article(r, "r", first=(n == 0))
                   + "          </li>\n")
    new_list = '<ul class="realizations__list" data-tag-list>\n' + "\n".join(lis) + "        </ul>"
    pat = re.compile(r'<ul class="realizations__list" data-tag-list>.*?\n        </ul>(?=\n      </div>\n    </section>)', re.S)
    if not pat.search(raw):
        raise SystemExit("Nie znaleziono listy realizacji w src/pages/realizacje.html")
    raw = pat.sub(lambda m: new_list, raw, count=1)
    if MARK not in raw:
        raw = raw.replace("-->\n", f"-->\n{MARK}\n", 1)
    path.write_text(raw)
    return path.name


# ---------------------------------------------------------------- OFERTA
def build_oferta():
    sections = []
    for n, c in enumerate(CATS):
        h = "h1" if n == 0 else "h2"
        cards = "".join(product_card(p) for p in PRODUCTS if p["category"] == c["slug"])
        sections.append(f"""    <section class="section offer" id="{c['slug']}" aria-labelledby="{c['slug']}-title">
      <div class="container">
        <header class="section-head offer-head">
          <{h} class="h-page" id="{c['slug']}-title">{e(c['name'])}</{h}>
          <p class="text-body-lg">{e(c['lead'])}</p>
        </header>
        <ul class="products__grid catalog" aria-label="{e(c['name'])}">
{cards}        </ul>
      </div>
    </section>
""")
    groups = []
    for g in dict.fromkeys(s["group"] for s in SERV):
        gid = "uslugi-" + re.sub(r"[^a-z0-9]+", "-", g.lower())
        cards = "".join(service_card(s, heading="h4") for s in SERV if s["group"] == g)
        groups.append(f"""        <h3 class="services__group" id="{gid}">{e(g)}</h3>
        <ul class="services" aria-labelledby="{gid}">
{cards}        </ul>
""")
    reals = "".join(showcase_row(r) for r in REAL[:2])
    body = breadcrumbs([("Oferta", None)])
    body += f"""
    <!-- Kategorie produktów (data/produkty.json); #urzadzenia = link „Produkty” w nawigacji -->
    <div id="urzadzenia">
{"".join(sections)}    </div>

    <!-- ============ USŁUGI (data/uslugi.json) ============ -->
    <section class="section offer" id="uslugi" aria-labelledby="uslugi-title">
      <div class="container">
        <header class="section-head offer-head">
          <h2 class="h-page" id="uslugi-title">Usługi</h2>
        </header>
{"".join(groups)}      </div>
    </section>

    <!-- ============ REALIZACJE ============ -->
    <section class="section" aria-labelledby="praktyka-title">
      <div class="container">
        <header class="section-head offer-head">
          <h2 class="h-page" id="praktyka-title">Zobacz nasze produkty w realizacji</h2>
        </header>
        <ul class="showcase">
{reals}        </ul>
        <a class="btn-line btn-line--lg" href="realizacje.html">Zobacz wszystkie realizacje
          {ARROW}
        </a>
      </div>
    </section>
"""
    meta = {"title": "Oferta – urządzenia i oprogramowanie do kontroli dostępu – Sport Data",
            "description": "Urządzenia do kontroli dostępu, kołowroty i bramki, zarządzanie parkingiem, automaty biletowe, oprogramowanie oraz usługi serwisowe i personalizacja – Sport Data.",
            "nav": "oferta", "css": ["css/pages/oferta.css"]}
    return write_page("oferta.html", meta, f'<main id="main">\n{body}  </main>')


if __name__ == "__main__":
    out = [build_product(p) for p in PRODUCTS]
    out += [build_service(s) for s in SERV]
    out += [build_realization(r) for r in REAL]
    out.append(build_realizacje_list())
    out.append(build_oferta())
    print(f"wygenerowano {len(out)} plików w src/pages/")
