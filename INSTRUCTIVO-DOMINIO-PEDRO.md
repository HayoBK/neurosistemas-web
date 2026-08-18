# Cambiar el dominio neurosistemas.cl al nuevo sitio

**Para:** Pedro Maldonado  
**De:** Hayo Breinbauer  
**Qué se te pide:** un solo cambio, en nic.cl, que toma unos cinco minutos

---

## En una frase

Hay que reemplazar los dos "servidores de nombre" que tiene el dominio hoy por otros dos
que yo te voy a pasar. Con eso el dominio deja de depender de la empresa que alojaba el
sitio antiguo y pasa a mostrar la página nueva.

Es un solo campo, en una sola pantalla del panel de nic.cl.

---

## Antes de empezar: los dos datos que van aquí

Yo te los mando junto con este documento. Son dos direcciones que terminan en
`ns.cloudflare.com`.

> **Servidor de nombre 1: alfred.ns.cloudflare.com
>
> **Servidor de nombre 2: chin.ns.cloudflare.com

Si este recuadro te llegó en blanco, pídemelos antes de entrar a nic.cl: sin ellos el
cambio no se puede hacer.

---

## Por qué lo hacemos así

El dominio está hoy delegado a **SiteGround**, la empresa donde vive el WordPress
antiguo. 

En vez de intentar recuperarla, la sacamos del camino: cambiamos los servidores de nombre
directamente desde nic.cl, que es donde tú sí tienes control. A partir de ese momento el
dominio queda administrado por nosotros y no depende de nadie más.

Es un cambio que **solo se puede hacer desde nic.cl**, y por eso te lo pido a ti.

---

## Lo que va a pasar, para que no te tome por sorpresa

**El sitio antiguo deja de verse.** Es lo que queremos. El WordPress sigue existiendo en
los servidores de SiteGround, pero dejará de ser lo que aparece al escribir la dirección.
Yo ya tengo respaldado todo su contenido, sus textos y sus imágenes en la página nueva.

**Puede haber unas horas, o incluso un par de días, en que la dirección no muestre nada
o dé error.** Es normal en este tipo de cambio y ya lo conversamos: preferimos eso antes
que seguir dependiendo de una cuenta a la que nadie puede entrar.

**Las direcciones de correo `@neurosistemas.cl` van a dejar de funcionar.** Me
confirmaste que nadie las usa. Si más adelante aparece alguien que sí tenía una, avísame:
se puede volver a habilitar, pero hay que hacerlo a propósito.

**No afecta el pago ni la propiedad del dominio.** `neurosistemas.cl` sigue siendo del
laboratorio y se sigue renovando en NIC Chile como siempre.

---

## Paso a paso

### 1. Entrar al panel

Ve a <https://clientes.nic.cl> e ingresa con tu usuario y clave de NIC Chile.

Si no recuerdas la clave, usa la recuperación por correo del mismo sitio. Es la cuenta
con la que se paga la renovación del dominio.

### 2. Abrir el dominio

En el listado, haz clic en **neurosistemas.cl**.

### 3. Ir a la configuración técnica

Busca la sección **Configuración técnica**. Dentro, en **Tipo de servicio**, elige la
opción **Servidores DNS**.

Vas a ver unos campos con los servidores actuales, que hoy dicen algo parecido a:

```
ns1.siteground.net
ns2.siteground.net
```

### 4. Anotar lo que había

Antes de borrar nada, **copia esos dos nombres en un papel o sácale una foto a la
pantalla**. Es lo único que se necesita para deshacer el cambio si hiciera falta.

### 5. Reemplazarlos

Borra los dos servidores que están y escribe en su lugar :

alfred.ns.cloudflare.com
chin.ns.cloudflare.com

Que queden **exactamente esos dos y ninguno más**. Si sobran campos con datos antiguos,
déjalos vacíos.

> **Importante:** si ves una casilla que dice **"Configurar a NIC Chile como servidor
> secundario"**, déjala **desmarcada**. Si estaba marcada, desmárcala. Marcarla puede
> hacer que el dominio no resuelva bien.

### 6. Guardar

Baja hasta el final de la página y presiona **Actualizar datos de dominio**.

### 7. Avisarme

Mándame un mensaje diciendo que ya está. Yo me encargo del resto y te confirmo cuando la
página esté funcionando en la dirección definitiva.

---

## Cuánto demora

NIC Chile publica los cambios de la zona `.cl` **cada media hora**. O sea, el cambio queda
registrado rápido.

Lo que demora más es que el cambio se difunda por el resto de internet: entre unas horas
y un par de días, según el proveedor desde el que uno se conecte. Durante ese lapso puede
pasar que tú veas la página nueva y otra persona todavía vea la antigua, o un error. Es
esperable y se resuelve solo.

Para revisar, abre <https://www.neurosistemas.cl> en una **ventana de incógnito**: la
ventana normal guarda copias antiguas y te puede confundir.

---

## Si algo sale mal

El cambio es completamente reversible y no destruye nada.

Para volver atrás, entra a la misma pantalla del Paso 3 y escribe de nuevo los dos
servidores que anotaste en el Paso 4:

```
ns1.siteground.net
ns2.siteground.net
```

El dominio vuelve a mostrar el WordPress antiguo en el mismo plazo de horas.

---

## Preguntas que quizás tengas

**¿Esto le da acceso a alguien externo a nuestro dominio?**
No. Los servidores nuevos son de una cuenta que administro yo a nombre del laboratorio, y
te la puedo traspasar o compartir cuando quieras. El dominio en sí sigue registrado a
nombre del laboratorio en NIC Chile, que es lo que determina la propiedad.

**¿Hay que pagar algo?**
No. La página nueva está alojada gratis y sin límite de visitas. El servicio de DNS que
vamos a usar también es gratuito. Lo único que se sigue pagando es la renovación anual del
dominio en NIC Chile, igual que hasta ahora.

**¿Se pierde el contenido del sitio antiguo?**
No. Todo está rescatado y ya publicado en la página nueva: las líneas de investigación,
el equipo completo, los ex miembros y el listado de publicaciones desde 1988.

**¿Y lo que aparece en Google?**
Durante unas semanas, algunos resultados de Google pueden llevar a direcciones que ya no
existen. Se corrige solo a medida que Google vuelve a indexar el sitio. Dejé
redirecciones para las direcciones más usadas del sitio antiguo, así que buena parte de
esos enlaces va a seguir funcionando.

**¿Puedo hacerlo yo solo o prefieres que lo hagamos juntos?**
Como prefieras. Si quieres, coordinamos una videollamada de diez minutos y lo hacemos
mientras conversamos: yo te voy indicando y tú aprietas.

---

## Resumen

1. Entrar a <https://clientes.nic.cl>
2. Abrir `neurosistemas.cl` → **Configuración técnica** → **Servidores DNS**
3. **Anotar** los dos servidores que están
4. Reemplazarlos por los dos que te pasé
5. Dejar **desmarcada** la casilla de servidor secundario de NIC Chile
6. **Actualizar datos de dominio**
7. Avisarme

Cualquier duda, escríbeme antes de apretar.
