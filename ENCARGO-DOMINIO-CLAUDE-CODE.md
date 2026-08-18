# Plan de migración del dominio neurosistemas.cl

**Decisión tomada:** sacamos el dominio de SiteGround por completo, sin intentar
recuperar el acceso a esa cuenta. Se acepta que haya horas o días de error 404 y pérdida
temporal de posicionamiento. El objetivo es tomar control total del dominio.

**El correo `@neurosistemas.cl` se da de baja**, confirmado con el laboratorio: nadie lo
usa. No se recrean registros MX ni SPF.

Este archivo tiene tres partes:

- **Parte A** — lo que hace Hayo a mano en Cloudflare (no se puede automatizar: requiere
  crear una cuenta en un navegador).
- **Parte B** — lo que ejecuta Claude Code en el repositorio.
- **Parte C** — verificación después de que Pedro cambie los servidores en nic.cl.

---

## Diagnóstico previo, verificado el 12 de agosto de 2026

```
NS      neurosistemas.cl       ns1.siteground.net, ns2.siteground.net
A       neurosistemas.cl       35.208.36.52
A       www.neurosistemas.cl   35.208.36.52
MX      neurosistemas.cl       mx10/20/30.mailspamprotection.com   ← se abandona
TXT     neurosistemas.cl       v=spf1 +a +mx +ip4:35.208.222.12 …  ← se abandona
DS / DNSKEY                    ninguno — el dominio NO tiene DNSSEC
```

**El dato que hace que esto sea seguro: no hay DNSSEC.** Si lo hubiera, cambiar los
servidores de nombre sin retirar antes los registros DS dejaría el dominio irresoluble
para medio internet. No es el caso, así que el cambio es limpio.

**Por qué hace falta Cloudflare:** NIC Chile no ofrece DNS primario. Está dicho con esas
palabras en su propia documentación: *"NIC Chile no entrega el servicio de DNS primario
para sus clientes."* En nic.cl solo se declara **a qué servidores** se delega el dominio;
la zona con los registros tiene que vivir en otra parte.

---

## Parte A — Cloudflare (Hayo, a mano, ~15 minutos)

Hazlo **antes** de que Pedro toque nic.cl. Así, cuando el cambio de delegación surta
efecto, la zona ya está lista y el sitio aparece de inmediato.

### A.1 Crear la cuenta

<https://dash.cloudflare.com/sign-up> — plan **Free**, no pide tarjeta.

> **Usa un correo institucional o del laboratorio, no uno personal.** Quien controla esta
> cuenta controla el dominio. Si mañana alguien más tiene que administrarlo, no queremos
> que dependa de una casilla individual. Activa además la verificación en dos pasos.

### A.2 Agregar el dominio

**Add a site** → `neurosistemas.cl` → plan **Free**.

Cloudflare va a escanear la zona actual e importar los registros que encuentre en
SiteGround. **Bórralos todos.** No queremos arrastrar nada del hosting antiguo: ni el
`A` que apunta a `35.208.36.52`, ni los MX, ni el SPF, ni subdominios como `mail`,
`webmail`, `ftp` o `cpanel`.

### A.3 Crear la zona desde cero

Deja exactamente estos registros y ninguno más:

| Tipo | Nombre | Contenido | Proxy |
|---|---|---|---|
| A | `@` | `185.199.108.153` | **DNS only** |
| A | `@` | `185.199.109.153` | **DNS only** |
| A | `@` | `185.199.110.153` | **DNS only** |
| A | `@` | `185.199.111.153` | **DNS only** |
| AAAA | `@` | `2606:50c0:8000::153` | **DNS only** |
| AAAA | `@` | `2606:50c0:8001::153` | **DNS only** |
| AAAA | `@` | `2606:50c0:8002::153` | **DNS only** |
| AAAA | `@` | `2606:50c0:8003::153` | **DNS only** |
| CNAME | `www` | `hayobk.github.io` | **DNS only** |

> **La nube tiene que quedar gris, no naranja.** Con el proxy activado, GitHub no puede
> completar la validación para emitir su certificado y el sitio queda con error de SSL o
> en bucle de redirección. Gris = "DNS only" = Cloudflare solo resuelve nombres. Es lo que
> queremos.
>
> Los AAAA son opcionales pero no cuestan nada y dan soporte IPv6.

