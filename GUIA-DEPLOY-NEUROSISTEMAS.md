# Guía de despliegue — Laboratorio de Neurosistemas

Todo lo que hay que hacer, una vez, para poner el sitio en línea.
Cuenta de GitHub: **HayoBK** (hayo.bk@gmail.com).

---

## 1. Crear el repositorio y hacer el primer push

Desde la terminal, en `~/Git_Web/Neurosistemas`:

```bash
cd ~/Git_Web/Neurosistemas

# Validar el build antes de nada
HUGO_ENVIRONMENT=production hugo --minify        # verde = sin ERROR

git init -b main
git add .
git commit -m "Sitio inicial del Laboratorio de Neurosistemas en Hugo"

# Crear el repo directamente en GitHub (gh ya está autenticado como HayoBK)
gh repo create HayoBK/neurosistemas-web --public --source=. --remote=origin --push
```

Si prefieres crearlo a mano en github.com, después:

```bash
git remote add origin https://HayoBK@github.com/HayoBK/neurosistemas-web.git
git push -u origin main
```

> El remoto lleva `HayoBK@` en la URL para que este repo use esa cuenta sin
> tener que hacer `gh auth switch`, igual que en LabONCE.

## 2. Activar GitHub Pages

En el repo → **Settings → Pages**:

- **Source:** `GitHub Actions` (NO "Deploy from a branch").

Con eso, el workflow `.github/workflows/deploy.yml` se encarga del resto en cada
push a `main`. La primera corrida tarda ~1 minuto.

URL provisoria: `https://hayobk.github.io/neurosistemas-web/`

## 3. Permitir que el bot de ORCID escriba en el repo

En **Settings → Actions → General → Workflow permissions**:

- Marcar **Read and write permissions**.

Sin esto, el workflow `orcid.yml` puede leer ORCID pero no commitear el JSON.

Después, correr la sincronización una primera vez a mano desde la pestaña
**Actions → Sincronizar publicaciones desde ORCID → Run workflow**.

## 4. Completar los ORCID iD

Editar `data/orcid.yaml` y rellenar el campo `orcid` de cada persona.
Se buscan en <https://orcid.org> por nombre; tienen la forma `0000-0002-1825-0097`.

Mientras estén en blanco, la página de Publicaciones muestra solo el archivo
histórico curado (1988–2023), que ya está completo. Nada se rompe.

## 5. Conectar el dominio neurosistemas.cl

El dominio hoy apunta al hosting del WordPress. Cuando quieras mudarlo:

1. Crear el archivo `static/CNAME` con una sola línea:

   ```
   www.neurosistemas.cl
   ```

2. Cambiar `baseURL` en `config/_default/hugo.yaml` a `https://www.neurosistemas.cl/`.

3. En el panel DNS del dominio (NIC Chile o donde esté delegado):

   | Tipo  | Nombre | Valor |
   |-------|--------|-------|
   | CNAME | `www`  | `hayobk.github.io.` |
   | A     | `@`    | `185.199.108.153` |
   | A     | `@`    | `185.199.109.153` |
   | A     | `@`    | `185.199.110.153` |
   | A     | `@`    | `185.199.111.153` |

4. En **Settings → Pages → Custom domain**, escribir `www.neurosistemas.cl` y
   esperar la verificación. Después marcar **Enforce HTTPS**.

5. Dejar el WordPress viejo en línea unos días como respaldo, y recién entonces
   darlo de baja.

## 6. Editar sin código (Pages CMS)

1. Entrar a <https://pagescms.org> con la cuenta de GitHub del repo.
2. Autorizar el repositorio `neurosistemas-web`.
3. Pages CMS lee `.pages.yml` y arma los formularios solos: equipo, líneas de
   investigación, noticias, galería y datos de contacto.

Cada cambio guardado desde el CMS es un commit, y cada commit dispara el
despliegue automático.

## 7. Comandos del día a día

```bash
cd ~/Git_Web/Neurosistemas

hugo server -D                                   # previsualizar en localhost:1313
HUGO_ENVIRONMENT=production hugo --minify        # validar build
python scripts/orcid_sync.py                     # sincronizar publicaciones a mano

git add -A && git commit -m "..." && git push     # publicar
```
