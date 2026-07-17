# Lote N — N35-FUN-004: `employees_dt` devuelve 500 en casos límite

## Instrucciones operativas
- Repo: nom035, rama base: auditoria-local
- Crear rama nueva: git checkout auditoria-local && git pull && git checkout -b fix/lote-n-employees-dt-500
- Entorno: usar el venv existente
- `surveys/views.py` usa TABS para indentación (confirmado con `cat -A` en la función `employees_dt`, líneas ~1139-1229) — respetar el estilo exacto.
- No requiere migración de base de datos.

## Contexto
`employees_dt` (`surveys/views.py`, línea 1139) es el endpoint AJAX que alimenta el DataTable de empleados en `workplace_detail.html` y `workplace_results.html`. El ownership (`Workplace.objects.filter(id=workplace_id, user=request.user).exists()`) ya se corrigió en el Lote A — este lote es exclusivamente sobre el comportamiento de error en casos límite, no sobre autorización.

Se identificaron **2 causas raíz concretas y reproducibles** de `500 Internal Server Error`, ambas explotables por cualquier usuario autenticado (dueño legítimo del workplace o no, ya que el crash ocurre en la validación de parámetros, no en el chequeo de ownership) simplemente manipulando la query string de la petición AJAX:

### Causa 1 — `ZeroDivisionError` con `length=0`
Líneas 1165-1168:
```python
page=(start/length)+1
paginator = Paginator(query.order_by("{}{}".format(order_direction, ordering[order])), length)
try:
    workplaces = paginator.page(page).object_list
```
Si la petición incluye `length=0` en la query string (ej. `/employees_dt/<id>/<t>/<eval>/?draw=1&start=0&length=0&...`), `Paginator(..., 0).page(...)` internamente calcula `num_pages` como `hits / per_page`, lo que lanza `ZeroDivisionError`. Esta excepción NO es `PageNotAnInteger` ni `EmptyPage` (los únicos 2 casos que el `try/except` actual captura), así que se propaga sin control y Django responde 500.

### Causa 2 — `TypeError` / `KeyError` con parámetros faltantes o fuera de rango
Líneas 1142-1147:
```python
draw = int(request.GET.get('draw'))
start = int(request.GET.get('start'))
length = int(request.GET.get('length'))
search = request.GET.get('search[value]')
order_direction=request.GET.get('order[0][dir]')
order=int(request.GET.get('order[0][column]'))
```
Si `draw`, `start`, `length` u `order[0][column]` no vienen en la petición (`request.GET.get(...)` devuelve `None`), `int(None)` lanza `TypeError` sin control → 500.

Adicionalmente, línea 1156-1158:
```python
if order>3:
    order=0
order_direction='' if order_direction=='asc' else '-'
```
Solo cubre el caso `order` mayor a 3. Si `order` es negativo (ej. `order[0][column]=-1`), no se corrige, y la línea 1166 (`ordering[order]`, donde `ordering={0:...,1:...,2:...,3:...}` es un `dict`, no una lista) lanza `KeyError` sin control → 500.

### Causa raíz adicional (menor, ya documentada como pendiente en ESTADO.md, se corrige de paso en este lote)
Línea 1165: `page=(start/length)+1` usa división de punto flotante (`/`) en vez de entera (`//`) — no causa un crash por sí sola en el caso normal, pero es inconsistente con el uso esperado de `Paginator.page()` (que espera un número de página entero). Se corrige junto con el resto porque toca la misma línea.

## Cambios requeridos

### surveys/views.py — `employees_dt` (líneas ~1139-1170 aprox.)
1. Envolver la lectura y conversión de `draw`, `start`, `length`, `order` en un bloque que valide que existen y son enteros válidos ANTES de usarlos. Si falta alguno o no es convertible a `int`, responder `JsonResponse({'draw':0,'recordsTotal':0,'recordsFiltered':0,'data':[]}, status=400)` en vez de dejar que la excepción se propague. Ejemplo de patrón (ajustar al estilo con tabs del archivo):
   ```python
   try:
       draw = int(request.GET.get('draw'))
       start = int(request.GET.get('start'))
       length = int(request.GET.get('length'))
       order = int(request.GET.get('order[0][column]'))
   except (TypeError, ValueError):
       return JsonResponse({'draw':0,'recordsTotal':0,'recordsFiltered':0,'data':[]}, status=400)
   ```
