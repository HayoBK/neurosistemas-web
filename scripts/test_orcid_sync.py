# -*- coding: utf-8 -*-
"""Prueba de orcid_sync.py con respuestas simuladas (no toca la red).

Uso:  python scripts/test_orcid_sync.py
Deja data/orcid.yaml y data/publicaciones_orcid.json tal como estaban.
"""
import sys, os, json, io
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))

import yaml
# 1) Rellenar temporalmente dos ORCID iD de prueba
cfg_path = os.path.join(R, "data", "orcid.yaml")
backup = io.open(cfg_path, encoding="utf-8").read()
cfg = yaml.safe_load(backup)
cfg["miembros"][0]["orcid"] = "0000-0000-0000-0001"   # Maldonado
cfg["miembros"][1]["orcid"] = "0000-0000-0000-0002"   # Devia
io.open(cfg_path, "w", encoding="utf-8").write(yaml.dump(cfg, allow_unicode=True, sort_keys=False))

import orcid_sync

WORKS = {
 "0000-0000-0000-0001": {"group": [
   {"external-ids": {"external-id": [{"external-id-type": "doi", "external-id-value": "https://doi.org/10.1038/S41598-025-99999-9"}]},
    "work-summary": [{"title": {"title": {"value": "Active vision in freely moving observers"}},
                      "journal-title": {"value": "Scientific Reports"},
                      "publication-date": {"year": {"value": "2025"}}, "type": "journal-article"}]},
   # duplicado exacto, debe colapsar con el de Devia
   {"external-ids": {"external-id": [{"external-id-type": "doi", "external-id-value": "10.1016/j.mex.2024.102500"}]},
    "work-summary": [{"title": {"title": {"value": "A shared methods paper"}},
                      "journal-title": {"value": "MethodsX"},
                      "publication-date": {"year": {"value": "2024"}}, "type": "journal-article"}]},
   # ya está en el histórico -> debe descartarse
   {"external-ids": {"external-id": [{"external-id-type": "doi", "external-id-value": "10.1016/j.mex.2023.102041"}]},
    "work-summary": [{"title": {"title": {"value": "SaFiDe"}}, "journal-title": {"value": "MethodsX"},
                      "publication-date": {"year": {"value": "2023"}}, "type": "journal-article"}]},
   # anterior a anio_minimo -> descartar
   {"external-ids": {"external-id": [{"external-id-type": "doi", "external-id-value": "10.1111/ejn.15326"}]},
    "work-summary": [{"title": {"title": {"value": "Integrate and fire"}}, "journal-title": {"value": "EJN"},
                      "publication-date": {"year": {"value": "2021"}}, "type": "journal-article"}]},
   # tipo no aceptado -> descartar
   {"external-ids": {"external-id": []},
    "work-summary": [{"title": {"title": {"value": "Una charla"}}, "publication-date": {"year": {"value": "2025"}},
                      "type": "lecture-speech"}]},
   # sin DOI pero válido -> se conserva por título
   {"external-ids": {"external-id": []},
    "work-summary": [{"title": {"title": {"value": "Un capítulo sin DOI"}},
                      "journal-title": {"value": "Editorial X"},
                      "publication-date": {"year": {"value": "2025"}}, "type": "book-chapter"}]},
 ]},
 "0000-0000-0000-0002": {"group": [
   {"external-ids": {"external-id": [{"external-id-type": "doi", "external-id-value": "10.1016/J.MEX.2024.102500"}]},
    "work-summary": [{"title": {"title": {"value": "A shared methods paper"}},
                      "journal-title": {"value": "MethodsX"},
                      "publication-date": {"year": {"value": "2024"}}, "type": "journal-article"}]},
 ]},
}
CROSSREF = {
 "10.1038/s41598-025-99999-9": {"message": {
   "author": [{"family": "Devia", "given": "Christ"}, {"family": "Pérez", "given": "Ana María"},
              {"family": "Maldonado", "given": "Pedro E."}],
   "container-title": ["Scientific Reports"], "volume": "15", "page": "1234",
   "issued": {"date-parts": [[2025, 4, 2]]}, "title": ["Active vision in freely moving observers"]}},
 "10.1016/j.mex.2024.102500": {"message": {
   "author": [{"family": "Madariaga", "given": "Samuel"}, {"family": "Babul", "given": "Cecilia"}],
   "container-title": ["MethodsX"], "volume": "12", "page": "102500",
   "issued": {"date-parts": [[2024]]}, "title": ["A shared methods paper"]}},
}

