# Dashboard de métricas — Línea de tiempo de suscripciones nuevas (v2)

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local` (ya tiene mergeado el dashboard v1 + SEC-009 + rediseño Replit)
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b feature/dashboard-timeline-suscripciones`
- `surveys/dashboard_views.py` usa 4 espacios (archivo nuevo de la v1, no usa el estilo TABS de `models.py`/`views.py`) — mantener ese estilo.
- `surveys/templates/dashboard_metricas.html` fue rediseñado visualmente con Replit (commit `e010cb0b`) — usa las clases y variables CSS ya definidas ahí (`.section-card`, `.section-card-header`, `.section-title`, `.title-dot`, `var(--color-primary)`, `var(--text-secondary)`, `var(--border)`, `var(--radius-lg)`, `var(--shadow-sm)`, tipografía Inter/Plus Jakarta Sans) — no reinventar estilos nuevos, seguir el mismo lenguaje visual del resto del archivo.
- No se requiere migración nueva — esta feature solo agrega una query de lectura sobre `PlanPurchaseEvent`, que ya existe (`surveys/migrations/0040_plan_purchase_event.py`).
- `python -m py_compile surveys/dashboard_views.py` antes de dar el lote por bueno.

## Contexto y objetivo

Agregar al dashboard de métricas de negocio (`/metricas/`) una gráfica de línea de tiempo: **volumen de suscripciones nuevas por periodo** (altas, no clientes activos netos — ver aclaración abajo), respetando el mismo filtro de fechas (`fecha_inicio`/`fecha_fin`) que ya existe en la vista.

### Decisión de diseño ya confirmada con Jorge: "altas", no "activos netos en el tiempo"

Esta gráfica cuenta **eventos de compra nuevos** (`PlanPurchaseEvent.record_create`) agrupados por día o semana — es decir, cuántas suscripciones nuevas entraron cada día/semana. **No** es un conteo de "cuántos clientes estaban activos en cada momento del pasado" (eso restaría las cancelaciones, y hoy no existe un registro histórico con fecha de cada cancelación — `_stripe_handle_subscription_change`, en `surveys/views.py`, solo limpia `stripe_plan_key`/`psico_plan_key` en el momento, sin dejar rastro con fecha). Reconstruir un neto histórico es una feature futura distinta (requeriría un modelo hermano tipo `PlanCancellationEvent`), fuera de alcance aquí.

### Granularidad automática (sin agregar un selector nuevo en la UI)

Reutilizar el rango de fechas que ya filtra el resto del dashboard:
- Si `(fecha_fin - fecha_inicio).days <= 31`: agrupar **por día**.
- Si es mayor: agrupar **por semana** (inicio de semana ISO).

Esto cubre "por día viendo una semana" y "por semana viendo un mes" sin UI adicional — el mismo filtro de fechas que ya existe controla todo.

## Datos disponibles (ya investigado, no repetir)

`PlanPurchaseEvent` (`surveys/models.py`, agregado en la v1 del dashboard): `user` (FK), `plan_key`, `modulo`, `precio`, `periodo`, `stripe_customer_id`, `record_create` (auto_now_add). Append-only, nunca se edita ni se borra — es exactamente la fuente de verdad para "cuándo entró cada suscripción nueva".

## Cambios requeridos

### 1. surveys/dashboard_views.py — nueva lógica dentro de `DashboardMetricasView.get()`

Agregar, después del bloque que arma `profundidad_uso` (antes del `return render(...)`):

```python
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncWeek

# ... dentro de get(), después de armar profundidad_uso:

rango_dias = (fecha_fin - fecha_inicio).days
granularidad = 'dia' if rango_dias <= 31 else 'semana'
trunc_fn = TruncDate if granularidad == 'dia' else TruncWeek

eventos_qs = PlanPurchaseEvent.objects.filter(
    user__is_staff=False, user__is_superuser=False,
    record_create__gte=fecha_inicio, record_create__lte=fecha_fin,
).annotate(bucket=trunc_fn('record_create')).values('bucket').annotate(total=Count('id'))

conteo_por_bucket = {row['bucket']: row['total'] for row in eventos_qs}

timeline_labels = []
timeline_data = []
if granularidad == 'dia':
    cursor = fecha_inicio.date()
    fin = fecha_fin.date()
    paso = timedelta(days=1)
else:
    # Normalizar al inicio de semana (lunes) para que el primer bucket coincida con TruncWeek
    cursor = fecha_inicio.date() - timedelta(days=fecha_inicio.date().weekday())
    fin = fecha_fin.date()
    paso = timedelta(days=7)

while cursor <= fin:
    timeline_labels.append(cursor.strftime('%d/%m'))
    timeline_data.append(conteo_por_bucket.get(cursor, 0))
    cursor += paso
```

Y agregar `granularidad`, `timeline_labels`, `timeline_data` al diccionario de contexto del `render(...)` final.

