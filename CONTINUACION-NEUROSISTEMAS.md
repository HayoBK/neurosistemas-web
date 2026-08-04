# Continuación — Laboratorio de Neurosistemas

Estado del repo y qué falta. Actualizar este archivo al cerrar cada sesión.

**Última actualización:** 4 de agosto de 2026

---

## Estado actual

Sitio compilado, rediseñado y publicado. En la sesión del 4 de agosto de 2026 se
hizo la primera compilación real (el repo venía de Cowork, que no tiene Hugo),
se descartó la estética original, se prepararon los derivados del logo, se
cosecharon los ORCID iD y se rescataron las imágenes del WordPress antiguo.

### Qué está listo

| Área | Estado |
|---|---|
| Esqueleto Hugo autocontenido | ✅ |
| Build de producción sin errores ni warnings | ✅ |
| CSS propio (`ns-`, estética "papel de laboratorio + espectro") | ✅ |
| Franja espectral + divisor EEG | ✅ |
| Asignación de color desde `data/colores.yaml` | ✅ |
| Navegación con submenús + menú móvil | ✅ |
| Home (hero con logo, cifras, líneas, publicaciones, equipo, noticias, financiamiento) | ✅ |
| Líneas de investigación (3 áreas, 12 proyectos) | ✅ |
| Publicaciones: 94 entradas (79 históricas + 15 de ORCID), dos columnas con año pegajoso | ✅ |
| Equipo: 26 miembros actuales en 5 grupos, 20 con foto | ✅ |
| Ex miembros: 51 personas con buscador | ✅ |
| Visitantes: 8 personas, todas con foto | ✅ |
| Noticias (con una nota de estreno) + RSS | ✅ |
| Galería: 3 fotos del laboratorio | ✅ |
| Contacto: correo, teléfono, dirección, mapa OSM, mailto | ⚠️ datos sin confirmar |
| Logo: PNG transparente, isotipo, favicon, imagen Open Graph | ✅ |
| ORCID: 6 de 11 iD cosechados + sincronización corriendo | ⚠️ faltan 5 |
| Pages CMS (`.pages.yml`) | ✅ |
| Workflow de deploy a GitHub Pages | ✅ |
| Página 404 | ✅ |

### Scripts nuevos (todos con `--simular` salvo el del logo)

| Script | Para qué |
|---|---|
| `scripts/preparar_logo.py` | Genera PNG transparente, isotipo, favicon y OG desde el JPG original |
| `scripts/eeg_path.py` | Genera el trazo del divisor EEG (semilla fija) |
| `scripts/cosechar_orcid.py` | Trae ORCID iD desde el repo del Departamento de Neurociencia |
| `scripts/buscar_orcid.py` | Busca los que faltan en la API de ORCID y escribe `INFORME-ORCID.md` |
| `scripts/rescatar_imagenes.py` | Baja fotos de equipo y galería del WordPress antiguo |

Necesitan `.venv` (está en `.gitignore`):
`python3 -m venv .venv && .venv/bin/pip install pillow requests PyYAML numpy`

---

## Pendientes, por prioridad

### 1. ORCID iD — faltan 5 (es lo que completa la actualización automática)
Ver **`INFORME-ORCID.md`**, que trae los candidatos con enlace a cada perfil.
- [ ] Confirmar el candidato único de **Samuel Madariaga**, **Ismael Jaras** y
      **Carolina Lindsay**: hay exactamente uno plausible para cada uno.
- [ ] **Karla Padilla**: 5 homónimos, ninguno declara afiliación. Preguntarle.
- [ ] **Cecilia Babul**: no aparece en la API pública. Puede no tener perfil.
- [ ] Al confirmarlos, copiar el iD a `data/orcid.yaml` **y** a `data/miembros.yaml`.
- [ ] Verificar que sus registros ORCID estén en **visibilidad pública**: la API
      solo devuelve lo público.
- [ ] Revisar `anio_minimo: 2023` en `data/orcid.yaml`. Está así para que ORCID no
      duplique el archivo histórico. Si se quiere que ORCID reemplace por completo
      al histórico, bajarlo y limpiar `publicaciones_historicas.yaml`.

> **Cuidado al asignar un ORCID a mano.** Buscar por apellido devuelve homónimos y
> también a gente que lo lleva como *segundo* apellido. Pasó con José Ignacio
> Egaña: el primer candidato era un investigador de relaciones internacionales y
> metió publicaciones ajenas al listado. Conviene abrir el perfil y mirar que sus
> obras y su afiliación calcen antes de escribir el iD.

### 2. Imágenes — faltan 6 personas
- [ ] Sin foto: **Simón San Martín, Rodrigo González, Antonia Haberle, Ricardo
      Mendoza, Sofía Onetti y Sofía Berndt.** No hay imagen suya en el WordPress
      antiguo. Mientras tanto se muestran sus iniciales sobre el color de su
      grupo, que se ve bien y no está roto.
      Formato: cuadrado 400×400 px, JPG, en `static/images/equipo/`, y el nombre
      del archivo en el campo `foto` de `data/miembros.yaml`.
