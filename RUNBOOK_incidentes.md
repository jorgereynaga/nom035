# Plan de contingencia — NormaIA (VPS de producción)

Guía de qué hacer si el sitio se cae o se comporta mal durante las pruebas de carga/ataque (o en cualquier otro momento). Ordenado de "más rápido de resolver" a "más grave".

**Infraestructura de referencia:**
- Droplet DigitalOcean `nom-035-srv-1609182030472-s-1vcpu-2gb-nyc3-01` (nyc3, 1 vCPU / 2GB).
- App en `/webapps/NormaIA`, corre con Docker Compose: servicio `web` (Django/gunicorn) + `db` (Postgres).
- Deploy normal: `cd /webapps/NormaIA && git pull && docker compose up -d --build web` (el propio contenedor corre `migrate` al arrancar — nunca correrlo aparte, ver incidente documentado en `ESTADO.md`).
- Backup diario automático (cron 3:15am): dump de la base de datos + volumen de media + `.env`/`docker-compose.yml`, comprimidos y subidos a Google Drive vía `rclone`. Retención 14 días. Log en `/root/backups/backup.log`.

---

## Escenario 0 — Freno de emergencia (si algo se ve muy mal y necesitas tiempo para pensar)

Si las pruebas están causando daño real (no solo lentitud) y quieres cortar el acceso mientras investigas:

```bash
cd /webapps/NormaIA
docker compose stop web
```

Esto apaga la aplicación (nadie puede entrar) sin tocar la base de datos ni borrar nada. Para levantarla de nuevo: `docker compose start web`.

---

## Escenario 1 — El sitio no responde / error 502, pero puedes entrar por SSH

El más probable durante las pruebas. El droplet está vivo, pero el contenedor de la app se cayó o se colgó.

1. **Diagnosticar:**
   ```bash
   cd /webapps/NormaIA
   docker compose ps
   ```
   Si `web` no aparece como "Up", se cayó.

2. **Ver por qué:**
   ```bash
   docker compose logs web --tail 100
   ```
   Busca: `OOM` (se quedó sin memoria — probable si las pruebas de carga son agresivas en un droplet de 2GB), tracebacks de Python, o que se quedó pegado en el arranque (migraciones, carga de datos).

3. **Revisar uso de recursos** (para saber si fue memoria/CPU lo que lo tumbó):
   ```bash
   docker stats --no-stream
   free -h
   ```

4. **Reintentar levantarlo:**
   ```bash
   docker compose up -d web
   ```
   Si no levanta, o si sospechas que el código quedó en mal estado, reconstruye:
   ```bash
   docker compose up -d --build web
   ```

5. **Confirmar que responde:**
   ```bash
   curl -I http://localhost:8000/
   ```

**Si se cae repetidamente por falta de memoria durante las pruebas:** es una señal de que el droplet (2GB RAM) no aguanta la carga que están generando, no necesariamente un bug — vale la pena avisarles a los que están probando que bajen la intensidad, o considerar escalar el droplet temporalmente desde el dashboard de DigitalOcean (Resize) mientras dura el ejercicio.

---

## Escenario 2 — La base de datos quedó en mal estado (datos corruptos, tablas dañadas, o quieres deshacer lo que las pruebas ensuciaron)

1. **Apaga la app primero** (para que nadie escriba mientras restauras):
   ```bash
   docker compose stop web
   ```

2. **Ubica el backup más reciente:**
   ```bash
   ls -lt /root/backups/db/ | head -5
   ```
   Si no está localmente (o quieres uno más viejo), bájalo de Drive:
   ```bash
   rclone ls gdrive:NormaIA-Backups/db/
   rclone copy gdrive:NormaIA-Backups/db/<archivo>.sql.gz /root/backups/db/
   ```

