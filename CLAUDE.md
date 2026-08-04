# CLAUDE.md — Sitio web del Laboratorio de Neurosistemas

Contexto y reglas para trabajar en este repositorio con Claude.
Propietario técnico: **Hayo Breinbauer** (otoneurólogo, dev Python). Idioma de trabajo: **español**.

---

## Qué es este repo
Sitio del **Laboratorio de Neurosistemas** — Facultad de Medicina, Universidad de Chile.
Reemplaza el WordPress de `https://www.neurosistemas.cl` (Elementor + qTranslate-X, lento y
con mantención pendiente).

Objetivo del sitio, en orden de importancia:
1. **Mostrar quiénes somos** (equipo, líneas de investigación).
2. **Contacto fácil** (sin formulario: correo, teléfono, dirección, mapa).
3. **Publicaciones siempre al día y bien presentadas**, con actualización automática desde ORCID.

Es un sitio deliberadamente **menos ambicioso** que LAB ONCE o el del Departamento de
Neurociencia: pocas páginas, cero fricción de mantención.

## Stack (idéntico a LAB ONCE, distinto a Neurociencia)
- **Hugo extended 0.162.1**, sitio **AUTOCONTENIDO**: sin Hugo Blox, sin módulos Go, sin
  Tailwind, sin npm/pnpm. Todas las plantillas están en `layouts/` y el CSS en
  `static/css/neurosistemas.css`.
- **GitHub Pages** vía GitHub Actions (`.github/workflows/deploy.yml`).
- **Pages CMS** (`.pages.yml`) para edición sin código.
- Cuenta de GitHub: **HayoBK** (hayo.bk@gmail.com). Ver `GUIA-DEPLOY-NEUROSISTEMAS.md`.

## baseURL y rutas (clave)
- `config/_default/hugo.yaml` tiene un placeholder: `https://hayobk.github.io/neurosistemas-web/`.
- En **producción no importa**: el workflow hace
  `hugo --baseURL "${{ steps.pages.outputs.base_url }}/"`.
- Por eso TODAS las rutas internas usan `relURL` / `.RelPermalink` / `pageRef`, nunca un path
  absoluto hardcodeado. Imágenes: `"images/x.jpg" | relURL` (sin slash inicial).

## Reglas de oro
1. **Valida el build antes de commitear:** `HUGO_ENVIRONMENT=production hugo --minify`.
   Sin `ERROR` = verde.
2. **CMS-safe:** lo editable vive en `data/*.yaml` o front-matter. Las plantillas toleran
   campos vacíos o ausentes (`with`, `default`).
3. **CSS propio:** un único archivo `static/css/neurosistemas.css`, clases prefijadas `ns-`.
   Variables en `:root` con prefijo `--ns-`.
4. **YAML:** escalares con `: `, `#` o `@` → entre comillas dobles.
5. **Nunca editar a mano** `data/publicaciones_orcid.json`: lo escribe el bot.
6. Commits chicos y claros, en español.

## Estética — "papel de laboratorio + espectro"
Limpio, científico y profesional: lienzo blanco, tinta negra, mucho aire y tipografía
fuerte, coloreado con la paleta del logo. La regla que ordena todo: **el color es
información, no decoración**. Nada de fondos de color grandes, degradados ni sombras.
- **Espectro (muestreado del logo):** rojo `#B12313`, naranja `#C65A16`, ámbar `#C98510`,
  lima `#6E9A1B`, verde `#2F8F5B`, cian `#2E9DBC`, azul `#2186B7`, morado `#762D60`,
  magenta `#9A2A53`.
- **Neutros:** tinta `#101214`, texto `#24282B`, suave `#5B6166`, tenue `#8A9298`,
  línea `#E3E6E8`, fondo `#FFFFFF`, fondo2 `#F6F8F9`.
- **Contraste:** como color de TEXTO sobre blanco solo sirven rojo, azul, morado, magenta
  y verde. Ámbar y lima van siempre como trazo o relleno con texto negro encima.
