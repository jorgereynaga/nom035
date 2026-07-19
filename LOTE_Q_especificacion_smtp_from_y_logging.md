# Lote Q — Remitente SMTP hardcodeado + observabilidad de errores de envío de correo

## Instrucciones operativas
- Repo: nom035, rama base: auditoria-local
- Crear rama nueva: git checkout auditoria-local && git pull && git checkout -b fix/lote-q-smtp-from-y-logging
- Entorno: usar el venv existente
- `surveys/views.py` usa TABS para indentación en las clases `EmailVerification` y `PasswordRecover` (confirmado con `cat -A`) — respetar el estilo exacto.
- `nom035/settings.py` sigue el patrón de `config()` ya usado para `EMAIL_HOST`/`EMAIL_HOST_USER`/etc. (Lote D y Lote P).
- No requiere migración de base de datos.
- Dos cambios independientes en el mismo lote, descritos por separado abajo — no mezclarlos ni tocar nada fuera de lo indicado.

## Contexto

Al cambiar la cuenta de Gmail usada para SMTP en Railway staging (de `n035.ihes@gmail.com` a `normaia.sistemas@gmail.com`, vía las variables de entorno `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` ya movidas en el Lote P), registrar/reenviar verificación de una cuenta nueva empezó a fallar con el mensaje "No pudimos enviarte un correo de confirmación, si tienes problemas contacta con soporte."

### Causa raíz 1 (confirmada, FIX PRINCIPAL)
`surveys/views.py`, función `send_mail()` (línea 134-140, es una función wrapper propia del proyecto, NO la de Django):
```python
def send_mail(to_emails,ctx,template='email-template.html',subject='...',text_content='...'):
	from_email='IHES <n035.ihes@gmail.com>'
	htmly=get_template(template)
	html_content=htmly.render(ctx)
	msg=EmailMultiAlternatives(subject, text_content, from_email, to_emails)
	msg.attach_alternative(html_content, "text/html")
	return msg.send()
```
El remitente (`From:`) está hardcodeado a la cuenta VIEJA, mientras que la autenticación SMTP (`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`) ahora usa la cuenta NUEVA. Gmail rechaza el envío cuando el remitente del mensaje no coincide con la cuenta autenticada (protección anti-spoofing) — esto explica el fallo actual.

### Causa raíz 2 (confirmada, motivo por el que no se puede ver el error real en logs)
Dos bloques `except:` desnudos capturan CUALQUIER excepción sin loguear nada:
- `EmailVerification.post()`, línea 703-704
- `PasswordRecover.post()`, línea 761-762 (el que envuelve específicamente el `send_mail(...)` de la rama `if email!="":` — **NO tocar** el otro `except:` de esa misma clase, línea 780-781, que envuelve la desencriptación/validación del código de recuperación, es lógica de seguridad ya revisada y cerrada en el Lote O, sin relación con el envío de correo)

## Cambio requerido

### 1. FIX PRINCIPAL — remitente SMTP consistente con la cuenta autenticada

**nom035/settings.py**, agregar junto a las variables de EMAIL ya existentes (líneas 183-188, después de `EMAIL_USE_TLS`):
```python
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
```
El default debe ser la variable `EMAIL_HOST_USER` ya definida arriba en el mismo archivo (no un string literal nuevo) — así, mientras no se configure `DEFAULT_FROM_EMAIL` explícitamente en Railway, el remitente siempre coincide automáticamente con la cuenta que autentica, sin importar cuál sea.

**surveys/views.py**, función `send_mail()` (línea 134-140): reemplazar
```python
from_email='IHES <n035.ihes@gmail.com>'
```
por
```python
from_email=f'NormaIA <{settings.DEFAULT_FROM_EMAIL}>'
```
(confirmar que `settings` ya está importado en este archivo — sí lo está, se usa en otras partes como `settings.RECAPTCHA_SECRET_KEY`). El nombre visible se actualiza de "IHES" a "NormaIA" para reflejar el rebranding ya aplicado en el resto del proyecto (ver ESTADO.md, sección "Branding: IHES → NormaIA").

### 2. FIX DE OBSERVABILIDAD — loguear el error real sin cambiar el comportamiento visible

En `surveys/views.py`, el archivo ya tiene un logger configurado (línea 46: `p_= logging.getLogger(__name__)`), usado en otras partes del archivo (ej. `p_.error(...)` en `UserappList.post()`). Usar el mismo patrón, NO crear un logger nuevo.

**EmailVerification.post()**, línea 703-704:
```python
					except:
						messages.success(request, "email_error")
```
cambiar a:
```python
					except Exception as e:
						p_.error(f"Error enviando correo de verificacion a {user.email}: {e}")
						messages.success(request, "email_error")
```

**PasswordRecover.post()**, línea 761-762 (SOLO este, no el de línea 780):
```python
				except:
					messages.success(request, "email_error")
```
cambiar a:
```python
				except Exception as e:
					p_.error(f"Error enviando correo de recuperacion a {user.email}: {e}")
					messages.success(request, "email_error")
```

El mensaje que ve el usuario final (`messages.success(request, "email_error")`, renderizado como "No pudimos enviarte un correo de confirmación...") NO cambia — el único cambio funcional es que ahora la excepción real queda registrada en los logs de Railway antes de mostrar el mensaje genérico.

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/views.py nom035/settings.py` sin errores
2. Confirmar con grep que ya no queda ningún `n035.ihes@gmail.com` hardcodeado como remitente en `send_mail()`: `grep -n "n035.ihes@gmail.com" surveys/views.py` — debe devolver vacío (o solo comentarios/código muerto ya existente y sin relación, confirmar caso por caso si aparece algo)
3. Confirmar que los 2 `except:` de este lote ahora son `except Exception as e:` con `p_.error(...)`, y que el otro `except:` de `PasswordRecover.post()` (línea ~780, validación de código) sigue intacto, sin tocar
4. Si es posible probar en staging: intentar registrar una cuenta nueva o reenviar verificación, confirmar en los logs de Railway que aparece la línea de `p_.error(...)` con el detalle real del error de SMTP (si el envío sigue fallando por cualquier motivo) — esto es lo que permitirá diagnosticar de una vez si el problema queda resuelto con el fix del remitente, o si hay una causa adicional

## Fuera de alcance de este lote (no tocar)
- El `except:` de la validación de código en `PasswordRecover.post()` (línea ~780) — lógica de seguridad del Lote O (SEC-006), no relacionada con envío de correo
- `UserappList.post()` — el registro de cuentas ya no envía correo (código comentado deliberadamente, `validated_email=True` se marca directo), sin cambios
- Cualquier otro uso de `send_mail()` en el archivo — todos pasan por la misma función corregida en el punto 1, no requieren cambios individuales
- SEC-006, INFRA-001, PN-01 a 06 — pendientes aparte