### A.4 Anotar los servidores de nombre

Cloudflare te va a mostrar dos direcciones del estilo `xxxx.ns.cloudflare.com`. Son
distintas para cada cuenta.

**Cópialas al recuadro de `INSTRUCTIVO-DOMINIO-PEDRO.md`** (está marcado con puntos
suspensivos) y regenera el PDF antes de enviárselo a Pedro. Sin esos dos datos el
instructivo no sirve.

### A.5 Avisar a Pedro

Recién ahora. Mándale el PDF ya completado.

---

## Parte B — Repositorio (Claude Code)

Se puede hacer en paralelo con la Parte A. Debe estar publicado **antes** de que el DNS
apunte a GitHub.

### B.1 Declarar el dominio

Crea `static/CNAME` con una sola línea, sin `https://` y sin barra final:

```
www.neurosistemas.cl
```

Ese archivo es lo que le dice a GitHub Pages cuál es el dominio propio; no hace falta
tocar nada en la interfaz web. Hugo lo copia a `public/` en cada build.

### B.2 Actualizar el baseURL

En `config/_default/hugo.yaml`:

```yaml
baseURL: "https://www.neurosistemas.cl/"
```

Actualiza también el comentario de arriba, que hoy explica que es un placeholder de
`github.io`.

### B.3 Redirecciones de las URLs del sitio antiguo

Aunque asumimos la pérdida de posicionamiento, estas redirecciones son gratis y rescatan
los enlaces que la gente tenga guardados o citados en publicaciones. Hugo genera una
página de redirección por cada entrada de `aliases`.

El WordPress era bilingüe con qTranslate-X, así que cada dirección existía sin prefijo,
con `/es/` y con `/en/`. Hay que cubrir las tres formas.

**`content/investigacion/_index.md`**

```yaml
aliases:
  - /investigaciones/
  - /es/investigaciones/
  - /en/investigaciones/
```

**`content/publicaciones/_index.md`**

```yaml
aliases:
  - /es/publicaciones/
  - /en/publications/
```

**`content/miembros/_index.md`**

```yaml
aliases:
  - /miembros-del-laboratorio/
  - /es/miembros-del-laboratorio/
  - /en/laboratory-members/
  - /miembros-del-laboratorio-version-antigua/
  - /en/miembros-del-laboratorio-version-antigua/
  # Fichas individuales del WordPress: el sitio nuevo no tiene página por persona,
  # así que todas caen en el listado del equipo.
  - /2020/11/01/pedro-maldonado/
  - /2020/11/01/christ-devia/
  - /2020/11/01/maria-de-los-angeles-juricic-urzua/
  - /2020/11/01/jose-ignacio-egana-tomic/
  - /2020/11/01/cecilia-babul/
  - /2020/11/01/cristian-lopez/
  - /2020/11/01/karla-margarita-padilla-olvera/
  - /2020/11/01/carolina-lindsay/
  - /2020/11/01/ismael-sebastian-jaras-castanos/
  - /2020/11/01/myriam-gutierrez/
  - /2020/11/01/samuel-madariaga/
  - /2020/11/01/camilo-jara/
  - /2020/11/01/cristian-fernandez/
  - /2020/11/01/camilo-espinosa/
  - /2020/11/01/armando-anibal-parraguez/
  - /2021/10/28/maria-soledad-hernandez/
  - /2021/11/04/rocio-loyola/
  - /2021/10/19/carlos-navarro/
  - /2023/04/20/rodrigo-gonzalez-cornejo/
  - /2023/04/20/simon-san-martin-rubilar/
  - /2023/04/20/ricardo-mendoza/
```

**`content/visitantes/_index.md`**

```yaml
aliases:
  - /miembros-visitantes/
  - /es/miembros-visitantes/
  - /en/visiting-members/
```

**`content/ex-miembros/_index.md`**

```yaml
aliases:
  - /es/ex-miembros/
  - /en/alumni/
```

**`content/galeria/_index.md`**

