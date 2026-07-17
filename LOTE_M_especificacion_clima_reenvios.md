# Lote M — CLM-INT-001: reenvíos ilimitados en Clima Laboral

## Instrucciones operativas
- Repo: nom035, rama base: auditoria-local
- Crear rama nueva: git checkout auditoria-local && git pull && git checkout -b fix/lote-m-clima-reenvios
- Entorno: usar el venv existente
- surveys/views.py usa TABS para indentación — verificar el estilo del bloque exacto donde se inserta (esta clase en particular, `ClimaLaboralView`, usa 4 espacios en vez de tabs, a diferencia del resto del archivo — confirmar con `cat -A` antes de editar y respetar el estilo LOCAL de esa clase, no asumir tabs solo porque el resto del archivo los usa)
- No se requiere migración de base de datos para el fix mínimo (ver sección 2). Si se opta por la variante con campo nuevo (sección 3, opcional), sí requiere migración manual escrita a mano.

## Contexto
`ClimaLaboralView` (`surveys/views.py`, líneas ~2733-2760) expone un formulario público de Clima Laboral en `/clima/<access_code>/` — deliberadamente sin login, porque lo llenan los empleados de la empresa cliente, identificados solo por `access_code` del Workplace (no hay autenticación de empleado individual, la encuesta es anónima por diseño, y así debe seguir siendo).

El problema (CLM-INT-001, hallazgo original de la auditoría): el método `post()` no tiene ningún límite de envíos. Cualquiera con el link puede enviar el formulario un número ilimitado de veces (recargar la página de "gracias" y volver a enviar, o automatizarlo con un script), y cada envío crea un nuevo `WorkEnvironmentSurvey` sin ninguna verificación. Esto permite:
1. Inflar o sesgar artificialmente los promedios de las 8 dimensiones de clima laboral que ve el empleador en `ClimaResultadosView` (`clima_resultados.html`)
2. Un usuario malintencionado (ej. un empleado descontento, o alguien externo con el link) puede manipular el resultado enviando decenas de respuestas idénticas

## Cambio requerido

### 1. surveys/views.py — ClimaLaboralView.post()
Agregar un control de "un envío por sesión de navegador, por centro de trabajo", usando la sesión de Django (`request.session`), que ya está disponible sin requerir login:

- Al recibir un POST exitoso, marcar en la sesión: `request.session[f'clima_submitted_{wk.id}'] = True`
- Al inicio de `post()`, después de validar que `wk` existe y que el workplace tiene plan activo (no antes, para no revelar el resultado de esas validaciones a través del mensaje de "ya enviado"), verificar si `request.session.get(f'clima_submitted_{wk.id}')` es `True`. Si ya existe:
  - Responder con el mismo template `clima_gracias.html` (mismo `ctx={'workplace': wk}` que el flujo exitoso) pero con un flag adicional en el contexto, ej. `ctx['ya_enviado'] = True`, para que la plantilla pueda opcionalmente mostrar un mensaje distinto ("Ya registramos tu respuesta anteriormente, gracias") — no es estrictamente necesario cambiar el HTML en este lote si no hay tiempo, con que el backend bloquee el segundo `WorkEnvironmentSurvey.objects.create(...)` es suficiente para cerrar el hallazgo. Si se agrega el mensaje, mantenerlo simple, sin alarmar al usuario (no es un error, es informativo)
- También aplicar el mismo chequeo en `ClimaLaboralView.get()`: si `request.session.get(f'clima_submitted_{wk.id}')` es `True`, renderizar directamente `clima_gracias.html` en vez de mostrarle el formulario de nuevo (evita que el usuario vea el formulario vacío después de haber respondido y sea tentado a llenarlo otra vez)

### 2. Consideración de diseño — por qué sesión y no IP
No usar bloqueo por IP: es común que varios empleados de un mismo centro de trabajo respondan desde la misma red/IP pública de oficina (NAT), lo que bloquearía indebidamente a empleados legítimos distintos. El control por sesión de navegador es el balance correcto entre prevenir el abuso trivial (recargar/reenviar) sin bloquear a empleados reales distintos usando la misma red.

Esto NO es una solución perfecta contra un atacante sofisticado que borre cookies o use ventanas de incógnito repetidamente — es una mitigación razonable proporcional a la severidad Media del hallazgo original, consistente con que la encuesta es intencionalmente anónima y sin autenticación de empleado individual. No se requiere ni se pide una solución más robusta (ej. tokens únicos por empleado) en este lote.

### 3. Fuera de alcance de este lote (no implementar, solo dejar anotado)
- Un sistema de tokens/links únicos por empleado (requeriría rediseñar el flujo de distribución del link, hoy es un solo `access_code` compartido por todo el Workplace) — cambio mayor, no es lo que pide CLM-INT-001
- Límite de envíos totales basado en `Employee.objects.filter(workplace=wk).count()` — se descarta: la plantilla de clima no vincula respuesta a empleado, y el número de empleados registrados puede no coincidir con quién realmente responde (rotación de personal, etc.), agregaría complejidad sin cerrar el hallazgo de forma más efectiva que el control de sesión

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/views.py` sin errores
2. Prueba local o en staging: abrir `/clima/<access_code>/` de un Workplace con plan activo, llenar y enviar el formulario completo → confirmar HTTP 200, `clima_gracias.html` se muestra, 1 registro `WorkEnvironmentSurvey` creado
3. Sin cerrar el navegador (misma sesión): volver a `/clima/<access_code>/` (GET) → confirmar que ya NO muestra el formulario vacío, sino `clima_gracias.html` directamente
4. Intentar un POST directo a la misma URL con la misma sesión (ej. reenviando el formulario con el botón "atrás" del navegador, o repitiendo la petición) → confirmar que NO se crea un segundo `WorkEnvironmentSurvey` (el conteo en `ClimaResultadosView` para ese workplace debe seguir en 1)
5. Abrir el mismo link en una sesión distinta (ventana de incógnito, o borrar cookies) → confirmar que SÍ puede enviar una respuesta nueva (no se debe bloquear a un empleado legítimo distinto)
6. Confirmar que `ClimaResultadosView` (la vista del empleador, con login) no sufrió ningún cambio de comportamiento

## Fuera de alcance de este lote (no tocar)
- `ClimaResultadosView` — sin cambios
- Cálculo de dimensiones/promedios — sin cambios
- SEC-006, INFRA-001, PN-01 a 06 — pendientes aparte