**Notas importantes para quien implemente:**
- `conteo_por_bucket` usa como llave el `bucket` que devuelve Django (un objeto `date`), por eso el bucle de relleno también compara con objetos `date` (`cursor`, que es `.date()` de un datetime) — no mezclar `date` con `datetime` al buscar en el diccionario o las cuentas no van a coincidir nunca y la gráfica saldría siempre en cero.
- El relleno del rango completo (loop `while cursor <= fin`) es intencional: sin esto, si un día/semana no tuvo compras, Chart.js conectaría los puntos existentes saltándose el hueco, dando una impresión visual incorrecta de continuidad. Con el relleno, esos periodos muestran explícitamente `0`.
- Si `rango_dias` es muy grande (ej. usuario pone un rango de varios años), el loop diario podría generar muchas iteraciones — pero como ya se decide `granularidad = 'semana'` para cualquier rango > 31 días, el loop nunca itera día por día en rangos grandes. No hace falta un límite adicional.

### 2. surveys/templates/dashboard_metricas.html — nueva sección + gráfica

Agregar una sección nueva, con el mismo patrón visual que las secciones existentes (`.section-card`), **inmediatamente después del `.kpi-grid` (resumen ejecutivo) y antes de la sección "Distribución de planes"** — es el orden lógico: primero la tendencia general, luego el desglose.

```html
<div class="section-card">
  <div class="section-card-header">
    <div class="section-title" style="margin-bottom:0;">
      <span class="title-dot" style="background:#10b981;"></span>
      Suscripciones nuevas por periodo
    </div>
    <span class="td-muted">Vista {{ granularidad|yesno:"diaria,semanal" }}</span>
  </div>
  <canvas id="timelineSuscripciones" style="max-height:280px;"></canvas>
</div>
```

(Ajustar el `<span class="td-muted">` si esa clase no calza bien fuera de una tabla — usar buen criterio visual, el punto es mostrar un texto pequeño tipo "Vista diaria"/"Vista semanal" junto al título, coherente con el resto del diseño de Replit.)

Y agregar, junto al `<script>` que ya inicializa la gráfica de pastel (mismo bloque `<script>` al final del archivo, o uno nuevo justo después):

```html
<script>
  const timelineLabels = {{ timeline_labels|safe }};
  const timelineData = {{ timeline_data|safe }};
  new Chart(document.getElementById('timelineSuscripciones'), {
    type: 'line',
    data: {
      labels: timelineLabels,
      datasets: [{
        label: 'Suscripciones nuevas',
        data: timelineData,
        borderColor: '#4f46e5',
        backgroundColor: 'rgba(79, 70, 229, 0.12)',
        fill: true,
        tension: 0.3,
        pointRadius: 3,
        pointBackgroundColor: '#4f46e5',
      }],
    },
    options: {
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 } },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });
</script>
```

**Nota técnica sobre `{{ timeline_labels|safe }}`**: en la vista, `timeline_labels` y `timeline_data` deben pasarse ya serializados a JSON (usar `json.dumps(timeline_labels)` y `json.dumps(timeline_data)` en `dashboard_views.py` antes de meterlos al contexto, exactamente igual de riesgo que el patrón ya usado para `distribucion_planes` en el `<script>` existente, que arma el array manualmente con `{% for %}` — aquí es más simple usar `json.dumps` desde Python porque son solo strings/números planos, no requiere iterar en el template). Alternativa aceptable: construir el array en el template con `{% for %}` igual que ya se hace para la gráfica de pastel, si se prefiere consistencia con el patrón existente — cualquiera de las dos formas es válida, usar buen criterio.

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/dashboard_views.py` sin errores.
2. Probar `/metricas/` en staging con distintos rangos de fecha:
   - Rango de 7 días → confirmar `granularidad == 'dia'`, la gráfica muestra 7 puntos (uno por día, aunque sea en 0)
   - Rango de 60 días → confirmar `granularidad == 'semana'`, la gráfica muestra ~8-9 puntos
   - Confirmar que los días/semanas sin compras muestran 0 explícito, no un hueco en la línea
3. Si es posible, simular 2-3 eventos `checkout.session.completed` de Stripe test mode en distintas fechas (igual que se hizo para validar SEC-009) y confirmar que los puntos correctos de la gráfica reflejan esas compras — si no es posible simular con fechas pasadas específicas (Stripe siempre usa la fecha/hora real del evento), al menos confirmar que una compra de HOY aparece en el bucket de hoy.
4. Confirmar visualmente que la nueva sección respeta el estilo del resto del dashboard (misma tipografía, mismo espaciado, mismos colores de marca).

## Fuera de alcance de este lote
- "Clientes activos netos a lo largo del tiempo" (con cancelaciones restadas) — requeriría un modelo nuevo de eventos de cancelación con fecha, decisión y especificación aparte si Jorge lo pide más adelante.
- Selector manual de granularidad (día/semana/mes) — se decidió que la granularidad automática basada en el rango de fechas ya existente es suficiente, sin UI adicional.
- Cualquier cambio a `PlanPurchaseEvent`, al webhook de Stripe, o a las demás secciones del dashboard (KPIs, distribución de planes, profundidad de uso) — todas quedan exactamente igual.
