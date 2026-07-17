# Lote P — Credenciales SMTP hardcodeadas en settings.py

## Instrucciones operativas
- Repo: nom035, rama base: auditoria-local
- Crear rama nueva: git checkout auditoria-local && git pull && git checkout -b fix/lote-p-smtp-env-vars
- Entorno: usar el venv existente
- `nom035/settings.py` no usa tabs consistentemente en esta sección (es un archivo de configuración estándar, con espacios) — seguir el estilo de las líneas ya migradas a `config()` en el mismo archivo (líneas 27-28, Lote D) como plantilla exacta.
- No requiere migración de base de datos.
- Este lote es EXCLUSIVAMENTE mover el valor de origen (de hardcodeado a variable de entorno con el mismo default), replicando el patrón ya usado y probado en el Lote D. NO es responsabilidad de este lote lograr que el envío de correo funcione de verdad en Railway (eso depende de causas externas al código — revisar por separado si Google bloqueó el inicio de sesión desde la IP de Railway, o si conviene migrar a un proveedor de email transaccional en el futuro).

## Contexto
`nom035/settings.py` líneas 183-188:
```python
#email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'n035.ihes@gmail.com'
EMAIL_HOST_PASSWORD = 'qwsloneabrhgcdgr'
EMAIL_USE_TLS = True
```
`EMAIL_HOST_USER` y, sobre todo, `EMAIL_HOST_PASSWORD` (una contraseña de aplicación real de Gmail, confirmada válida — CWE-798) están hardcodeados en texto plano en el código fuente. Mismo patrón exacto que `AES_ENCRYPTION_KEY` y `RECAPTCHA_SECRET_KEY`, ya corregidos en el Lote D (`nom035/settings.py` líneas 27-28):
```python
AES_ENCRYPTION_KEY = config('AES_ENCRYPTION_KEY', default='test1234test1234')
RECAPTCHA_SECRET_KEY = config('RECAPTCHA_SECRET_KEY', default='6Le3XCEtAAAAAFDF0__aZfnj9DQjwe6lkzdylREY')
```
`from decouple import config` ya está importado en el archivo (línea 24), no requiere import nuevo.

## Cambio requerido

### nom035/settings.py — líneas 183-188
Reemplazar:
```python
#email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'n035.ihes@gmail.com'
EMAIL_HOST_PASSWORD = 'qwsloneabrhgcdgr'
EMAIL_USE_TLS = True
```
por:
```python
#email
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='n035.ihes@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='qwsloneabrhgcdgr')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
```
Los `default=` deben ser EXACTAMENTE los valores actuales (mismo criterio que el Lote D: "mover sin alterar comportamiento" — mientras Railway no tenga las variables de entorno configuradas, el sistema debe seguir funcionando idéntico a como funciona hoy, ni mejor ni peor).

### No tocar
- Ningún otro archivo — este es un cambio de una sola sección en `settings.py`
- La lógica de `send_mail()` en `surveys/views.py` — sin cambios
- `PasswordRecover`, `EmailVerification` — sin cambios (ya se corrigió `PasswordRecover` en el Lote O, sin relación con este lote)

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile nom035/settings.py` sin errores
2. Confirmar que Django arranca sin errores localmente o en staging (`python manage.py check` o el deploy normal) — el comportamiento debe ser IDÉNTICO al actual mientras no se configuren las variables de entorno en Railway (sigue usando `n035.ihes@gmail.com` con la misma contraseña por default)
3. Confirmar con `grep -n "EMAIL_HOST_PASSWORD\|qwsloneabrhgcdgr" nom035/settings.py` que el valor solo aparece una vez, como `default=` de `config()` — no debe quedar ninguna otra ocurrencia hardcodeada suelta en el archivo

## Fuera de alcance de este lote (no tocar, ni intentar resolver aquí)
- Diagnóstico de por qué el envío real de correo falla en Railway (posible bloqueo de Google por IP, alerta de seguridad pendiente de aprobar en la bandeja de `n035.ihes@gmail.com`, o límites de Gmail SMTP para envío servidor-a-servidor) — Jorge lo investiga aparte
- Evaluar migrar a un proveedor de email transaccional dedicado (SendGrid, Mailgun, Amazon SES, etc.) — decisión de infraestructura a futuro, no es parte de este lote
- Configurar las variables de entorno reales en Railway (staging y producción) — acción manual de Jorge en el dashboard de Railway, fuera del alcance de un lote de código
- SEC-006 (ya cerrado, Lote O), INFRA-001 — pendientes aparte
