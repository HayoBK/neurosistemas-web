#!/usr/bin/env python3
"""Cosecha ORCID iD desde el repo del Departamento de Neurociencia.

Varias personas del laboratorio también son académicos del Departamento, y ese
repo ya tiene el ORCID iD en el front-matter de cada ficha. Este script los
empareja por nombre y rellena los campos vacíos de:

    data/miembros.yaml     (campo orcid de cada persona)
    data/exmiembros.yaml   (se agrega el campo si no existe)
    data/orcid.yaml        (lo que enciende la sincronización diaria)

Uso:
    .venv/bin/python scripts/cosechar_orcid.py                 # aplica
    .venv/bin/python scripts/cosechar_orcid.py --simular       # solo muestra
    .venv/bin/python scripts/cosechar_orcid.py --repo RUTA     # otro repo

Es idempotente y NUNCA pisa un valor ya escrito: si el campo trae algo, lo
deja como está. Por eso se puede correr las veces que haga falta.

Los YAML se editan línea a línea en vez de con PyYAML porque los archivos
llevan comentarios de uso que hay que conservar.
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
REPO_NEUROCIENCIA = Path.home() / "Git_Web" / "Neurociencia"

# Palabras que no aportan a la identificación de una persona.
RUIDO = {
    "dr", "dra", "drs", "prof", "profesor", "profesora", "sr", "sra", "ph",
    "phd", "md", "de", "del", "la", "las", "los", "y", "da", "do", "van", "von",
}

RE_ORCID = re.compile(r"\b(\d{4}-\d{4}-\d{4}-\d{3}[\dX])\b")


def normalizar(texto):
    """Minúsculas sin acentos ni puntuación."""
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^\w\s]", " ", texto)
    return texto.lower()


def tokens(nombre):
    """Palabras significativas de un nombre, en orden."""
    return [p for p in normalizar(nombre).split() if p and p not in RUIDO and len(p) > 1]


def coincide(a, b):
    """¿Son la misma persona?

    Se exige que compartan el nombre de pila y al menos un apellido. Con solo
    el apellido habría falsos positivos (hay varios Rivera y varios Torres), y
    con solo el nombre de pila, más todavía.
    """
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return False
    if ta[0] != tb[0]:
        return False
    apellidos_a = {t for t in ta[1:] if len(t) > 3}
    apellidos_b = {t for t in tb[1:] if len(t) > 3}
    return bool(apellidos_a & apellidos_b)


def leer_academicos(repo):
    """Devuelve [(nombre, orcid)] de las fichas que traen ORCID."""
    carpeta = repo / "content" / "academicos"
    if not carpeta.is_dir():
        raise SystemExit(f"No encuentro {carpeta}. Usa --repo para indicar la ruta.")

    fichas = []
    for archivo in sorted(carpeta.glob("*/index.md")):
        texto = archivo.read_text(encoding="utf-8", errors="replace")
        cabecera = texto.split("---", 2)[1] if texto.startswith("---") else texto[:3000]

        m_titulo = re.search(r"^title:\s*(.+)$", cabecera, re.M)
        m_orcid = re.search(r"^orcid:\s*(.+)$", cabecera, re.M)
        if not (m_titulo and m_orcid):
            continue
        orcid = RE_ORCID.search(m_orcid.group(1))
        if not orcid:
            continue
        nombre = m_titulo.group(1).strip().strip('"').strip("'")
        fichas.append((nombre, orcid.group(1)))
    return fichas


# ----------------------------------------------------------------------------
# Edición de los YAML preservando comentarios
# ----------------------------------------------------------------------------

RE_NOMBRE = re.compile(r"^(\s*)-?\s*nombre:\s*(.+?)\s*$")
RE_CAMPO_ORCID = re.compile(r"^(\s*)orcid:\s*(.*?)\s*$")


def bloques_de_personas(lineas):
    """[(nombre, inicio, fin)] de cada entrada con campo 'nombre'."""
    marcas = []
    for i, linea in enumerate(lineas):
        m = RE_NOMBRE.match(linea)
        if m and not linea.lstrip().startswith("#"):
            nombre = m.group(2).strip().strip('"').strip("'")
            marcas.append((nombre, i))

    bloques = []
    for k, (nombre, inicio) in enumerate(marcas):
        fin = marcas[k + 1][1] if k + 1 < len(marcas) else len(lineas)
        bloques.append((nombre, inicio, fin))
    return bloques


def vacio(valor):
    return valor.split("#")[0].strip().strip('"').strip("'") == ""


def rellenar(ruta, buscar_orcid, crear_campo=False, simular=False):
    """Rellena el campo orcid de cada persona del archivo.

    buscar_orcid(nombre) -> orcid o None
    crear_campo: si la entrada no tiene campo orcid, lo agrega.
    Devuelve (rellenados, ya_tenian, sin_candidato).
    """
    lineas = ruta.read_text(encoding="utf-8").splitlines(keepends=True)
    rellenados, ya, sin = [], [], []
    inserciones = []  # (indice, texto)

    for nombre, inicio, fin in bloques_de_personas(lineas):
        idx_orcid = None
        for i in range(inicio, fin):
            m = RE_CAMPO_ORCID.match(lineas[i])
            if m:
                idx_orcid = i
                break

        if idx_orcid is not None and not vacio(RE_CAMPO_ORCID.match(lineas[idx_orcid]).group(2)):
            ya.append(nombre)
            continue

        orcid = buscar_orcid(nombre)
        if not orcid:
            sin.append(nombre)
            continue

        if idx_orcid is not None:
            sangria = RE_CAMPO_ORCID.match(lineas[idx_orcid]).group(1)
            lineas[idx_orcid] = f'{sangria}orcid: "{orcid}"\n'
        elif crear_campo:
            sangria = re.match(r"^(\s*)-?\s*", lineas[inicio]).group(1)
            # Alinear con el resto de los campos de la entrada: si la línea del
            # nombre empieza con "- ", los campos van dos espacios más adentro.
            if lineas[inicio].lstrip().startswith("- "):
                sangria += "  "
            inserciones.append((inicio + 1, f'{sangria}orcid: "{orcid}"\n'))
        else:
            sin.append(nombre)
            continue

        rellenados.append((nombre, orcid))

    for i, texto in sorted(inserciones, reverse=True):
        lineas.insert(i, texto)

    if rellenados and not simular:
        ruta.write_text("".join(lineas), encoding="utf-8")

    return rellenados, ya, sin


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=str(REPO_NEUROCIENCIA),
                    help="ruta del repo del Departamento de Neurociencia")
    ap.add_argument("--simular", action="store_true",
                    help="muestra lo que haría, sin escribir")
    args = ap.parse_args()

    academicos = leer_academicos(Path(args.repo).expanduser())
    print(f"Académicos con ORCID en el repo de Neurociencia: {len(academicos)}\n")

    def buscar(nombre):
        for nombre_ac, orcid in academicos:
            if coincide(nombre, nombre_ac):
                return orcid
        return None

    objetivos = [
        (DATA / "miembros.yaml", False),
        (DATA / "exmiembros.yaml", True),
        (DATA / "orcid.yaml", False),
    ]

    total = 0
    for ruta, crear in objetivos:
        if not ruta.exists():
            print(f"  (no existe {ruta.name}, se omite)")
            continue
        rellenados, ya, sin = rellenar(ruta, buscar, crear_campo=crear, simular=args.simular)
        total += len(rellenados)
        print(f"{ruta.name}: {len(rellenados)} rellenados, {len(ya)} ya tenían, "
              f"{len(sin)} sin candidato")
        for nombre, orcid in rellenados:
            print(f"    + {nombre:42s} {orcid}")

    if args.simular:
        print("\n(simulación: no se escribió nada)")
    else:
        print(f"\nTotal de campos rellenados: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
