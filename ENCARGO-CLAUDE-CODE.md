# Encargo para Claude Code — Laboratorio de Neurosistemas

Este archivo es el brief completo de la sesión. Léelo entero antes de tocar nada,
junto con `CLAUDE.md`, `CONTINUACION-NEUROSISTEMAS.md` y `GUIA-DEPLOY-NEUROSISTEMAS.md`.

**Contexto:** el repo fue construido en Cowork, que no tiene el binario de Hugo ni
salida a GitHub. Todo el contenido está portado y validado con chequeos estáticos,
pero **el sitio nunca se ha compilado**. Tú sí tienes Hugo, git, `gh` (autenticado
como HayoBK) y red abierta: eres las manos.

**Modelo sugerido:** Sonnet alcanza para todo, salvo la tarea B (rediseño visual),
donde conviene Opus. Si vas a hacer todo de una pasada, usa Opus.

**Orden obligatorio:** A → B → C → D → E → F. No pases a la siguiente sin dejar la
anterior en verde.

---

## A. Compilar por primera vez y dejar el build limpio

```bash
cd ~/Git_Web/Neurosistemas
HUGO_ENVIRONMENT=production hugo --minify
```

Es la primera compilación real. Espera errores y corrígelos. Puntos que ya sé que
son delicados y que debes revisar aunque el build pase:

1. `layouts/publicaciones/list.html` castea `int .anio` porque Hugo decodifica los
   números de JSON como `float64` y los de YAML como `int`. Verifica que los años
   salgan agrupados sin duplicar (no debe haber dos bloques "2023").
2. `sort (uniq $anios) "value" "desc"` — confirma que el orden es de mayor a menor.
3. `time.Format "2 Jan 2006" .Date` debe entregar el mes en español. Si sale en
   inglés, revisa `defaultContentLanguage` o pasa a `.Date.Format` con un `dict` de
   meses en `i18n/`.
4. `layouts/partials/paginacion.html` es propio, no uses `_internal/pagination.html`.
5. `substr` en `persona.html` y `ex-miembros/list.html` para las iniciales: revisa
   que no reviente con nombres de una sola palabra.

Cuando esté verde, `hugo server -D` y revisa las 9 páginas en el navegador antes de
seguir. Anota lo que se vea mal; la tarea B lo va a reemplazar igual.

---

## B. Rediseño visual — este es el corazón del encargo

**La estética actual se descarta.** El CSS vigente (`static/css/neurosistemas.css`,
concepto "mapa de fijaciones": papel cálido, coral y cobalto, scanpath animado en
canvas) no le gustó a Hayo. Reescríbelo completo.

### Concepto nuevo: "papel de laboratorio + espectro"

Limpio, científico y profesional — blanco, negro, mucho aire, tipografía fuerte —
pero **coloreado con la paleta del logo**, que es lo que le da carácter.

La regla que ordena todo: **el color es información, no decoración.** El lienzo es
blanco y la tinta es negra; el espectro entra en dosis pequeñas y siempre
significando algo (qué área, qué sección, qué grupo). Nada de fondos de color
grandes, nada de degradados, nada de sombras.

### Paleta

Los 9 tonos vienen muestreados del archivo `static/images/logo-neurosistemas.jpg`.
No inventes otros.

```
--ns-rojo     #B12313      --ns-verde    #2F8F5B
--ns-naranja  #C65A16      --ns-cian     #2E9DBC
--ns-ambar    #C98510      --ns-azul     #2186B7
--ns-lima     #6E9A1B      --ns-morado   #762D60
                           --ns-magenta  #9A2A53
```

Neutros:

```
--ns-tinta    #101214   (titulares, igual de negro que el wordmark)
--ns-texto    #24282B
--ns-suave    #5B6166
--ns-tenue    #8A9298
--ns-linea    #E3E6E8
--ns-fondo    #FFFFFF
--ns-fondo2   #F6F8F9
```

**Contraste:** los 9 tonos están pensados para trazos, puntos, barras y bordes. Para
texto sobre blanco, solo `--ns-rojo`, `--ns-azul`, `--ns-morado`, `--ns-magenta` y
`--ns-verde` pasan AA cómodos. Ámbar y lima **nunca** como color de texto: úsalos
como relleno con texto negro encima, o como trazo.

### Asignación de color (fija, no aleatoria)

