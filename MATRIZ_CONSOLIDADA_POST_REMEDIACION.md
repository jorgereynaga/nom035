# Matriz consolidada de hallazgos — NormaIA (post-auditoría original)

Actualizado: 15 Jul 2026, sesión 14. Este documento complementa (no reemplaza) los 7 entregables originales de la auditoría del 13 Jul 2026 (`MATRIZ_FINAL_HALLAZGOS.md`, `INFORME_EJECUTIVO_NORMAIA_QA.md`, etc.). Aquí se consolidan: (1) hallazgos nuevos encontrados durante la remediación que NO estaban en los 22 originales, y (2) el estado de remediación de todo lo trabajado hasta ahora.

## Cómo usar este documento (para la otra cuenta de Claude)

1. Lee esto primero para entender qué ya se corrigió y qué falta
2. Revisa `ESTADO.md` (rama `auditoria-local`) para el detalle técnico completo de cada lote (archivos exactos, líneas, comandos)
3. El flujo de trabajo establecido: Claude investiga y escribe especificación → Codex implementa en rama nueva `fix/lote-X` → Jorge revisa diff → prueba en staging (Railway, environment `staging`, conectado a `auditoria-local` normalmente, se cambia temporalmente a la rama del lote durante pruebas) → merge a `auditoria-local` → NUNCA se ha llevado nada a producción real todavía (decisión explícita)

## Estado de remediación — hallazgos ORIGINALES de la auditoría (22 totales)

| ID | Título | Estado |
|---|---|---|
| N35-SEC-001 | Acceso horizontal NOM-035 (IDOR) | ✅ **CORREGIDO** — Lote A |
| EVI-SEC-001 | Archivos /media/ sin autenticación | ✅ **CORREGIDO** — Lote C2 |
| N35-INT-001 | Persistencia pese a HTTP 403 sin créditos | ⏳ Pendiente |
| N35-INT-002 | Duplicados y consumo repetido de créditos | ⏳ Pendiente |
| N35-INT-003 | Selección silenciosa `.last()` | ⏳ Pendiente |
| EVI-SEC-002 | EXE y contenido falso aceptados | ⏳ Pendiente |
| PSI-VAL-001 a 006 | Validación backend insuficiente en los 6 instrumentos | ⏳ Pendiente |
| DEP-001 | Migración 0023 duplica campo de 0022 | ✅ Confirmado y mitigado con `--fake` en staging (fix definitivo de migraciones aún no diseñado) |
| DEP-002 | Procfile omite 2 instrumentos | ✅ Confirmado, mitigado manualmente en staging (fix definitivo al Procfile aún no aplicado) |
| N35-FUN-004 | `employees_dt` devuelve 500 | ⏳ Pendiente (nota: el ownership de esta vista SÍ se corrigió en el Lote A, pero el comportamiento de error 500 en casos límite sigue sin revisar) |
| CLM-INT-001 | Reenvíos ilimitados Clima Laboral | ⏳ Pendiente |
| PN-01 a PN-06 | Hallazgos de Perfil Narrativo | ⏳ Pendiente (proveedor de IA aún no conectado realmente) |
| Resto (controles efectivos, descartados) | Sin cambios, siguen vigentes como estaban documentados |

## Hallazgos NUEVOS encontrados durante la remediación (no estaban en los 22 originales)