```yaml
aliases:
  - /galeria-de-imagenes/
  - /es/galeria-de-imagenes/
  - /en/image-gallery/
```

**`content/contacto/_index.md`**

```yaml
aliases:
  - /es/contacto/
  - /en/contact/
```

**`content/noticias/_index.md`**

```yaml
aliases:
  - /es/noticias/
  - /en/news/
```

**`content/_index.md`**

```yaml
aliases:
  - /es/
  - /en/
```

### B.4 Compilar y publicar

```bash
cd ~/Git_Web/Neurosistemas
HUGO_ENVIRONMENT=production hugo --minify
cat public/CNAME                                   # www.neurosistemas.cl
ls public/investigaciones/index.html public/en/alumni/index.html
git add -A
git commit -m "Conectar dominio propio y redirigir las URLs del sitio anterior"
git push
gh run watch
gh api repos/HayoBK/neurosistemas-web/pages --jq '{cname: .cname, estado: .status, https: .https_enforced}'
```

Debe aparecer `cname: www.neurosistemas.cl`. El certificado todavía no estará listo:
GitHub no lo puede emitir hasta que el DNS apunte hacia él.

**Aquí te detienes** y avisas que la parte del repositorio está lista.

> Efecto secundario esperado y correcto: desde que existe el archivo `CNAME`, la URL
> `hayobk.github.io/neurosistemas-web/` redirige a `www.neurosistemas.cl`. Mientras la
> delegación no cambie, esa dirección no va a responder. Para previsualizar usa
> `hugo server`. No lo trates como un error.

---

## Parte C — Después del cambio en nic.cl

Pedro reemplaza los servidores de nombre. NIC Chile republica la zona `.cl` cada 30
minutos, y la difusión completa puede tardar hasta un par de días.

### C.1 Verificar la delegación

```bash
dig +short NS neurosistemas.cl
dig +short NS neurosistemas.cl @a.nic.cl        # directo al registro .cl, sin caché
```

Deben aparecer los dos de Cloudflare. Mientras siga saliendo `siteground`, el cambio no ha
llegado a ese resolutor todavía.

### C.2 Verificar los registros

```bash
dig +short www.neurosistemas.cl
dig +short neurosistemas.cl
dig +short @8.8.8.8 www.neurosistemas.cl
```

`www` debe responder `hayobk.github.io.` y las cuatro IP `185.199.108–111.153`; el dominio
raíz, esas mismas cuatro.

### C.3 Activar HTTPS

GitHub emite el certificado solo, y puede tardar hasta una hora desde que el DNS resuelve
bien. Cuando `status` sea `built`:

```bash
gh api -X PUT repos/HayoBK/neurosistemas-web/pages -f https_enforced=true
```

Si responde que el certificado no está disponible, espera y reintenta. No sirve forzarlo.

### C.4 Prueba final

```bash
curl -sI https://www.neurosistemas.cl                  | head -1   # 200
curl -sI http://neurosistemas.cl                       | head -3   # 301 hacia www
curl -sI https://www.neurosistemas.cl/investigaciones/ | head -3   # alias redirige
curl -s  https://www.neurosistemas.cl | grep -c "Neurosistemas"
```

En el navegador: candado sin advertencias y páginas con estilos. Si se ven en blanco y
negro, quedó alguna ruta absoluta y hay que revisar el `baseURL`.

---

## Al terminar, actualizar `CONTINUACION-NEUROSISTEMAS.md`

Deja escrito:

- Fecha del cambio de dominio y de delegación.
- Que la zona DNS vive ahora en **Cloudflare**, con qué cuenta se creó y quién tiene
  acceso. Es la información que más falta hace dentro de tres años.
- Que el `baseURL` ya no es el placeholder de github.io.
- Que **el correo `@neurosistemas.cl` quedó dado de baja a propósito**, y que si alguna
  vez se quiere reactivar hay que crear registros MX nuevos apuntando a un proveedor de
  correo. Esto tiene que quedar explícito: si dentro de un tiempo alguien reporta que un
  correo al laboratorio rebotó, la explicación debe estar a mano.
- Que SiteGround quedó completamente fuera y su cuenta puede darse de baja sin
  consecuencias para el dominio.
