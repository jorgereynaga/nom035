# Contenerización del proyecto — Dockerfile + docker-compose (dev y VPS)

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b feature/dockerizacion`
- Archivos nuevos únicamente — no se toca ningún `.py` de `surveys/`, ni `settings.py`, ni el `Procfile`/`nixpacks.toml` existentes (esos siguen usándose para Railway, que no se toca en este lote).
- No requiere migración, no requiere `py_compile` de nada (son archivos de infraestructura, no Python).

## Contexto y objetivo

Jorge va a mover el proyecto a un VPS propio (fuera de Railway). Railway usa Nixpacks para construir el contenedor automáticamente a partir de `nixpacks.toml` + `Procfile` + `requirements.txt` — en el VPS no hay Nixpacks, así que se necesita un `Dockerfile` explícito + `docker-compose.yml` para levantar el proyecto ahí (y de paso, sirve también para desarrollo local en vez de depender del venv).

## Decisiones ya tomadas (no repetir la investigación ni la discusión)

1. **WeasyPrint NO se intenta arreglar en este lote.** Ya está roto hoy en Railway (warning "WeasyPrint could not import some external libraries" en cada deploy), el código que lo usa (`pdf_reports_task` en `surveys/tasks.py`, disparado desde `SaveCharts`/`PDFCreate` en `surveys/views.py`) es código muerto confirmado — ninguna plantilla ni JS del frontend llama a `/api/save_chart/` ni `/api/create_pdf/`. El Dockerfile **no necesita instalar** las librerías nativas de WeasyPrint (`pango`, `cairo`, `harfbuzz`, etc. — lo que sí tiene `nixpacks.toml` hoy). Si en el futuro se decide arreglar WeasyPrint de verdad, es un lote aparte.
2. **Celery/Redis quedan completamente afuera.** Confirmado: no hay worker de Celery corriendo hoy en producción (`Procfile` solo define el proceso `web`), `CELERY_BROKER_URL` apunta a un `amqp://localhost` que no existe, y las 2 únicas llamadas `.delay()` en el código son inalcanzables desde el frontend. No se agrega ningún servicio de Celery/Redis a `docker-compose.yml`.
3. **Se entregan ambos**: `Dockerfile` (para producción en el VPS) + `docker-compose.yml` (con un servicio `db` de Postgres, útil también para desarrollo local en vez del venv + Postgres nativo que se usa hoy).

## Datos ya investigados (no repetir)

