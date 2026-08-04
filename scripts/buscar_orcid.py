#!/usr/bin/env python3
"""Busca en ORCID los iD que faltan y deja un informe para revisión humana.

Complementa a cosechar_orcid.py: lo que no estaba en el repo del Departamento
de Neurociencia se busca en la API pública de ORCID.

Criterio de auto-relleno, deliberadamente estricto: solo se escribe un iD
cuando la consulta acotada a la Universidad de Chile devuelve UN único
candidato. Todo lo demás queda en INFORME-ORCID.md con sus candidatos y una
columna para que Hayo marque el correcto. Aquí no se adivina.

Uso:
    .venv/bin/python scripts/buscar_orcid.py
    .venv/bin/python scripts/buscar_orcid.py --simular
"""

import argparse
import sys
import time
import unicodedata
from pathlib import Path

import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosechar_orcid import rellenar  # noqa: E402  (mismo paquete de scripts)

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
INFORME = RAIZ / "INFORME-ORCID.md"

API = "https://pub.orcid.org/v3.0/expanded-search/"
AFILIACION = "Universidad de Chile"
PAUSA = 0.4  # segundos entre consultas, para no castigar la API pública
FILAS = 20


def consultar(sesion, q):
    try:
        r = sesion.get(API, params={"q": q, "rows": FILAS}, timeout=25)
        r.raise_for_status()
        d = r.json()
    except (requests.RequestException, ValueError) as e:
        print(f"    ! error consultando ORCID: {e}")
        return None, []
    time.sleep(PAUSA)
    return d.get("num-found", 0), d.get("expanded-result") or []


def apellido_principal_calza(resultado, apellido):
    """¿El apellido buscado es el PRIMER apellido del perfil?

    Sin esto, buscar "Egaña" devuelve a "José Sebastián Monsalve Egaña" —donde
    Egaña es el segundo apellido— y como además comparte el nombre de pila y la
    afiliación, pasaba como candidato único. Ese perfil es de otra persona y
    metía publicaciones ajenas al listado.
    """
    perfil = sin_acentos(resultado.get("family-names") or "").lower()
    buscado = sin_acentos(apellido).lower()
    primero_perfil = perfil.replace("-", " ").split()
    primero_buscado = buscado.replace("-", " ").split()
    if not primero_perfil or not primero_buscado:
        return False
    return primero_perfil[0] == primero_buscado[0]


def candidato(r):
    return {
        "orcid": r.get("orcid-id", ""),
        "nombre": " ".join(x for x in (r.get("given-names"), r.get("family-names")) if x),
        "instituciones": r.get("institution-name") or [],
    }


