# Encargo — logo grande, texto chico, perfiles del equipo y contacto por persona

Brief completo de la sesión. Léelo entero antes de tocar nada, junto con `CLAUDE.md` y
`CONTINUACION-NEUROSISTEMAS.md`.

**Contexto:** el sitio ya está en producción en <https://www.neurosistemas.cl>, con dominio
propio, HTTPS y la sincronización ORCID funcionando. Esto es una sesión de mejoras, no una
migración. Nada de lo que se pide aquí toca el DNS, Cloudflare ni la publicación.

**Lo que ya está hecho y NO hay que rehacer** (lo preparó Cowork, que no tiene Hugo):

- `static/images/logo-neurosistemas.png` — logo nuevo en alta resolución, 1400×593,
  fondo transparente, 139 KB. Reemplaza al anterior.
- `static/images/isotipo.png` y `static/images/favicon.png` — regenerados desde el logo HD.
- 10 retratos nuevos o actualizados en `static/images/equipo/`, ya recortados cuadrados a
  600×600 con el rostro centrado.
- **31 fichas en `content/miembros/*.md`**, una por persona activa, con front-matter y
  biografía. Son la parte central de este encargo.
- `data/orcid.yaml` — 18 personas, 14 con ORCID.
- `data/exmiembros.yaml` — se agregó Simón San Martín (52 en total).
- `config/_default/params.yaml` — se eliminaron el correo y el teléfono de contacto.

Tu trabajo es el código: plantillas, CSS, build y despliegue.

---

## Tarea A — Hero: el logo es el título

Es el cambio estético que más importa. Hoy el logo se ve chico y el lema
"Percepción activa, redes neuronales y estados mentales" domina la portada con un tamaño de
hasta 3.6 rem. Hay que invertir esa jerarquía.

**Qué se quiere:**

1. **El logo mucho más grande**, y que sea el título de la página. Hoy está limitado a
   440 px de ancho; debe llegar a alrededor de **820 px** en pantallas grandes, escalando
   con el ancho disponible.
2. **El lema mucho más chico.** Deja de ser un titular de display y pasa a ser una bajada
   discreta: alrededor de **1.15–1.45 rem**, peso normal o medio, no 700.
3. **Todo el texto del hero más chico**, incluido el párrafo descriptivo y el rótulo de
   arriba. El hero debe respirar y dejar que el logo mande.

**Semántica, importante para accesibilidad y SEO:** si el logo pasa a ser el título, el
`<h1>` debe contenerlo, no desaparecer. Envuelve la imagen en el `h1` y deja el texto
alternativo como el nombre del laboratorio:

```html
<h1 class="ns-hero__titulo">
  <img class="ns-hero__logo" src="..." alt="Laboratorio de Neurosistemas" width="1400" height="593">
</h1>
<p class="ns-hero__lema">Percepción activa, redes neuronales y estados mentales</p>
```

Cuida que el `h1` no arrastre los estilos de titular (tamaño de fuente, márgenes,
`letter-spacing`) que hoy tiene `.ns-hero__titulo`: reinícialos a algo neutro y deja que
mande la imagen. Ajusta también `width`/`height` del `img` a las dimensiones reales del
archivo nuevo (1400×593) para que no haya salto de maquetación al cargar.

Revisa el resultado en móvil: con el logo a ancho completo, el hero no debe quedar
desproporcionado ni empujar todo el contenido fuera de la primera pantalla.

---

## Tarea B — Páginas de perfil del equipo

Hoy el equipo vive en `data/miembros.yaml` y se muestra solo como una grilla de tarjetas.
Se quiere que **cada persona activa tenga su propia página**, aunque su información sea
escasa.

### B.1 — Lo que ya está creado

**31 archivos en `content/miembros/`**, uno por persona. Front-matter de ejemplo:

```yaml
---
title: Iván Plaza Rosales
rol: Líder de grupo
grupo: Investigadores principales
weight: 106
foto: ivan-plaza.jpg
email: ivanp@uchile.cl
orcid: 0000-0002-2112-8439
perfil: ''
intereses: Biomarcadores no invasivos, neuroimagen multimodal, neuroftalmología traslacional.
draft: false
---

Cuerpo en markdown con la biografía, y a veces una sección "## Temas de investigación".
```