3. **Restaura** (esto reemplaza los datos actuales — confirma que es lo que quieres antes de correrlo):
   ```bash
   gunzip -c /root/backups/db/<archivo>.sql.gz > /tmp/restore.sql
   docker compose up -d db
   docker compose exec -T db psql -U $POSTGRES_USER -d $POSTGRES_DB < /tmp/restore.sql
   ```
   (`$POSTGRES_USER`/`$POSTGRES_DB` están en tu `.env` — revísalos con `cat .env` si no los recuerdas.)

4. **Levanta la app de nuevo:**
   ```bash
   docker compose up -d web
   ```

**Antes de cualquier prueba agresiva:** vale la pena correr un backup manual fresco justo antes de empezar (no esperar al cron de las 3:15am), así el punto de restauración es de minutos antes, no de horas:
```bash
/root/backups/backup_normaia.sh
```

---

## Escenario 3 — El droplet completo no responde (no hay SSH, está "colgado")

1. Entra al dashboard de DigitalOcean → tu droplet → pestaña **"Access"** → **"Launch Droplet Console"** (consola web, funciona aunque SSH esté caído).
2. Si desde ahí tampoco reacciona: botón **"Power Cycle"** (equivalente a desconectar y reconectar la energía — más agresivo que un reinicio normal, pero no borra el disco).
3. Una vez que vuelva a responder, repite el diagnóstico del Escenario 1.

---

## Escenario 4 — Pérdida total del droplet (borrado, comprometido más allá de recuperación, DigitalOcean lo suspende, etc.)

El peor caso. Reconstruir desde cero:

1. **Crear droplet nuevo** en DigitalOcean (mismo tamaño o mayor).
2. **Instalar Docker y Docker Compose** en el droplet nuevo.
3. **Clonar el código:**
   ```bash
   git clone https://github.com/jorgereynaga/nom035.git /webapps/NormaIA
   cd /webapps/NormaIA
   ```
4. **Restaurar configuración** — bajar de Drive el backup de config más reciente:
   ```bash
   rclone copy gdrive:NormaIA-Backups/config/<archivo>.tar.gz .
   tar -xzf <archivo>.tar.gz
   ```
   (esto trae de vuelta `.env` y `docker-compose.yml` con los valores reales — sin esto la app no arranca).
5. **Levantar la base de datos vacía**, luego restaurar el dump más reciente de Drive (mismos pasos que Escenario 2, pasos 2-3, pero con `db` recién creado).
6. **Restaurar media** (logos, resultados, evidencias subidas):
   ```bash
   rclone copy gdrive:NormaIA-Backups/media/<archivo>.tar.gz .
   docker compose up -d db
   tar -xzf <archivo>.tar.gz -C /var/lib/docker/volumes/normaia_media_data/_data/
   ```
   (ajusta la ruta exacta del volumen si difiere — confírmala con `docker volume inspect normaia_media_data`).
7. **Levantar todo:**
   ```bash
   docker compose up -d --build
   ```
8. **Actualizar DNS** si la IP del droplet nuevo cambió (registro A de `normaia.ihes.mx` apuntando a la IP nueva).

---

## Vacíos conocidos (pendientes, no bloqueantes para las pruebas de esta semana)

- **No hay snapshots automáticos del droplet completo** (solo backup de datos/config, no una imagen completa del servidor) — DigitalOcean ofrece "Droplet Backups" semanales de pago; lo evaluamos, Jorge no lo ha confirmado todavía. Sin esto, el Escenario 4 toma más tiempo (hay que reinstalar Docker a mano) pero sí es recuperable.
- **No hay firewall a nivel de red** (Cloud Firewall de DigitalOcean, o algo como Cloudflare) — si las pruebas incluyen un ataque volumétrico serio (no solo fuerza bruta a nivel de aplicación, que ya mitigamos con rate limiting esta semana), no hay una capa que lo filtre antes de llegar al droplet. Vale la pena considerarlo si las pruebas van a incluir ese tipo de carga.
- **Restaurar la base de datos completa** significa perder cualquier dato real capturado *después* del backup usado — para pruebas está bien (nadie tiene cuentas reales todavía, como confirmaste), pero una vez que haya clientes reales, este plan necesita un backup manual justo antes de cualquier prueba similar.