- [ ] **Galería:** hay 3 fotos. La biblioteca del WordPress tiene ~713 archivos
      más, con fotos de laboratorio de 2013–2017 sin curar. Para sumar alguna,
      agregar su nombre a `GALERIA_ARCHIVOS` en `scripts/rescatar_imagenes.py` y
      volver a correrlo. **Hacerlo antes de dar de baja el WordPress.**
- [ ] **Logo:** el original es un JPG de 553×230, así que el wordmark negro no
      sirve sobre fondos oscuros y el favicon no se lee a 16 px. Si aparece el
      archivo vectorial, conviene rehacer los derivados con
      `scripts/preparar_logo.py`.

### 3. Datos de contacto (verificar cuanto antes)
En `config/_default/params.yaml` quedaron valores **provisorios**, porque el sitio
antiguo solo tenía un formulario sin datos visibles:
- [ ] `email` → hoy `neurosistemas@med.uchile.cl`. **Confirmar.**
- [ ] `telefono` → hoy `+56 2 2978 6034`. **Confirmar.**
- [ ] `direccion` y coordenadas del mapa (`mapa` y el `bbox` del iframe en
      `layouts/contacto/list.html`). Hoy apuntan a Independencia 1027.

### 4. Decisiones abiertas
- [ ] **Bilingüe.** El WordPress tenía español/inglés vía qTranslate-X, con las
      traducciones bastante incompletas. El sitio nuevo es solo español. Si se
      quiere inglés, Hugo lo hace nativo con `config/_default/languages.yaml` y
      archivos `*.en.md` — es una tarea de una sesión, más el costo de traducir.
- [ ] **Publicación duplicada.** El listado del WordPress tenía dos veces la misma
      referencia de 2023 (Plaza-Rosales et al., *Front. Aging Neurosci.*). En el sitio
      nuevo quedó una sola vez, a propósito.
- [ ] **Iván Plaza** aparece en el sitio viejo como "Líder de grupo" pero no está
      mencionado en el texto de bienvenida original. Aquí sí se lo incluyó en la
      bienvenida. Confirmar con el laboratorio.
- [ ] Revisar si hay miembros nuevos o salidas desde 2023: los datos del sitio
      viejo son de esa fecha.
- [ ] **Ritmo del Home.** Quedó casi todo blanco, con el divisor EEG separando
      secciones en vez de alternar fondos grises. Es más fiel al "mucho aire" del
      concepto; si se prefiere más contraste, se alterna agregando
      `ns-seccion--alt` a las secciones de `layouts/index.html`.
- [ ] **Fotos de ex miembros.** El WordPress tiene 46 retratos de ex miembros que
      no se bajaron, porque su plantilla los muestra como filas compactas con
      iniciales. Si alguna vez se quieren, hay que rescatarlos antes de dar de
      baja el sitio antiguo.

---

## Notas de diseño (para no romper la coherencia)

- Todo el CSS vive en `static/css/neurosistemas.css`, clases `ns-`, variables `--ns-`.
- Concepto: **"papel de laboratorio + espectro"**. Lienzo blanco, tinta negra, mucho
  aire, y los 9 tonos del logo en dosis pequeñas. La regla es que **el color es
  información, no decoración**: siempre significa qué área, qué grupo o qué sección.
  Nada de fondos de color grandes, degradados ni sombras.
- El color no se escribe en el CSS ni en las plantillas: vive en `data/colores.yaml`.
  Las plantillas lo resuelven con `partials/color.html` y lo inyectan como
  `style="--ns-acento:#XXX"`. Para cambiar la asignación, editar solo ese YAML.
- Dos motivos recurrentes y nada más: la **franja espectral** de 4 px (bajo el header y
  al inicio del pie, único color a ancho completo) y el **divisor EEG**
  (`partials/eeg.html`). El path del EEG es fijo, lo genera `scripts/eeg_path.py` con
  semilla fija; si se quiere otra forma, correr el script y pegar la salida.
- Contraste: como color de texto sobre blanco solo sirven rojo, azul, morado, magenta y
  verde. Ámbar y lima van como trazo o como relleno con texto negro encima.
- Formas: radio 4 px en controles, 6 px en tarjetas; bordes hairline; sin `box-shadow`
  salvo el anillo de foco; el hover solo cambia color de borde y de acento.
- Las tres estéticas de la familia de sitios: LAB ONCE = navy/aqua vestibular;
  Neurociencia UChile = institucional; Neurosistemas = papel de laboratorio blanco con
  el espectro del logo. No cruzarlas.
- **Descartado (agosto 2026):** la estética previa "mapa de fijaciones" (papel cálido
  `#FCF8F2`, coral/cobalto, textura `.ns-puntos` y scanpath animado en canvas en el
  hero). No reintroducir esos motivos.