| Elemento | Color |
|---|---|
| Área de investigación 01 | `--ns-azul` |
| Área de investigación 02 | `--ns-ambar` |
| Área de investigación 03 | `--ns-magenta` |
| Investigadores principales | `--ns-azul` |
| Gestión y apoyo técnico | `--ns-verde` |
| Postdoc / asistentes | `--ns-cian` |
| Estudiantes de postgrado | `--ns-morado` |
| Pregrado y ayudantes | `--ns-lima` |
| Publicaciones | `--ns-rojo` |
| Noticias | `--ns-naranja` |

Guárdalo en `data/colores.yaml` y léelo desde las plantillas, para que no quede
hardcodeado y Hayo lo pueda cambiar desde el CMS.

### La firma del sitio: la franja espectral

Una barra de **4 px** con los 9 tonos en bandas iguales (mismo orden del logo:
rojo → naranja → ámbar → lima → verde → cian → azul → morado → magenta).
Va justo bajo el header, y otra vez al inicio del footer. Es el único momento en que
el color ocupa ancho completo. Hazla con `linear-gradient` de tramos duros
(`... 0 11.11%, ... 11.11% 22.22%, ...`), no con degradado suave.

### La línea EEG

El logo tiene un trazo de EEG bajo el wordmark. Recupéralo como **divisor de
sección**: un SVG inline, hairline, negro al 18 % de opacidad, ancho completo,
~28 px de alto. Va entre secciones del Home. Genera el path con una función
determinista (no ruido aleatorio) para que sea idéntico en cada build.

### Tipografía

- Titulares: **Archivo** (Google Fonts), pesos 600/700. Es un grotesco ancho que
  rima con el wordmark del logo sin imitarlo.
- El H1 del Home puede ir en **Archivo** 700 con `letter-spacing: -0.03em` y
  `text-transform: uppercase` solo si se ve bien; si queda pesado, déjalo normal.
- Cuerpo: **Inter**, 400/500. Tamaño base 17 px, `line-height: 1.65`.
- Rótulos, años, DOIs, metadatos: **IBM Plex Mono** 400/500, 11–12 px,
  `letter-spacing: .08em`, mayúsculas.

### Reglas de forma

- `border-radius`: **4 px** en controles y chips, **6 px** en tarjetas. Nada de 14.
- Bordes `1px solid var(--ns-linea)`. Sin `box-shadow` en ningún lado (solo el anillo
  de foco). Sin `backdrop-filter`. Sin `transform: translateY` en hover: el hover
  cambia el color del borde y del acento, nada más.
- Tarjetas: fondo blanco, borde hairline, y **una barra de 3 px del color asignado
  en el borde superior**. Ese es el único adorno permitido.
- Listas de publicaciones: nada de círculos con halo. Un cuadrado de 6 px del color
  de la sección, o directamente el año en mono a la izquierda.

### Cambios concretos en las plantillas

- **Elimina** el canvas del scanpath: el bloque `#ns-scanpath` en
  `layouts/index.html` y todo su script en `layouts/partials/scripts.html`.
- **Elimina** la clase `.ns-puntos` y sus `radial-gradient` de fondo.
- **Hero:** blanco, sin animación. Logo grande centrado o a la izquierda, H1,
  bajada, dos botones, franja espectral. Que respire.
- **Cifras:** sin fondo de tarjeta. Número grande en Archivo, rótulo en mono debajo,
  separados por una línea vertical hairline. Cada cifra toma un color distinto del
  espectro para el número.
- **Publicaciones:** convierte la lista en una grilla de dos columnas —año pegajoso
  (`position: sticky`) a la izquierda, publicaciones a la derecha. Es el patrón de
  las revistas científicas y es lo que Hayo quiere ver bien.
- **Equipo:** fotos circulares está bien, pero el anillo de color debe ser el del
  grupo, 2 px, sin sombra. El fallback de iniciales usa el color del grupo al 10 %
  de opacidad con el texto en el color pleno.
- **Botones:** rectangulares con radio 4 px. Primario negro con texto blanco.
  Secundario borde hairline. El color del espectro no se usa en botones.
- **Footer:** fondo `--ns-fondo2` (gris muy claro), no negro. Texto oscuro.
  Franja espectral arriba. Mucho más discreto que ahora.

Mantén el prefijo `ns-` en todas las clases y las variables en `:root`.
Un solo archivo CSS. Al terminar, actualiza la sección "Estética" de `CLAUDE.md` y
la de "Notas de diseño" de `CONTINUACION-NEUROSISTEMAS.md` para que describan esto
y no lo viejo.

---

