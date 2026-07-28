# Fix: actualizar dominio viejo `035.ihes.mx` -> `normaia.ihes.mx`

## Contexto

Jorge recordaba que ya no se usaba nada con el dominio `035.ihes.mx`. Antes
de tocar codigo se investigo si el dominio seguia vivo: se confirmo por
navegador que `https://035.ihes.mx` **sigue resolviendo y sirviendo la app
real** (mismos assets, mismo `app.js`/`toastr`/`blockUI` que produccion
actual), es decir, no es un dominio muerto sino el dominio viejo antes de la
migracion a `normaia.ihes.mx` (VPS propio, ver ESTADO.md linea ~1979).

Ya existia un precedente de este mismo tipo de bug: en una sesion anterior
se corrigieron los links de verificacion de correo / recuperacion de
contrasena que apuntaban a `035.ihes.mx` en vez de `normaia.ihes.mx`
(ESTADO.md linea ~2125-2126). Esta correccion cierra los casos que quedaron
fuera de ese fix.

## Cambios

1. `surveys/templates/survey.html` (linea ~289): redirect JS entre pasos
   del cuestionario (registro -> trauma -> riesgo A/B), ruta activa y
   principal del flujo de encuesta de empleados.
2. `surveys/views.py`:
   - Comentario informativo linea 51 (formato historico de enlace).
   - `Index.get()` linea ~223: `access_code` usado para compartir por
     WhatsApp, envuelto en Firebase Dynamic Link (`n035.page.link`).
   - `PDFCreate` (dos ocurrencias casi identicas, ~477-489 y ~3278-3279):
     URLs `chart1..4` y `pdf` usadas para descargar graficas/PDF de
     resultados generados.
   - Linea ~1715: enlace de WhatsApp para invitar a contestar encuestas
     (mismo patron Firebase Dynamic Link que el punto anterior).
3. `surveys/templates/tyc.html` (linea ~172): mencion textual del dominio
   dentro de los Terminos y Condiciones.

## Fuera de alcance (decision explicita de Jorge)

- Referencias a `035.ihes.mx` en el bot de Facebook Messenger
  (`surveys/views.py` lineas ~3330-3420): Jorge confirmo que ese bot **ya
  no esta activo**, se dejan sin tocar (codigo muerto, no vale la pena
  actualizar un dominio que ese flujo ya no usa).
- `nom035/settings.py` (`CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS`,
  lineas ~86 y ~91): son solo valores *por defecto* si la variable de
  entorno no esta configurada en el VPS; el valor real de produccion vive
  en el `.env` del servidor, no en este repo. No se toco.

## Validacion

- `python -m py_compile surveys/views.py` -> OK.
- Verificado por navegador que `https://035.ihes.mx/app/access/` carga la
  misma app (confirma que el bug era cosmetico/de marca, no de
  disponibilidad: el flujo funcionaba, pero via el dominio incorrecto).
- Pendiente validar en produccion (VPS) tras el deploy: completar una
  encuesta de empleado de principio a fin y confirmar que cada redirect
  usa `normaia.ihes.mx`.