- **Python**: `3.11.9` (ver `.python-version`, coincide con lo que muestra Railway)
- **`requirements.txt`** ya existe con todas las dependencias — incluye `celery==5.3.6` y `redis==5.0.1`, que ya no se necesitan para correr el contenedor (ver decisión #2), pero **no los quites de `requirements.txt` en este lote** — eso es un cambio de dependencias del proyecto completo, fuera de alcance aquí (que Jorge lo decida aparte si quiere).
- **Comando de arranque** (`Procfile` actual, replicar la misma secuencia en el `CMD`/entrypoint del contenedor):
  ```
  python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py cargar_disc && python manage.py cargar_moss && python manage.py cargar_raven && python manage.py cargar_zavic && python manage.py cargar_competencias && python manage.py cargar_comercial && gunicorn nom035.wsgi --log-file - --timeout 120 --workers 1 --threads 2 --preload
  ```
  Los comandos `cargar_*` son idempotentes (ya confirmado en logs de Railway: "DISC ya esta cargado, omitiendo", etc.) — seguros de correr en cada arranque del contenedor.
- **Static/media** (`nom035/settings.py`):
  - `STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'`, `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')` — whitenoise sirve los estáticos directo desde la app, no se necesita nginx para estáticos.
  - `PERSISTENT_STORAGE_ROOT = config('PERSISTENT_STORAGE_ROOT', default=BASE_DIR)`, y `MEDIA_ROOT`/`PROTECTED_MEDIA_ROOT` cuelgan de ahí — en Railway apunta al mount path del Volume persistente (fix de INFRA-001). En el VPS, `PERSISTENT_STORAGE_ROOT` debe apuntar a un volumen Docker montado (para que archivos subidos por usuarios sobrevivan a un `docker-compose up --build`), no al filesystem efímero del contenedor.
- **Variables de entorno usadas hoy** (todas vía `python-decouple` `config()` u `os.environ.get()` en `settings.py`, `surveys/psico_views.py`):
  - `SECRET_KEY` (requerida, sin default)
  - `ALLOWED_HOSTS` (requerida, sin default, separada por comas)
  - `DATABASE_URL` (requerida, sin default — formato `postgresql://user:pass@host:port/dbname`)
  - `DEBUG` (default `False`)
  - `AES_ENCRYPTION_KEY` (default inseguro `test1234test1234` — ya documentado como hallazgo SEC-006 pendiente en la matriz de auditoría, no es parte de este lote)
  - `RECAPTCHA_SECRET_KEY` / `RECAPTCHA_SITE_KEY` (tienen default hardcodeado en `settings.py`)
  - `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` (tienen default hardcodeado a los dominios de Railway — **para el VPS, si el dominio final es distinto, hay que pasarlos como env var explícita**, anotar esto en el `.env.example` con un comentario)
  - `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` / `DEFAULT_FROM_EMAIL` (⚠️ **hallazgo nuevo encontrado durante esta investigación, anótalo tal cual en el `.env.example` con un comentario de advertencia, no lo arregles aquí**: `EMAIL_HOST_PASSWORD` tiene como *default* una contraseña de aplicación de Gmail con apariencia real hardcodeada en `settings.py` — el fix histórico de SEC-005 movió las credenciales a variables de entorno pero dejó el valor real como fallback si la env var no está seteada. Esto debería reportarse como hallazgo nuevo para la matriz de auditoría en una sesión aparte, **no corregirlo en este lote de dockerización**.)
  - `STRIPE_PUBLIC_KEY` / `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` (default `''`)
  - `PERSISTENT_STORAGE_ROOT` (default `BASE_DIR`, ver arriba)
  - `ANTHROPIC_API_KEY` (usada en `surveys/psico_views.py:502`, default `''`)

## Archivos a crear

### 1. `Dockerfile` (raíz del repo)

Requisitos:
- `FROM python:3.11.9-slim` (o `-bookworm`, usar buen criterio de cuál imagen base slim de Python 3.11.9 esté disponible y sea estable)
- Instalar solo las dependencias de sistema estrictamente necesarias para `pip install -r requirements.txt` (probablemente `build-essential`/`gcc` y headers de libpq si `psycopg2-binary` los llegara a necesitar en esa imagen base — usualmente `psycopg2-binary` trae wheels precompilados y no necesita nada extra, pero verificar con un build de prueba). **No instalar las libs de WeasyPrint** (decisión #1 arriba).
- Copiar `requirements.txt` primero e instalar dependencias antes de copiar el resto del código (para aprovechar cache de capas de Docker).
- Copiar el resto del código de la aplicación.
- Exponer el puerto que use `gunicorn` (verificar cuál puerto usa Railway hoy vía la variable `PORT`, o fijar uno explícito como `8000` para el VPS ya que no hay una variable `$PORT` dinámica fuera de Railway — usar buen criterio, revisar si `gunicorn nom035.wsgi` en el `Procfile` actual depende de `$PORT` o usa un puerto fijo).
- El `CMD` del Dockerfile debe replicar la secuencia completa del `Procfile` (migrate, collectstatic, los 6 `cargar_*`, luego `gunicorn`).
- Usar buen criterio para agregar un `.dockerignore` correspondiente (ver abajo) para no copiar `venv/`, `.git/`, `db.sqlite3`, `media/`, `staticfiles/`, `__pycache__/`, archivos de especificación `.md`, etc. dentro de la imagen.

### 2. `docker-compose.yml` (raíz del repo)

Dos servicios:
- **`web`**: build desde el `Dockerfile` de este mismo repo, `env_file: .env` (Jorge llena su propio `.env` a partir de `.env.example`, nunca commitear un `.env` real), puerto mapeado al host, `depends_on: db`, volumen montado para `PERSISTENT_STORAGE_ROOT` (ej. un volumen nombrado `media_data` mapeado a la ruta que uses como `PERSISTENT_STORAGE_ROOT` dentro del contenedor) para que sobreviva a rebuilds.
- **`db`**: `postgres:15` (o la versión estable que uses de criterio, verificar compatibilidad con `psycopg2-binary==2.9.9` y Django 3.2 — debería ser compatible con cualquier Postgres reciente), variables `POSTGRES_DB`/`POSTGRES_USER`/`POSTGRES_PASSWORD` que coincidan con lo que se ponga en `DATABASE_URL` del `.env`, volumen nombrado para el directorio de datos de Postgres (para no perder la BD local entre reinicios).
- **Sin servicio de Celery ni Redis** (decisión #2).

### 3. `.dockerignore` (raíz del repo)

Excluir al menos: `venv/`, `.git/`, `.github/` si existiera, `__pycache__/`, `*.pyc`, `db.sqlite3`, `media/`, `staticfiles/`, `files/`, `*.md` (los archivos de especificación de lotes anteriores no deben viajar dentro de la imagen), `.env` (nunca debe copiarse al build), `node_modules/` si aplica.

### 4. `.env.example` (raíz del repo)

Listar **todas** las variables enumeradas arriba en "Variables de entorno usadas hoy", cada una con un comentario breve de qué es y si tiene default inseguro/hardcodeado que debería sobreescribirse en producción real. Sin valores reales, solo placeholders (ej. `SECRET_KEY=cambia-esto-por-una-clave-real`). Incluir el comentario de advertencia sobre `EMAIL_HOST_PASSWORD` y sobre `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS` necesitando el dominio real del VPS.

## Validación requerida antes de dar el lote por terminado
1. `docker compose build` sin errores.
2. `docker compose up` levanta ambos servicios, Postgres queda healthy, y el servicio `web` corre migrate/collectstatic/cargar_* sin tronar (con un `.env` de prueba local, `DATABASE_URL` apuntando al servicio `db` del compose, `SECRET_KEY`/`ALLOWED_HOSTS` con valores de prueba).
3. Confirmar que `http://localhost:<puerto mapeado>/login/` carga (aunque no haya datos reales, solo confirmar que Django responde y no hay un 500 de arranque).
4. Confirmar que un archivo subido a `MEDIA_ROOT` (ej. logo de perfil) sobrevive a `docker compose down && docker compose up` (prueba del volumen persistente).
5. Confirmar que `docker compose down -v` (borrando volúmenes) seguido de `docker compose up` reconstruye la BD desde cero sin errores (para asegurar que el flujo de "ambiente limpio" funciona, útil para cuando Jorge arme el VPS por primera vez).

## Fuera de alcance de este lote
- Arreglar WeasyPrint — ver decisión #1.
- Agregar Celery/Redis — ver decisión #2.
- Nginx/reverse proxy, HTTPS/certificados, configuración específica del VPS (firewall, dominio, DNS) — esto es un lote de infraestructura aparte, una vez que el contenedor ya funcione localmente.
- Corregir el hallazgo de `EMAIL_HOST_PASSWORD` con default hardcodeado — reportar aparte para la matriz de auditoría, no tocar el código de `settings.py` en este lote.
- Quitar `celery`/`redis` de `requirements.txt` — decisión de Jorge aparte, no se toca aquí.
- Cualquier cambio a `Procfile` o `nixpacks.toml` (Railway sigue funcionando con esos, sin cambios).