def pedir_falso(s, url, intentos=3, espera=2.0):
    if url.startswith(orcid_sync.ORCID_API):
        return WORKS.get(url.split("/")[-2])
    if url.startswith(orcid_sync.CROSSREF_API):
        return CROSSREF.get(url.split("works/")[-1])
    return None

orcid_sync.pedir = pedir_falso
orcid_sync.PAUSA = 0
rc = orcid_sync.main()

# Restaurar orcid.yaml original
io.open(cfg_path, "w", encoding="utf-8").write(backup)

print("\n--- JSON generado ---")
doc = json.load(io.open(os.path.join(R, "data", "publicaciones_orcid.json"), encoding="utf-8"))
print(json.dumps(doc, ensure_ascii=False, indent=2)[:2200])

pubs = doc["publicaciones"]
ok = True
def chk(cond, msg):
    global ok
    print(("  ✓ " if cond else "  ✗ ") + msg); ok = ok and cond

print("\n--- Aserciones ---")
chk(len(pubs) == 3, f"3 publicaciones tras filtrar y deduplicar (obtuve {len(pubs)})")
chk(all(p["anio"] >= 2023 for p in pubs), "ninguna anterior a anio_minimo")
chk(not any("safide" in p["titulo"].lower() for p in pubs), "descarta lo que ya está en el histórico")
chk(not any("charla" in p["titulo"].lower() for p in pubs), "descarta tipos no aceptados")
compartida = [p for p in pubs if "shared" in p["titulo"].lower()]
chk(len(compartida) == 1, "el DOI compartido aparece una sola vez")
chk(len(compartida[0]["miembros"]) == 2, f"acredita a los 2 miembros ({compartida[0]['miembros']})")
sr = [p for p in pubs if "Active vision" in p["titulo"]][0]
chk("<b>Devia, C.</b>" in sr["autores"] and "<b>Maldonado, P. E.</b>" in sr["autores"],
    "resalta en negrita a los miembros del lab")
chk("Pérez, A. M." in sr["autores"] and "<b>Pérez" not in sr["autores"], "no resalta a autores externos")
chk(sr["revista"] == "Scientific Reports, 15, 1234", f"revista con volumen y páginas: {sr['revista']}")
chk(sr["doi"] == "10.1038/s41598-025-99999-9", "DOI normalizado a minúsculas y sin prefijo URL")
chk(pubs[0]["anio"] >= pubs[-1]["anio"], "ordenado por año descendente")
chk(doc["actualizado"] != "", "registra la fecha de actualización")

# Prueba de resiliencia: ORCID caído -> conserva el JSON anterior
print("\n--- Resiliencia (ORCID caído) ---")
antes = io.open(os.path.join(R, "data", "publicaciones_orcid.json"), encoding="utf-8").read()
cfg["miembros"][0]["orcid"] = "0000-0000-0000-0001"
cfg["miembros"][1]["orcid"] = ""
io.open(cfg_path, "w", encoding="utf-8").write(yaml.dump(cfg, allow_unicode=True, sort_keys=False))
orcid_sync.pedir = lambda *a, **k: None
orcid_sync.main()
despues = io.open(os.path.join(R, "data", "publicaciones_orcid.json"), encoding="utf-8").read()
io.open(cfg_path, "w", encoding="utf-8").write(backup)
chk(antes == despues, "con ORCID caído no borra el JSON existente")

# Dejar el JSON semilla limpio
io.open(os.path.join(R, "data", "publicaciones_orcid.json"), "w", encoding="utf-8").write(
    '{\n  "actualizado": "",\n  "fuentes": [],\n  "publicaciones": []\n}\n')
print("\nJSON restaurado a la semilla vacía.")
print("\nRESULTADO:", "TODO OK" if ok else "HAY FALLAS")
sys.exit(0 if ok else 1)
