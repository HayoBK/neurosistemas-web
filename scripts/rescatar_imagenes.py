#!/usr/bin/env python3
"""Rescata las imágenes del WordPress antiguo antes de que lo den de baja.

El sitio viejo (neurosistemas.cl, Elementor) tiene las fotos del equipo y del
laboratorio. Este script las baja, las recorta y las deja listas para el sitio
nuevo:

    static/images/equipo/<slug>.jpg    400x400, JPG calidad 82
    static/images/galeria/<slug>.jpg   lado mayor 1600 px
    data/miembros.yaml / visitantes.yaml   se rellena el campo 'foto'
    data/galeria.yaml                      se listan las imágenes de laboratorio

Uso:
    .venv/bin/python scripts/rescatar_imagenes.py
    .venv/bin/python scripts/rescatar_imagenes.py --simular

En las páginas de Elementor cada persona vive en un `elementor-column` que
contiene su <img> y un <h3> con su nombre. De ahí sale el emparejamiento; no
se confía en el nombre del archivo, que a veces es "circle-cropped-55".

Es idempotente: no vuelve a bajar lo que ya está y no pisa un campo 'foto'
que ya tenga valor.
"""

import argparse
import html
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
EQUIPO = RAIZ / "static" / "images" / "equipo"
GALERIA = RAIZ / "static" / "images" / "galeria"

# El WordPress responde unas páginas bajo /web/ y otras en la raíz, así que
# se prueban las dos formas y se usa la que conteste 200.
BASES = ("https://neurosistemas.cl", "https://neurosistemas.cl/web")
PAGINAS_EQUIPO = {
    "miembros": "miembros-del-laboratorio",
    "visitantes": "miembros-visitantes",
    "exmiembros": "ex-miembros",
}
PAGINA_GALERIA = "galeria-de-imagenes"

# Fotos del laboratorio para la galería. Van por nombre explícito y no por
# barrido: la biblioteca del WordPress tiene más de 700 archivos, casi todos
# retratos, afiches y material suelto sin curar. Para sumar más fotos, agregar
# aquí el nombre del archivo tal como está en wp-content/uploads.
GALERIA_ARCHIVOS = (
    "Fotolab.jpg",
    "WhatsApp-Image-2020-07-06-at-22.27.10.jpeg",
    "WhatsApp-Image-2020-07-06-at-22.35.15.jpeg",
)

# Imágenes que no son fotos de nadie: el logo y el marcador genérico de
# "sin foto". Quien tenga ese marcador se queda con sus iniciales.
DESCARTAR = ("untitled_artwork", "logoide", "cropped-untitled", "logo",
             # "rut" descarta escaneos de cédula subidos a la biblioteca:
             # hay al menos uno y no es un retrato publicable.
             "-rut-", "_rut_", "rut-1", "carnet")

LADO = 400
CALIDAD = 82
LADO_GALERIA = 1600

RE_COLUMNA = re.compile(r'elementor-column\b')
RE_IMG = re.compile(r'<img[^>]+src="([^"]+wp-content/uploads/[^"]+)"', re.I)
RE_H3 = re.compile(r"<h3[^>]*>(.*?)</h3>", re.I | re.S)
RE_TAGS = re.compile(r"<[^>]+>")


def texto_plano(fragmento):
    return html.unescape(RE_TAGS.sub(" ", fragmento)).replace("\xa0", " ").strip()


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", texto.lower())


def slug(texto):
    base = normalizar(texto).strip()
    return re.sub(r"\s+", "-", base)[:60]


def tokens(nombre):
    ruido = {"dr", "dra", "prof", "sr", "sra", "de", "del", "la", "las", "los",
             "y", "ph", "phd", "md", "mg", "flga", "klgo", "tm"}
    return [p for p in normalizar(nombre).split() if len(p) > 1 and p not in ruido]


def parecidos(a, b):
    """Tolera variantes de un mismo nombre de pila.

    El sitio viejo escribe "Cristián López" y el YAML "Christian López"; sin
    esto se perdía esa foto. El umbral es alto para no confundir a personas
    distintas que compartan apellido.
    """
    return a == b or SequenceMatcher(None, a, b).ratio() >= 0.8


