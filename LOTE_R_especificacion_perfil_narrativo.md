# Lote R — PN-01 a PN-06: hallazgos de Perfil Narrativo (IA)

## Instrucciones operativas
- Repo: nom035, rama base: auditoria-local
- Crear rama nueva: git checkout auditoria-local && git pull && git checkout -b fix/lote-r-perfil-narrativo
- Entorno: usar el venv existente
- **`surveys/psico_views.py` usa 4 ESPACIOS para indentación** (confirmado con `cat -A`), a diferencia de `surveys/views.py` que usa TABS. `surveys/models.py` usa TABS (confirmado). Verificar con `cat -A` antes de insertar cualquier línea nueva en cada archivo y respetar el estilo LOCAL de cada uno — no asumir que todo el proyecto usa el mismo estilo.
- Migración manual escrita a mano, número siguiente disponible: `0039_...` (la última existente es `0038_unique_survey_per_evaluation.py`). NO usar `makemigrations` real.
- `django.utils.timezone` ya está importado en `psico_views.py` (línea 3) — usar `timezone.now()` para timestamps nuevos, no `datetime.now()`.
- `psico_views.py` NO tiene logger configurado todavía — agregar `import logging` y `p_ = logging.getLogger(__name__)` al inicio del archivo, mismo patrón ya usado en `surveys/views.py` (línea 46: `p_= logging.getLogger(__name__)`).

## Contexto

Los 6 hallazgos originales de la auditoría (PN-01 a PN-06, severidad Media) están todos en `GenerarPerfilNarrativoView` (`surveys/psico_views.py`, líneas 435-501). Esta vista genera el "Perfil Narrativo" con IA (Anthropic, modelo `claude-haiku-4-5-20251001`) a partir de los resultados psicométricos de un candidato. La conexión con el proveedor de IA YA FUNCIONA (`ANTHROPIC_API_KEY` configurada y con crédito en Railway staging) — eso ya no es un bloqueo, es la razón por la que estos hallazgos vuelven a ser prioritarios ahora.

Confirmado por revisión de código actual (no solo por el informe original):
- El ownership SÍ está bien resuelto (`get_object_or_404(TestSession, id=session_id, candidate__user=request.user, status='completada')`) — no hay IDOR aquí, no forma parte de los 6 hallazgos y no se toca en este lote.
- **No existe ningún botón ni JS en ningún template que dispare esta vista** — solo es alcanzable posteando directo a `/psico/perfil-narrativo/<session_id>/`. No hay UI que agregar en este lote (fuera de alcance), pero es relevante saber que cualquier prueba manual debe hacerse con POST directo (fetch/Postman), no navegando la UI.

## Cambios requeridos

Todos los cambios son dentro de `GenerarPerfilNarrativoView` (`surveys/psico_views.py`, líneas 435-501), salvo el nuevo campo del modelo.

### 1. surveys/models.py — nuevo campo en TestResult (resuelve PN-02 y PN-03 juntos)
Agregar, justo después de `perfil_narrativo` (línea 624):
```python
perfil_narrativo_historial = models.JSONField(u'Historial de perfiles narrativos (IA)', default=list)
```
Cada elemento del historial es un dict: `{"texto": str, "timestamp": str ISO-8601, "usuario_id": int, "modelo": str}`. `perfil_narrativo` (el campo `TextField` existente) se sigue usando como "el perfil actual" para no romper `psico_reporte.html` (línea 131-135, que lee `r.perfil_narrativo` directo) — no cambiar esa plantilla. El campo nuevo es el registro histórico/auditable de cada generación y regeneración, con su propio timestamp (esto cierra PN-03 sin necesitar un campo de fecha separado).

Migración manual nueva `surveys/migrations/0039_perfil_narrativo_historial.py`: un solo `AddField`, dependencia a `0038_unique_survey_per_evaluation`. Campo con `default=list` no requiere backfill de datos existentes.

### 2. surveys/psico_views.py — GenerarPerfilNarrativoView.post()

**PN-05 (límite de regeneraciones) — va primero en el flujo**, antes de llamar al proveedor de IA: justo después de obtener `result = get_object_or_404(TestResult, session=session)` (línea 448), agregar:
- Si `len(result.perfil_narrativo_historial) >= 5`: responder `JsonResponse({'error': 'Se alcanzó el límite de regeneraciones para este perfil.'}, status=429)` y no continuar (no llamar al proveedor).
- Si hay al menos 1 entrada previa en el historial: comparar su `timestamp` contra `timezone.now()`; si pasaron menos de 60 segundos, responder `JsonResponse({'error': 'Espera un momento antes de generar el perfil de nuevo.'}, status=429)` y no continuar.
- Ambos límites (5 y 60s) como constantes al inicio de la vista o del método, con nombre descriptivo (ej. `MAX_REGENERACIONES = 5`, `COOLDOWN_SEGUNDOS = 60`), no como números mágicos sueltos.

