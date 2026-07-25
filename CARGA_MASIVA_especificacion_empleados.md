# Carga masiva de empleados por Excel

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/carga-masiva-empleados`
- `surveys/views.py` usa TABS (confirmado con `cat -A`, no usar espacios al indentar). `surveys/templates/*.html` es HTML/JS.
- No se agrega ningún modelo ni migración nueva — esta feature solo crea instancias de `Employee`, que ya existe.
- `openpyxl` ya está disponible en el venv como dependencia transitiva de `django-import-export`/`tablib` (confirmado: `openpyxl==3.1.5` instalado), pero **no está declarado explícitamente en `requirements.txt`**. Agregarlo explícito (ver sección 1) para no depender de una resolución transitiva frágil en el rebuild de Docker.
- `python -m py_compile surveys/views.py` antes de cualquier commit.
- `python manage.py check` antes de cualquier commit (no debe haber migraciones pendientes relacionadas con esto — no se tocó ningún modelo).

## Contexto

Hallazgo #2 de `SOCIOS_feedback_correcciones.md`, marcado por Jorge como **prioridad alta, bloqueante antes de vender** (24 jul 2026): hoy el alta de empleados es 100% manual, uno por uno, vía `employeeform.html` → `POST /api/employee/` (`EmployeeList.post`, `surveys/views.py`). Para centros con muchos empleados (o cuentas con varios centros) esto es inviable.

Jorge aprobó un mockup (pestaña nueva "Carga masiva" junto a la pantalla actual de alta individual) con este flujo:
1. Descargar una plantilla `.xlsx` con las 14 columnas ya listas, menús desplegables reales de Excel en los campos de catálogo (para no forzar al usuario a memorizar códigos), y 2 filas de ejemplo claramente marcadas para borrar.
2. Llenar la plantilla.
3. Subir el archivo. Se valida fila por fila: **las filas correctas se importan de inmediato; las filas con error se reportan una por una con el motivo exacto, sin rechazar el archivo completo** (decisión de producto ya confirmada — no aplica el criterio de "todo o nada").
4. El único caso de rechazo total del archivo es un **desajuste estructural** (encabezados no coinciden con la plantilla) — ahí no se puede ni mapear columnas, así que se rechaza completo con un mensaje claro.

**Nota importante para Fase 3-C:** el importador de plantillas construido aquí (parseo de `.xlsx` subido, reporte de errores fila por fila, patrón de respuesta JSON) es la pieza de infraestructura que se reutiliza para el Plan de Acción del numeral 8.4 (Fase 3-C) — mantener el diseño del parser lo más genérico posible en nombres de función/variables para facilitar esa reutilización futura, pero **no** construir ninguna abstracción compartida todavía (YAGNI — se factoriza cuando exista el segundo caso de uso real).

**Esta especificación NO modifica el alta individual existente** (`EmployeeFormView`, `EmployeeList.post`, el formulario "Uno por uno") — solo agrega la pestaña y los endpoints nuevos junto a lo que ya existe.

## Mapeo de campos y catálogos (fuente única de verdad)

Este mapeo debe vivir en **una sola función/diccionario reutilizado tanto por el generador de la plantilla como por el parser** (no duplicar los textos en dos lugares). Los textos de catálogo replican exactamente lo que ya usa `employeeform.html` (formulario individual) para que la experiencia sea consistente — nótese que para "Sexo" el texto del formulario individual ("Masculino"/"Femenino") difiere del `verbose_name` de las choices en `models.py` ("Hombre"/"Mujer"); se usa el texto del formulario porque es lo que el usuario ya conoce de la app.

Columnas de la plantilla, en este orden exacto:

| # | Columna (encabezado) | Campo `Employee` | Tipo | Opciones válidas (label → código) |
|---|---|---|---|---|
| 1 | Nombre completo | `name` | texto libre | — (mínimo 6 caracteres, igual que la regla ya existente en el JS del alta individual) |
| 2 | Sexo | `gender` | catálogo | Masculino→1, Femenino→2 |
| 3 | Edad | `age` | catálogo | 15–19 años→0, 20–24 años→1, 25–29 años→2, 30–34 años→3, 35–39 años→4, 40–44 años→5, 45–49 años→6, 50–54 años→7, 55–59 años→8, 60–64 años→9, 65–69 años→10, 70 o más años→11 |
| 4 | Estado civil | `civil_state` | catálogo | Casado→0, Divorciado→1, Soltero→2, Viudo→3, Unión Libre→4 |
| 5 | Nivel de estudios | `study_level` | catálogo | Sin formación→0, Primaria→1, Secundaria→2, Preparatoria o Bachillerato→3, Técnico superior→4, Licenciatura→5, Maestría→6, Doctorado→7 |
| 6 | Ocupación, Profesión o Puesto | `ocupation` | texto libre | — |
| 7 | Departamento, Sección o Área | `department` | texto libre | — (no lleva menú desplegable; si el texto no coincide con un departamento ya existente en el centro, simplemente se crea uno nuevo — igual que ya ocurre hoy en el alta individual vía el select2 con `tags:true`) |
| 8 | Tipo de puesto | `charge_type` | catálogo | Operativo→0, Supervisor→1, Profesional o Técnico→2, Gerente→3 |
| 9 | Tipo de contratación | `contract_type` | catálogo | Por obra o proyecto→0, Por tiempo determinado (Temporal)→1, Por tiempo indeterminado→2, Por Honorarios→3 |
| 10 | Tipo de personal | `employee_type` | catálogo | Sindicalizado→0, Confianza→1, Ninguno→2 |
| 11 | Tipo de jornada | `shift_type` | catálogo | Fijo Nocturno (20:00 – 06:00 hrs)→0, Fijo Diurno (06:00 – 20:00 hrs)→1, Fijo Mixto (Combinación)→2 |
| 12 | Rotación de turnos | `shift_rotation` | catálogo | Sí→0, No→1 |
| 13 | Tiempo en el puesto actual | `time_in_charge` | catálogo | Menos de 6 meses→0, Entre 6 meses y un año→1, Entre 1 a 4 años→2, Entre 5 a 9 años→3, Entre 10 a 14 años→4, Entre 15 a 19 años→5, Entre 20 a 24 años→6, 25 años o más→7 |
| 14 | Tiempo de experiencia laboral | `exp` | catálogo | (mismas 8 opciones que la columna 13) |

Todas las 14 columnas son obligatorias (ninguna puede quedar vacía).

## Cambios requeridos

### 1. `requirements.txt` — declarar `openpyxl` explícito

Agregar la línea (junto a las demás dependencias, por ejemplo después de `Pillow==10.4.0`):

```
openpyxl==3.1.5
```

### 2. `surveys/views.py` — imports nuevos

Agregar a los imports existentes al inicio del archivo (junto a los demás imports de `django`/stdlib, no reordenar los que ya existen):

```python
from io import BytesIO
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Font, PatternFill, Alignment
```

### 3. `surveys/views.py` — diccionario único de catálogos (fuente de verdad)

Agregar antes de la clase `EmployeeFormView` (línea ~1156 actual), un módulo-nivel dict con el mapeo de la tabla de arriba:

```python
EMPLEADO_CAMPOS_CARGA_MASIVA = [
	("Nombre completo", "name", None),
	("Sexo", "gender", [("Masculino", 1), ("Femenino", 2)]),
	("Edad", "age", [
		("15–19 años", 0), ("20–24 años", 1), ("25–29 años", 2), ("30–34 años", 3),
		("35–39 años", 4), ("40–44 años", 5), ("45–49 años", 6), ("50–54 años", 7),
		("55–59 años", 8), ("60–64 años", 9), ("65–69 años", 10), ("70 o más años", 11),
	]),
	("Estado civil", "civil_state", [
		("Casado", 0), ("Divorciado", 1), ("Soltero", 2), ("Viudo", 3), ("Unión Libre", 4),
	]),
	("Nivel de estudios", "study_level", [
		("Sin formación", 0), ("Primaria", 1), ("Secundaria", 2),
		("Preparatoria o Bachillerato", 3), ("Técnico superior", 4),
		("Licenciatura", 5), ("Maestría", 6), ("Doctorado", 7),
	]),
	("Ocupación, Profesión o Puesto", "ocupation", None),
	("Departamento, Sección o Área", "department", None),
	("Tipo de puesto", "charge_type", [
		("Operativo", 0), ("Supervisor", 1), ("Profesional o Técnico", 2), ("Gerente", 3),
	]),
	("Tipo de contratación", "contract_type", [
		("Por obra o proyecto", 0), ("Por tiempo determinado (Temporal)", 1),
		("Por tiempo indeterminado", 2), ("Por Honorarios", 3),
	]),
	("Tipo de personal", "employee_type", [
		("Sindicalizado", 0), ("Confianza", 1), ("Ninguno", 2),
	]),
	("Tipo de jornada", "shift_type", [
		("Fijo Nocturno (20:00 – 06:00 hrs)", 0), ("Fijo Diurno (06:00 – 20:00 hrs)", 1),
		("Fijo Mixto (Combinación)", 2),
	]),
	("Rotación de turnos", "shift_rotation", [("Sí", 0), ("No", 1)]),
	("Tiempo en el puesto actual", "time_in_charge", [
		("Menos de 6 meses", 0), ("Entre 6 meses y un año", 1), ("Entre 1 a 4 años", 2),
		("Entre 5 a 9 años", 3), ("Entre 10 a 14 años", 4), ("Entre 15 a 19 años", 5),
		("Entre 20 a 24 años", 6), ("25 años o más", 7),
	]),
	("Tiempo de experiencia laboral", "exp", [
		("Menos de 6 meses", 0), ("Entre 6 meses y un año", 1), ("Entre 1 a 4 años", 2),
		("Entre 5 a 9 años", 3), ("Entre 10 a 14 años", 4), ("Entre 15 a 19 años", 5),
		("Entre 20 a 24 años", 6), ("25 años o más", 7),
	]),
]
CARGA_MASIVA_MAX_FILAS = 500
```

### 4. `surveys/views.py` — vista `download_employee_template`

Agregar justo después del diccionario anterior:

```python
def download_employee_template(request, workplace_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse_lazy('login'))
	if not request.user.workplaces.filter(id=workplace_id).exists():
		return HttpResponseRedirect(reverse_lazy('workplaces'))
	wk = Workplace.objects.filter(id=workplace_id).last()

	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Empleados"

	header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
	header_font = Font(color="FFFFFF", bold=True)
	example_fill = PatternFill(start_color="FFF9DB", end_color="FFF9DB", fill_type="solid")

	for col_idx, (label, field, opciones) in enumerate(EMPLEADO_CAMPOS_CARGA_MASIVA, start=1):
		cell = ws.cell(row=1, column=col_idx, value=label)
		cell.font = header_font
		cell.fill = header_fill
		cell.alignment = Alignment(wrap_text=True, vertical="center")
		ws.column_dimensions[cell.column_letter].width = 26

	ejemplos = [
		["EJEMPLO 1 — borra esta fila antes de subir", "Masculino", "30–34 años", "Casado",
			"Licenciatura", "Operador", "Producción", "Operativo", "Por tiempo indeterminado",
			"Sindicalizado", "Fijo Diurno (06:00 – 20:00 hrs)", "No", "Entre 1 a 4 años", "Entre 1 a 4 años"],
		["EJEMPLO 2 — borra esta fila antes de subir", "Femenino", "40–44 años", "Soltero",
			"Técnico superior", "Supervisora", "Logística", "Supervisor", "Por tiempo indeterminado",
			"Confianza", "Fijo Nocturno (20:00 – 06:00 hrs)", "Sí", "Entre 5 a 9 años", "Entre 10 a 14 años"],
	]
	for row_idx, fila in enumerate(ejemplos, start=2):
		for col_idx, valor in enumerate(fila, start=1):
			cell = ws.cell(row=row_idx, column=col_idx, value=valor)
			cell.fill = example_fill

	# Hoja oculta con las listas de cada catalogo, usada por las validaciones de datos
	ws_listas = wb.create_sheet("Listas")
	ws_listas.sheet_state = "hidden"
	for col_idx, (label, field, opciones) in enumerate(EMPLEADO_CAMPOS_CARGA_MASIVA, start=1):
		if not opciones:
			continue
		for row_idx, (texto, _codigo) in enumerate(opciones, start=1):
			ws_listas.cell(row=row_idx, column=col_idx, value=texto)
		col_letter = ws_listas.cell(row=1, column=col_idx).column_letter
		rango = f"Listas!${col_letter}$1:${col_letter}${len(opciones)}"
		dv = DataValidation(type="list", formula1=f"={rango}", allow_blank=False, showErrorMessage=True)
		dv.error = "Selecciona una opción de la lista."
		dv.errorTitle = "Valor no válido"
		main_col_letter = ws.cell(row=1, column=col_idx).column_letter
		dv.add(f"{main_col_letter}4:{main_col_letter}{CARGA_MASIVA_MAX_FILAS + 3}")
		ws.add_data_validation(dv)

	ws.freeze_panes = "A2"

	buffer = BytesIO()
	wb.save(buffer)
	buffer.seek(0)
	response = HttpResponse(
		buffer.getvalue(),
		content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	)
	nombre_archivo = f"plantilla_empleados_{wk.name}.xlsx".replace(" ", "_")
	response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
	return response
```

**Nota:** las filas de validación de datos se aplican desde la fila 4 (`{main_col_letter}4`) hasta la `CARGA_MASIVA_MAX_FILAS + 3`, dejando las filas 2 y 3 (ejemplos) sin el menú forzado por si el usuario decide editarlas en vez de borrarlas — no es crítico, pero evita fricción si alguien reutiliza esas filas de ejemplo en vez de borrarlas.

### 5. `surveys/views.py` — vista `upload_employees_bulk`

Agregar justo después de `download_employee_template`:

```python
def upload_employees_bulk(request):
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
		ws = wb["Empleados"] if "Empleados" in wb.sheetnames else wb.active
	except Exception:
		return JsonResponse({'status': 'error', 'error': 'No se pudo leer el archivo. Verifica que sea un .xlsx válido y no esté dañado.'}, status=400)

	encabezados_esperados = [campo[0] for campo in EMPLEADO_CAMPOS_CARGA_MASIVA]
	encabezados_archivo = [cell.value for cell in ws[1]][:len(encabezados_esperados)]
	if encabezados_archivo != encabezados_esperados:
		return JsonResponse({
			'status': 'error',
			'error': 'Los encabezados del archivo no coinciden con la plantilla. Descarga la plantilla actual y no modifiques los nombres de columna.',
		}, status=400)

	filas_datos = list(ws.iter_rows(min_row=2, values_only=False))
	if len(filas_datos) > CARGA_MASIVA_MAX_FILAS:
		return JsonResponse({
			'status': 'error',
			'error': f'El archivo tiene más de {CARGA_MASIVA_MAX_FILAS} filas. Divide la carga en varios archivos.',
		}, status=400)

	# Mapas de traduccion texto->codigo por columna, para validar y convertir cada celda
	mapas_por_columna = []
	for label, field, opciones in EMPLEADO_CAMPOS_CARGA_MASIVA:
		mapas_por_columna.append({texto.strip().lower(): codigo for texto, codigo in opciones} if opciones else None)

	creados = 0
	errores = []
	cupo_restante = wk.employee_num - wk.employees.count()

	for fila in filas_datos:
		numero_fila_excel = fila[0].row
		valores = [c.value for c in fila]
		if all((v is None or str(v).strip() == '') for v in valores):
			continue

		nombre = str(valores[0]).strip() if valores[0] is not None else ''
		datos_limpios = {}
		error_fila = None

		for idx, (label, field, opciones) in enumerate(EMPLEADO_CAMPOS_CARGA_MASIVA):
			valor_crudo = valores[idx]
			valor_txt = str(valor_crudo).strip() if valor_crudo is not None else ''
			if not valor_txt:
				error_fila = f'"{label}" no puede quedar vacío.'
				break
			if field == 'name':
				if len(valor_txt) < 6:
					error_fila = '"Nombre completo" debe tener al menos 6 caracteres.'
					break
				datos_limpios['name'] = valor_txt
			elif opciones is None:
				datos_limpios[field] = valor_txt
			else:
				codigo = mapas_por_columna[idx].get(valor_txt.lower())
				if codigo is None:
					opciones_validas = ', '.join(texto for texto, _c in opciones)
					error_fila = f'"{label}" — "{valor_txt}" no coincide con ninguna opción. Usa una del menú desplegable: {opciones_validas}.'
					break
				datos_limpios[field] = codigo

		if error_fila:
			errores.append({'fila': numero_fila_excel, 'empleado': nombre or '(fila sin nombre)', 'error': error_fila})
			continue

		if cupo_restante <= 0:
			errores.append({
				'fila': numero_fila_excel,
				'empleado': nombre,
				'error': f'Límite del centro — ya se alcanzó el máximo de {wk.employee_num} empleados para este centro de trabajo.',
			})
			continue

		Employee.objects.create(workplace=wk, **datos_limpios)
		creados += 1
		cupo_restante -= 1

	return JsonResponse({'status': 'ok', 'creados': creados, 'errores': errores})
```

### 6. `nom035/urls.py` — rutas nuevas

Buscar la línea `path('employeeform/<int:workplace_id>/', EmployeeFormView.as_view(), name='employeeform'),` (línea 81 actual) y agregar justo después:

```python
    path('employeeform/<int:workplace_id>/plantilla/', download_employee_template, name='download_employee_template'),
    path('employeeform/carga_masiva/', upload_employees_bulk, name='upload_employees_bulk'),
```

(`surveys.views` se importa con wildcard en este archivo — no requiere agregarse a ninguna lista explícita de imports, a diferencia de `surveys.psico_views`.)

### 7. `surveys/views.py` — `EmployeeFormView.get()` — contexto adicional

En el método `get` (línea ~1159-1170 actual), agregar el cupo de empleados del centro al contexto, dentro del bloque `if 'workplace_id' in kwargs:` (línea 1164-1167 actual):

```python
		if 'workplace_id' in kwargs:
			ctx['workplace_id']=kwargs['workplace_id']
			if not request.user.workplaces.filter(id=kwargs['workplace_id']).exists():
				return HttpResponseRedirect(reverse_lazy('workplaces'))
			wk = Workplace.objects.filter(id=kwargs['workplace_id']).last()
			ctx['employee_num'] = wk.employee_num
			ctx['employee_current_count'] = wk.employees.count()
		else:
			return HttpResponseRedirect(reverse_lazy('workplaces'))
```

### 8. `surveys/templates/employeeform.html` — pestaña "Carga masiva"

**8.1 — Tab switcher.** Después de `<div class="form-card-header">...</div>` (línea 178 actual, justo antes de `<div class="form-card-body">` en línea 180), agregar:

```html
  <div class="mode-tabs">
    <button type="button" class="mode-tab active" id="btn-tab-individual">Uno por uno</button>
    <button type="button" class="mode-tab" id="btn-tab-masiva">Carga masiva</button>
  </div>
```

Agregar el CSS de `.mode-tabs`/`.mode-tab` al bloque `<style>` existente (junto a `.form-card-header`, por ejemplo después de la línea 34 `.form-card-subtitle`):

```css
.mode-tabs { display:flex; gap:4px; padding:6px; margin:18px 28px 0; background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius-md); width:fit-content; }
.mode-tab { appearance:none; border:none; background:transparent; padding:8px 16px; font-family:'Inter',sans-serif; font-size:12.5px; font-weight:700; color:var(--text-secondary); border-radius:var(--radius-sm); cursor:pointer; transition:background .15s,color .15s; }
.mode-tab.active { background:var(--bg-base); color:var(--primary); box-shadow:var(--shadow-sm); }
.mode-tab:not(.active):hover { color:var(--text-primary); }
```

**8.2 — Envolver el formulario existente.** El `<div class="form-card-body">` actual (línea 180-341, que contiene el `<form id="register_form">`) se envuelve en un `<div id="panel-individual">`, sin modificar nada de su contenido interno:

```html
  <div class="form-card-body">
    <div id="panel-individual">
      <form action="." id="register_form" method="post">
        ... (todo el contenido existente del formulario, sin cambios) ...
      </form>
    </div>

    <div id="panel-masiva" style="display:none;">
      ... (ver 8.3) ...
    </div>
  </div>
```

**8.3 — Contenido de `#panel-masiva`.** Estructura tomada del mockup aprobado (2 estados: `#masiva-inicial` y `#masiva-resultado`, alternando con `display:none`/`block` vía JS):

```html
    <div id="panel-masiva" style="display:none;">
      <div id="masiva-inicial">
        <p class="form-section-label">Cómo funciona</p>
        <div class="steps">
          <div class="step">
            <div class="step-num">1</div>
            <div class="step-body">
              <p class="step-title">Descarga la plantilla</p>
              <p class="step-desc">Un archivo de Excel con las columnas ya listas y menús desplegables en cada campo de catálogo — no hay que memorizar códigos. Incluye 2 filas de ejemplo marcadas para borrar antes de subir.</p>
              <div class="seat-note">
                Este centro admite <b>{{employee_num}}</b> empleados. Ya tiene <b>{{employee_current_count}}</b> registrados.
              </div>
              <div class="actions-row">
                <a class="btn btn-primary" href="{% url 'download_employee_template' workplace_id %}">Descargar plantilla (.xlsx)</a>
              </div>
            </div>
          </div>
          <div class="step">
            <div class="step-num">2</div>
            <div class="step-body">
              <p class="step-title">Llena la plantilla</p>
              <p class="step-desc">Agrega una fila por empleado. En los campos con lista, elige una opción del menú desplegable de esa celda.</p>
            </div>
          </div>
          <div class="step">
            <div class="step-num">3</div>
            <div class="step-body">
              <p class="step-title">Sube el archivo lleno</p>
              <p class="step-desc">Las filas correctas se agregan de inmediato; si alguna tiene error, te decimos exactamente cuál.</p>
              <input type="file" id="input-archivo-masiva" accept=".xlsx" style="margin-bottom:14px;">
              <div class="actions-row">
                <button type="button" class="btn btn-primary" id="btn-procesar-masiva">Procesar archivo</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div id="masiva-resultado" style="display:none;">
        <p class="form-section-label">Resultado de la importación</p>
        <div class="result-summary">
          <div class="result-tile ok">
            <div class="result-tile-num" id="masiva-num-creados">0</div>
            <div class="result-tile-label">Empleados agregados</div>
          </div>
          <div class="result-tile err">
            <div class="result-tile-num" id="masiva-num-errores">0</div>
            <div class="result-tile-label">Filas con error, no agregadas</div>
          </div>
        </div>
        <table class="error-table" id="masiva-tabla-errores" style="display:none;">
          <thead><tr><th class="row-num">Fila</th><th>Empleado</th><th>Error</th></tr></thead>
          <tbody id="masiva-tabla-errores-body"></tbody>
        </table>
        <div class="actions-row" style="margin-top:18px;">
          <button type="button" class="btn btn-outline" id="btn-reintentar-masiva">Subir otro archivo</button>
          <a class="btn btn-primary" href="/workplaces/{{workplace_id}}">Ver empleados del centro</a>
        </div>
      </div>
    </div>
```

Agregar también al bloque `<style>` (reutilizando exactamente el CSS ya validado en el mockup aprobado, adjunto como referencia en esta rama si Jorge lo comparte, o replicar las clases `.steps`, `.step`, `.step-num`, `.step-body`, `.step-title`, `.step-desc`, `.seat-note`, `.actions-row`, `.result-summary`, `.result-tile`, `.result-tile.ok`, `.result-tile.err`, `.result-tile-num`, `.result-tile-label`, `.error-table` y sus `th`/`td`/`.row-num`/`.row-field` — usar las variables CSS ya definidas en el archivo, mismos valores usados en el mockup aprobado).

**8.4 — JS de tabs y carga masiva.** Agregar dentro del `$(document).ready(...)` existente (después del bloque de `select2` y `get_departments`, antes del segundo `$(function(){ ... $("#register_form").validate(...) })`, o en un bloque `<script>` propio al final de `{% block scripts %}`):

```javascript
$('#btn-tab-individual').on('click', function(){
    $(this).addClass('active');
    $('#btn-tab-masiva').removeClass('active');
    $('#panel-individual').show();
    $('#panel-masiva').hide();
    $('.form-footer').show();
});
$('#btn-tab-masiva').on('click', function(){
    $(this).addClass('active');
    $('#btn-tab-individual').removeClass('active');
    $('#panel-masiva').show();
    $('#panel-individual').hide();
    $('.form-footer').hide();
});
$('#btn-procesar-masiva').on('click', function(){
    var archivo = document.getElementById('input-archivo-masiva').files[0];
    if (!archivo) {
        toastr.error('Error', 'Selecciona un archivo .xlsx primero', {positionClass:'toast-bottom-right', containerId:'toast-bottom-right'});
        return;
    }
    var formData = new FormData();
    formData.append('file', archivo);
    formData.append('workplace_id', '{{workplace_id}}');
    $.ajax({
        url: "{% url 'upload_employees_bulk' %}",
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        dataType: 'json',
        success: function(data){
            $('#masiva-inicial').hide();
            $('#masiva-resultado').show();
            $('#masiva-num-creados').text(data.creados);
            $('#masiva-num-errores').text(data.errores.length);
            if (data.errores.length){
                var filasHtml = data.errores.map(function(e){
                    return '<tr><td class="row-num">' + e.fila + '</td><td>' + e.empleado + '</td><td>' + e.error + '</td></tr>';
                }).join('');
                $('#masiva-tabla-errores-body').html(filasHtml);
                $('#masiva-tabla-errores').show();
            } else {
                $('#masiva-tabla-errores').hide();
            }
        },
        error: function(xhr){
            var msg = 'Ocurrió un error al procesar el archivo';
            try { msg = JSON.parse(xhr.responseText).error || msg; } catch(e) {}
            toastr.error('Error', msg, {positionClass:'toast-bottom-right', containerId:'toast-bottom-right'});
        }
    });
});
$('#btn-reintentar-masiva').on('click', function(){
    $('#masiva-resultado').hide();
    $('#masiva-inicial').show();
    document.getElementById('input-archivo-masiva').value = '';
});
```

## Validación requerida

1. `python -m py_compile surveys/views.py`.
2. `python manage.py check` (no debe reportar migraciones pendientes — no se tocó ningún modelo).
3. Descargar la plantilla desde un centro real (vía `GET /employeeform/<workplace_id>/plantilla/` autenticado como el dueño del centro) y confirmar en Excel/LibreOffice: 14 columnas, encabezados exactos, 2 filas de ejemplo marcadas, menús desplegables funcionando en las columnas de catálogo desde la fila 4 en adelante.
4. Confirmar que un usuario NO dueño del centro recibe redirect (plantilla) — mismo patrón de ownership ya usado en el resto de la app.
5. Llenar la plantilla con datos válidos y subirla vía `POST /employeeform/carga_masiva/`: confirmar que se crean los `Employee` correctos, con los campos numéricos mapeados bien (comparar contra lo que hubiera generado el alta individual con esos mismos valores).
6. Probar con una fila con un valor de catálogo inválido (ej. "Union libre" sin tilde): debe reportarse en `errores` con el mensaje exacto y las opciones válidas listadas, sin bloquear las demás filas.
7. Probar con una fila con un campo vacío: debe reportarse el mensaje `"<Columna>" no puede quedar vacío.`.
8. Probar con encabezados alterados (ej. columna renombrada o reordenada): debe rechazar el archivo completo con el mensaje de desajuste estructural, sin crear ningún empleado.
9. Probar el tope de cupo: subir un archivo con más filas válidas que el cupo restante del centro (`employee_num - employees.count()`) — las primeras filas hasta llenar el cupo se crean, las siguientes se reportan como error de límite alcanzado.
10. Probar con un archivo que no sea `.xlsx` (ej. `.csv` renombrado): debe rechazarse con el mensaje de formato.
11. Prueba visual en navegador: pestaña "Carga masiva" alterna correctamente con "Uno por uno" (el footer con "Guardar empleado"/"Cancelar" se oculta en modo carga masiva), el flujo completo (descargar → subir → ver resultado → "Subir otro archivo") funciona sin errores de consola.
12. Confirmar que el alta individual ("Uno por uno") sigue funcionando exactamente igual que antes (no debe haber regresión).

## Fuera de alcance

- No se modifica `EmployeeList.post()` ni el flujo de alta individual existente.
- No se agrega soporte para `.csv` (solo `.xlsx`, para poder usar menús desplegables reales de Excel).
- No se construye ninguna abstracción compartida con la futura Fase 3-C todavía — se factoriza cuando exista el segundo caso de uso real de importación de plantillas.
- No se agrega historial ni auditoría de qué archivos se subieron (solo el resultado inmediato en pantalla).
- No se guarda el archivo subido en el servidor — se procesa en memoria y se descarta (mismo principio ya aplicado en Fase 2-B para evidencias).
