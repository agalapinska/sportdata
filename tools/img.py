#!/usr/bin/env python3
"""Optymalizacja zdjęć do WebP w kilku szerokościach (pod srcset).

python3 -I tools/img.py ŹRÓDŁO.png assets/img/<strona>/<nazwa> --widths 480,960 [--crop x0,y0,x1,y1] [--quality 80]
--crop przyjmuje ułamki 0–1 (kadr z Figmy). Przy jednej szerokości plik nie dostaje sufiksu -<w>.
"""
import argparse
from pathlib import Path
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--widths", default="480,960")
ap.add_argument("--crop", default=None)
ap.add_argument("--quality", type=int, default=80)
a = ap.parse_args()
im = Image.open(a.src)
im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
if a.crop:
    x0, y0, x1, y1 = map(float, a.crop.split(","))
    w, h = im.size
    im = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
widths = [int(x) for x in a.widths.split(",")]
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
for w in widths:
    w2 = min(w, im.size[0]); h2 = round(im.size[1] * w2 / im.size[0])
    r = im.resize((w2, h2), Image.LANCZOS)
    name = f"{a.out}.webp" if len(widths) == 1 else f"{a.out}-{w}.webp"
    r.save(name, "WEBP", quality=a.quality, method=6)
    print(name, r.size)
