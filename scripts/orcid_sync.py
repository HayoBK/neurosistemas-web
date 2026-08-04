#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronizador de publicaciones ORCID → data/publicaciones_orcid.json
Laboratorio de Neurosistemas — Facultad de Medicina, Universidad de Chile.

Qué hace
--------
1. Lee data/orcid.yaml y toma los ORCID iD de los miembros del laboratorio.
2. Consulta la API pública de ORCID (no requiere credenciales) y arma la
   lista de trabajos públicos de cada perfil.
3. Deduplica por DOI y, si no hay DOI, por título normalizado.
4. Descarta lo que ya está en data/publicaciones_historicas.yaml y lo
   anterior a `anio_minimo`, para no duplicar el archivo curado.
5. Opcionalmente enriquece cada entrada con Crossref (autores completos,
   revista, volumen y páginas).
6. Escribe data/publicaciones_orcid.json.

Diseño defensivo: si ORCID o Crossref fallan, el script conserva el JSON
anterior en vez de dejar el sitio sin publicaciones, y termina con código 0
para no marcar el workflow en rojo por una caída externa.

Uso local:
    pip install requests PyYAML
    python scripts/orcid_sync.py
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import time
import unicodedata

try:
    import requests
    import yaml
except ImportError:  # pragma: no cover
    print("Faltan dependencias. Instala con:  pip install requests PyYAML")
    sys.exit(1)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(RAIZ, "data", "orcid.yaml")
HIST = os.path.join(RAIZ, "data", "publicaciones_historicas.yaml")
SALIDA = os.path.join(RAIZ, "data", "publicaciones_orcid.json")

ORCID_API = "https://pub.orcid.org/v3.0"
CROSSREF_API = "https://api.crossref.org/works"
PAUSA = 0.12  # segundos entre llamadas, para ser buenos ciudadanos


