#!/usr/bin/env python3
"""Składa strony: src/pages/*.html + src/partials/* -> *.html w katalogu głównym.

Każdy plik w src/pages zaczyna się blokiem metadanych (JSON):
<!--page
{"title": "...", "description": "...", "nav": "realizacje", "css": ["css/pages/realizacje.css"],
 "cta": "Poznaj ofertę", "head": "<link rel=...>", "js": ["js/pages/x.js"]}
-->
a dalej zawiera <main id="main">...</main>.
Uruchom:  python3 tools/build.py
"""
import json, re, sys, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

NAV = [  # (klucz, etykieta, href)
    ("oferta", "Oferta", "oferta.html"),
    ("produkty", "Produkty", "oferta.html#urzadzenia"),
    ("realizacje", "Realizacje", "realizacje.html"),
    ("blog", "Blog", "blog.html"),
    ("pomoc", "Pomoc", "pomoc.html"),
]

HEAD = """<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#ed7c00">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:locale" content="pl_PL">

  <link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap">
{extra_head}  <link rel="stylesheet" href="css/styles.css">
{page_css}  <script src="js/main.js" defer></script>
{page_js}</head>
<body{body_attr}>
  <a class="skip-link" href="#main">Przejdź do treści</a>
"""

def nav_html(active, cta):
    items = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if key == active else ""
        items.append(f'          <li><a href="{href}"{cur}>{label}</a></li>')
    return (Path(SRC / "partials/header.html").read_text()
            .replace("{{NAV_LINKS}}", "\n".join(items))
            .replace("{{CTA_LABEL}}", cta))

def build(page: Path):
    raw = page.read_text()
    m = re.match(r"\s*<!--page\s*(\{.*?\})\s*-->\s*", raw, re.S)
    if not m:
        sys.exit(f"Brak bloku <!--page {{...}} --> w {page}")
    meta = json.loads(m.group(1))
    body = raw[m.end():].rstrip() + "\n"
    esc = lambda s: html.escape(s, quote=True)
    out = HEAD.format(
        title=esc(meta["title"]),
        description=esc(meta.get("description", "")),
        og_image=meta.get("og_image", "assets/img/hero-card-960.webp"),
        extra_head="".join(f"  {l}\n" for l in meta.get("head", [])),
        page_css="".join(f'  <link rel="stylesheet" href="{c}">\n' for c in meta.get("css", [])),
        page_js="".join(f'  <script src="{j}" defer></script>\n' for j in meta.get("js", [])),
        body_attr=f' class="{meta["body_class"]}"' if meta.get("body_class") else "",
    )
    out += "\n" + nav_html(meta.get("nav", ""), meta.get("cta", "Poznaj ofertę")) + "\n"
    out += "  " + body.strip() + "\n\n"
    out += (SRC / "partials/footer.html").read_text().rstrip() + "\n</body>\n</html>\n"
    target = ROOT / page.name
    target.write_text(out)
    return target.name

if __name__ == "__main__":
    pages = sorted((SRC / "pages").glob("*.html"))
    only = set(sys.argv[1:])
    for p in pages:
        if only and p.stem not in only and p.name not in only:
            continue
        print("zbudowano", build(p))