**PN-06 (minimizar PII en el prompt)**: en las 5 ramas de construcción del prompt (líneas 457, 461, 464, 470, 474), quitar el nombre del candidato del texto que se envía al proveedor. Cambiar el patrón `"...sobre el candidato {candidato} que aplica al puesto de {puesto}..."` por `"...sobre un candidato que aplica al puesto de {puesto}..."` en las 5 ocurrencias. La variable `candidato` (línea 451, `candidato = session.candidate.nombre`) queda sin uso en ningún otro punto de la función una vez quitada de los 5 prompts (confirmado con grep sobre todo el archivo) — eliminar esa línea de asignación por completo. NO tocar cómo se muestra el nombre en la UI/reportes, solo lo que se le manda al proveedor externo.

**PN-01 (respuesta vacía aceptada)**: dentro del bloque `try` (línea 493-499), después de extraer `texto = data["content"][0]["text"]`, validar `texto.strip()`. Si está vacío (o, opcionalmente, si tiene menos de ~20 caracteres — usar buen criterio, no sobre-especificar), NO hacer `result.save()`, y responder `JsonResponse({'error': 'El proveedor de IA devolvió una respuesta vacía, intenta de nuevo.'}, status=502)`. El `perfil_narrativo` (y el historial) existentes deben quedar intactos si la respuesta es inválida.

**PN-02 (historial en vez de sobrescritura)**: cuando la respuesta SÍ es válida, en vez de solo `result.perfil_narrativo = texto; result.save()`, además hacer `result.perfil_narrativo_historial.append({...})` con el timestamp actual (`timezone.now().isoformat()`), `usuario_id=request.user.id`, `modelo='claude-haiku-4-5-20251001'` (mismo string ya usado en el payload, no hardcodear un segundo literal — reutilizar la constante/valor existente), y guardar. `perfil_narrativo` sigue actualizándose al texto más reciente (comportamiento visible sin cambios para el usuario).

**PN-04 (no filtrar `str(e)` al cliente)**: en el `except Exception as e:` (línea 500-501), loguear el detalle real con `p_.error(f"Error generando perfil narrativo para session_id={session_id}: {e}")`, y responder al cliente `JsonResponse({'error': 'No se pudo generar el perfil narrativo, intenta de nuevo más tarde.'}, status=500)` — sin incluir `str(e)` en la respuesta HTTP.

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/psico_views.py surveys/models.py` sin errores
2. Confirmar que la migración `0039` se puede aplicar sobre una base local/staging sin error (`python manage.py migrate` en el entorno de prueba correspondiente, NUNCA contra producción)
3. Probar directamente contra el endpoint (POST a `/psico/perfil-narrativo/<session_id>/` con una sesión de prueba completada, ya que no hay UI):
   - Generación normal → 200, `perfil_narrativo` se actualiza, `perfil_narrativo_historial` tiene 1 entrada nueva con timestamp
   - Confirmar que el prompt enviado (loguearlo temporalmente durante la prueba, o inspeccionar el payload) ya NO incluye el nombre del candidato en ninguna de las 6 ramas de instrumento
   - Regenerar antes de que pasen 60 segundos → 429, sin llamar al proveedor de nuevo, historial NO crece
   - Regenerar 5 veces (esperando el cooldown entre cada una) y luego un sexto intento → 429 por límite alcanzado
   - Simular/forzar una respuesta vacía del proveedor si es posible (o revisar por código que la validación efectivamente bloquea el guardado) → error controlado, `perfil_narrativo` anterior NO se sobrescribe
   - Simular un error del proveedor (ej. API key inválida temporalmente, o un timeout) → confirmar que la respuesta al cliente NO incluye el texto de la excepción, y que SÍ aparece en los logs de Railway vía `p_.error(...)`
4. Confirmar que `psico_reporte.html` sigue mostrando el perfil narrativo actual sin cambios visuales (sigue leyendo `r.perfil_narrativo`, ese campo no cambió de significado)

## Fuera de alcance de este lote (no tocar)
- Agregar una UI/botón para disparar esta vista — no existe hoy, no es parte de los 6 hallazgos, se evalúa aparte si Jorge lo pide
- Ownership/autorización de la vista — ya está correctamente resuelto, confirmado en este mismo diagnóstico
- Cualquier otro instrumento o vista de reportes (`ReporteUnificadoView`, `psico_reporte.html` más allá de lo indicado) — sin cambios
- SMTP, INFRA-001 — pendientes aparte, sin relación