Estado de las 31 fichas: **13 con biografía**, 25 con foto, 14 con ORCID y 10 con correo.
Las plantillas tienen que verse bien en todos los casos: una ficha sin biografía, sin foto y
sin enlaces no debe quedar como una página rota ni vacía.

`weight` ordena todo: los grupos van espaciados de 100 en 100 y las personas dentro de cada
grupo en el orden correcto. Ordena siempre por `weight`, nunca alfabéticamente.

Los cinco grupos, en orden:

| weight | Grupo | Personas |
|---|---|---|
| 100 | Investigadores principales | 6 |
| 200 | Gestión y apoyo técnico | 2 |
| 300 | Investigadores postdoctorales y asistentes | 5 |
| 400 | Estudiantes de postgrado | 13 |
| 600 | Estudiantes de pregrado y ayudantes | 5 |

El rango 500 quedó libre a propósito, por si más adelante se agrega un grupo intermedio.

### B.2 — Cambios respecto del roster anterior

- **Hayo Breinbauer** se suma como Líder de grupo, al mismo nivel que Christ Devia.
- **Samuel Madariaga** pasó de estudiante de doctorado a investigador postdoctoral.
- **Joaquín Valdés Bize** se suma como investigador postdoctoral.
- **Andrés Contreras, Pablo Pozo Santelices, Matías Urrea Cabezas e Irma Cisternas** se
  suman como estudiantes de postgrado.
- **Cristian Fernández** pasó de magíster a doctorado.
- **Simón San Martín** salió del equipo activo y quedó en `data/exmiembros.yaml`, con el
  mismo formato que el resto de los ex miembros. No tiene ficha propia.

### B.3 — Plantillas

**`layouts/miembros/single.html`** (nueva). La página de cada persona. Debe incluir:

- Foto grande, o el círculo de iniciales si no hay foto — reutiliza `partials/iniciales.html`.
- Nombre como `h1`, rol y grupo.
- Los chips que ya existen en `partials/persona.html`: correo, ORCID, perfil externo.
- `intereses` destacado como una línea de áreas de interés.
- El cuerpo markdown, con el ancho de lectura del sitio (`.ns-wrap-txt` o equivalente).
- **Sus publicaciones**, filtradas desde `hugo.Data.publicaciones_orcid`: recorre
  `.publicaciones` y quédate con aquellas cuyo arreglo `miembros` contenga el nombre de
  esta persona. Si no hay ninguna, omite la sección entera en vez de mostrarla vacía.
  Ojo: el nombre en `publicaciones_orcid.json` viene del campo `nombre` de
  `data/orcid.yaml`, que no siempre es idéntico al `title` de la ficha. Empareja de forma
  tolerante, o agrega en el front-matter un campo explícito si te resulta más limpio.
- Enlace de vuelta a `/miembros/`.
- Color del grupo como acento, con `partials/color.html`, igual que hoy hace la grilla.

**`layouts/miembros/list.html`** (reescribir). Hoy recorre `hugo.Data.miembros`. Debe pasar
a recorrer `.Pages`, agrupadas por el parámetro `grupo` y ordenadas por `weight`. En Hugo:

```
{{ range .Pages.GroupByParam "grupo" }}
```

`GroupByParam` ordena los grupos alfabéticamente por defecto, que **no** es lo que
queremos. Ordena los grupos por el `weight` mínimo de sus páginas, o construye el orden a
partir de la tabla de arriba. Verifica en el navegador que el orden final sea el de la
tabla y no alfabético: es el error fácil de esta tarea.

**`layouts/partials/persona.html`** (ajustar). Que la tarjeta enlace a la página de la
persona: nombre y foto clicables hacia `.RelPermalink`. El partial hoy recibe un `dict` con
una entrada de YAML; adáptalo para recibir la página, manteniendo el aspecto visual actual
de la grilla.

**`layouts/index.html`** (ajustar). La sección "Quiénes lideran el laboratorio" y la cifra
"Miembros activos" hoy leen `hugo.Data.miembros`. Pásalas a leer las páginas de
`content/miembros/`. Ahora los líderes son **6**, no 5.

### B.4 — Limpieza

- Una vez que todo lea las páginas, **borra `data/miembros.yaml`** y quita su entrada de
  `.pages.yml`. Tener el roster en dos lugares es exactamente el tipo de duplicación que se
  desincroniza en tres meses.
