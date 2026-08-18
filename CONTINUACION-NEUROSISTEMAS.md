# Continuación — Laboratorio de Neurosistemas

Estado del repo y qué falta. Actualizar este archivo al cerrar cada sesión.

**Última actualización:** 18 de agosto de 2026

---

## Estado actual

Sitio compilado, rediseñado y publicado. En la sesión del 4 de agosto de 2026 se
hizo la primera compilación real (el repo venía de Cowork, que no tiene Hugo),
se descartó la estética original, se prepararon los derivados del logo, se
cosecharon los ORCID iD y se rescataron las imágenes del WordPress antiguo.

El **18 de agosto de 2026** se migró el dominio propio: `www.neurosistemas.cl`
dejó de apuntar al WordPress y hoy sirve este sitio, con HTTPS forzado. Ver
**"Dominio y publicación"** más abajo.

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
| Dominio propio `www.neurosistemas.cl` con HTTPS forzado | ✅ |
| Redirecciones de las URLs del WordPress antiguo (`aliases`) | ✅ |
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

## Dominio y publicación

Migrado el **18 de agosto de 2026**. El sitio vive en
**https://www.neurosistemas.cl** con HTTPS forzado (certificado emitido por
GitHub, se renueva solo).

### Cómo está armado

- **Zona DNS: Cloudflare.** La zona de `neurosistemas.cl` se trasladó a
  Cloudflare, que es hoy la única fuente de verdad del DNS. `www` es un CNAME a
  `hayobk.github.io`, en modo **solo DNS** (nube gris): Cloudflare no hace de
  proxy, el tráfico llega directo a GitHub Pages y el certificado lo emite
  GitHub. No activar el proxy sin pensarlo, porque cambia quién sirve el TLS.
- **SiteGround quedó fuera.** Era el hosting del WordPress antiguo y ya **no
  interviene en nada**: ni DNS, ni web, ni correo. Cualquier instructivo que
  mande a tocar el panel de SiteGround está obsoleto.
- **Correo `@neurosistemas.cl`: dado de baja a propósito.** Se decidió no migrar
  las casillas del dominio; no hay registros MX apuntando a un servidor de
  correo. El contacto del laboratorio va por la dirección institucional de la
  Universidad (`config/_default/params.yaml`). Si alguna vez se quiere correo en
  el dominio, hay que crear los MX en Cloudflare desde cero.

### Dos cosas que no son obvias

1. **El `baseURL` sale de `config/_default/hugo.yaml`**, que dice
   `https://www.neurosistemas.cl/`. El workflow **ya no** pasa
   `--baseURL "${{ steps.pages.outputs.base_url }}/"`, porque ese valor devuelve
   la URL de `github.io` y compilaría el sitio con el prefijo
   `/neurosistemas-web/`, dejándolo sin CSS. El paso de build es solo
   `hugo --gc --minify`. **No reponer esa bandera.**
2. **`static/CNAME` no basta por sí solo.** Como el repo publica con
   `build_type: workflow` (GitHub Actions), GitHub no registra el dominio a
   partir del archivo del artefacto: hubo que declararlo por API con
   `gh api -X PUT repos/HayoBK/neurosistemas-web/pages -f cname=www.neurosistemas.cl`.
   El archivo igual es necesario y debe quedarse. Si alguna vez el dominio
   "se pierde", revisar primero ese registro:
   `gh api repos/HayoBK/neurosistemas-web/pages --jq '{cname,https_enforced}'`.
   (Ojo: `https_enforced` es booleano, va con `-F`, no con `-f`.)

### URLs del sitio antiguo

Las rutas del WordPress se preservan con `aliases` en el front-matter de
`content/*/_index.md`: las variantes `/es/` y `/en/`, los slugs largos
(`/miembros-del-laboratorio/`, `/galeria-de-imagenes/`…) y las **fichas
individuales** de cada persona (`/2020/11/01/pedro-maldonado/` y compañía), que
el sitio nuevo no tiene y por eso caen todas en el listado del equipo. Hugo
genera 46 redirecciones. Al renombrar una sección, mover su `aliases` con ella.

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
- [x] ~~**Galería:** sumar fotos desde la biblioteca del WordPress (~713 archivos
      de 2013–2017 sin curar) con `GALERIA_ARCHIVOS` en
      `scripts/rescatar_imagenes.py`.~~ **Ya no se puede: se acabó el plazo.**
      Desde el 18 de agosto de 2026 `neurosistemas.cl` apunta a GitHub Pages, así
      que `scripts/rescatar_imagenes.py` no tiene de dónde bajar (su `BASES` y el
      `wp-json` apuntan a ese dominio). Quedan las 3 fotos actuales. Para sumar
      más habrá que pedirle imágenes al laboratorio, o un respaldo del WordPress
      si alguien lo guardó.
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
- [x] ~~**Fotos de ex miembros.** Rescatar del WordPress los 46 retratos que no se
      bajaron.~~ **Cerrado sin hacer**, por la misma razón que la galería: el
      dominio ya no sirve el sitio antiguo. La plantilla de ex miembros los
      muestra como filas compactas con iniciales, así que no se ve roto.

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
