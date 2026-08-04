#!/usr/bin/env python3
"""Prepara los derivados del logo del laboratorio.

Entrada:   static/images/logo-neurosistemas.jpg  (553x230, fondo blanco plano)
           Ese archivo es el original y no se toca nunca.

Salidas:   static/images/logo-neurosistemas.png  logo completo con transparencia
           static/images/isotipo.png             solo la neurona, para el header
           static/images/favicon.png             180x180, sobre blanco
           static/images/og-neurosistemas.jpg    1200x630 para redes sociales

Uso:   .venv/bin/python scripts/preparar_logo.py

El fondo se quita por luminancia, no por umbral binario: el alfa se calcula a
partir del canal más oscuro de cada píxel y el color se "des-premultiplica",
de modo que los bordes antialiasing de las letras negras y del splatter quedan
suaves en vez de dentados. Todo lo que supere BLANCO (246) queda transparente.
"""

from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
IMAGENES = RAIZ / "static" / "images"
ORIGINAL = IMAGENES / "logo-neurosistemas.jpg"

BLANCO = 246  # a partir de aquí se considera fondo

# Recorte del isotipo dentro del original: la neurona con su splatter, sin
# nada del wordmark. Comprobado a ojo sobre el JPG de 553x230.
ISOTIPO_CAJA = (370, 0, 487, 84)
# Para el favicon se recorta pegado al soma de la neurona: es lo único que
# sigue leyéndose a 32 px. Con el splatter completo queda una mancha.
FAVICON_CAJA = (388, 18, 452, 78)

# Espectro del sitio, en el orden del logo. Debe coincidir con data/colores.yaml.
ESPECTRO = [
    "#B12313", "#C65A16", "#C98510", "#6E9A1B", "#2F8F5B",
    "#2E9DBC", "#2186B7", "#762D60", "#9A2A53",
]


def sin_fondo(im):
    """Devuelve el RGBA del original con el blanco convertido en transparencia."""
    a = np.asarray(im.convert("RGB")).astype(np.float64)
    mn = a.min(axis=2)

    alfa = 255.0 - mn
    alfa[mn >= BLANCO] = 0.0

    # Des-premultiplicar: el píxel visible es  fondo*(1-α) + color*α  con
    # fondo blanco. Se despeja el color original para no oscurecer los bordes.
    a_seg = np.where(alfa > 0, alfa, 1.0)[..., None]
    color = (a - (255.0 - alfa)[..., None]) * 255.0 / a_seg
    color = np.clip(color, 0, 255)

    rgba = np.dstack([color, alfa]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def recortar_a_contenido(im, margen=0):
    """Recorta al área con algo de opacidad, con un margen opcional."""
    caja = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if caja is None:
        return im
    izq, arr, der, aba = caja
    return im.crop((
        max(0, izq - margen), max(0, arr - margen),
        min(im.width, der + margen), min(im.height, aba + margen),
    ))


def alto_fijo(im, alto):
    return im.resize((max(1, round(im.width * alto / im.height)), alto), Image.LANCZOS)


def franja_espectral(ancho, alto):
    """Barra con los 9 tonos en bandas iguales, tramos duros."""
    barra = Image.new("RGB", (ancho, alto), "#FFFFFF")
    px = barra.load()
    n = len(ESPECTRO)
    for x in range(ancho):
        c = ESPECTRO[min(n - 1, x * n // ancho)]
        rgb = tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
        for y in range(alto):
            px[x, y] = rgb
    return barra


def main():
    if not ORIGINAL.exists():
        raise SystemExit(f"No encuentro el original: {ORIGINAL}")

    original = Image.open(ORIGINAL)
    print(f"original: {original.size[0]}x{original.size[1]}")

    # --- 1. Logo completo con transparencia -------------------------------
    logo = recortar_a_contenido(sin_fondo(original), margen=2)
    logo.save(IMAGENES / "logo-neurosistemas.png", optimize=True)
    print(f"logo-neurosistemas.png: {logo.size[0]}x{logo.size[1]}")

    # --- 2. Isotipo para el header ----------------------------------------
    # 128 px de alto: se muestra a 34 px, así queda nítido en pantallas 2x y 3x.
    iso = recortar_a_contenido(sin_fondo(original.crop(ISOTIPO_CAJA)))
    iso = alto_fijo(iso, 128)
    iso.save(IMAGENES / "isotipo.png", optimize=True)
    print(f"isotipo.png: {iso.size[0]}x{iso.size[1]}")

    # --- 3. Favicon 180x180 sobre blanco ----------------------------------
    # Opaco a propósito: es también el apple-touch-icon, y ahí la transparencia
    # se rellena de negro en algunos sistemas.
    fav_src = recortar_a_contenido(sin_fondo(original.crop(FAVICON_CAJA)))
    lienzo = 180
    util = 152  # deja un margen parejo alrededor
    escala = min(util / fav_src.width, util / fav_src.height)
    fav_src = fav_src.resize(
        (max(1, round(fav_src.width * escala)), max(1, round(fav_src.height * escala))),
        Image.LANCZOS,
    )
    favicon = Image.new("RGBA", (lienzo, lienzo), (255, 255, 255, 255))
    favicon.paste(
        fav_src,
        ((lienzo - fav_src.width) // 2, (lienzo - fav_src.height) // 2),
        fav_src,
    )
    favicon.convert("RGB").save(IMAGENES / "favicon.png", optimize=True)
    print(f"favicon.png: {lienzo}x{lienzo}")

    # --- 4. Imagen Open Graph ---------------------------------------------
    ancho, alto, franja = 1200, 630, 12
    og = Image.new("RGB", (ancho, alto), "#FFFFFF")
    og_logo = logo.copy()
    escala = min(760 / og_logo.width, 320 / og_logo.height)
    og_logo = og_logo.resize(
        (round(og_logo.width * escala), round(og_logo.height * escala)), Image.LANCZOS
    )
    og.paste(
        og_logo,
        ((ancho - og_logo.width) // 2, (alto - franja - og_logo.height) // 2),
        og_logo,
    )
    og.paste(franja_espectral(ancho, franja), (0, alto - franja))
    og.save(IMAGENES / "og-neurosistemas.jpg", quality=88, optimize=True)
    print(f"og-neurosistemas.jpg: {ancho}x{alto}")


if __name__ == "__main__":
    main()