- Agrega a `.pages.yml` una colección para `content/miembros` (excluyendo `_index.md`) con
  los campos del front-matter, para que las fichas se puedan editar desde Pages CMS.
- Conserva los `aliases` que ya tiene `content/miembros/_index.md`: son las redirecciones
  del WordPress antiguo y no deben perderse.

---

## Tarea C — Contacto: se acabó el buzón genérico

El correo `neurosistemas@med.uchile.cl` y el teléfono `+56 2 2978 6034` que estaban
publicados **eran marcadores inventados** al montar el sitio y nunca existieron. Ya los
saqué de `config/_default/params.yaml`. Ahora hay que sacarlos también de las plantillas y
reemplazar la lógica de contacto.

**La decisión:** el laboratorio no tiene una casilla institucional. El contacto se hace con
cada integrante, a través de su ficha. En `params.yaml` quedaron solo `institucion`,
`direccion` y `mapa`.

**`layouts/contacto/list.html`:**

- Elimina el bloque de correo y el de teléfono.
- **Elimina el botón "Escribirnos un correo".** Es un `mailto:` que apunta directamente a
  `site.Params.contacto.email` sin estar protegido por un `with`, así que ahora generaría
  un enlace vacío. Hay que borrarlo, no solo esconderlo.
- Deja la institución, la dirección y el mapa.
- Agrega en su lugar un bloque que explique que se escribe directamente a la persona
  correspondiente, con un botón hacia `/miembros/`. Redáctalo de forma útil: quien busca
  hacer una tesis debería entender que conviene escribirle a quien lidera la línea que le
  interesa.
- Revisa el cuerpo de `content/contacto/_index.md`: el texto dice "escríbenos" y hay que
  ajustarlo a que el contacto es por persona.

**`layouts/partials/footer.html`:** quita las entradas de correo y teléfono de la columna
"Contacto". Deja institución y dirección.

Después, busca en todo el repositorio referencias sueltas a
`site.Params.contacto.email` o `.telefono` y elimínalas. No deben quedar enlaces
`mailto:` vacíos en ninguna página.

---

## Tarea D — Compilar, revisar y publicar

```bash
cd ~/Git_Web/Neurosistemas
HUGO_ENVIRONMENT=production hugo --minify
hugo server -D
```

Revisa en el navegador antes de subir:

- La portada, con el logo grande y el lema chico. También en móvil.
- `/miembros/` con los cinco grupos en el orden correcto.
- Tres fichas de prueba: una con biografía larga y publicaciones (Iván Plaza), una con
  biografía corta (Matías Urrea) y una sin biografía, sin foto y sin enlaces
  (Antonia Haberle).
- `/contacto/` sin rastro del correo ni el teléfono, y sin enlaces `mailto:` vacíos.
- Que `/investigaciones/` siga redirigiendo a `/investigacion/`: los alias no se deben
  haber roto.

Después:

```bash
git add -A
git commit -m "Hero con el logo como título, fichas de perfil del equipo y contacto por persona"
git push
gh run watch
```

Verifica que <https://www.neurosistemas.cl> siga sirviendo con HTTPS y que las fichas
nuevas respondan.

---

## Fuera de alcance

No toques el DNS, Cloudflare, el script de ORCID ni el workflow de despliegue. No cambies
la paleta ni la estructura de `data/colores.yaml`. No rehagas las imágenes: ya están
procesadas.

---

## Pendientes que NO se resuelven aquí, pero deben quedar anotados en `CONTINUACION`

1. **Cuatro personas sin ORCID** en `data/orcid.yaml`: Cecilia Babul, Karla Padilla,
   Ismael Jaras y Carolina Lindsay.
2. **18 fichas sin biografía.** Se pueden completar con el mismo formulario que ya
   respondieron los demás.
3. **Faltan retratos** de Antonia Haberle, Ricardo Mendoza, Sofía Onetti, Sofía Berndt,
   Rodrigo González y Hayo Breinbauer. El WordPress antiguo ya no es alcanzable, así que
   hay que pedirlas.
4. **La dirección de `params.yaml`** (Av. Independencia 1027) es la de la Facultad de
   Medicina y es plausible, pero nunca se confirmó con el laboratorio, igual que las
   coordenadas del mapa. Conviene verificarla.
5. La galería tiene solo 3 imágenes.