- **Tipografías:** Archivo 600/700 (títulos), Inter 400/500/600 (cuerpo, base 17 px),
  IBM Plex Mono 400/500 (rótulos, años, DOIs; 11–12 px, `letter-spacing:.08em`, mayúsculas).
- **Forma:** radio 4 px en controles y chips, 6 px en tarjetas. Bordes `1px solid --ns-linea`.
  Sin `box-shadow` (salvo el anillo de foco), sin `backdrop-filter`, sin `translateY` en hover:
  el hover solo cambia color de borde y de acento.
- **Motivos:** la **franja espectral** de 4 px con los 9 tonos en bandas iguales (bajo el
  header y al inicio del pie — el único color a ancho completo), y el **divisor EEG**
  (`partials/eeg.html`, hairline al 18 %, entre secciones del Home).

### Cómo se aplica el color
`data/colores.yaml` mapea qué tono le toca a cada área, grupo, sección y cifra. El CSS
es estático y no puede leerlo, así que las plantillas inyectan `style="--ns-acento:#XXX"`
en cada bloque y el CSS usa `var(--ns-acento)`. El partial `color.html` resuelve el hex y
cae en un tono de reserva si la clave no está, para que nada quede sin color al renombrar
algo desde el CMS.

## Arquitectura
- `layouts/_default/baseof.html` → esqueleto.
- `partials/`: `head.html`, `header.html` (navbar con dropdowns desde `menus.yaml`),
  `footer.html`, `scripts.html`, `encabezado.html`, `persona.html`, `publicacion.html`,
  `color.html` (resuelve el acento desde `colores.yaml`), `eeg.html` (divisor de sección),
  `iniciales.html` (primer nombre + último apellido, saltando partículas).
- `layouts/index.html` → Home: hero + quiénes somos + 3 líneas + publicaciones recientes +
  líderes + noticias + financiamiento.
- Secciones: `investigacion/`, `publicaciones/`, `miembros/`, `visitantes/`, `ex-miembros/`,
  `noticias/`, `galeria/`, `contacto/` — cada una con su `list.html`.
- **Datos:** `data/lineas.yaml`, `miembros.yaml`, `visitantes.yaml`, `exmiembros.yaml`,
  `financiamiento.yaml`, `galeria.yaml`, `colores.yaml` (paleta y asignación),
  `publicaciones_historicas.yaml` (curado, 1988–2023), `orcid.yaml` (configuración) y
  `publicaciones_orcid.json` (generado).

## Publicaciones: cómo funciona la fusión
La página `/publicaciones/` concatena **dos fuentes** y agrupa por año:
1. `data/publicaciones_orcid.json` → automático, escrito por `scripts/orcid_sync.py`.
2. `data/publicaciones_historicas.yaml` → archivo curado a mano, no se toca.

El partial `publicacion.html` distingue ambos formatos: si la entrada trae `cita`, la
renderiza tal cual (histórico); si trae `titulo` + `autores`, la arma por campos (ORCID).

`scripts/orcid_sync.py` corre a diario en `.github/workflows/orcid.yml`:
consulta la API pública de ORCID por cada iD de `data/orcid.yaml`, deduplica por DOI, descarta
lo que ya está en el histórico y lo anterior a `anio_minimo`, y enriquece con Crossref
(autores completos, revista, páginas). Si ORCID o Crossref fallan, **conserva el JSON
anterior** y sale con código 0.

**Pendiente crítico:** `data/orcid.yaml` está con los ORCID iD en blanco. Hasta que se
completen, el sitio muestra solo el archivo histórico.

## Modo de trabajo — MODO DUAL
- **El chat (Cowork)** = cerebro: planifica, investiga, edita archivos, diseña. No corre
  hugo ni git.
- **Claude Code (terminal sobre `~/Git_Web/Neurosistemas`)** = manos: corre hugo y git,
  valida el build, hace commits y push.
- Recomendación por defecto para Claude Code: **Sonnet**; **Opus** solo si el razonamiento
  es delicado.

## Pendientes
Ver `CONTINUACION-NEUROSISTEMAS.md`.
