# Fase 3-C — Plan de acción (numeral 8.4), alcance reducido v1

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/fase3-c-plan-accion-numeral-8-4`
- `surveys/views.py` usa TABS (confirmado con `cat -A`, no usar espacios al indentar). `surveys/templates/*.html` es HTML/JS. `evidence.html` usa Vue.js (delimitadores `${ }`, no `{{ }}`) — no confundir con Django template tags, que sí usan `{{ }}`/`{% %}`.
- Migración nueva: `0044_plan_accion_item.py` (última existente es `0043_evaluation_history.py`).
- `openpyxl` ya está declarado en `requirements.txt` (agregado en la carga masiva de empleados) — no se necesita ninguna dependencia nueva. Reutilizar el mismo patrón de generación/parseo de `.xlsx` con menús desplegables ya usado ahí (`surveys/views.py`, `EMPLEADO_CAMPOS_CARGA_MASIVA`, `download_employee_template`, `upload_employees_bulk`) como referencia de estilo — **no** reutilizar código compartido todavía (YAGNI, ver "Fuera de alcance").
- `python -m py_compile surveys/views.py surveys/models.py` antes de cualquier commit.
- `python manage.py makemigrations --check --dry-run` y `python manage.py check` antes de cualquier commit.

## Contexto

Decisión de Jorge ya confirmada (24 jul 2026, documentada en `SOCIOS_feedback_correcciones.md` y `ESTADO.md`): en vez del CRUD completo tipo kanban originalmente contemplado para el numeral 8.4 ("Programa de intervención" — control de avances), la v1 es: el usuario descarga una plantilla `.xlsx` con las 6 columnas que exige el numeral 8.4, la llena, la sube, y el sistema importa cada fila como una acción real en base de datos (no se guarda el archivo). Cada acción importada queda con un **selector de estado inline** (mismo patrón visual que el checklist de documentos de Fase 2-B2 en `evidence.html`: `<select>` + botón "Guardar" que se habilita solo cuando el valor cambia), permitiendo actualizar el avance sin necesitar un archivo nuevo ni un tablero kanban.

Jorge aprobó un mockup: la nueva sección "Plan de acción — numeral 8.4" vive **dentro de Portafolio de Evidencias** (`evidence.html`), como una tarjeta nueva (`.section-card`) debajo del banner de cumplimiento documental y antes/después del checklist existente — reutiliza el Vue app ya montado en esa página (`app`, delimitadores `${ }`).

**Las 6 columnas que exige el numeral 8.4** (ya verificadas y documentadas en sesión previa, no volver a cuestionar):
1. Área o trabajadores sujetos a la acción
2. Tipo de acción (descripción de la medida/actividad)
3. Fecha programada
4. Responsable
5. Estado (Pendiente / En proceso / Completado)
6. Evaluación posterior (cómo se dará seguimiento/verificará la acción)

## Cambios requeridos

### 1. `surveys/models.py` — nuevo modelo `PlanAccionItem`

Agregar al final del archivo:

```python
class PlanAccionItem(models.Model):
	ESTADO_CHOICES = (
		('pendiente', 'Pendiente'),
		('en_proceso', 'En proceso'),
		('completado', 'Completado'),
	)
	workplace = models.ForeignKey(Workplace, related_name="plan_accion_items", verbose_name='Centro de trabajo', on_delete=models.CASCADE)
	area_trabajadores = models.CharField(u'Área o trabajadores sujetos', max_length=300)
	tipo_accion = models.CharField(u'Tipo de acción', max_length=300)
	fecha_programada = models.DateField(u'Fecha programada')
	responsable = models.CharField(u'Responsable', max_length=200)
	estado = models.CharField(u'Estado', max_length=20, choices=ESTADO_CHOICES, default='pendiente')
	evaluacion_posterior = models.CharField(u'Evaluación posterior', max_length=300)
	record_create = models.DateTimeField(auto_now_add=True)
	record_update = models.DateTimeField(auto_now=True)
	def __str__(self):
		return f"{self.tipo_accion} - {self.workplace.name} ({self.get_estado_display()})"
	class Meta:
		ordering = ['fecha_programada']
```

### 2. Migración `surveys/migrations/0044_plan_accion_item.py`

```python
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('surveys', '0043_evaluation_history'),
	]

	operations = [
		migrations.CreateModel(
			name='PlanAccionItem',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('area_trabajadores', models.CharField(max_length=300, verbose_name='Área o trabajadores sujetos')),
				('tipo_accion', models.CharField(max_length=300, verbose_name='Tipo de acción')),
				('fecha_programada', models.DateField(verbose_name='Fecha programada')),
				('responsable', models.CharField(max_length=200, verbose_name='Responsable')),
				('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_proceso', 'En proceso'), ('completado', 'Completado')], default='pendiente', max_length=20, verbose_name='Estado')),
				('evaluacion_posterior', models.CharField(max_length=300, verbose_name='Evaluación posterior')),
				('record_create', models.DateTimeField(auto_now_add=True)),
				('record_update', models.DateTimeField(auto_now=True)),
				('workplace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plan_accion_items', to='surveys.workplace', verbose_name='Centro de trabajo')),
			],
			options={
				'ordering': ['fecha_programada'],
			},
		),
	]
```

Generar con `python manage.py makemigrations surveys` y comparar contra lo anterior — si Django numera distinto, está bien, es solo referencia.

### 3. `surveys/views.py` — imports (ya existen, no agregar de nuevo)

`openpyxl`, `DataValidation`, `Font`, `PatternFill`, `Alignment`, `BytesIO` ya se importaron en la carga masiva de empleados — no duplicar imports.

### 4. `surveys/views.py` — diccionario de catálogo y vistas nuevas

Agregar después de `upload_employees_bulk` (después de la línea donde termina esa función, buscar `return JsonResponse({'status': 'ok', 'creados': creados, 'errores': errores})` dentro de esa función y agregar justo después del bloque completo):

```python
PLAN_ACCION_CAMPOS = [
	("Área o trabajadores sujetos", "area_trabajadores", None),
	("Tipo de acción", "tipo_accion", None),
	("Fecha programada", "fecha_programada", "fecha"),
	("Responsable", "responsable", None),
	("Estado", "estado", [("Pendiente", "pendiente"), ("En proceso", "en_proceso"), ("Completado", "completado")]),
	("Evaluación posterior", "evaluacion_posterior", None),
]
PLAN_ACCION_MAX_FILAS = 200

def download_plan_accion_template(request, workplace_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse_lazy('login'))
	if not request.user.workplaces.filter(id=workplace_id).exists():
		return HttpResponseRedirect(reverse_lazy('workplaces'))
	wk = Workplace.objects.filter(id=workplace_id).last()

	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "PlanAccion"

	header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
	header_font = Font(color="FFFFFF", bold=True)
	example_fill = PatternFill(start_color="FFF9DB", end_color="FFF9DB", fill_type="solid")

	for col_idx, (label, field, opciones) in enumerate(PLAN_ACCION_CAMPOS, start=1):
		cell = ws.cell(row=1, column=col_idx, value=label)
		cell.font = header_font
		cell.fill = header_fill
		cell.alignment = Alignment(wrap_text=True, vertical="center")
		ws.column_dimensions[cell.column_letter].width = 30

	ejemplos = [
		["EJEMPLO 1 — borra esta fila antes de subir", "Rediseño de cargas de trabajo en Producción",
			"2026-09-15", "Ing. Rosa Delgado", "En proceso", "Reaplicación de cuestionario en 6 meses"],
		["EJEMPLO 2 — borra esta fila antes de subir", "Campaña de sensibilización contra la violencia laboral",
			"2026-10-01", "Lic. Marco Reyes", "Pendiente", "Encuesta de percepción post-campaña"],
	]
	for row_idx, fila in enumerate(ejemplos, start=2):
		for col_idx, valor in enumerate(fila, start=1):
			cell = ws.cell(row=row_idx, column=col_idx, value=valor)
			cell.fill = example_fill

	ws_listas = wb.create_sheet("Listas")
	ws_listas.sheet_state = "hidden"
	for col_idx, (label, field, opciones) in enumerate(PLAN_ACCION_CAMPOS, start=1):
		if not opciones or opciones == "fecha":
			continue
		for row_idx, (texto, _codigo) in enumerate(opciones, start=1):
			ws_listas.cell(row=row_idx, column=col_idx, value=texto)
		col_letter = ws_listas.cell(row=1, column=col_idx).column_letter
		rango = f"Listas!${col_letter}$1:${col_letter}${len(opciones)}"
		dv = DataValidation(type="list", formula1=f"={rango}", allow_blank=False, showErrorMessage=True)
		dv.error = "Selecciona una opción de la lista."
		dv.errorTitle = "Valor no válido"
		main_col_letter = ws.cell(row=1, column=col_idx).column_letter
		dv.add(f"{main_col_letter}4:{main_col_letter}{PLAN_ACCION_MAX_FILAS + 3}")
		ws.add_data_validation(dv)

	# Columna de fecha: formato de celda como texto guia, sin forzar tipo (evita rechazos por localizacion de Excel)
	fecha_col_letter = ws.cell(row=1, column=3).column_letter
	for r in range(4, PLAN_ACCION_MAX_FILAS + 4):
		ws.cell(row=r, column=3).number_format = 'YYYY-MM-DD'

	ws.freeze_panes = "A2"

	buffer = BytesIO()
	wb.save(buffer)
	buffer.seek(0)
	response = HttpResponse(
		buffer.getvalue(),
		content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	)
	nombre_archivo = f"plan_accion_{wk.name}.xlsx".replace(" ", "_")
	response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
	return response

def upload_plan_accion_bulk(request):
	if request.method != 'POST':
		return JsonResponse({'status': 'error', 'error': 'Método no permitido'}, status=405)
	if not request.user.is_authenticated:
		return JsonResponse({'status': 'error', 'error': 'No autenticado'}, status=401)
	workplace_id = request.POST.get('workplace_id')
	if not request.user.workplaces.filter(id=workplace_id).exists():
		return JsonResponse({'status': 'error', 'error': 'Centro de trabajo no encontrado'}, status=403)
	wk = Workplace.objects.filter(id=workplace_id).last()

	archivo = request.FILES.get('file')
	if not archivo:
		return JsonResponse({'status': 'error', 'error': 'No se recibió ningún archivo'}, status=400)
	if not archivo.name.lower().endswith('.xlsx'):
		return JsonResponse({'status': 'error', 'error': 'El archivo debe ser .xlsx (el generado por "Descargar plantilla")'}, status=400)
	if archivo.size > 5 * 1024 * 1024:
		return JsonResponse({'status': 'error', 'error': 'El archivo excede el tamaño máximo permitido (5 MB)'}, status=400)

	try:
		wb = openpyxl.load_workbook(archivo, data_only=True)
		ws = wb["PlanAccion"] if "PlanAccion" in wb.sheetnames else wb.active
	except Exception:
		return JsonResponse({'status': 'error', 'error': 'No se pudo leer el archivo. Verifica que sea un .xlsx válido y no esté dañado.'}, status=400)

	encabezados_esperados = [campo[0] for campo in PLAN_ACCION_CAMPOS]
	encabezados_archivo = [cell.value for cell in ws[1]][:len(encabezados_esperados)]
	if encabezados_archivo != encabezados_esperados:
		return JsonResponse({
			'status': 'error',
			'error': 'Los encabezados del archivo no coinciden con la plantilla. Descarga la plantilla actual y no modifiques los nombres de columna.',
		}, status=400)

	filas_datos = list(ws.iter_rows(min_row=2, values_only=False))
	if len(filas_datos) > PLAN_ACCION_MAX_FILAS:
		return JsonResponse({
			'status': 'error',
			'error': f'El archivo tiene más de {PLAN_ACCION_MAX_FILAS} filas. Divide la carga en varios archivos.',
		}, status=400)

	mapas_por_columna = []
	for label, field, opciones in PLAN_ACCION_CAMPOS:
		mapas_por_columna.append({texto.strip().lower(): codigo for texto, codigo in opciones} if isinstance(opciones, list) else None)

	creados = 0
	errores = []

	for fila in filas_datos:
		numero_fila_excel = fila[0].row
		valores = [c.value for c in fila]
		if all((v is None or str(v).strip() == '') for v in valores):
			continue
		primer_valor = str(valores[0]).strip() if valores[0] is not None else ''
		if primer_valor.upper().startswith('EJEMPLO '):
			continue

		datos_limpios = {}
		error_fila = None

		for idx, (label, field, opciones) in enumerate(PLAN_ACCION_CAMPOS):
			valor_crudo = valores[idx]
			if field == 'fecha_programada':
				if valor_crudo is None or (isinstance(valor_crudo, str) and not valor_crudo.strip()):
					error_fila = f'"{label}" no puede quedar vacío.'
					break
				if hasattr(valor_crudo, 'date'):
					datos_limpios[field] = valor_crudo.date() if hasattr(valor_crudo, 'date') and callable(valor_crudo.date) else valor_crudo
				elif hasattr(valor_crudo, 'year'):
					datos_limpios[field] = valor_crudo
				else:
					try:
						from datetime import datetime as _dt
						datos_limpios[field] = _dt.strptime(str(valor_crudo).strip(), '%Y-%m-%d').date()
					except ValueError:
						error_fila = f'"{label}" — "{valor_crudo}" no es una fecha válida. Usa el formato AAAA-MM-DD (ej. 2026-09-15).'
						break
				continue
			valor_txt = str(valor_crudo).strip() if valor_crudo is not None else ''
			if not valor_txt:
				error_fila = f'"{label}" no puede quedar vacío.'
				break
			if opciones is None:
				datos_limpios[field] = valor_txt
			else:
				codigo = mapas_por_columna[idx].get(valor_txt.lower())
				if codigo is None:
					opciones_validas = ', '.join(texto for texto, _c in opciones)
					error_fila = f'"{label}" — "{valor_txt}" no coincide con ninguna opción. Usa una del menú desplegable: {opciones_validas}.'
					break
				datos_limpios[field] = codigo

		if error_fila:
			errores.append({'fila': numero_fila_excel, 'accion': datos_limpios.get('tipo_accion', primer_valor) or '(fila sin tipo de acción)', 'error': error_fila})
			continue

		PlanAccionItem.objects.create(workplace=wk, **datos_limpios)
		creados += 1

	return JsonResponse({'status': 'ok', 'creados': creados, 'errores': errores})

def get_plan_accion(request):
	workplace_id = request.GET.get('workplace_id')
	if not request.user.workplaces.filter(id=workplace_id).exists():
		return JsonResponse({'items': []})
	items = PlanAccionItem.objects.filter(workplace_id=workplace_id).order_by('fecha_programada')
	data = [{
		'id': item.id,
		'area_trabajadores': item.area_trabajadores,
		'tipo_accion': item.tipo_accion,
		'fecha_programada': item.fecha_programada.strftime('%d/%m/%Y'),
		'responsable': item.responsable,
		'evaluacion_posterior': item.evaluacion_posterior,
		'estado': item.estado,
		'estado_display': item.get_estado_display(),
	} for item in items]
	return JsonResponse({'items': data})

def guardar_estado_accion(request, accion_id):
	if request.method != 'POST':
		return JsonResponse({'error': 'method_not_allowed'}, status=405)
	item = PlanAccionItem.objects.filter(id=accion_id, workplace__user=request.user).first()
	if not item:
		return JsonResponse({'error': 'not_found'}, status=404)
	estado = request.POST.get('estado')
	if estado not in dict(PlanAccionItem.ESTADO_CHOICES):
		return JsonResponse({'error': 'estado_invalido'}, status=400)
	item.estado = estado
	item.save()
	return JsonResponse({'ok': True})
```

**Nota sobre la columna de fecha:** `openpyxl`, al leer una celda que Excel reconoce como fecha (independientemente de cómo la haya tecleado el usuario, siempre que Excel la interprete como fecha), devuelve un objeto `datetime`/`date` directamente en `cell.value` — por eso el parser primero revisa `hasattr(valor_crudo, 'year')` antes de intentar parsear texto plano con `strptime('%Y-%m-%d')` como respaldo (por si el usuario escribió la fecha como texto sin que Excel la reconociera como fecha real).

### 5. `nom035/urls.py` — rutas nuevas

Buscar la línea `path('get_portafolio_status/', get_portafolio_status, name='get_portafolio_status'),` (línea 103 actual) y agregar justo después:

```python
    path('workplaces/<int:workplace_id>/plan_accion/plantilla/', download_plan_accion_template, name='download_plan_accion_template'),
    path('plan_accion/carga_masiva/', upload_plan_accion_bulk, name='upload_plan_accion_bulk'),
    path('get_plan_accion/', get_plan_accion, name='get_plan_accion'),
    path('guardar_estado_accion/<int:accion_id>/', guardar_estado_accion, name='guardar_estado_accion'),
```

### 6. `surveys/templates/evidence.html` — nueva sección "Plan de acción"

**6.1 — CSS.** Agregar al bloque `<style>` existente (junto a las clases `.checklist-*` ya definidas, por ejemplo después de la línea donde termina `.checklist-empty-hint`):

```css
/* ── Plan de accion (numeral 8.4) ─────────────────────────── */
.section-card { background: var(--bg-base); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); overflow: hidden; margin-bottom: 22px; }
.section-card-header { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; padding:18px 22px; border-bottom:1px solid var(--border); }
.section-card-title { font-family:'Plus Jakarta Sans',sans-serif; font-size:14px; font-weight:800; color:var(--text-primary); }
.section-card-sub { font-size:11.5px; color:var(--text-muted); margin-top:2px; }
.section-card-body { padding:20px 22px; }
.pa-steps { display:flex; flex-direction:column; gap:0; margin-bottom:18px; }
.pa-step { display:flex; gap:16px; padding:16px 0; }
.pa-step:not(:last-child) { border-bottom:1px solid var(--border); }
.pa-step-num { width:26px; height:26px; border-radius:50%; background:var(--primary-light); color:var(--primary); display:flex; align-items:center; justify-content:center; font-family:'Plus Jakarta Sans',sans-serif; font-weight:800; font-size:12px; flex-shrink:0; }
.pa-step-title { font-family:'Plus Jakarta Sans',sans-serif; font-size:13.5px; font-weight:700; margin:2px 0 4px; }
.pa-step-desc { font-size:12.5px; color:var(--text-secondary); line-height:1.55; margin:0 0 12px; }
.pa-result-summary { display:flex; gap:12px; margin-bottom:16px; }
.pa-result-tile { flex:1; border-radius:var(--radius-md); padding:12px 16px; border:1px solid var(--border); }
.pa-result-tile.ok { background:#f0fdf4; border-color:#bbf0cd; }
.pa-result-tile.err { background:#fef2f2; border-color:#fbd0d0; }
.pa-result-tile-num { font-family:'Plus Jakarta Sans',sans-serif; font-size:20px; font-weight:800; }
.pa-result-tile.ok .pa-result-tile-num { color:#16a34a; }
.pa-result-tile.err .pa-result-tile-num { color:#dc2626; }
.pa-error-table { width:100%; border-collapse:collapse; font-size:12px; margin-top:10px; }
.pa-error-table th, .pa-error-table td { padding:8px 10px; border:1px solid var(--border); text-align:left; }
.pa-error-table th { background:var(--bg-surface); font-weight:700; color:var(--text-secondary); }
.accion-item { display:grid; grid-template-columns:1fr 172px 128px; align-items:center; gap:14px; padding:16px 18px; background:var(--bg-base); border:1px solid var(--border); border-left:4px solid var(--text-muted); border-radius:var(--radius-md); margin-bottom:10px; }
.accion-item.is-en_proceso { border-left-color:#d97706; }
.accion-item.is-completado { border-left-color:#16a34a; }
.accion-tipo { font-size:13px; font-weight:700; color:var(--text-primary); margin:0 0 3px; }
.accion-meta { font-size:11.5px; color:var(--text-muted); display:flex; flex-wrap:wrap; gap:4px 12px; }
.accion-meta b { color:var(--text-secondary); font-weight:600; }
.accion-pill { display:inline-block; font-size:10.5px; font-weight:700; padding:2px 8px; border-radius:999px; margin-left:8px; }
.accion-item.is-pendiente .accion-pill { background:#f1f5f9; color:#475569; }
.accion-item.is-en_proceso .accion-pill { background:#fffbeb; color:#d97706; }
.accion-item.is-completado .accion-pill { background:#f0fdf4; color:#16a34a; }
.accion-select { width:100%; padding:8px 10px; font-size:12.5px; border:1.5px solid var(--border); border-radius:var(--radius-sm); background:var(--bg-base); color:var(--text-primary); }
.accion-save-btn[disabled] { opacity:.45; cursor:not-allowed; }
```

**6.2 — HTML.** Insertar la nueva tarjeta justo después del cierre del `<div class="checklist">...</div>` existente (después de la línea 354 actual, antes del comentario `<!-- Results -->` en línea 356 actual):

```html
      <!-- Plan de accion (numeral 8.4) -->
      <div class="section-card" v-if="workplace">
        <div class="section-card-header">
          <div>
            <p class="section-card-title">Plan de acción — numeral 8.4</p>
            <p class="section-card-sub">Control de avances del Programa de intervención</p>
          </div>
        </div>
        <div class="section-card-body">

          <div class="checklist-instruction-banner">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            <p>Descarga la plantilla, regístrala con las acciones definidas en tu Programa de intervención y súbela aquí. Cada acción queda como una fila con su propio estado, que puedes actualizar cuando avances — sin necesidad de volver a subir el archivo.</p>
          </div>

          <div class="pa-steps">
            <div class="pa-step">
              <div class="pa-step-num">1</div>
              <div>
                <p class="pa-step-title">Descarga la plantilla</p>
                <p class="pa-step-desc">Incluye las 6 columnas del numeral 8.4 (área o trabajadores sujetos, tipo de acción, fecha programada, responsable, estado, evaluación posterior) con 2 filas de ejemplo.</p>
                <a class="btn btn-primary" :href="'/workplaces/' + workplace + '/plan_accion/plantilla/'">Descargar plantilla (.xlsx)</a>
              </div>
            </div>
            <div class="pa-step">
              <div class="pa-step-num">2</div>
              <div>
                <p class="pa-step-title">Sube el archivo lleno</p>
                <p class="pa-step-desc">Las filas correctas se agregan de inmediato; si alguna tiene error, se reporta con el motivo exacto.</p>
                <input type="file" id="input-archivo-plan-accion" accept=".xlsx" style="margin-bottom:12px;">
                <div>
                  <button type="button" class="btn btn-primary" @click="procesarPlanAccion">Procesar archivo</button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="plan_accion_resultado">
            <div class="pa-result-summary">
              <div class="pa-result-tile ok"><div class="pa-result-tile-num">${plan_accion_resultado.creados}</div><div>Acciones agregadas</div></div>
              <div class="pa-result-tile err"><div class="pa-result-tile-num">${plan_accion_resultado.errores.length}</div><div>Filas con error</div></div>
            </div>
            <table class="pa-error-table" v-if="plan_accion_resultado.errores.length">
              <thead><tr><th>Fila</th><th>Acción</th><th>Error</th></tr></thead>
              <tbody>
                <tr v-for="err in plan_accion_resultado.errores">
                  <td>${err.fila}</td><td>${err.accion}</td><td>${err.error}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <p class="checklist-section-label" v-if="plan_accion.length">Acciones registradas</p>
          <div v-for="item in plan_accion" class="accion-item" :class="'is-' + item.estado">
            <div>
              <p class="accion-tipo">${item.tipo_accion}<span class="accion-pill">${item.estado_display}</span></p>
              <p class="accion-meta">
                <span><b>Área/trabajadores:</b> ${item.area_trabajadores}</span>
                <span><b>Fecha programada:</b> ${item.fecha_programada}</span>
                <span><b>Responsable:</b> ${item.responsable}</span>
                <span><b>Evaluación posterior:</b> ${item.evaluacion_posterior}</span>
              </p>
            </div>
            <select class="accion-select" v-model="item.estado_nuevo">
              <option value="pendiente">Pendiente</option>
              <option value="en_proceso">En proceso</option>
              <option value="completado">Completado</option>
            </select>
            <button
              class="btn btn-primary accion-save-btn"
              type="button"
              :disabled="item.estado_nuevo === item.estado"
              @click="guardarEstadoAccion(item)"
            >Guardar</button>
          </div>
          <p class="empty-hint" v-if="workplace && !plan_accion.length">Aún no hay acciones registradas para este centro.</p>

        </div>
      </div>
```

**6.3 — JS.** En el bloque `data` del Vue app (línea 499-504 actuales), agregar 2 propiedades nuevas:

```javascript
    data: {
      workplace: {% if preselected_workplace_id %}{{ preselected_workplace_id }}{% else %}null{% endif %},
      results: [],
      portafolio_status: [],
      cumplimiento_pct: 0,
      plan_accion: [],
      plan_accion_resultado: null
    },
```

En `methods`, agregar 3 métodos nuevos (junto a `guardarEstadoChecklist`), y llamar `get_plan_accion()` dentro de `on_workplace_change()`:

```javascript
      on_workplace_change(){
        this.get_portafolio_status();
        this.get_results();
        this.get_plan_accion();
      },
```

```javascript
      get_plan_accion(){
        var dis=this;
        if(!dis.workplace){ return; }
        $.ajax({
          url: "{% url 'get_plan_accion' %}",
          data: {'workplace_id': dis.workplace},
          dataType: 'json',
          success: function(data){
            data.items.forEach(function(item){ item.estado_nuevo = item.estado; });
            dis.plan_accion = data.items;
          }
        });
      },
      guardarEstadoAccion(item){
        var dis=this;
        $.ajax({
          type: 'POST',
          url: '/guardar_estado_accion/' + item.id + '/',
          data: {'estado': item.estado_nuevo},
          dataType: 'json',
          success: function(resp){
            if (resp.ok) { dis.get_plan_accion(); }
          },
          error: function(){ alert('No se pudo guardar el estado, intenta de nuevo.'); }
        });
      },
      procesarPlanAccion(){
        var dis=this;
        var archivo = document.getElementById('input-archivo-plan-accion').files[0];
        if (!archivo) {
          toastr.error('Error', 'Selecciona un archivo .xlsx primero', {positionClass:'toast-bottom-right', containerId:'toast-bottom-right'});
          return;
        }
        var formData = new FormData();
        formData.append('file', archivo);
        formData.append('workplace_id', dis.workplace);
        $.ajax({
          url: "{% url 'upload_plan_accion_bulk' %}",
          method: 'POST',
          data: formData,
          processData: false,
          contentType: false,
          dataType: 'json',
          success: function(data){
            dis.plan_accion_resultado = data;
            dis.get_plan_accion();
          },
          error: function(xhr){
            var msg = 'Ocurrió un error al procesar el archivo';
            try { msg = JSON.parse(xhr.responseText).error || msg; } catch(e) {}
            toastr.error('Error', msg, {positionClass:'toast-bottom-right', containerId:'toast-bottom-right'});
          }
        });
      },
```

(`toastr` ya está disponible globalmente en el layout base, igual que en `employeeform.html`.)

## Validación requerida

1. `python -m py_compile surveys/views.py surveys/models.py`.
2. `python manage.py makemigrations --check --dry-run` (no debe generar migraciones pendientes fuera de la `0044` ya creada) y `python manage.py check`.
3. `python manage.py migrate` local sin errores.
4. Descargar la plantilla desde un centro real: confirmar 6 columnas, encabezados exactos, 2 filas de ejemplo, menús desplegables en "Estado" desde la fila 4.
5. Subir la plantilla sin editar (con las 2 filas de ejemplo): debe reportar `creados: 0, errores: []` (las filas de ejemplo se ignoran, igual que en carga masiva de empleados).
6. Subir con datos válidos: confirmar que se crean los `PlanAccionItem` correctos, con `fecha_programada` parseada correctamente como fecha real (no como texto).
7. Probar con una fila con "Estado" inválido (ej. "En progreso" en vez de "En proceso"): debe reportarse con las opciones válidas listadas.
8. Probar con una fecha inválida (texto que no sea fecha ni parseable como `AAAA-MM-DD`): debe reportarse el error específico de fecha.
9. Probar con encabezados alterados: debe rechazar el archivo completo.
10. Probar `get_plan_accion`: devuelve las acciones del centro ordenadas por fecha programada, con `estado_display` legible.
11. Probar `guardar_estado_accion`: cambiar el estado de una acción real, confirmar que persiste en BD; probar con un `accion_id` de un centro ajeno (debe devolver 404, sin modificar nada); probar con un valor de `estado` inválido (debe devolver 400).
12. Prueba visual en navegador: en Portafolio de Evidencias, con un centro seleccionado, aparece la tarjeta "Plan de acción — numeral 8.4"; descargar/subir plantilla funciona; cada acción muestra su borde de color según estado, el botón "Guardar" se habilita solo al cambiar el selector, y guardar persiste y refresca la lista sin recargar la página. Sin errores de consola.
13. Confirmar que el checklist de documentos existente y la sección de Resultados siguen funcionando exactamente igual (no debe haber regresión).

## Fuera de alcance

- No se construye ninguna abstracción compartida entre el importador de carga masiva de empleados y el de plan de acción — son funciones/vistas independientes, cada una con su propio diccionario de campos (`EMPLEADO_CAMPOS_CARGA_MASIVA` / `PLAN_ACCION_CAMPOS`). Se factoriza si en el futuro aparece un tercer caso de uso real.
- No se agrega vista tipo kanban ni tablero de arrastrar y soltar (explícitamente diferido a v2.0).
- No se agregan recordatorios/notificaciones basados en `fecha_programada`.
- No se agrega gráfica ni reporte de avance histórico del plan.
- No se permite asignar `responsable` a un usuario real del sistema — sigue siendo texto libre.
- No se guarda el archivo `.xlsx` subido en el servidor — se procesa en memoria y se descarta.
- No se modifica el checklist de documentos existente (`EvidenciaFaseC`) ni la sección de Resultados de `evidence.html`.