| ID propuesto | Título | Severidad | Estado | Dónde |
|---|---|---|---|---|
| N35-SEC-002 | `EmployeeList` sin filtro devolvía TODOS los empleados de la plataforma (no solo cruce de una cuenta) | Crítica | ✅ **CORREGIDO** — Lote A | `surveys/views.py`, `EmployeeList.get_queryset()` |
| N35-SEC-003 | `get_workplaces` aceptaba `user_id` externo del cliente, permitía enumerar centros de cualquier usuario | Alta | ✅ **CORREGIDO** — Lote A | `surveys/views.py` |
| N35-SEC-004 | 5 endpoints function-based completamente públicos, sin `@login_required` (`employees_dt`, `get_results`, `get_workplaces`, `get_departments`, `get_chart_data`) — más grave que N35-SEC-001 porque ni siquiera requería estar autenticado | Crítica | ✅ **CORREGIDO** — Lote A | `surveys/views.py` |
| EVI-SEC-003 | `download_file2`: falta rama `else` de validación de ownership cuando no hay token — permitía descargar PDF de resultados de cualquier empresa sin sesión | Alta | ✅ **CORREGIDO** — Lote C1 | `surveys/views.py` |
| BUG-001 | `UnboundLocalError` preexistente en `download_file2` (import local de `HttpResponse` ocultaba el global) — rompía descargas legítimas exitosas | Media (funcional, no seguridad) | ✅ **CORREGIDO** — Lote C1 | `surveys/views.py` |
| SEC-005 | Llave AES hardcodeada en `encript()`/`decript()` (`key="test1234test1234"`) | Alta | ⏳ **Pendiente — siguiente lote recomendado** | `surveys/views.py` ~línea 667-676 |
| SEC-006 | **CRÍTICO — bypass total de `PasswordRecover`**: el endpoint que cambia contraseña nunca revalida el código de verificación; explotable sin sesión, sin correo, sin importar si SMTP está configurado | **Crítica** | ⏳ **Pendiente — bloqueante antes de producción real** (decisión de Jorge) | `surveys/views.py`, clase `PasswordRecover` |
| SEC-007 | Secret key de reCAPTCHA hardcodeada (`"6Le3XCEtAAAAAFDF0__aZfnj9DQjwe6lkzdylREY"`) + site key hardcodeada en template | Alta | ⏳ Pendiente (mismo lote candidato que SEC-005) | `surveys/views.py` ~1873, `auth-register.html` |
| CONFIG-001 | `CSRF_TRUSTED_ORIGINS` y `CORS_ALLOWED_ORIGINS` hardcodeados en `settings.py`, no usan variable de entorno (inconsistente con `ALLOWED_HOSTS` que sí la usa) | Media | ⏳ Pendiente | `nom035/settings.py` ~80-88 |
| CONFIG-002 | Dominio placeholder sin usar en `CORS_ALLOWED_ORIGINS` (`"https://tu-frontend.com"`) | Baja/cosmético | ⏳ Pendiente | `nom035/settings.py` |
| INFRA-001 | **Sin Volume persistente en Railway** — archivos en `MEDIA_ROOT`/`PROTECTED_MEDIA_ROOT` se pierden en cada redeploy. Aplica también a producción actual | **Alta** (pérdida de datos, no vulnerabilidad de seguridad) | ⏳ **Pendiente — bloqueante antes de producción real** | Infraestructura Railway, no código |
| SEC-008 | Llaves de Conekta (pagos) comentadas y visibles en el código fuente | Baja | ⏳ Pendiente, revisar si son válidas o ya revocadas | `surveys/views.py` ~51-53 |
| SEC-009 | **CRÍTICO — Webhook de Stripe duplicado, la implementación "correcta" nunca se ejecuta.** `nom035/urls.py` registra `/stripe/webhook/` 3 veces; Django usa la primera coincidencia (línea 39, función `stripe_webhook()` en `surveys/views.py:2562`), dejando `StripeWebhookView` (`surveys/stripe_views.py`) como código muerto pese a parecer la implementación oficial. La función activa: solo maneja `checkout.session.completed` (cancelaciones de suscripción probablemente nunca se procesan), tiene un fallback peligroso (`User.objects.first()` si no encuentra al comprador — asignaría el plan pagado a un usuario cualquiera), y solo usa `print()` con emojis como logging. Presente también en `main` (producción). Encontrado durante el trabajo del dashboard de métricas de negocio (rama `auditoria-local`), no forma parte de ese lote. Detalle completo en `ESTADO.md`. | **Crítica** | ⏳ **Pendiente — requiere su propio lote y rama, validación completa en staging con Stripe test mode antes de tocar main** | `nom035/urls.py` líneas 39/114/136, `surveys/views.py:2562`, `surveys/stripe_views.py`, `surveys/services/credits.py` |

## Total actualizado

- **Hallazgos originales corregidos:** 2 de 22 (los 2 críticos: N35-SEC-001, EVI-SEC-001)
- **Hallazgos nuevos encontrados:** 13
- **Hallazgos nuevos corregidos:** 5 (N35-SEC-002, N35-SEC-003, N35-SEC-004, EVI-SEC-003, BUG-001)
- **Hallazgos nuevos pendientes:** 8 (SEC-005, SEC-006, SEC-007, CONFIG-001, CONFIG-002, INFRA-001, SEC-008, SEC-009)

## Recomendación de siguiente lote (decisión pendiente de Jorge al retomar)

**Lote D sugerido — Llaves hardcodeadas (SEC-005 + SEC-007):** ambos son el mismo patrón (CWE-798, secretos en código fuente), cambio relativamente contenido (mover a variables de entorno), y quick win de severidad Alta. Se pueden trabajar juntos en un solo lote.

**INFRA-001 (Volume persistente)** es importante pero es una decisión de infraestructura/Railway, no un lote de código con Codex — se puede resolver en paralelo sin bloquear el trabajo de seguridad (agregar un Volume en Railway es un clic en el dashboard, no requiere especificación para Codex). Se recomienda resolverlo cuando Jorge tenga un momento, sin que compita por prioridad con los lotes de seguridad.

**SEC-006 (PasswordRecover)** ya se decidió dejarlo para el final, justo antes de llevar el proyecto a producción real — es el hallazgo más grave que queda, pero Jorge prefiere cerrarlo como último paso.

## Reglas de trabajo vigentes (recordatorio para continuidad)

- Migraciones siempre manuales, nunca `makemigrations` real (solo diagnóstico con `--check --dry-run`)
- Cada lote en su propia rama `fix/lote-X`, partiendo de `auditoria-local` actualizada
- Codex necesita instrucción EXPLÍCITA de "implementa la especificación completa" — no asume la acción solo con recibir el archivo
- Para pruebas en staging que requieran acceso directo a la base de datos: reactivar TCP Proxy en Postgres de staging (Settings → Networking → "+ New"), ESPERAR 1-2 minutos, usar `DATABASE_URL` sobreescrita en el comando (nunca `railway run`), ELIMINAR el proxy después de cada uso
- `CSRF_TRUSTED_ORIGINS` requiere ajuste temporal (sin commit final) cada vez que se prueba en staging con formularios POST — recordar revertirlo antes de mergear cada lote
- Ambiente de staging: proyecto Railway, environment `staging`, servicio de la app — cambiar el "Source" branch ahí para apuntar a la rama del lote durante pruebas, y regresar a `auditoria-local` después del merge