2. Además, validar explícitamente `length` antes de usarlo en `Paginator`: si `length <= 0`, responder el mismo 400 (o, alternativa más permisiva: forzar `length=10` como valor por defecto razonable en vez de rechazar — se deja a criterio de Codex cuál de las dos opciones implementar, ambas cierran el hallazgo; preferible responder 400 por ser más explícito y consistente con el resto del fix).
3. Cambiar el chequeo `if order>3: order=0` por uno que cubra ambos extremos: `if order not in ordering: order = 0` (recordar que `ordering` se define más abajo en la función, línea 1155 — puede requerir mover esa línea antes de este chequeo, o mantener el orden actual del código si `ordering` ya está definido antes de usarse; confirmar el orden real de las líneas en el archivo antes de escribir el fix, no asumir el orden de este documento).
4. Cambiar `page=(start/length)+1` por `page=(start//length)+1` (división entera) — solo después de haber garantizado que `length` ya es un entero válido y mayor a 0 por los pasos anteriores.
5. NO tocar la lógica de negocio del resto de la función (armado de `arr`, whatsapp link, badges de riesgo, etc.) — el alcance es exclusivamente la validación de parámetros de entrada y el manejo de la paginación.

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/views.py` sin errores
2. Con una cuenta de prueba dueña de un workplace con al menos 1 empleado, probar contra `/employees_dt/<workplace_id>/0/<evaluation>/`:
   - Petición normal con `draw=1&start=0&length=10&order[0][column]=0&order[0][dir]=asc` → 200, datos correctos (sin regresión)
   - Petición con `length=0` (resto de parámetros normales) → 400, NO 500
   - Petición sin el parámetro `draw` → 400, NO 500
   - Petición sin el parámetro `start` → 400, NO 500
   - Petición sin el parámetro `length` → 400, NO 500
   - Petición con `order[0][column]=-1` → 400, o si se optó por no rechazar sino solo corregir a 0, confirmar que responde 200 sin crashear (según qué variante implementó Codex en el punto 3)
   - Petición con `order[0][column]=99` (ya cubierto antes por `order>3`) → sigue funcionando (200, no crash) — no debe romperse el comportamiento ya existente
3. Confirmar con el DataTable real de `workplace_detail.html` y `workplace_results.html` en staging que la tabla de empleados sigue cargando y paginando con normalidad (sin regresión funcional)

## Fuera de alcance de este lote (no tocar)
- Ownership check (ya corregido en Lote A)
- Lógica de armado de `arr`, badges de riesgo psicosocial, links de WhatsApp — sin cambios
- El patrón de URL `path('employees_dt/<int:workplace_id>/<int:t>/', employees_dt, name='employees_dt')` (sin `evaluation`) en `nom035/urls.py` línea 81 hace que la función crashee con `TypeError: missing 1 required positional argument: 'evaluation'` si alguien la invoca directamente — en la práctica NINGÚN template del proyecto usa esta variante de 2 segmentos (todos usan la de 3 segmentos con `evaluation`, confirmado con grep), así que no es explotable por el flujo normal de la aplicación. Queda anotado como hallazgo menor adicional pero NO se corrige en este lote para no ampliar el alcance — si se quiere cerrar también, la opción más simple sería agregar `evaluation=0` como valor por defecto en la firma de la función (ya existe la lógica que interpreta `evaluation==0` como "usar la última evaluación"), pero eso queda a decisión de Jorge para un lote aparte o un ajuste menor posterior
- SEC-006, INFRA-001, PN-01 a 06 — pendientes aparte