def sin_acentos(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def variantes(texto):
    """El texto tal cual y, si tiene acentos, también sin ellos.

    El índice de ORCID no normaliza: buscar "Rocío" devuelve cero y "Rocio"
    devuelve el perfil correcto. Lo mismo pasa con "Iván" y "Egaña".
    """
    v = [texto]
    plano = sin_acentos(texto)
    if plano != texto:
        v.append(plano)
    return v


def buscar_persona(sesion, nombre, apellidos):
    """Devuelve (auto, candidatos).

    auto es el iD cuando la consulta acotada a la U. de Chile da exactamente
    un resultado; si no, None. candidatos es la lista para el informe.
    """
    pila = nombre.split()[0]
    pila_plano = sin_acentos(pila).lower()
    auto = None
    vistos, candidatos = set(), []

    def agregar(res, solo_chilenos=False, solo_misma_pila=False):
        for r in res:
            c = candidato(r)
            if c["orcid"] in vistos:
                continue
            if solo_chilenos and not any("chile" in i.lower() for i in c["instituciones"]):
                continue
            if solo_misma_pila:
                dado = sin_acentos(r.get("given-names") or "").lower()
                if not dado.startswith(pila_plano[:4]):
                    continue
            vistos.add(c["orcid"])
            candidatos.append(c)

    for apellido in apellidos:
        for ap in variantes(apellido):
            for pl in variantes(pila):
                # 1) Consulta acotada: apellido + nombre de pila + afiliación.
                q = (f'family-name:{ap} AND given-names:{pl} AND '
                     f'affiliation-org-name:"{AFILIACION}"')
                n, res = consultar(sesion, q)
                if (n == 1 and res and auto is None
                        and apellido_principal_calza(res[0], ap)):
                    auto = res[0].get("orcid-id")
                agregar(res)

            if auto:
                continue

            # 2) Solo apellido + afiliación, quedándose con quienes además
            #    tengan un nombre de pila compatible. Cubre los perfiles que
            #    escriben el nombre distinto (iniciales, nombre compuesto).
            _, res2 = consultar(sesion, f'family-name:{ap} AND affiliation-org-name:"{AFILIACION}"')
            agregar(res2, solo_misma_pila=True)

            # 3) Consulta abierta, solo para nutrir el informe.
            #    Si devuelve pocos resultados se listan todos aunque no
            #    declaren afiliación: mucha gente tiene el perfil creado y
            #    vacío, y descartarlos dejaba a la persona sin candidatos.
            #    Si devuelve muchos, solo los de afiliación chilena.
            for pl in variantes(pila):
                n3, res3 = consultar(sesion, f"family-name:{ap} AND given-names:{pl}")
                agregar(res3, solo_chilenos=(n3 or 0) > 3)

    # Último recurso: si no quedó ningún candidato, se listan los primeros
    # homónimos aunque no digan nada de Chile. No sirve para decidir solo,
    # pero le da a quien revise algo por dónde empezar en vez de una sección
    # vacía. En el informe van marcados como coincidencia solo por nombre.
    if not auto and not candidatos:
        for ap in variantes(apellidos[0]):
            for pl in variantes(pila):
                _, res = consultar(sesion, f"family-name:{ap} AND given-names:{pl}")
                agregar(res[:5])
            if candidatos:
                break

    return auto, candidatos


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def escribir_informe(filas, autocompletados, resueltos):
    t = time.localtime()
    hoy = f"{t.tm_mday} de {MESES[t.tm_mon - 1]} de {t.tm_year}"
    L = []
    L.append("# Informe de búsqueda de ORCID iD\n")
    L.append(f"Generado por `scripts/buscar_orcid.py` el {hoy}.\n")
    L.append(
        "\nEste archivo existe porque **la búsqueda automática no alcanza para "
        "decidir**. Se rellenó solo lo inequívoco; el resto necesita que alguien "
        "del laboratorio confirme cuál es el perfil correcto.\n"
    )
    L.append("\n## Cómo completarlo\n")
    L.append(
        "\n1. Revisa los candidatos de cada persona (el enlace abre su perfil ORCID).\n"
        "2. Marca con una `X` la columna **¿Es?** del que corresponda.\n"
        "3. Copia ese iD al campo `orcid` de `data/orcid.yaml` — es el que enciende\n"
        "   la sincronización diaria — y también al de `data/miembros.yaml`, que es\n"
        "   el que hace aparecer el botón ORCID en su ficha.\n"
        "4. Si la persona no tiene ORCID, o su perfil está en privado, déjalo vacío:\n"
        "   la API pública solo devuelve registros públicos y no se rompe nada.\n"
    )

    L.append("\n## Estado actual\n")
    L.append(f"\n{len(resueltos)} de {len(resueltos) + len(filas)} personas de "
             "`data/orcid.yaml` ya tienen su iD.\n\n")
    if resueltos:
        L.append("| Persona | ORCID iD |\n|---|---|\n")
        for nombre, orcid in resueltos:
            L.append(f"| {nombre} | [{orcid}](https://orcid.org/{orcid}) |\n")

    if autocompletados:
        L.append("\n### Rellenados en esta corrida\n")
        L.append("\nÚnico candidato con afiliación en la Universidad de Chile.\n\n")
        L.append("| Persona | ORCID iD | Afiliaciones declaradas |\n")
        L.append("|---|---|---|\n")
        for nombre, orcid, inst in autocompletados:
            L.append(f"| {nombre} | [{orcid}](https://orcid.org/{orcid}) | {inst} |\n")

    L.append("\n## Pendientes de confirmación\n")
    pendientes = [f for f in filas if not f["auto"]]
    if not pendientes:
        L.append("\nNinguno: todas las personas quedaron resueltas.\n")
    for f in pendientes:
        L.append(f"\n### {f['nombre']}\n\n")
        if not f["candidatos"]:
            L.append(
                "Sin candidatos con afiliación chilena en la API pública de ORCID. "
                "Puede que no tenga perfil, que esté en privado o que no haya "
                "declarado afiliación.\n"
            )
            continue
        L.append("| ¿Es? | ORCID iD | Nombre en ORCID | Afiliaciones declaradas |\n")
        L.append("|:---:|---|---|---|\n")
        for c in f["candidatos"]:
            inst = ", ".join(c["instituciones"]) or "—"
            L.append(
                f"|  | [{c['orcid']}](https://orcid.org/{c['orcid']}) | "
                f"{c['nombre']} | {inst} |\n"
            )

    INFORME.write_text("".join(L), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--simular", action="store_true", help="no escribe los YAML")
    args = ap.parse_args()

    cfg = yaml.safe_load((DATA / "orcid.yaml").read_text(encoding="utf-8"))
    personas = cfg.get("miembros") or []
    faltan = [p for p in personas if not (p.get("orcid") or "").strip()]

    print(f"Personas en data/orcid.yaml: {len(personas)}")
    print(f"Sin ORCID iD: {len(faltan)}\n")

    sesion = requests.Session()
    sesion.headers.update({
        "Accept": "application/json",
        "User-Agent": "neurosistemas-web/1.0 (https://neurosistemas.cl)",
    })

    filas, autocompletados, encontrados = [], [], {}
    for p in faltan:
        nombre = p.get("nombre", "")
        apellidos = p.get("apellidos") or [nombre.split()[-1]]
        print(f"  buscando {nombre} ({', '.join(apellidos)})…")
        auto, candidatos = buscar_persona(sesion, nombre, apellidos)
        filas.append({"nombre": nombre, "auto": auto, "candidatos": candidatos})
        if auto:
            inst = next((", ".join(c["instituciones"]) for c in candidatos
                         if c["orcid"] == auto), "")
            autocompletados.append((nombre, auto, inst))
            encontrados[nombre] = auto
            print(f"    -> {auto}")
        else:
            print(f"    -> sin decisión automática ({len(candidatos)} candidatos)")

    if encontrados and not args.simular:
        def buscar(nombre):
            return encontrados.get(nombre)

        for archivo in ("orcid.yaml", "miembros.yaml"):
            rell, ya, sin = rellenar(DATA / archivo, buscar)
            print(f"\n{archivo}: {len(rell)} rellenados")

    # Se relee el YAML para que el informe muestre el estado final, incluidos
    # los iD que trajo cosechar_orcid.py y los que se hayan escrito a mano.
    cfg = yaml.safe_load((DATA / "orcid.yaml").read_text(encoding="utf-8"))
    resueltos = [(p.get("nombre", ""), p["orcid"].strip())
                 for p in (cfg.get("miembros") or [])
                 if (p.get("orcid") or "").strip()]

    escribir_informe(filas, autocompletados, resueltos)
    print(f"\nInforme escrito en {INFORME.name}")
    print(f"Autocompletados: {len(autocompletados)} · "
          f"Pendientes: {len(filas) - len(autocompletados)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
