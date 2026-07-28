# Dashboard ejecutivo — resumen a nivel empresa (NOM-035 + Clima Laboral) + Acciones pendientes

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/dashboard-ejecutivo-resumen-empresa`
- `surveys/views.py` usa TABS (confirmado con `cat -A`). `surveys/templates/*.html` es HTML/JS, no confundir con Django tags.
- No se agrega ningún modelo ni migración nueva — se reutilizan `Workplace`, `PlanAccionItem` (ya existe desde Fase 3-C) y `WorkEnvironmentSurvey` (encuestas de clima).
- `python -m py_compile surveys/views.py` antes de cualquier commit.
- `python manage.py check` antes de cualquier commit (no debe haber migraciones pendientes — no se tocó ningún modelo).

## Contexto

Jorge detectó (probando en producción) que el Dashboard muestra 3 tarjetas completas (NOM-035, Psicometría, Clima Laboral) **por cada centro de trabajo** — con 10 centros serían 30 tarjetas, dejando de ser un dashboard ejecutivo. Jorge aprobó un mockup con este rediseño:

1. **Fila de KPIs a nivel empresa** (Centros de trabajo, Empleados totales, Evaluaciones aplicadas, Cumplimiento documental promedio, Riesgo predominante) — **movida** desde la página "Centros de Trabajo" (`workplace.html`, Fase 3-A) al Dashboard. Se quita de `workplace.html` (ya no se duplica ahí).
2. **NOM-035 → "Centros que necesitan atención"**: en vez de listar los 10 centros, solo los que tienen mayor nivel de riesgo (top 3), con link "Ver todos los centros" hacia `workplaces`.
3. **Nueva sección "Acciones pendientes"**: acciones del Plan de Acción (numeral 8.4, `PlanAccionItem`) de **todos** los centros del usuario, no completadas, ordenadas por fecha programada — priorizando las ya vencidas.
4. **Clima Laboral → resumen agregado**: promedio general, tasa de respuesta, y la dimensión con menor puntaje, calculados sobre **todos** los centros — con link "Ver por centro" hacia `clima_resultados` (o a `workplaces`, ver punto 5 de Validación).
5. **Psicometría**: sin cambios — sigue siendo a nivel cuenta, no por centro. **No tocar la Sección 2 de `index.html`.**

**Nota de diseño (decisión de Jorge):** esta implementación es funcional, no visual — el diseño final se refinará después con Replit, igual que se hizo con otras pantallas. Reutilizar las clases CSS ya existentes en el archivo (`.db-section`, `.db-section-header`, etc.) y las de `workplace.html` para la fila de KPIs (`.kpi-row`, `.kpi-card`, etc.) tal cual, sin inventar un sistema de diseño nuevo.

## Cambios requeridos

### 1. `surveys/views.py` — `Index.get()` (clase en línea ~150 actual)

**1.1 — Dentro del bucle existente** (`for item in Workplace.objects.filter(user_id=self.request.user.id):`, líneas ~155-206 actuales), agregar el cálculo de riesgo general y cumplimiento documental de cada centro, reutilizando el mismo patrón ya usado en `WorkplaceView.get()` (línea 532 actual). Agregar al inicio del bucle (justo después de `employees=item.employees.all()` y `eval_to_check = ...`, antes del bloque `if item.survey_type() != 3:`):

```python
			from django.test import RequestFactory
			factory = RequestFactory()
			fake_req_riesgo = factory.get('/get_riesgo_general/', {'workplace_id': str(item.id), 'evaluation': str(eval_to_check)})
			fake_req_riesgo.user = request.user
			riesgo_data = json.loads(get_riesgo_general(fake_req_riesgo).content)
			if riesgo_data.get('status') == 'ok':
				riesgo_nivel = riesgo_data['riesgo_general']['nivel']
				riesgo_nivel_nombre = riesgo_data['riesgo_general']['nivel_nombre']
			else:
				riesgo_nivel = None
				riesgo_nivel_nombre = 'Sin datos'
			fake_req_portafolio = factory.get('/get_portafolio_status/', {'workplace_id': str(item.id)})
			fake_req_portafolio.user = request.user
			portafolio_data = json.loads(get_portafolio_status(fake_req_portafolio).content)
			cumplimiento_pct_item = portafolio_data.get('porcentaje_cumplimiento', 0)
```

(`from django.test import RequestFactory` puede quedar duplicado dentro del bucle sin problema — Python no penaliza un import repetido; seguir el mismo estilo ya usado en `WorkplaceView.get()`, que también lo importa dentro del método.)

**1.2 — Agregar al diccionario `wk.append({...})` existente** (líneas ~199-206 actuales) los campos nuevos, sin quitar ninguno de los existentes:

```python
			"riesgo_nivel":riesgo_nivel,
			"riesgo_nivel_nombre":riesgo_nivel_nombre,
			"cumplimiento_pct":cumplimiento_pct_item,
			"empleados_registrados":employees.count(),
			"evaluaciones_aplicadas":max(0, item.evaluation - 1),
```

**1.3 — Antes de `return render(request, 'index.html',ctx)`** (línea ~262 actual), agregar el cálculo de KPIs, la lista de centros que necesitan atención, el resumen de clima laboral, y las acciones pendientes:

```python
		NIVEL_NOMBRE = {0:"Nulo",1:"Bajo",2:"Medio",3:"Alto",4:"Muy alto"}
		total_centros = len(wk)
		niveles_presentes = [w['riesgo_nivel'] for w in wk if w['riesgo_nivel'] is not None]
		riesgo_predominante_nivel = max(niveles_presentes) if niveles_presentes else None
		ctx['kpi_total_centros'] = total_centros
		ctx['kpi_empleados_totales'] = sum(w['empleados_registrados'] for w in wk)
		ctx['kpi_evaluaciones_totales'] = sum(w['evaluaciones_aplicadas'] for w in wk)
		ctx['kpi_cumplimiento_promedio'] = round(sum(w['cumplimiento_pct'] for w in wk) / total_centros) if total_centros else 0
		ctx['kpi_riesgo_predominante_nivel'] = riesgo_predominante_nivel
		ctx['kpi_riesgo_predominante_nombre'] = NIVEL_NOMBRE[riesgo_predominante_nivel] if riesgo_predominante_nivel is not None else 'Sin datos'

		centros_ordenados = sorted(wk, key=lambda w: w['riesgo_nivel'] if w['riesgo_nivel'] is not None else -1, reverse=True)
		ctx['centros_atencion'] = [w for w in centros_ordenados if w['riesgo_nivel'] is not None][:3]

		todas_las_dimensiones_clima = []
		suma_climate_surveys = 0
		suma_employee_num = 0
		for w in wk:
			todas_las_dimensiones_clima.extend(w['climate_dimensions_preview'])
			suma_climate_surveys += w['climate_surveys_count']
			suma_employee_num += w['employee_count']
		if todas_las_dimensiones_clima:
			promedio_general_clima = round(sum(d['prom'] for d in todas_las_dimensiones_clima) / len(todas_las_dimensiones_clima), 2)
			peor_dimension = min(todas_las_dimensiones_clima, key=lambda d: d['prom'])
		else:
			promedio_general_clima = None
			peor_dimension = None
		ctx['clima_resumen'] = {
			'promedio_general': promedio_general_clima,
			'tasa_respuesta_pct': round((suma_climate_surveys / suma_employee_num) * 100) if suma_employee_num else 0,
			'peor_dimension': peor_dimension,
		}

		hoy = timezone.now().date()
		acciones_qs = PlanAccionItem.objects.filter(workplace__user=request.user).exclude(estado='completado').order_by('fecha_programada')[:5]
		ctx['acciones_pendientes'] = [{
			'id': a.id,
			'tipo_accion': a.tipo_accion,
			'workplace_nombre': a.workplace.name,
			'responsable': a.responsable,
			'fecha_programada': a.fecha_programada.strftime('%d/%m/%Y'),
			'es_vencida': a.fecha_programada < hoy,
		} for a in acciones_qs]

		return render(request, 'index.html',ctx)
```

(`timezone` ya está importado en `surveys/views.py` — verificar que sea `from django.utils import timezone`, ya presente en el archivo.)

### 2. `surveys/templates/index.html` — CSS nuevo

Agregar junto a las reglas `.db-section`/`.db-section-header`/etc. ya existentes (después de la línea con `.db-section-icon svg { width: 16px; height: 16px; }`, línea ~735 actual):

```css
      /* KPI row — movido desde workplace.html */
      .kpi-row{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:26px;}
      .kpi-card{background:var(--bg-base);border:1px solid var(--border);border-radius:var(--radius-lg);padding:14px 16px;box-shadow:var(--shadow-sm);}
      .kpi-label{font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted);margin:0 0 6px;}
      .kpi-value{font-family:'Plus Jakarta Sans',sans-serif;font-size:22px;font-weight:800;color:var(--text-primary);display:flex;align-items:baseline;gap:6px;}
      .kpi-badge-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;}
      .kpi-sub{font-size:11px;color:var(--text-muted);margin-top:2px;}

      /* Centros que necesitan atencion */
      .atencion-list{display:flex;flex-direction:column;gap:10px;}
      .atencion-card{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:13px 16px;border:1px solid var(--border);border-left:4px solid var(--text-muted);border-radius:var(--radius-md);background:var(--bg-surface);}
      .atencion-card.risk-4{border-left-color:#dc2626;}
      .atencion-card.risk-3{border-left-color:#f97316;}
      .atencion-card.risk-2{border-left-color:#eab308;}
      .atencion-name{font-size:13.5px;font-weight:700;color:var(--text-primary);margin:0 0 2px;}
      .atencion-meta{font-size:11.5px;color:var(--text-muted);}
      .risk-pill{font-size:11px;font-weight:800;padding:4px 10px;border-radius:999px;white-space:nowrap;}
      .risk-pill.risk-4{background:#fee2e2;color:#dc2626;}
      .risk-pill.risk-3{background:#ffedd5;color:#c2410c;}
      .risk-pill.risk-2{background:#fef9c3;color:#a16207;}
      .risk-pill.risk-1{background:#dcfce7;color:#15803d;}
      .risk-pill.risk-0{background:#f1f5f9;color:#475569;}
      .link-all{font-size:12.5px;font-weight:700;color:var(--primary);text-decoration:none;display:flex;align-items:center;gap:4px;}

      /* Acciones pendientes */
      .accion-pend-item{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:12px 16px;border:1px solid var(--border);border-radius:var(--radius-md);background:var(--bg-surface);margin-bottom:8px;}
      .accion-pend-item.vencida{border-left:4px solid var(--danger);}
      .accion-pend-name{font-size:13px;font-weight:700;color:var(--text-primary);margin:0 0 2px;}
      .accion-pend-meta{font-size:11px;color:var(--text-muted);}
      .accion-pend-fecha{font-size:11.5px;font-weight:700;color:var(--warning);white-space:nowrap;}
      .accion-pend-fecha.vencida{color:var(--danger);}

      /* Clima laboral resumen agregado */
      .clima-summary-row{display:grid;grid-template-columns:1fr 1fr 1.4fr;gap:16px;align-items:center;}
      .clima-stat{text-align:center;padding:14px;border-radius:var(--radius-md);background:#f0fdfa;border:1px solid #99f6e4;}
      .clima-stat-val{font-family:'Plus Jakarta Sans',sans-serif;font-size:24px;font-weight:800;color:#0f766e;}
      .clima-stat-label{font-size:11px;color:#0f766e;font-weight:600;margin-top:2px;}
      .clima-worst{padding:14px 16px;border-radius:var(--radius-md);background:#fffbeb;border:1px solid #fde68a;}
      .clima-worst-label{font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:#a16207;margin:0 0 4px;}
      .clima-worst-name{font-size:14px;font-weight:800;color:#78350f;margin:0 0 2px;}
      .clima-worst-val{font-size:12px;color:#92400e;}
```

### 3. `surveys/templates/index.html` — fila de KPIs (nueva)

Insertar justo antes del comentario `<!-- SECCIÓN 1 · NOM-035 -->` (línea 1084 actual):

```html
    <div class="kpi-row">
      <div class="kpi-card">
        <p class="kpi-label">Centros de trabajo</p>
        <p class="kpi-value">{{kpi_total_centros}}</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">Empleados totales</p>
        <p class="kpi-value">{{kpi_empleados_totales}}</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">Evaluaciones aplicadas</p>
        <p class="kpi-value">{{kpi_evaluaciones_totales}}</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">Cumplimiento documental</p>
        <p class="kpi-value">{{kpi_cumplimiento_promedio}}%</p>
        <p class="kpi-sub">promedio de todos los centros</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">Riesgo predominante</p>
        <p class="kpi-value">{% if kpi_riesgo_predominante_nivel is not None %}<span class="kpi-badge-dot" data-nivel="{{kpi_riesgo_predominante_nivel}}"></span>{% endif %}{{kpi_riesgo_predominante_nombre}}</p>
        <p class="kpi-sub">peor caso entre tus centros</p>
      </div>
    </div>
```

Agregar también el script que colorea `.kpi-badge-dot` según `data-nivel`, copiado tal cual de `workplace.html` (buscar `document.querySelectorAll('.kpi-badge-dot'` en ese archivo y replicar la misma función de mapeo nivel→color) dentro de `{% block scripts %}` de `index.html`.

### 4. `surveys/templates/index.html` — reemplazar SECCIÓN 1 (NOM-035)

Reemplazar el bloque completo desde el comentario `SECCIÓN 1 · NOM-035` hasta su `</section>` de cierre (líneas 1084-1240 actuales) por:

```html
    <!-- ══════════════════════════════════════════════════════════
         SECCIÓN 1 · NOM-035 — Centros que necesitan atención
    ══════════════════════════════════════════════════════════ -->
    <section class="db-section section-nom035">

      <div class="db-section-header">
        <div class="db-section-title">
          <div class="db-section-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
          </div>
          NOM-035 — Centros que necesitan atención
        </div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
          <span class="credit-pill credit-pill-blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:12px;height:12px"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>
            {{nom035_disponibles}} crédito{% if nom035_disponibles != 1 %}s{% endif %} disponible{% if nom035_disponibles != 1 %}s{% endif %}
          </span>
          <a href="{% url 'workplaces' %}" class="link-all">
            Ver todos los centros
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>
        </div>
      </div>

      {% if centros_atencion %}
      <div class="atencion-list">
        {% for item in centros_atencion %}
        <div class="atencion-card risk-{{item.riesgo_nivel}}">
          <div>
            <p class="atencion-name">{{item.name}}</p>
            <p class="atencion-meta">{{item.empleados_registrados}} empleados · Evaluación #{{item.cat}} · {{item.survey_completion}}% aplicado</p>
          </div>
          <span class="risk-pill risk-{{item.riesgo_nivel}}">{{item.riesgo_nivel_nombre}}</span>
          <a href="{% url 'single_workplace' item.id %}" class="btn btn-outline btn-sm">Ver centro</a>
        </div>
        {% endfor %}
      </div>
      {% elif not has_workplaces %}
      <div class="card">
        <div class="card-body">
          <div class="empty-state">
            <div class="empty-state-icon" style="background:#dbeafe;border-color:#bfdbfe;color:#2563eb;">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>
            </div>
            <p>No hay centros registrados. <a href="/workplaceform/" style="color:#2563eb;font-weight:600;">Registra el primero</a>.</p>
          </div>
        </div>
      </div>
      {% else %}
      <div class="dim-empty">Aún no hay datos de riesgo suficientes en tus centros para mostrar aquí.</div>
      {% endif %}

    </section>

    <!-- ══════════════════════════════════════════════════════════
         SECCIÓN 1-B · ACCIONES PENDIENTES (Plan de acción, numeral 8.4)
    ══════════════════════════════════════════════════════════ -->
    <section class="db-section">
      <div class="db-section-header">
        <div class="db-section-title">
          <div class="db-section-icon" style="background:#fef2f2;color:#dc2626;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          Acciones pendientes — Plan de acción
        </div>
      </div>
      {% if acciones_pendientes %}
        {% for a in acciones_pendientes %}
        <div class="accion-pend-item {% if a.es_vencida %}vencida{% endif %}">
          <div>
            <p class="accion-pend-name">{{a.tipo_accion}} — {{a.workplace_nombre}}</p>
            <p class="accion-pend-meta">Responsable: {{a.responsable}}</p>
          </div>
          <span class="accion-pend-fecha {% if a.es_vencida %}vencida{% endif %}">
            {% if a.es_vencida %}Venció el {{a.fecha_programada}}{% else %}Vence el {{a.fecha_programada}}{% endif %}
          </span>
        </div>
        {% endfor %}
      {% else %}
      <div class="dim-empty">No tienes acciones pendientes registradas en tu Plan de acción.</div>
      {% endif %}
    </section>
```

**No modificar la SECCIÓN 2 · PSICOMETRÍA** (líneas 1241-1344 actuales aprox., justo después del `</section>` de cierre de la nueva Sección 1-B).

### 5. `surveys/templates/index.html` — reemplazar SECCIÓN 3 (Clima Laboral)

Reemplazar el bloque completo desde el comentario `SECCIÓN 3 · CLIMA LABORAL` hasta su `</section>` de cierre (líneas 1346-1476 actuales) por:

```html
    <!-- ══════════════════════════════════════════════════════════
         SECCIÓN 3 · CLIMA LABORAL — resumen general
    ══════════════════════════════════════════════════════════ -->
    <section class="db-section section-clima">

      <div class="db-section-header">
        <div class="db-section-title">
          <div class="db-section-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </div>
          Clima Laboral — resumen general
        </div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
          <span class="included-badge">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:11px;height:11px"><polyline points="20 6 9 17 4 12"/></svg>
            Incluido en todos los planes
          </span>
          <a href="{% url 'workplaces' %}" class="link-all">
            Ver por centro
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>
        </div>
      </div>

      {% if clima_resumen.promedio_general is not None %}
      <div class="clima-summary-row">
        <div class="clima-stat">
          <div class="clima-stat-val">{{clima_resumen.promedio_general}}</div>
          <div class="clima-stat-label">Promedio general</div>
        </div>
        <div class="clima-stat">
          <div class="clima-stat-val">{{clima_resumen.tasa_respuesta_pct}}%</div>
          <div class="clima-stat-label">Tasa de respuesta</div>
        </div>
        <div class="clima-worst">
          <p class="clima-worst-label">Dimensión con menor puntaje</p>
          <p class="clima-worst-name">{{clima_resumen.peor_dimension.name}}</p>
          <p class="clima-worst-val">{{clima_resumen.peor_dimension.prom}} — {{clima_resumen.peor_dimension.nivel}}</p>
        </div>
      </div>
      {% elif not has_workplaces %}
      <div class="card" style="border-top:3px solid #0d9488;">
        <div class="card-body">
          <div class="empty-state">
            <div class="empty-state-icon" style="background:#ccfbf1;border-color:#99f6e4;color:#0d9488;">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
            </div>
            <p>Registra un centro de trabajo para activar las encuestas de clima laboral.
              <a href="/workplaceform/" style="color:#0d9488;font-weight:600;">Registrar ahora</a>
            </p>
          </div>
        </div>
      </div>
      {% else %}
      <div class="dim-empty">Aún no hay respuestas de clima laboral suficientes para mostrar un resumen.</div>
      {% endif %}

    </section>
```

(El script `copyClimaLink` ya definido más abajo en el archivo deja de usarse desde esta sección — puede quedarse intacto, no forma parte de este cambio; no se toca.)

### 6. `surveys/templates/workplace.html` — quitar la fila de KPIs (movida al Dashboard)

Quitar el bloque `<div class="kpi-row">...</div>` completo (líneas 148-172 actuales aprox., buscar el div que contiene los 5 `.kpi-card` con "Centros de trabajo", "Empleados totales", "Evaluaciones aplicadas", "Cumplimiento documental", "Riesgo predominante"). **No quitar** el resto de la página (buscador, filtros, tarjetas por centro) — solo esa fila de KPIs superior, ya que ahora vive en el Dashboard.

También se puede dejar el CSS `.kpi-row`/`.kpi-card`/etc. de `workplace.html` sin tocar (queda sin uso en ese archivo, no rompe nada) — no es necesario limpiarlo en esta spec.

## Validación requerida

1. `python -m py_compile surveys/views.py`.
2. `python manage.py check` (no debe haber migraciones pendientes).
3. Prueba con un usuario con varios centros de trabajo reales (mezcla de niveles de riesgo, ej. usar los centros de prueba "Centro Riesgo A/B" + "Empresa Demo"): confirmar que las 5 KPIs del Dashboard coinciden con los valores que antes se veían en "Centros de Trabajo" (antes de quitarlos de ahí).
4. Confirmar que "Centros que necesitan atención" muestra máximo 3 centros, ordenados de mayor a menor riesgo, y que un centro sin evaluación (`riesgo_nivel is None`) no aparece en esa lista.
5. Confirmar que "Acciones pendientes" muestra hasta 5 acciones no completadas de **todos** los centros del usuario, ordenadas por fecha programada, con las vencidas marcadas visualmente distinto (borde/fecha en rojo) de las próximas (ámbar).
6. Confirmar que "Clima Laboral" muestra el promedio general, tasa de respuesta y peor dimensión agregados de todos los centros — comparar manualmente contra la suma/promedio esperado de 2-3 centros con datos de clima conocidos.
7. Confirmar que la sección "Psicometría" del Dashboard no cambió en absoluto (mismo HTML, mismos datos, mismo comportamiento que antes de este cambio).
8. Confirmar que "Centros de Trabajo" (`workplace.html`) ya no muestra la fila de KPIs arriba, pero el resto de la página (buscador, filtros, tarjetas por centro) sigue funcionando igual que antes.
9. Probar con un usuario sin ningún centro de trabajo (`has_workplaces=False`): debe seguir mostrando los estados vacíos correspondientes en cada sección, sin errores.
10. Prueba visual en navegador real: cargar el Dashboard con datos reales, confirmar que se ve razonable (no hace falta pulir el diseño, eso lo hará Replit después), sin errores de consola.
11. Confirmar que no hay una regresión de rendimiento grave — el Dashboard ya iteraba sobre todos los centros antes; ahora agrega 2 llamadas internas más (`get_riesgo_general`, `get_portafolio_status`) por centro dentro del mismo bucle existente, mismo orden de magnitud que ya hace `WorkplaceView` en la página de Centros de Trabajo.

## Fuera de alcance

- No se toca la Sección 2 (Psicometría) del Dashboard.
- No se hace ningún ajuste de diseño visual fino (colores, espaciados, tipografía) más allá de reutilizar las clases ya existentes — eso se refina después con Replit.
- No se pagina ni se filtra la lista de "Acciones pendientes" — se muestra un máximo fijo de 5, sin scroll ni "ver más" todavía.
- No se excluyen los centros de trabajo demo (`es_demo=True`) del cálculo de KPIs ni de "centros que necesitan atención" — se mantiene el mismo comportamiento que ya tenía `workplace.html` (que tampoco los excluye hoy).
- No se cambia ningún otro endpoint ni vista fuera de `Index.get()`.