def misma_persona(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return False
    if set(ta) == set(tb):
        return True
    if not parecidos(ta[0], tb[0]):
        return False
    return bool({t for t in ta[1:] if len(t) > 3} & {t for t in tb[1:] if len(t) > 3})


def descartable(url):
    return any(d in url.lower() for d in DESCARTAR)


def descargar_paginas(sesion, ruta):
    """Todas las versiones de una página que respondan 200.

    Las dos formas de URL contestan para algunas rutas, pero no con el mismo
    contenido: /miembros-del-laboratorio/ existe en ambas y solo la de /web/
    trae las fotos. Por eso se bajan las dos y decide quien llama.
    """
    docs, ultimo = [], None
    for base in BASES:
        url = f"{base}/{ruta}/"
        try:
            r = sesion.get(url, timeout=40)
            if r.status_code == 200:
                docs.append(r.text)
            else:
                ultimo = f"{r.status_code} en {url}"
        except requests.RequestException as e:
            ultimo = str(e)
    if not docs:
        raise requests.RequestException(ultimo or "sin respuesta")
    return docs


def personas_de(doc):
    """[(nombre, url_foto)] leídos de una página de Elementor."""

    encontrados, vistos = [], set()
    # Cada columna de Elementor es una tarjeta de persona: se corta por ahí y
    # dentro de cada trozo se busca la primera imagen y el primer <h3>.
    trozos = RE_COLUMNA.split(doc)
    for trozo in trozos:
        img = RE_IMG.search(trozo)
        h3 = RE_H3.search(trozo)
        if not (img and h3):
            continue
        url = html.unescape(img.group(1))
        nombre = texto_plano(h3.group(1))
        nombre = re.sub(r"\s+", " ", nombre).strip(" .,-")
        if not nombre or len(nombre) < 4 or descartable(url):
            continue
        if url in vistos:
            continue
        vistos.add(url)
        encontrados.append((nombre, url))
    return encontrados


RE_SUFIJOS = re.compile(
    r"(-scaled|-modified|-min|-cropped|-copia|-copy|-e\d{6,}|-\d+x\d+|-\d{1,2})+$", re.I)


def clave_de_archivo(url):
    """Nombre de archivo reducido a letras, para comparar con un nombre.

    'CFernandez-1-scaled.jpg' -> 'cfernandez'
    'foto-rocioloyola.jpg'    -> 'fotorocioloyola'
    """
    base = url.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    base = RE_SUFIJOS.sub("", base)
    return re.sub(r"[^a-z]", "", normalizar(base))


def archivo_es_de(url, nombre):
    """¿El nombre del archivo identifica a esta persona?

    Se exige el apellido completo y, además, el nombre de pila entero o su
    inicial pegada al apellido. Solo con el apellido habría confusiones —hay
    varios Fernández y varios González en la biblioteca.
    """
    clave = clave_de_archivo(url)
    ts = tokens(nombre)
    if len(ts) < 2 or len(clave) < 5:
        return False
    pila, apellidos = ts[0], [t for t in ts[1:] if len(t) > 3]
    for ap in apellidos:
        if ap not in clave:
            continue
        if pila in clave:
            return True
        if f"{pila[0]}{ap}" in clave:
            return True
    return False


def catalogo_de_medios(sesion, tope=12):
    """URLs de la biblioteca de medios, vía la API REST de WordPress.

    La API solo contesta en el dominio raíz, no bajo /web/.
    """
    urls, pagina = [], 1
    while pagina <= tope:
        r = sesion.get(
            "https://neurosistemas.cl/wp-json/wp/v2/media",
            params={"per_page": 100, "page": pagina, "_fields": "source_url"},
            timeout=45,
        )
        if r.status_code != 200:
            break
        lote = r.json()
        if not isinstance(lote, list) or not lote:
            break
        urls.extend(m.get("source_url", "") for m in lote)
        pagina += 1
    return [u for u in urls if u]


def bajar_imagen(sesion, url):
    r = sesion.get(url, timeout=60)
    r.raise_for_status()
    return Image.open(BytesIO(r.content))


def guardar_cuadrada(im, destino):
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        fondo = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        fondo.paste(im, mask=im.split()[-1])
        im = fondo
    else:
        im = im.convert("RGB")
    im = ImageOps.fit(im, (LADO, LADO), Image.LANCZOS, centering=(0.5, 0.4))
    im.save(destino, "JPEG", quality=CALIDAD, optimize=True, progressive=True)


def guardar_grande(im, destino):
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((LADO_GALERIA, LADO_GALERIA), Image.LANCZOS)
    im.save(destino, "JPEG", quality=CALIDAD, optimize=True, progressive=True)


# --- escritura del campo 'foto' preservando comentarios -------------------

RE_NOMBRE = re.compile(r"^(\s*)-?\s*nombre:\s*(.+?)\s*$")
RE_FOTO = re.compile(r"^(\s*)foto:\s*(.*?)\s*$")


def escribir_fotos(ruta, asignaciones, simular=False):
    """asignaciones: {nombre_en_el_yaml: archivo}. Devuelve cuántos escribió."""
    lineas = ruta.read_text(encoding="utf-8").splitlines(keepends=True)
    marcas = [(m.group(2).strip().strip('"').strip("'"), i)
              for i, l in enumerate(lineas)
              if (m := RE_NOMBRE.match(l)) and not l.lstrip().startswith("#")]

    inserciones, escritos = [], 0
    for k, (nombre, inicio) in enumerate(marcas):
        fin = marcas[k + 1][1] if k + 1 < len(marcas) else len(lineas)
        archivo = asignaciones.get(nombre)
        if not archivo:
            continue

        idx = next((i for i in range(inicio, fin) if RE_FOTO.match(lineas[i])), None)
        if idx is not None:
            actual = RE_FOTO.match(lineas[idx]).group(2).strip("\"'")
            if actual:            # ya tenía foto: no se pisa
                continue
            sangria = RE_FOTO.match(lineas[idx]).group(1)
            lineas[idx] = f'{sangria}foto: "{archivo}"\n'
        else:
            sangria = re.match(r"^(\s*)-?\s*", lineas[inicio]).group(1)
            if lineas[inicio].lstrip().startswith("- "):
                sangria += "  "
            inserciones.append((inicio + 1, f'{sangria}foto: "{archivo}"\n'))
        escritos += 1

    for i, texto in sorted(inserciones, reverse=True):
        lineas.insert(i, texto)
    if escritos and not simular:
        ruta.write_text("".join(lineas), encoding="utf-8")
    return escritos


def nombres_del_yaml(ruta, anidado):
    """Lista de nombres tal como están escritos en el YAML."""
    import yaml
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8")) or []
    if anidado:
        return [p.get("nombre", "") for g in datos for p in (g.get("personas") or [])]
    return [p.get("nombre", "") for p in datos]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--simular", action="store_true")
    args = ap.parse_args()

    EQUIPO.mkdir(parents=True, exist_ok=True)
    GALERIA.mkdir(parents=True, exist_ok=True)

    sesion = requests.Session()
    sesion.headers.update({"User-Agent": "neurosistemas-web/1.0 (rescate de imágenes)"})

    # ---- 1. Fotos del equipo -------------------------------------------
    destinos = [
        (DATA / "miembros.yaml", True),
        (DATA / "visitantes.yaml", False),
    ]
    del_yaml = {ruta: nombres_del_yaml(ruta, anidado) for ruta, anidado in destinos}

    hallados = []
    for etiqueta, ruta in PAGINAS_EQUIPO.items():
        try:
            # Se prueban ambas URL y se usa la que traiga más personas.
            gente = max((personas_de(d) for d in descargar_paginas(sesion, ruta)),
                        key=len, default=[])
        except requests.RequestException as e:
            print(f"  ! no pude leer {ruta}: {e}")
            continue
        print(f"{etiqueta}: {len(gente)} personas con foto en el sitio viejo")
        hallados.extend(gente)

    asignaciones = {ruta: {} for ruta, _ in destinos}
    bajadas, sin_uso = 0, []

    for nombre_web, url in hallados:
        objetivo = None
        for ruta, _ in destinos:
            for nombre_yaml in del_yaml[ruta]:
                if misma_persona(nombre_web, nombre_yaml):
                    objetivo = (ruta, nombre_yaml)
                    break
            if objetivo:
                break

        if not objetivo:
            sin_uso.append(nombre_web)
            continue

        ruta, nombre_yaml = objetivo
        archivo = f"{slug(nombre_yaml)}.jpg"
        destino = EQUIPO / archivo
        if not destino.exists():
            if args.simular:
                print(f"    (bajaría) {nombre_yaml} -> {archivo}")
            else:
                try:
                    guardar_cuadrada(bajar_imagen(sesion, url), destino)
                    bajadas += 1
                    print(f"    ✓ {nombre_yaml} -> {archivo}")
                except Exception as e:
                    print(f"    ! {nombre_yaml}: {e}")
                    continue
        asignaciones[ruta][nombre_yaml] = archivo

    # ---- 1b. Segunda pasada: biblioteca de medios ------------------------
    # Varias personas no aparecen en la página de Elementor pero sí tienen su
    # foto en la biblioteca (Carlos-Navarro.jpg, foto-rocioloyola.jpg…). Se
    # emparejan por nombre de archivo, que es más frágil, así que el criterio
    # de archivo_es_de() es estricto.
    faltantes = [(ruta, n) for ruta, _ in destinos for n in del_yaml[ruta]
                 if n not in asignaciones[ruta]]
    if faltantes:
        try:
            medios = [u for u in catalogo_de_medios(sesion)
                      if not descartable(u) and "/thumbs/" not in u]
        except requests.RequestException as e:
            print(f"  ! no pude leer la biblioteca de medios: {e}")
            medios = []

        for ruta, nombre in faltantes:
            cands = [u for u in dict.fromkeys(medios) if archivo_es_de(u, nombre)]
            if not cands:
                continue
            # Preferir las versiones ya recortadas para avatar.
            cands.sort(key=lambda u: (
                "cropped" not in u.lower(), "modified" not in u.lower(), len(u)))
            archivo = f"{slug(nombre)}.jpg"
            destino = EQUIPO / archivo
            if not destino.exists():
                if args.simular:
                    print(f"    (bajaría, biblioteca) {nombre} -> {archivo}")
                else:
                    try:
                        guardar_cuadrada(bajar_imagen(sesion, cands[0]), destino)
                        bajadas += 1
                        print(f"    ✓ {nombre} -> {archivo}  "
                              f"({cands[0].rsplit('/', 1)[-1]})")
                    except Exception as e:
                        print(f"    ! {nombre}: {e}")
                        continue
            asignaciones[ruta][nombre] = archivo

    print(f"\nFotos descargadas: {bajadas}")
    for ruta, _ in destinos:
        n = escribir_fotos(ruta, asignaciones[ruta], simular=args.simular)
        print(f"  {ruta.name}: {n} campos 'foto' escritos")
    if sin_uso:
        print(f"  fotos del sitio viejo sin persona equivalente: {len(sin_uso)}")
        for n in sin_uso:
            print(f"    - {n}")

    # ---- 2. Galería ------------------------------------------------------
    # La página /galeria-de-imagenes/ del sitio viejo quedó vacía: solo trae el
    # logo. Las fotos siguen en la biblioteca de medios, así que se buscan por
    # nombre en la API REST de WordPress.
    print("\nGalería:")
    urls, titulos = [], []
    try:
        medios = catalogo_de_medios(sesion)
        print(f"  biblioteca de medios: {len(medios)} archivos")
        for nombre in GALERIA_ARCHIVOS:
            coincide = [u for u in medios if u.rsplit("/", 1)[-1] == nombre]
            if coincide:
                urls.append(coincide[0])
            else:
                print(f"  ! no encontré {nombre} en la biblioteca")
    except requests.RequestException as e:
        print(f"  ! no pude leer la biblioteca de medios: {e}")

    entradas = []
    for i, u in enumerate(urls, 1):
        archivo = f"laboratorio-{i:02d}.jpg"
        destino = GALERIA / archivo
        if not destino.exists() and not args.simular:
            try:
                guardar_grande(bajar_imagen(sesion, u), destino)
                print(f"    ✓ {archivo}  ({u.rsplit('/', 1)[-1]})")
            except Exception as e:
                print(f"    ! {u}: {e}")
                continue
        entradas.append(archivo)

    if entradas and not args.simular:
        lineas = [
            "# ============================================================\n",
            "# Galería de imágenes del laboratorio\n",
            "# archivo : nombre del archivo dentro de static/images/galeria/\n",
            "# titulo  : texto que aparece bajo la foto (opcional)\n",
            "# Rescatadas del sitio antiguo por scripts/rescatar_imagenes.py\n",
            "# ============================================================\n",
        ]
        for a in entradas:
            lineas.append(f'- archivo: "{a}"\n  titulo: ""\n')
        (DATA / "galeria.yaml").write_text("".join(lineas), encoding="utf-8")
        print(f"  data/galeria.yaml: {len(entradas)} imágenes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
