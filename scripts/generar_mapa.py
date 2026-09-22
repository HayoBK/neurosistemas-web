#!/usr/bin/env python3
"""
Genera layouts/partials/mapa-mundo.html: las siluetas de los continentes del
mapa de /ex-miembros/, en un recorte "atlántico" (lon -135…60, lat -57…72),
proyección equirectangular con el eje vertical estirado ×1.15.

Fuente: countries.geo.json de https://github.com/johan/world.geo.json
(dominio público). Descargarlo junto a este script y correr:

    python3 scripts/generar_mapa.py countries.geo.json

Las mismas constantes de proyección viven en layouts/ex-miembros/list.html
($LON0, $SX, $LAT1, $SY): si se cambia el recorte, cambiar ambos.
"""
import json, math, sys

LON0, LON1, LAT0, LAT1 = -135, 60, -57, 72
W = 1000
SX = W / (LON1 - LON0)
SY = SX * 1.15
H = round((LAT1 - LAT0) * SY)


def proj(lon, lat):
    return ((lon - LON0) * SX, (LAT1 - lat) * SY)


def rdp(pts, eps):
    """Simplificación de Ramer-Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L if L else math.hypot(x - x1, y - y1)
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return rdp(pts[: idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def area(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2


def main(src, dst="layouts/partials/mapa-mundo.html"):
    g = json.load(open(src))
    paths = []
    for f in g["features"]:
        if f["id"] == "ATA":  # Antártida queda fuera del recorte
            continue
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "Polygon" else [p for mp in geom["coordinates"] for p in mp]
        for ring in polys:
            pts = [proj(lon, lat) for lon, lat in ring]
            if all(x < 0 or x > W or y < 0 or y > H for x, y in pts):
                continue
            if area(pts) < 6:
                continue
            s = rdp(pts, 1.2)
            if len(s) < 4:
                continue
            paths.append("M" + " ".join(f"{x:.0f},{y:.0f}" for x, y in s) + "z")
    svg = "".join(f'<path d="{d}"/>' for d in paths)
    out = f"""{{{{- /*
  Mapa mundial (recorte atlántico, lon {LON0}…{LON1}, lat {LAT0}…{LAT1}) en proyección
  equirectangular con el eje vertical estirado ×1.15. Generado desde
  world.geo.json (johan/world.geo.json, dominio público) por
  scripts/generar_mapa.py; no editar a mano.

  Proyección (misma que usa layouts/ex-miembros/list.html para los puntos):
    x = (lon - ({LON0})) * {SX:.4f}
    y = ({LAT1} - lat) * {SY:.4f}
  viewBox: 0 0 {W} {H}
*/ -}}}}
<g class="ns-mapa__tierra">{svg}</g>
"""
    open(dst, "w").write(out)
    print(f"{len(paths)} polígonos, {len(out)//1024} KB → {dst}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "countries.geo.json")