## C. Logo e identidad

El logo original está en `static/images/logo-neurosistemas.jpg` (553×230, fondo
blanco, JPG). Falta prepararlo:

1. **PNG con transparencia** en `static/images/logo-neurosistemas.png`. El fondo es
   blanco plano, así que sirve una máscara por luminancia con Pillow. Cuida los
   antialiasing de las letras negras: usa un umbral alto (blanco > 245) y un canal
   alfa suave, no binario, o los bordes van a quedar dentados.
2. Versión **compacta para el header** (solo el isotipo del splatter + neurona, sin
   el texto), ~64 px de alto → `static/images/isotipo.png`. Recórtala de la zona
   derecha del original.
3. **Favicon** desde el isotipo: `static/images/favicon.png` (180×180) y
   `static/images/favicon.svg` si logras vectorizarlo decentemente. Si no, deja solo
   el PNG y ajusta `head.html`.
4. **Imagen Open Graph** `static/images/og-neurosistemas.jpg` (1200×630): logo
   centrado sobre blanco, franja espectral abajo.
5. Reemplaza el SVG placeholder actual (`logo-neurosistemas.svg`, un scanpath que
   dibujé yo) en `partials/header.html` y bórralo.

Deja el logo original sin tocar como respaldo.

---

## D. ORCID — cosechar los identificadores

Esto es lo que enciende la actualización automática de publicaciones.
`data/orcid.yaml` tiene la lista de miembros con el campo `orcid` en blanco.

### D.1 — Cosecha local (gratis e inmediata)

El repo del Departamento de Neurociencia, en `~/Git_Web/Neurociencia`, ya tiene
ORCID en el front-matter de sus académicos:

```
content/academicos/<slug>/index.md   →   orcid: "https://orcid.org/0000-0000-0000-0000"
```

Hay 15 académicos con ORCID de 35. **Ya verifiqué los cruces con Neurosistemas:**

| Persona | Estado en `~/Git_Web/Neurociencia` |
|---|---|
| María de los Ángeles Juricic | ✅ `0000-0002-9059-1988` — miembro **actual** |
| Rómulo Fuentes | ✅ `0000-0002-6282-7287` — ex miembro |
| Paul Délano | ✅ `0000-0003-2588-4757` — ex miembro |
| José Luis Valdés | ✅ `0000-0002-9178-2743` — ex miembro |
| Julio Torres | ✅ `0000-0003-2645-9170` — ex miembro |
| Gonzalo Rivera | ✅ `0000-0002-8157-4086` — ex miembro |
| Pedro Maldonado | ⚠️ tiene ficha, **sin** campo `orcid` |
| Christ Devia | ⚠️ tiene ficha, **sin** campo `orcid` |

Escribe `scripts/cosechar_orcid.py` que recorra ese repo, empareje por apellido
normalizado contra `data/miembros.yaml` / `data/exmiembros.yaml`, y rellene el campo
`orcid` (guardando solo el identificador, sin el prefijo `https://orcid.org/`).
Que sea idempotente y que **nunca pise** un valor ya escrito a mano.

### D.2 — Búsqueda en ORCID para el resto

Para los que no aparecen, usa la API pública de búsqueda:

```
https://pub.orcid.org/v3.0/expanded-search/?q=family-name:Maldonado+AND+given-names:Pedro
```

con `Accept: application/json`. Filtra por afiliación que contenga "Chile".

**No adivines.** Genera `INFORME-ORCID.md` en la raíz con una tabla: persona,
candidatos encontrados, ORCID iD, afiliación e institución de cada candidato, y una
columna vacía para que Hayo marque el correcto. Rellena automáticamente **solo**
cuando haya exactamente un candidato con afiliación en Universidad de Chile; el
resto queda para revisión humana.

### D.3 — Correr el sincronizador de verdad

```bash
pip install requests PyYAML
python scripts/test_orcid_sync.py     # 13 aserciones, todas deben pasar
python scripts/orcid_sync.py          # primera corrida real contra ORCID + Crossref
```

Revisa `data/publicaciones_orcid.json` a ojo: que los años sean correctos, que los
autores del lab salgan en negrita y que no se dupliquen entradas que ya están en
`data/publicaciones_historicas.yaml`. Si ves duplicados, el filtro por título en
`orcid_sync.py` es demasiado laxo o demasiado estricto — ajústalo y vuelve a correr.

