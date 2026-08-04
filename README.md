# Laboratorio de Neurosistemas — sitio web

Sitio estático del Laboratorio de Neurosistemas, Facultad de Medicina,
Universidad de Chile. Reemplaza el antiguo WordPress de neurosistemas.cl.

- **Generador:** Hugo extended 0.162.1 (autocontenido, sin npm ni módulos Go)
- **Hosting:** GitHub Pages vía GitHub Actions
- **Edición sin código:** [Pages CMS](https://pagescms.org) (`.pages.yml`)
- **Publicaciones:** sincronizadas a diario desde ORCID + archivo histórico curado

## Desarrollo local

```bash
hugo server -D           # http://localhost:1313
```

## Build de producción

```bash
HUGO_ENVIRONMENT=production hugo --minify
```

## Sincronizar publicaciones a mano

```bash
pip install requests PyYAML
python scripts/orcid_sync.py
```

## Estructura

```
config/_default/   hugo.yaml · menus.yaml · params.yaml
content/           una carpeta por sección, con _index.md
data/              contenido editable (equipo, líneas, publicaciones)
layouts/           plantillas propias (nada de temas externos)
scripts/           orcid_sync.py
static/            css/neurosistemas.css · images/
```

Documentación completa en `CLAUDE.md` y `GUIA-DEPLOY-NEUROSISTEMAS.md`.
