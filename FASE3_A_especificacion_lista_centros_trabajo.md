# Fase 3-A — Rediseño de la lista de Centros de Trabajo (KPIs + tarjetas enriquecidas)

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/fase3-a-lista-centros-trabajo`
- `surveys/views.py` usa TABS. `surveys/templates/*.html` es HTML/JS.
- Sin migración (no toca modelos).
- `python -m py_compile surveys/views.py` antes de cualquier commit.
- **Depende de Fase 2-A y 2-B ya desplegadas** (`get_riesgo_general`, `get_portafolio_status`) — ambas ya están en `auditoria-local`/`main`, así que esto no debería ser un problema, pero si por algún motivo tu clon no las tiene, avisa antes de improvisar.

## Contexto

Mockup aprobado por Jorge el 24 jul 2026 (ver conversación): la lista de "Centros de Trabajo" (`workplace.html`, vista `WorkplaceView` en `surveys/views.py:528-534`) pasa de ser tarjetas simples (nombre + conteo de empleados + "Ver detalle") a incluir: un renglón de 5 KPIs agregados arriba, una barra de búsqueda/filtro, y tarjetas con más información por centro (riesgo, cumplimiento documental, evaluaciones aplicadas, 2 botones de acceso).

**Decisiones de producto ya confirmadas con Jorge, no volver a preguntar:**
1. "Riesgo predominante" (KPI agregado) = **peor caso** entre los centros del usuario (si un centro está en Alto, el KPI general muestra Alto), no un promedio ni la moda — conservador, nunca esconde el peor centro.
2. "Evaluaciones aplicadas" por centro = `max(0, workplace.evaluation - 1)`. Razonamiento: `evaluation` es el número de ciclo ACTUAL (incrementa solo cuando `EndEvaluation` finaliza un ciclo, ver nota técnica ya existente en `ESTADO.md`: "EndEvaluation: incrementa evaluation+1, pone paid=False"), así que el número de evaluaciones ya completadas es siempre `evaluation - 1`, independientemente de si la evaluación actual está pagada/en curso o no. Un centro nuevo sin evaluar tiene `evaluation=1` → 0 evaluaciones aplicadas.
3. "Cumplimiento documental" (KPI agregado) = promedio simple del `porcentaje_cumplimiento` (de `get_portafolio_status`) entre todos los centros del usuario — NUNCA derivado del riesgo (mismo principio ya aplicado en toda la Fase 2).

## Cambios requeridos

### 1. surveys/views.py — `WorkplaceView.get()` (líneas 528-534 actuales)

Reescribir para calcular, por cada centro, el nivel de riesgo y el % de cumplimiento documental reutilizando `get_riesgo_general` y `get_portafolio_status` — mismo patrón que ya usa `get_portafolio_status` internamente para llamar a `get_chart_data` (`RequestFactory`, líneas 987-992 actuales de ese mismo archivo), no reinventar la lógica de cálculo:

```python
class WorkplaceView(LoginRequiredMixin,View):
	login_url = reverse_lazy('login')
	redirect_field_name = 'redirect_to'
	def get(self, request, *args, **kwargs):
		from django.test import RequestFactory
		factory = RequestFactory()
		NIVEL_NOMBRE = {0:"Nulo",1:"Bajo",2:"Medio",3:"Alto",4:"Muy alto"}

		workplaces_qs = Workplace.objects.filter(user_id=self.request.user.id)
		workplaces = []
		niveles_riesgo_presentes = []
		suma_cumplimiento = 0
		suma_evaluaciones = 0
		suma_empleados_registrados = 0

		for wk in workplaces_qs:
			eval_to_check = wk.evaluation if wk.paid else max(1, wk.evaluation - 1)

			fake_req = factory.get('/get_riesgo_general/', {'workplace_id': str(wk.id), 'evaluation': str(eval_to_check)})
			fake_req.user = request.user
			riesgo_data = json.loads(get_riesgo_general(fake_req).content)
			if riesgo_data.get('status') == 'ok':
				nivel = riesgo_data['riesgo_general']['nivel']
				nivel_nombre = riesgo_data['riesgo_general']['nivel_nombre']
				niveles_riesgo_presentes.append(nivel)
			else:
				nivel = None
				nivel_nombre = 'Sin datos'

			fake_req2 = factory.get('/get_portafolio_status/', {'workplace_id': str(wk.id)})
			fake_req2.user = request.user
			portafolio_data = json.loads(get_portafolio_status(fake_req2).content)
			cumplimiento_pct = portafolio_data.get('porcentaje_cumplimiento', 0)

			evaluaciones_aplicadas = max(0, wk.evaluation - 1)
			empleados_registrados = wk.employees.count()

			suma_cumplimiento += cumplimiento_pct
			suma_evaluaciones += evaluaciones_aplicadas
			suma_empleados_registrados += empleados_registrados

			workplaces.append({
				"id": wk.id,
				"name": wk.name,
				"address": wk.address,
				"employee_count": wk.employee_num,
				"empleados_registrados": empleados_registrados,
				"evaluaciones_aplicadas": evaluaciones_aplicadas,
				"cumplimiento_pct": cumplimiento_pct,
				"riesgo_nivel": nivel,
				"riesgo_nivel_nombre": nivel_nombre,
			})

		total_centros = len(workplaces)
		riesgo_predominante_nivel = max(niveles_riesgo_presentes) if niveles_riesgo_presentes else None
		riesgo_predominante_nombre = NIVEL_NOMBRE[riesgo_predominante_nivel] if riesgo_predominante_nivel is not None else 'Sin datos'

		ctx = {
			"workplaces": workplaces,
			"kpi_total_centros": total_centros,
			"kpi_empleados_totales": suma_empleados_registrados,
			"kpi_evaluaciones_totales": suma_evaluaciones,
			"kpi_cumplimiento_promedio": round(suma_cumplimiento / total_centros) if total_centros else 0,
			"kpi_riesgo_predominante_nivel": riesgo_predominante_nivel,
			"kpi_riesgo_predominante_nombre": riesgo_predominante_nombre,
		}
		return render(request, 'workplace.html', ctx)
```

Notas:
- `empleados_registrados` (`wk.employees.count()`) reemplaza el `employee_count` (`wk.employee_num`, la capacidad contratada, no el conteo real) que usaba la tarjeta antes — es un cambio deliberado: para las tarjetas nuevas, mostrar cuántos empleados REALES están registrados es más útil que la capacidad contratada. `employee_count` (capacidad) se conserva en el contexto por si se sigue usando en otro lado del template, pero las tarjetas nuevas deben mostrar `empleados_registrados`.
- No existe ningún campo de "Estado" (activo/inactivo) en el modelo `Workplace` — el mockup mostraba una tarjeta de ejemplo con "Estado: Activo" como placeholder, pero no hay dato real detrás. **No agregar esa columna/stat** en la implementación real — usar en su lugar los 4 datos que sí tienen respaldo real: Empleados registrados, Evaluaciones aplicadas, % Cumplimiento, y el badge de Riesgo.
- Este enfoque hace 2 llamadas internas (`get_riesgo_general` + `get_portafolio_status`, esta última ya hace una llamada interna adicional a `get_chart_data`) por cada centro de trabajo del usuario. Para la cantidad típica de centros por cliente esto es aceptable; si en el futuro un usuario llega a tener docenas de centros, se puede revisar optimización (cache, cálculo asíncrono) — fuera de alcance de este lote.

### 2. surveys/templates/workplace.html — reescribir

**2.1 — CSS**: agregar (junto al bloque existente `.wp-grid`/`.wp-card`, sin borrar nada de eso, los `.wp-card-new` existentes se conservan tal cual):

```css
.page-header{display:flex; align-items:flex-start; justify-content:space-between; gap:16px; flex-wrap:wrap; margin-bottom:18px;}
.kpi-row{display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:20px;}
.kpi-card{background:var(--bg-base); border:1px solid var(--border); border-radius:var(--radius-lg); padding:14px 16px; box-shadow:var(--shadow-sm);}
.kpi-label{font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); margin:0 0 6px;}
.kpi-value{font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:800; color:var(--text-primary); display:flex; align-items:baseline; gap:6px;}
.kpi-badge-dot{width:10px;height:10px;border-radius:50%; flex-shrink:0;}
.kpi-sub{font-size:11px; color:var(--text-muted); margin-top:2px;}
.filter-bar{display:flex; gap:10px; margin-bottom:18px; flex-wrap:wrap;}
.filter-input, .filter-select{border:1px solid var(--border); border-radius:var(--radius-md); padding:9px 12px; font-size:12.5px; color:var(--text-primary); background:var(--bg-base);}
.filter-input{flex:1 1 240px;}
.filter-select{flex:0 0 160px;}
.wp-card-addr{font-size:11.5px; color:var(--text-muted); margin:0;}
.risk-pill{font-size:10px; font-weight:800; letter-spacing:.02em; padding:3px 9px; border-radius:999px; white-space:nowrap;}
.wp-stats{display:grid; grid-template-columns:1fr 1fr; gap:10px;}
.wp-stat{background:var(--bg-surface); border-radius:var(--radius-md); padding:9px 11px;}
.wp-stat-value{font-family:'Plus Jakarta Sans',sans-serif; font-size:16px; font-weight:800; color:var(--text-primary);}
.wp-stat-label{font-size:10px; color:var(--text-muted); text-transform:uppercase; letter-spacing:.04em; margin-top:2px;}
.wp-card-footer .btn{flex:1; justify-content:center;}
```
Los 5 colores del `.risk-pill` (Nulo/Bajo/Medio/Alto/Muy alto) deben reutilizar los mismos que ya se usan en `workplace_detail.html` (Fase 2-C): `#9be5f7`/`#6bf56e`/`#eab308`/`#ffc000`/`#ff7070` para el punto/fondo, con texto oscuro legible — no inventar colores nuevos. Para "Sin datos", usar un gris neutro (`var(--bg-surface)`/`var(--text-muted)`).

**2.2 — HTML**: el bloque `{% block dashboard %}` (línea 115 actual) cambia de:
```html
<div class="page-header">
  <div class="page-header-text">
    <h1>Centros de Trabajo</h1>
    <p>Gestiona tus centros y su cumplimiento NOM-035</p>
  </div>
  <a href="/workplaceform" class="btn btn-primary btn-sm">...Nuevo centro</a>
</div>
```
a (mismo header, sin cambios) + agregar el renglón de KPIs justo debajo:
```html
<div class="kpi-row">
  <div class="kpi-card">
    <p class="kpi-label">Centros de trabajo</p>
    <p class="kpi-value">{{ kpi_total_centros }}</p>
  </div>
  <div class="kpi-card">
    <p class="kpi-label">Empleados totales</p>
    <p class="kpi-value">{{ kpi_empleados_totales }}</p>
  </div>
  <div class="kpi-card">
    <p class="kpi-label">Evaluaciones aplicadas</p>
    <p class="kpi-value">{{ kpi_evaluaciones_totales }}</p>
  </div>
  <div class="kpi-card">
    <p class="kpi-label">Cumplimiento documental</p>
    <p class="kpi-value">{{ kpi_cumplimiento_promedio }}%</p>
    <p class="kpi-sub">promedio de todos los centros</p>
  </div>
  <div class="kpi-card">
    <p class="kpi-label">Riesgo predominante</p>
    <p class="kpi-value">
      {% if kpi_riesgo_predominante_nivel is not None %}<span class="kpi-badge-dot" data-nivel="{{ kpi_riesgo_predominante_nivel }}"></span>{% endif %}
      {{ kpi_riesgo_predominante_nombre }}
    </p>
    <p class="kpi-sub">peor caso entre tus centros</p>
  </div>
</div>

<div class="filter-bar">
  <input class="filter-input" type="text" id="wp-search" placeholder="Buscar centro de trabajo..." />
  <select class="filter-select" id="wp-filter-riesgo">
    <option value="">Riesgo: Todos</option>
    <option value="0">Nulo</option>
    <option value="1">Bajo</option>
    <option value="2">Medio</option>
    <option value="3">Alto</option>
    <option value="4">Muy alto</option>
  </select>
</div>
```

Reemplazar el `{% for item in workplaces %}` (línea 130 actual) del `.wp-grid` por:
```html
{% for item in workplaces %}
<div class="wp-card" data-nombre="{{ item.name|lower }}" data-riesgo="{% if item.riesgo_nivel is not None %}{{ item.riesgo_nivel }}{% endif %}">
  <div class="wp-card-top">
    <div style="display:flex; gap:12px; align-items:flex-start; min-width:0;">
      <div class="wp-card-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>
      </div>
      <div style="min-width:0;">
        <p class="wp-card-name">{{ item.name }}</p>
        <p class="wp-card-addr">{{ item.address }}</p>
      </div>
    </div>
    <span class="risk-pill" data-nivel="{% if item.riesgo_nivel is not None %}{{ item.riesgo_nivel }}{% else %}na{% endif %}">{{ item.riesgo_nivel_nombre }}</span>
  </div>
  <div class="wp-stats">
    <div class="wp-stat"><div class="wp-stat-value">{{ item.empleados_registrados }}</div><div class="wp-stat-label">Empleados</div></div>
    <div class="wp-stat"><div class="wp-stat-value">{{ item.evaluaciones_aplicadas }}</div><div class="wp-stat-label">Evaluaciones</div></div>
    <div class="wp-stat" style="grid-column:span 2;"><div class="wp-stat-value">{{ item.cumplimiento_pct }}%</div><div class="wp-stat-label">Cumplimiento documental</div></div>
  </div>
  <div class="wp-card-footer">
    <a href="{% url 'single_workplace' item.id %}" class="btn btn-outline">Ver detalle</a>
    {% if item.riesgo_nivel is not None %}
    <a href="/workplace_result/{{ item.id }}/" class="btn btn-outline">Ver resultados</a>
    {% else %}
    <span class="btn btn-outline" style="opacity:.5; pointer-events:none;">Ver resultados</span>
    {% endif %}
  </div>
</div>
{% endfor %}
```
(la tarjeta `.wp-card-new` de "Nuevo centro de trabajo", después del `{% endfor %}`, se deja exactamente igual a como está hoy, líneas 154-159 actuales).

**2.3 — JS**: agregar, dentro de `{% block scripts %}` (junto al `$(document).ready` existente):
```javascript
$(function(){
  document.querySelectorAll('.kpi-badge-dot, .risk-pill').forEach(function(el){
    var nivel = el.getAttribute('data-nivel');
    var colores = {'0':'#9be5f7','1':'#6bf56e','2':'#eab308','3':'#ffc000','4':'#ff7070'};
    if (nivel && colores[nivel]) {
      el.style.background = colores[nivel];
    }
  });
  $('#wp-search').on('input', function(){
    var q = $(this).val().toLowerCase();
    $('.wp-card[data-nombre]').each(function(){
      $(this).toggle($(this).data('nombre').toString().indexOf(q) !== -1);
    });
  });
  $('#wp-filter-riesgo').on('change', function(){
    var v = $(this).val();
    $('.wp-card[data-nombre]').each(function(){
      var r = $(this).attr('data-riesgo');
      $(this).toggle(v === '' || r === v);
    });
  });
});
```
Nota: los colores se aplican por JS en vez de clases CSS fijas por nivel porque el nivel es dinámico (viene del backend) — seguir este patrón simple, no es necesario Vue ni nada más complejo para esta vista (a diferencia de `evidence.html`, `workplace.html` no usa Vue hoy, no introducirlo aquí).

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/views.py` sin errores.
2. Confirmar visualmente en local, con un usuario de prueba con al menos 2-3 centros en distintos estados (uno con riesgo alto y encuestas completas, uno sin ninguna encuesta contestada, uno con el checklist documental parcialmente lleno):
   - Los 5 KPIs muestran los agregados correctos (verificar a mano: cumplimiento promedio, riesgo predominante = el peor entre los centros con datos).
   - Cada tarjeta muestra su badge de riesgo con el color correcto, o "Sin datos" si no tiene encuestas.
   - "Ver resultados" está deshabilitado en el centro sin datos, habilitado en los demás.
   - El buscador filtra por nombre en tiempo real.
   - El filtro de riesgo funciona.
   - La tarjeta "Nuevo centro de trabajo" sigue funcionando igual que antes (clic lleva a `/workplaceform`).
3. Probar con un usuario que tenga 0 centros de trabajo — confirmar que los KPIs muestran 0/0%/"Sin datos" sin error, y solo se ve la tarjeta de "Nuevo centro".
4. Confirmar que `/workplaces/<id>/` (ficha de detalle) sigue funcionando exactamente igual, sin regresión — este lote no la toca.

## Fuera de alcance de este lote (no tocar)
- `workplace_detail.html`, `workplace_results.html`, `evidence.html` — sin cambios, ya son Fase 2-A/2-B/2-B2/2-C, cerradas.
- Cualquier campo nuevo en el modelo `Workplace` (ej. un campo real de "activo/inactivo") — no es parte de este lote, se evaluaría aparte si Jorge lo pide explícitamente.
- Paginación de la lista de centros si un usuario tiene muchos — no está en el mockup aprobado, se puede agregar después si hace falta.