# ---------------------------------------------------------------- utilidades
def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes y sin puntuación: para comparar títulos."""
    if not texto:
        return ""
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9]+", " ", texto.lower())
    return texto.strip()


def limpiar_doi(doi: str) -> str:
    """Deja solo el identificador: 10.xxxx/yyyy."""
    if not doi:
        return ""
    doi = doi.strip().lower()
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi.strip().rstrip(".")


def escapar(texto: str) -> str:
    return (texto or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def leer_yaml(ruta: str, por_defecto):
    try:
        with open(ruta, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or por_defecto
    except FileNotFoundError:
        return por_defecto


def sesion_http(correo: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Accept": "application/json",
        "User-Agent": f"neurosistemas-web/1.0 (https://neurosistemas.cl; mailto:{correo})",
    })
    return s


def pedir(s: requests.Session, url: str, intentos: int = 3, espera: float = 2.0):
    """GET con reintentos. Devuelve dict o None."""
    for n in range(intentos):
        try:
            r = s.get(url, timeout=25)
            if r.status_code == 404:
                return None
            if r.status_code == 429:
                time.sleep(espera * (n + 2))
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            if n == intentos - 1:
                print(f"   ! no se pudo leer {url}  ({e})")
                return None
            time.sleep(espera * (n + 1))
    return None


# ------------------------------------------------------------------- ORCID
def trabajos_de(s: requests.Session, orcid: str) -> list[dict]:
    """Resúmenes de trabajos públicos de un perfil ORCID."""
    datos = pedir(s, f"{ORCID_API}/{orcid}/works")
    if not datos:
        return []
    salida = []
    for grupo in datos.get("group", []):
        resumenes = grupo.get("work-summary") or []
        if not resumenes:
            continue
        w = resumenes[0]

        titulo = (((w.get("title") or {}).get("title") or {}).get("value") or "").strip()
        if not titulo:
            continue

        revista = ((w.get("journal-title") or {}) or {}).get("value") or ""
        tipo = (w.get("type") or "").lower()

        anio = None
        fecha = w.get("publication-date") or {}
        if fecha and fecha.get("year"):
            try:
                anio = int(fecha["year"]["value"])
            except (KeyError, TypeError, ValueError):
                anio = None

        doi = ""
        url = ""
        for eid in ((grupo.get("external-ids") or {}).get("external-id") or []):
            clase = (eid.get("external-id-type") or "").lower()
            valor = eid.get("external-id-value") or ""
            if clase == "doi" and not doi:
                doi = limpiar_doi(valor)
            elif clase in ("uri", "handle") and not url:
                url = valor
        if not url:
            url = ((w.get("url") or {}) or {}).get("value") or ""

        salida.append({
            "titulo": titulo,
            "revista": revista.strip(),
            "anio": anio,
            "doi": doi,
            "url": url,
            "tipo": tipo,
        })
    return salida


# ---------------------------------------------------------------- Crossref
def enriquecer(s: requests.Session, doi: str) -> dict | None:
    datos = pedir(s, f"{CROSSREF_API}/{doi}")
    if not datos:
        return None
    m = datos.get("message") or {}

    autores = []
    for a in (m.get("author") or [])[:22]:
        apellido = (a.get("family") or "").strip()
        nombre = (a.get("given") or "").strip()
        if not apellido:
            apellido = (a.get("name") or "").strip()
        if not apellido:
            continue
        iniciales = " ".join(p[0].upper() + "." for p in re.split(r"[\s\-]+", nombre) if p)
        autores.append(f"{apellido}, {iniciales}".strip().rstrip(","))
    if len(m.get("author") or []) > 22:
        autores.append("et al.")

    contenedor = (m.get("container-title") or [""])[0]
    volumen = m.get("volume") or ""
    paginas = m.get("page") or ""
    revista = contenedor
    if volumen:
        revista = f"{revista}, {volumen}"
    if paginas:
        revista = f"{revista}, {paginas}"

    anio = None
    for clave in ("published-print", "published-online", "issued", "created"):
        partes = ((m.get(clave) or {}).get("date-parts") or [[None]])[0]
        if partes and partes[0]:
            anio = int(partes[0])
            break

    return {
        "autores": autores,
        "revista": revista.strip(", "),
        "anio": anio,
        "titulo": (m.get("title") or [""])[0],
    }


def resaltar(autores: list[str], apellidos_lab: set[str]) -> str:
    """Pone en negrita a los autores que son miembros del laboratorio."""
    if not autores:
        return ""
    partes = []
    for a in autores:
        apellido = normalizar(a.split(",")[0])
        if apellido and apellido in apellidos_lab:
            partes.append(f"<b>{escapar(a)}</b>")
        else:
            partes.append(escapar(a))
    if len(partes) > 1:
        return ", ".join(partes[:-1]) + " &amp; " + partes[-1]
    return partes[0]


# --------------------------------------------------------------------- main
def main() -> int:
    cfg = leer_yaml(CFG, {})
    miembros = cfg.get("miembros") or []
    op = cfg.get("opciones") or {}
    anio_minimo = int(op.get("anio_minimo") or 0)
    usar_crossref = bool(op.get("usar_crossref", True))
    correo = op.get("correo_contacto") or "webmaster@neurosistemas.cl"
    tipos_ok = {t.lower() for t in (op.get("tipos_aceptados") or [])}

    con_id = [m for m in miembros if (m.get("orcid") or "").strip()]
    if not con_id:
        print("No hay ningún ORCID iD configurado en data/orcid.yaml.")
        print("El sitio seguirá mostrando solo el archivo histórico curado.")
        return 0

    # Apellidos del laboratorio, para resaltar
    apellidos_lab = set()
    for m in miembros:
        for ap in (m.get("apellidos") or []):
            apellidos_lab.add(normalizar(ap))

    # DOIs y títulos que ya están en el archivo curado
    historicas = leer_yaml(HIST, []) or []
    dois_hist = {limpiar_doi(p.get("doi", "")) for p in historicas if p.get("doi")}
    titulos_hist = {normalizar(p.get("cita", "")[:90]) for p in historicas}

    s = sesion_http(correo)
    por_doi: dict[str, dict] = {}
    por_titulo: dict[str, dict] = {}
    fuentes = []

    for m in con_id:
        orcid = m["orcid"].strip()
        nombre = m.get("nombre") or orcid
        print(f"→ {nombre}  ({orcid})")
        trabajos = trabajos_de(s, orcid)
        print(f"   {len(trabajos)} trabajos públicos")
        fuentes.append({"nombre": nombre, "orcid": orcid, "trabajos": len(trabajos)})
        time.sleep(PAUSA)

        for t in trabajos:
            if tipos_ok and t["tipo"] and t["tipo"] not in tipos_ok:
                continue
            if t["anio"] and anio_minimo and t["anio"] < anio_minimo:
                continue

            doi = t["doi"]
            if doi and doi in dois_hist:
                continue

            clave_t = normalizar(t["titulo"])
            if any(clave_t and clave_t[:60] in h for h in titulos_hist):
                continue

            destino = por_doi if doi else por_titulo
            clave = doi or clave_t
            if not clave:
                continue
            if clave in destino:
                destino[clave].setdefault("miembros", [])
                if nombre not in destino[clave]["miembros"]:
                    destino[clave]["miembros"].append(nombre)
                continue
            t = dict(t)
            t["miembros"] = [nombre]
            destino[clave] = t

    entradas = list(por_doi.values()) + list(por_titulo.values())

    # Segunda pasada, por título. La deduplicación de arriba es por DOI, así
    # que un mismo trabajo entra dos veces cuando el preprint y la versión
    # publicada tienen DOI distinto. Se conserva la entrada del año más
    # reciente —la versión final— y se juntan los miembros de ambas.
    unicas: dict[str, dict] = {}
    sin_titulo = []
    for e in entradas:
        clave = normalizar(e.get("titulo", ""))[:80]
        if not clave:
            sin_titulo.append(e)
            continue
        previa = unicas.get(clave)
        if previa is None:
            unicas[clave] = e
            continue
        nueva, vieja = ((e, previa) if (e.get("anio") or 0) > (previa.get("anio") or 0)
                        else (previa, e))
        miembros = list(nueva.get("miembros") or [])
        for m in vieja.get("miembros") or []:
            if m not in miembros:
                miembros.append(m)
        nueva = dict(nueva)
        nueva["miembros"] = miembros
        unicas[clave] = nueva
        print(f"   · fusionadas dos versiones de: {nueva['titulo'][:60]}…")

    entradas = list(unicas.values()) + sin_titulo
    print(f"\n{len(entradas)} publicaciones únicas tras deduplicar.")

    # Enriquecimiento vía Crossref
    if usar_crossref:
        for i, e in enumerate(entradas, 1):
            if not e.get("doi"):
                continue
            extra = enriquecer(s, e["doi"])
            time.sleep(PAUSA)
            if not extra:
                continue
            if extra.get("revista"):
                e["revista"] = extra["revista"]
            if extra.get("anio") and not e.get("anio"):
                e["anio"] = extra["anio"]
            if extra.get("titulo"):
                e["titulo"] = extra["titulo"]
            e["autores"] = resaltar(extra.get("autores") or [], apellidos_lab)
            if i % 20 == 0:
                print(f"   Crossref: {i}/{len(entradas)}")

    # Limpieza final
    salida = []
    for e in entradas:
        if not e.get("anio"):
            continue
        salida.append({
            "anio": int(e["anio"]),
            "titulo": e.get("titulo", "").strip(),
            "autores": e.get("autores", ""),
            "revista": e.get("revista", ""),
            "doi": e.get("doi", ""),
            "url": e.get("url", "") if not e.get("doi") else "",
            "tipo": e.get("tipo", ""),
            "miembros": e.get("miembros", []),
            "fuente": "orcid",
        })
    salida.sort(key=lambda x: (-x["anio"], normalizar(x["titulo"])))

    if not salida:
        print("ORCID no devolvió publicaciones nuevas. Se conserva el JSON anterior.")
        return 0

    documento = {
        "actualizado": dt.date.today().isoformat(),
        "fuentes": fuentes,
        "publicaciones": salida,
    }
    with open(SALIDA, "w", encoding="utf-8") as fh:
        json.dump(documento, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"✓ Escrito {os.path.relpath(SALIDA, RAIZ)} con {len(salida)} publicaciones.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as err:  # noqa: BLE001
        print(f"Error inesperado: {err}")
        print("Se conserva data/publicaciones_orcid.json sin cambios.")
        sys.exit(0)