Ojo con `anio_minimo: 2023` en `data/orcid.yaml`: está así para que ORCID no repita
el archivo histórico. Si la cosecha trae poco, bájalo y revisa duplicados.

---

## E. Rescatar las imágenes del WordPress viejo

`www.neurosistemas.cl` sigue en pie pero se va a dar de baja. **Bájalas ahora.**

- Fotos del equipo: `https://neurosistemas.cl/web/wp-content/uploads/elementor/thumbs/*.png`
  y `https://neurosistemas.cl/web/wp-content/uploads/2023/04/*.jpg`
- Fotos del laboratorio para la galería:
  `.../uploads/2020/06/Fotolab.jpg` y las dos `WhatsApp-Image-2020-07-06-*.jpeg`

Las páginas de origen son `/miembros-del-laboratorio/`, `/ex-miembros/`,
`/miembros-visitantes/` y `/galeria-de-imagenes/`. Parsea el HTML, descarga, y:

1. Guarda las del equipo en `static/images/equipo/` con nombres slug
   (`pedro-maldonado.jpg`, `christ-devia.jpg`…), recortadas cuadradas a 400×400.
2. Escribe el nombre del archivo en el campo `foto` de `data/miembros.yaml` y
   `data/visitantes.yaml`, emparejando por nombre.
3. Las de laboratorio van a `static/images/galeria/` y se listan en
   `data/galeria.yaml`.
4. Ignora el placeholder `Untitled_Artwork-2-*` — es el genérico de "sin foto", no
   sirve. Esas personas se quedan con las iniciales.

Comprime todo (JPG calidad 82). El repo no debería crecer más de ~15 MB.

---

## F. Publicar

Recién ahora. Sigue `GUIA-DEPLOY-NEUROSISTEMAS.md`; el resumen:

```bash
cd ~/Git_Web/Neurosistemas
HUGO_ENVIRONMENT=production hugo --minify        # verde obligatorio

git init -b main
git add .
git commit -m "Sitio del Laboratorio de Neurosistemas en Hugo"
gh repo create HayoBK/neurosistemas-web --public --source=. --remote=origin --push
```

Después, con `gh` (no lo dejes para que Hayo lo haga a mano si puedes hacerlo tú):

- Pages con origen GitHub Actions:
  `gh api -X POST repos/HayoBK/neurosistemas-web/pages -f build_type=workflow`
- Permisos de escritura para Actions (necesario para el bot de ORCID):
  `gh api -X PUT repos/HayoBK/neurosistemas-web/actions/permissions/workflow -f default_workflow_permissions=write`
- Dispara la sincronización:
  `gh workflow run orcid.yml`
- Verifica que ambos workflows quedaron verdes: `gh run list --limit 5`

Entrega la URL de Pages funcionando.

**No toques el DNS de neurosistemas.cl.** Eso queda para cuando Hayo revise el sitio
en la URL de github.io.

---

## Reglas de la casa (no negociables)

1. Valida el build antes de cada commit: `HUGO_ENVIRONMENT=production hugo --minify`.
   Sin `ERROR` = verde.
2. Rutas siempre con `relURL` / `.RelPermalink` / `pageRef`. Nunca un path absoluto.
   Imágenes: `"images/x.jpg" | relURL`, sin slash inicial.
3. Un solo archivo CSS, clases `ns-`, variables `--ns-`.
4. Lo editable vive en `data/*.yaml` o front-matter, y las plantillas toleran campos
   vacíos o ausentes. Si agregas un archivo en `data/`, agrégalo también a
   `.pages.yml` para que sea editable desde el CMS.
5. Nunca edites `data/publicaciones_orcid.json` a mano: lo escribe el bot.
6. Commits chicos, en español, uno por tarea (A, B, C…).
7. Al terminar, actualiza `CONTINUACION-NEUROSISTEMAS.md`: qué quedó hecho, qué
   quedó pendiente y qué decisiones tomaste.

## Qué necesito de vuelta

Un resumen corto con:

- URL de GitHub Pages funcionando.
- Errores de build que encontraste y cómo los resolviste.
- Cuántos ORCID quedaron cosechados y cuántos siguen pendientes (con el
  `INFORME-ORCID.md` listo para que Hayo lo complete).
- Cuántas fotos rescataste y quiénes se quedaron sin foto.
- Qué decisiones de diseño tomaste donde este brief era ambiguo.

Los datos de contacto en `config/_default/params.yaml` (correo, teléfono, dirección)
son **provisorios y sin confirmar**. No los des por buenos y déjalo anotado.
