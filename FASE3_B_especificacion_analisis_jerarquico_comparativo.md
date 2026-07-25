# Fase 3-B — Análisis jerárquico (Categoría → Dominio → Dimensión) + Comparativo histórico

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/fase3-b-analisis-jerarquico-comparativo`
- `surveys/views.py` usa TABS (confirmado con `cat -A`, no usar espacios al indentar). `surveys/templates/*.html` es HTML/JS.
- Migración nueva: `0043_evaluation_history.py` (última existente es `0042_evidencia_fase_c_estados_reetiquetados.py`).
- `python -m py_compile surveys/views.py` antes de cualquier commit.
- `python manage.py makemigrations --check --dry-run` y `python manage.py check` antes de cualquier commit.
- **No tocar `get_chart_data`** (líneas ~1440-1943 actuales). Esa función y sus 3 pestañas (`pair-cat`/`pair-dom`/`pair-dim`) se retiran de `workplace_results.html` en esta fase, pero la función en sí se deja intacta en el backend (puede tener otros consumidores no descartados, y no aporta retirarla ahora — soló se deja de invocar/renderizar). Editar `workplace_results.html` para dejar de llamarla y de pintar esas 3 pestañas.
- `get_riesgo_general` (líneas 1944-2087 actuales) se **extiende**, no se reescribe desde cero: se agregan bloques nuevos y se enriquece el JSON de respuesta, conservando el bloque `riesgo_general`/`recomendacion_general`/`dominios` ya existente (usado hoy por la pestaña "Resumen", que no cambia en esta fase).

## Contexto

Jorge aprobó un mockup (Categoría en pills horizontales → clic expande sus Dominios → cada Dominio se expande mostrando sus Dimensiones) que sustituye las 3 pestañas planas "Categoría / Dominio / Dimensión" (heatmaps ECharts desconectados entre sí) por una sola pestaña "Análisis por dominio" que respeta la jerarquía real de la norma. Se agrega también una pestaña "Comparativo" con la evolución del Riesgo General entre evaluaciones ya finalizadas, etiquetadas con la fecha real de finalización (no "Evaluación #1/#2/#3").

**Decisiones de producto ya confirmadas con Jorge, no volver a preguntar:**

1. **Dimensión se muestra sin clasificación de riesgo inventada.** La norma NO define umbrales oficiales para Dimensión (solo existen para Cfinal, Categoría y Dominio). El código ya desplegado de `get_chart_data` inventa umbrales genéricos idénticos (`<1/<2/<3/<4` sobre una escala 0-4) para las ~20-25 dimensiones — es un bug pre-existente, no se replica. En la nueva jerarquía, cada Dimensión se muestra únicamente con un dato neutral (**% respecto al máximo posible de esa dimensión**, sin badge de color ni nivel de riesgo). El propósito de mostrar Dimensión es dar contexto granular dentro de su Dominio, no clasificar.
2. **Categoría sí tiene umbrales oficiales** (Tabla de la norma, ya verificados contra el texto del DOF) y se clasifica igual que Dominio y Cfinal.
3. **Las evaluaciones históricas no se re-etiquetan ni se migran con fecha real.** Solo se registra `fecha_finalizacion` para evaluaciones finalizadas a partir de que este cambio se despliegue. Evaluaciones previas sin registro se etiquetan como "Evaluación #N (sin fecha registrada)" en el comparativo — no hay clientes reales todavía, así que no hace falta backfill.
4. **El comparativo solo incluye evaluaciones ya finalizadas** (con datos suficientes, `status=='ok'`) — la evaluación en curso (actual) se incluye siempre al final, etiquetada como "Actual (en curso)".
5. Alcance de esta fase: **no** incluye gráficas de tendencia histórica más allá de Riesgo General + tabla de cambio por dominio entre las 2 evaluaciones más recientes (comparativas más ricas quedan documentadas como pendiente v2.0 en `ESTADO.md`, ya registrado en la sesión anterior).

## Cambios requeridos

### 1. `surveys/models.py` — nuevo modelo `EvaluationHistory`

Agregar al final del archivo (después de la última clase existente):

```python
class EvaluationHistory(models.Model):
	workplace = models.ForeignKey(Workplace, related_name="evaluation_history", on_delete=models.CASCADE)
	numero_evaluacion = models.IntegerField(u'Número de evaluación')
	guia = models.IntegerField(u'Guía aplicada (2 o 3)')
	fecha_finalizacion = models.DateTimeField(u'Fecha de finalización', auto_now_add=True)
	def __str__(self):
		return f"{self.workplace.name} - Evaluación {self.numero_evaluacion}"
	class Meta:
		ordering = ['numero_evaluacion']
```

### 2. Migración `surveys/migrations/0043_evaluation_history.py`

```python
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('surveys', '0042_evidencia_fase_c_estados_reetiquetados'),
	]

	operations = [
		migrations.CreateModel(
			name='EvaluationHistory',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('numero_evaluacion', models.IntegerField(verbose_name='Número de evaluación')),
				('guia', models.IntegerField(verbose_name='Guía aplicada (2 o 3)')),
				('fecha_finalizacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de finalización')),
				('workplace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluation_history', to='surveys.workplace')),
			],
			options={
				'ordering': ['numero_evaluacion'],
			},
		),
	]
```

Generar con `python manage.py makemigrations surveys` y comparar contra lo anterior — si Django numera distinto o agrega algo más, está bien, es solo referencia.

### 3. `surveys/views.py` — `EndEvaluation.get()` (líneas 2637-2652 actuales)

Registrar el historial de la evaluación que se está cerrando **antes** de incrementar `workplace.evaluation`:

```python
class EndEvaluation(APIView):
	http_method_names = ['get',]
	permission_classes = (IsAuthenticated,)
	authentication_classes = (TokenAuthentication,SessionAuthentication)
	def get(self, request, format=None):
		try:
			workplace_id=request.query_params.get('workplace_id') or request.data.get('workplace_id')
			workplace=Workplace.objects.filter(id=workplace_id).last()
			if workplace.es_demo:
				return Response({'status':'error', 'error':'No es posible avanzar evaluacion en un centro de trabajo de demostracion.'})
			EvaluationHistory.objects.create(
				workplace=workplace,
				numero_evaluacion=workplace.evaluation,
				guia=workplace.survey_type(),
			)
			workplace.evaluation=workplace.evaluation+1
			workplace.paid=False
			workplace.save()
			return Response({'status':'ok'})
		except Exception as e:
			return Response({'status':'error', 'error':f"error::{e}"})
```

Nota: `survey_type()` devuelve 1/2/3 según `employee_num` (1=Guía I, ≤15 empleados; el resto del código de `get_riesgo_general` solo distingue Guía II vs III vía `guia3 = wk.survey_type()==3`, así que guardar el valor crudo de `survey_type()` es suficiente para referencia futura).

### 4. `surveys/views.py` — extender `get_riesgo_general` (líneas 1944-2087 actuales)

Agregar, dentro de la misma función, después de los diccionarios `domainsA`/`domainsB` ya existentes (después de la línea 1974) y antes de `UMBRALES_DOMINIO_GUIA_II`:

```python
	dimensionA={
		"Condiciones peligrosas e inseguras":["r2_p2"],
		"Condiciones deficientes e insalubres":["r2_p1"],
		"Trabajos peligrosas":["r2_p3"],
		"Cargas cuantitativas":["r2_p4","r2_p9"],
		"Ritmos de trabajo acelerado":["r2_p5","r2_p6"],
		"Carga mental":["r2_p7","r2_p8"],
		"Cargas psicológicas emocionales":["r2_p41","r2_p42","r2_p43"],
		"Cargas de alta responsabilidad":["r2_p10","r2_p11"],
		"Cargas contradictorias o inconsistentes":["r2_p12","r2_p13"],
		"Falta de control y autonomía sobre el trabajo":["r2_p20","r2_p21","r2_p22"],
		"Limitada o nula posibilidad de desarrollo":["r2_p18","r2_p19"],
		"Limitada o inexistente capacitación":["r2_p26","r2_p27",],
		"Jornadas de trabajo extensas":["r2_p14","r2_p15"],
		"Influencia del trabajo fuera del centro laboral":["r2_p16"],
		"Influencia de las responsabilidades familiares":["r2_p17"],
		"Escasa claridad de funciones":["r2_p23","r2_p24","r2_p25"],
		"Características del liderazgo":["r2_p28","r2_p29"],
		"Relaciones sociales en el trabajo":["r2_p30","r2_p31","r2_p32"],
		"Deficiente relación con los colaboradores que supervisa":["r2_p44","r2_p45","r2_p46"],
		"Violencia laboral":["r2_p33","r2_p34","r2_p35","r2_p36","r2_p37","r2_p38","r2_p39","r2_p40"],
	}
	dimensionB={
		"Condiciones peligrosas e inseguras":["r3_p1","r3_p3"],
		"Condiciones deficientes e insalubres":["r3_p2","r3_p4"],
		"Trabajos peligrosas":["r3_p5"],
		"Cargas cuantitativas":["r3_p6","r3_p12"],
		"Ritmos de trabajo acelerado":["r3_p7","r3_p8"],
		"Carga mental":["r3_p9","r3_p10","r3_p11"],
		"Cargas psicológicas emocionales":["r3_p65","r3_p66","r3_p67","r3_p68"],
		"Cargas de alta responsabilidad":["r3_p13","r3_p14"],
		"Cargas contradictorias o inconsistentes":["r3_p15","r3_p16"],
		"Falta de control y autonomía sobre el trabajo":["r3_p25","r3_p26","r3_p27","r3_p28"],
		"Limitada o nula posibilidad de desarrollo":["r3_p23","r3_p24"],
		"Insuficiente participación y manejo del cambio":["r3_p29","r3_p30"],
		"Limitada o inexistente capacitación":["r3_p35","r3_p36"],
		"Jornadas de trabajo extensas":["r3_p17","r3_p18"],
		"Influencia del trabajo fuera del centro laboral":["r3_p19","r3_p20"],
		"Influencia de las responsabilidades familiares":["r3_p21","r3_p22"],
		"Escasa claridad de funciones":["r3_p31","r3_p32","r3_p33","r3_p34"],
		"Características del liderazgo":["r3_p37","r3_p38","r3_p39","r3_p40","r3_p41"],
		"Relaciones sociales en el trabajo":["r3_p42","r3_p43","r3_p44","r3_p45","r3_p46"],
		"Deficiente relación con los colaboradores que supervisa":["r3_p69","r3_p70","r3_p71","r3_p72"],
		"Violencia laboral":["r3_p57","r3_p58","r3_p59","r3_p60","r3_p61","r3_p62","r3_p63","r3_p64"],
		"Escasa o nula retroalimentación del desempeño":["r3_p47","r3_p48"],
		"Escasa o nulo reconocimiento y compensación":["r3_p49","r3_p50","r3_p51","r3_p52"],
		"Limitado sentido de pertenencia":["r3_p53","r3_p54"],
		"Inestabilidad laboral":["r3_p55","r3_p56"],
	}
	catA={"Ambiente de trabajo":["r2_p1","r2_p2","r2_p3"],
		"Factores propios de la actividad":["r2_p18","r2_p19","r2_p20","r2_p21","r2_p22","r2_p26","r2_p27","r2_p4","r2_p5","r2_p6","r2_p7","r2_p8","r2_p9","r2_p10","r2_p11","r2_p12","r2_p13","r2_p41","r2_p42","r2_p43"],
		"Organización del tiempo de trabajo":["r2_p14","r2_p15","r2_p16","r2_p17"],
		"Liderazgo y relaciones en el trabajo":["r2_p23","r2_p24","r2_p25","r2_p28","r2_p29","r2_p30","r2_p31","r2_p32","r2_p44","r2_p45","r2_p46","r2_p33","r2_p34","r2_p35","r2_p36","r2_p37","r2_p38","r2_p39","r2_p40"],
	}
	catB={"Ambiente de trabajo":["r3_p1","r3_p2","r3_p3","r3_p4","r3_p5"],
		"Factores propios de la actividad":["r3_p23","r3_p24","r3_p25","r3_p26","r3_p27","r3_p28","r3_p29","r3_p30","r3_p35","r3_p36","r3_p6","r3_p7","r3_p8","r3_p9","r3_p10","r3_p11","r3_p12","r3_p13","r3_p14","r3_p15","r3_p16","r3_p65","r3_p66","r3_p67","r3_p68"],
		"Organización del tiempo de trabajo":["r3_p17","r3_p18","r3_p19","r3_p20","r3_p21","r3_p22"],
		"Liderazgo y relaciones en el trabajo":["r3_p57","r3_p58","r3_p59","r3_p60","r3_p61","r3_p62","r3_p63","r3_p64","r3_p31","r3_p32","r3_p33","r3_p34","r3_p37","r3_p38","r3_p39","r3_p40","r3_p41","r3_p42","r3_p43","r3_p44","r3_p45","r3_p46","r3_p69","r3_p70","r3_p71","r3_p72",],
		"Entorno organizacional":["r3_p47","r3_p48","r3_p49","r3_p50","r3_p51","r3_p52","r3_p53","r3_p54","r3_p55","r3_p56",]}

	CATEGORIA_DOMINIOS_A = {
		"Ambiente de trabajo": ["Condiciones en el ambiente de trabajo"],
		"Factores propios de la actividad": ["Carga de trabajo", "Falta de control sobre el trabajo"],
		"Organización del tiempo de trabajo": ["Jornada de trabajo", "Interferencia en la relación trabajo-familia"],
		"Liderazgo y relaciones en el trabajo": ["Liderazgo", "Relaciones en el trabajo", "Violencia"],
	}
	CATEGORIA_DOMINIOS_B = {
		"Ambiente de trabajo": ["Condiciones en el ambiente de trabajo"],
		"Factores propios de la actividad": ["Carga de trabajo", "Falta de control sobre el trabajo"],
		"Organización del tiempo de trabajo": ["Jornada de trabajo", "Interferencia en la relación trabajo-familia"],
		"Liderazgo y relaciones en el trabajo": ["Liderazgo", "Relaciones en el trabajo", "Violencia"],
		"Entorno organizacional": ["Reconocimiento del desempeño", "Insuficiente sentido de pertenencia e inestabilidad"],
	}
	DOMINIO_DIMENSIONES_A = {
		"Condiciones en el ambiente de trabajo": ["Condiciones peligrosas e inseguras", "Condiciones deficientes e insalubres", "Trabajos peligrosas"],
		"Carga de trabajo": ["Cargas cuantitativas", "Ritmos de trabajo acelerado", "Carga mental", "Cargas psicológicas emocionales", "Cargas de alta responsabilidad", "Cargas contradictorias o inconsistentes"],
		"Falta de control sobre el trabajo": ["Falta de control y autonomía sobre el trabajo", "Limitada o nula posibilidad de desarrollo", "Limitada o inexistente capacitación"],
		"Jornada de trabajo": ["Jornadas de trabajo extensas"],
		"Interferencia en la relación trabajo-familia": ["Influencia del trabajo fuera del centro laboral", "Influencia de las responsabilidades familiares"],
		"Liderazgo": ["Escasa claridad de funciones", "Características del liderazgo"],
		"Relaciones en el trabajo": ["Relaciones sociales en el trabajo", "Deficiente relación con los colaboradores que supervisa"],
		"Violencia": ["Violencia laboral"],
	}
	DOMINIO_DIMENSIONES_B = {
		"Condiciones en el ambiente de trabajo": ["Condiciones peligrosas e inseguras", "Condiciones deficientes e insalubres", "Trabajos peligrosas"],
		"Carga de trabajo": ["Cargas cuantitativas", "Ritmos de trabajo acelerado", "Carga mental", "Cargas psicológicas emocionales", "Cargas de alta responsabilidad", "Cargas contradictorias o inconsistentes"],
		"Falta de control sobre el trabajo": ["Falta de control y autonomía sobre el trabajo", "Limitada o nula posibilidad de desarrollo", "Insuficiente participación y manejo del cambio", "Limitada o inexistente capacitación"],
		"Jornada de trabajo": ["Jornadas de trabajo extensas"],
		"Interferencia en la relación trabajo-familia": ["Influencia del trabajo fuera del centro laboral", "Influencia de las responsabilidades familiares"],
		"Liderazgo": ["Escasa claridad de funciones", "Características del liderazgo"],
		"Relaciones en el trabajo": ["Relaciones sociales en el trabajo", "Deficiente relación con los colaboradores que supervisa"],
		"Violencia": ["Violencia laboral"],
		"Reconocimiento del desempeño": ["Escasa o nula retroalimentación del desempeño", "Escasa o nulo reconocimiento y compensación"],
		"Insuficiente sentido de pertenencia e inestabilidad": ["Limitado sentido de pertenencia", "Inestabilidad laboral"],
	}

	UMBRALES_CATEGORIA_GUIA_II = {
		"Ambiente de trabajo": [3,5,7,9],
		"Factores propios de la actividad": [10,20,30,40],
		"Organización del tiempo de trabajo": [4,6,9,12],
		"Liderazgo y relaciones en el trabajo": [10,18,28,38],
	}
	UMBRALES_CATEGORIA_GUIA_III = {
		"Ambiente de trabajo": [5,9,11,14],
		"Factores propios de la actividad": [15,30,45,60],
		"Organización del tiempo de trabajo": [5,7,10,13],
		"Liderazgo y relaciones en el trabajo": [14,29,42,58],
		"Entorno organizacional": [10,14,18,23],
	}
```

(Estos umbrales de Categoría ya fueron verificados contra el texto de la norma en una sesión previa de este mismo proyecto — no se replican aquí explicaciones adicionales del origen porque ya están documentadas en `ESTADO.md`.)

Después de la línea `domains_dict = domainsB if guia3 else domainsA` (línea 2029 actual), agregar las variables equivalentes para categoría/dimensión:

```python
	domains_dict = domainsB if guia3 else domainsA
	dimensions_dict = dimensionB if guia3 else dimensionA
	cat_dict = catB if guia3 else catA
	categoria_dominios = CATEGORIA_DOMINIOS_B if guia3 else CATEGORIA_DOMINIOS_A
	dominio_dimensiones = DOMINIO_DIMENSIONES_B if guia3 else DOMINIO_DIMENSIONES_A
	umbrales_categoria = UMBRALES_CATEGORIA_GUIA_III if guia3 else UMBRALES_CATEGORIA_GUIA_II
	umbrales_dominio = UMBRALES_DOMINIO_GUIA_III if guia3 else UMBRALES_DOMINIO_GUIA_II
	umbrales_cfinal = UMBRALES_CFINAL_GUIA_III if guia3 else UMBRALES_CFINAL_GUIA_II
	survey_model = RiskSurveyB if guia3 else RiskSurveyA
```

En el bucle principal (líneas 2037-2048 actuales), junto a `sumas_por_dominio`, acumular también sumas por categoría y por dimensión (mismo patrón, reutilizando `survey` ya obtenido — no se vuelve a consultar la base de datos):

```python
	cfinal_por_empleado = []
	sumas_por_dominio = {d: [] for d in domains_dict}
	sumas_por_categoria = {c: [] for c in cat_dict}
	sumas_por_dimension = {dm: [] for dm in dimensions_dict}

	for emp in employees:
		survey = emp.surveyB.filter(evaluation=evaluation).last() if guia3 else emp.surveyA.filter(evaluation=evaluation).last()
		if not survey:
			continue
		emp_cfinal = 0
		for domain, preguntas in domains_dict.items():
			_sum = 0
			for question in preguntas:
				_sum += getattr(survey, survey_model._meta.get_field(question).attname) or 0
			sumas_por_dominio[domain].append(_sum)
			emp_cfinal += _sum
		for categoria, preguntas in cat_dict.items():
			_sum = 0
			for question in preguntas:
				_sum += getattr(survey, survey_model._meta.get_field(question).attname) or 0
			sumas_por_categoria[categoria].append(_sum)
		for dimension, preguntas in dimensions_dict.items():
			_sum = 0
			for question in preguntas:
				_sum += getattr(survey, survey_model._meta.get_field(question).attname) or 0
			sumas_por_dimension[dimension].append(_sum)
		cfinal_por_empleado.append(emp_cfinal)
```

Después del bloque `dominios_detalle`/`conteo_dominios_nivel` ya existente (líneas 2059-2070 actuales), agregar el cálculo de categorías (con clasificación oficial) y dimensiones (dato neutral, sin clasificación), y construir la jerarquía anidada:

```python
	categorias_detalle = []
	nivel_por_categoria = {}
	for categoria in cat_dict:
		valores = sumas_por_categoria[categoria]
		promedio_cat = sum(valores) / len(valores) if valores else 0
		nivel_cat = clasificar_nivel(promedio_cat, umbrales_categoria[categoria])
		nivel_por_categoria[categoria] = nivel_cat
		categorias_detalle.append({'nombre': categoria, 'nivel': nivel_cat, 'nivel_nombre': NIVEL_NOMBRE[nivel_cat]})

	nivel_por_dominio = {d['nombre']: d['nivel'] for d in dominios_detalle}

	dimensiones_pct = {}
	for dimension, preguntas in dimensions_dict.items():
		valores = sumas_por_dimension[dimension]
		promedio_dim = sum(valores) / len(valores) if valores else 0
		maximo_dim = len(preguntas) * 4
		dimensiones_pct[dimension] = round((promedio_dim / maximo_dim) * 100, 1) if maximo_dim else 0

	jerarquia = []
	for categoria, dominios_de_categoria in categoria_dominios.items():
		dominios_json = []
		for dominio in dominios_de_categoria:
			dimensiones_json = [
				{'nombre': dim, 'porcentaje': dimensiones_pct.get(dim, 0)}
				for dim in dominio_dimensiones.get(dominio, [])
			]
			dominios_json.append({
				'nombre': dominio,
				'nivel': nivel_por_dominio.get(dominio),
				'nivel_nombre': NIVEL_NOMBRE.get(nivel_por_dominio.get(dominio)),
				'dimensiones': dimensiones_json,
			})
		jerarquia.append({
			'nombre': categoria,
			'nivel': nivel_por_categoria[categoria],
			'nivel_nombre': NIVEL_NOMBRE[nivel_por_categoria[categoria]],
			'dominios': dominios_json,
		})
```

Y agregar `'jerarquia': jerarquia,` al diccionario final del `JsonResponse` (líneas 2072-2087 actuales), sin quitar ninguna clave existente:

```python
	return JsonResponse({
		'status': 'ok',
		'guia': 3 if guia3 else 2,
		'riesgo_general': {
			'promedio': round(promedio_cfinal, 1),
			'nivel': nivel_general,
			'nivel_nombre': NIVEL_NOMBRE[nivel_general],
			'distribucion': distribucion,
			'total_empleados': len(cfinal_por_empleado),
		},
		'recomendacion_general': RECOMENDACION_NIVEL_GENERAL[nivel_general],
		'dominios': {
			'conteo_por_nivel': conteo_dominios_nivel,
			'detalle': dominios_detalle,
		},
		'jerarquia': jerarquia,
	})
```

**Nota de rendimiento:** este cambio recorre 3 diccionarios adicionales por empleado en el mismo bucle que ya existía (no agrega bucles nuevos sobre `employees`, solo trabajo adicional dentro del bucle existente) — no debería notarse en tiempo de respuesta para los volúmenes actuales (hasta ~50-500 empleados por centro).

### 5. `surveys/views.py` — nueva vista `get_comparativo_evaluaciones`

Agregar después de `get_riesgo_general` (después de la línea 2087 actual, antes de `class ValidateCodeList`):

```python
def get_comparativo_evaluaciones(request):
	from django.test import RequestFactory
	workplace_id=request.GET.get('workplace_id',None)
	if not Workplace.objects.filter(id=workplace_id, user=request.user).exists():
		return JsonResponse({'error':'not_found'}, status=403)
	wk=Workplace.objects.filter(id=workplace_id).last()
	factory = RequestFactory()

	historial = {h.numero_evaluacion: h.fecha_finalizacion for h in wk.evaluation_history.all()}
	evaluaciones = []
	for numero in range(1, wk.evaluation + 1):
		fake_req = factory.get('/get_riesgo_general/', {'workplace_id': str(workplace_id), 'evaluation': str(numero)})
		fake_req.user = request.user
		data = json.loads(get_riesgo_general(fake_req).content)
		if data.get('status') != 'ok':
			continue
		es_actual = (numero == wk.evaluation)
		if es_actual:
			etiqueta = "Actual (en curso)"
		elif numero in historial:
			etiqueta = historial[numero].strftime('%d/%m/%Y')
		else:
			etiqueta = f"Evaluación #{numero} (sin fecha registrada)"
		evaluaciones.append({
			'numero_evaluacion': numero,
			'etiqueta': etiqueta,
			'es_actual': es_actual,
			'promedio': data['riesgo_general']['promedio'],
			'nivel': data['riesgo_general']['nivel'],
			'nivel_nombre': data['riesgo_general']['nivel_nombre'],
			'dominios': data['dominios']['detalle'],
		})

	if len(evaluaciones) < 1:
		return JsonResponse({'status': 'no_data'})

	cambio_dominios = []
	if len(evaluaciones) >= 2:
		anterior = evaluaciones[-2]['dominios']
		actual = evaluaciones[-1]['dominios']
		anterior_por_nombre = {d['nombre']: d for d in anterior}
		for dom_actual in actual:
			dom_anterior = anterior_por_nombre.get(dom_actual['nombre'])
			if not dom_anterior:
				continue
			if dom_actual['nivel'] > dom_anterior['nivel']:
				tendencia = 'empeoro'
			elif dom_actual['nivel'] < dom_anterior['nivel']:
				tendencia = 'mejoro'
			else:
				tendencia = 'sin_cambio'
			cambio_dominios.append({
				'nombre': dom_actual['nombre'],
				'nivel_anterior': dom_anterior['nivel_nombre'],
				'nivel_actual': dom_actual['nivel_nombre'],
				'tendencia': tendencia,
			})

	return JsonResponse({
		'status': 'ok',
		'evaluaciones': evaluaciones,
		'cambio_dominios': cambio_dominios,
		'etiqueta_anterior': evaluaciones[-2]['etiqueta'] if len(evaluaciones) >= 2 else None,
		'etiqueta_actual': evaluaciones[-1]['etiqueta'],
	})
```

### 6. `nom035/urls.py` — nueva ruta

Buscar la línea con `path('get_riesgo_general/'` (o equivalente `get_riesgo_general`) y agregar justo después:

```python
	path('get_comparativo_evaluaciones/', views.get_comparativo_evaluaciones, name='get_comparativo_evaluaciones'),
```

(Verificar el nombre exacto de importación de `views` usado en ese archivo — seguir el mismo patrón que la línea de `get_riesgo_general` ya existente.)

### 7. `surveys/templates/workplace_results.html` — reemplazo de pestañas

**7.1 — Radios de pestaña** (líneas 376-379 actuales): reemplazar `tab-cat`/`tab-dom`/`tab-dim` por `tab-analisis`/`tab-comparativo`:

```html
    <input type="radio" name="chart-tab" id="tab-resumen" checked>
    <input type="radio" name="chart-tab" id="tab-analisis">
    <input type="radio" name="chart-tab" id="tab-comparativo">
```

**7.2 — Labels de navegación** (líneas 382-397 actuales): reemplazar los 3 labels (`tab-cat`/`tab-dom`/`tab-dim`) por 2:

```html
      <label for="tab-resumen">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19V9"/><path d="M10 19V5"/><path d="M16 19v-7"/><path d="M22 19H2"/></svg>
        Resumen
      </label>
      <label for="tab-analisis">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
        Análisis por dominio
      </label>
      <label for="tab-comparativo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
        Comparativo
      </label>
```

Actualizar el CSS de selectores de pestaña (líneas 190-197 actuales, `#tab-cat:checked ~ ... #pair-cat`, etc.) para usar `#tab-analisis`/`#pair-analisis` y `#tab-comparativo`/`#pair-comparativo` en vez de los 3 selectores anteriores — mismo mecanismo CSS `:checked ~`, solo cambian los IDs.

**7.3 — Cuerpo de pestañas** (líneas 421-470 actuales, los 3 `chart-tab-pair` de cat/dom/dim): eliminar esos 3 bloques completos (incluyendo `#chart`, `#chart2`, `#chart3`, `#chart4`, `#chart5`, `#chart6`) y sustituir por:

```html
      <div class="chart-tab-pair" id="pair-analisis">
        <div class="chart-card" style="grid-column: 1 / -1;">
          <p class="chart-card-title">Análisis por Categoría → Dominio → Dimensión</p>
          <div id="analisis-status" style="font-size:13px;color:#94a3b8;"></div>
          <div id="analisis-cat-pills" class="cat-pills"></div>
          <div id="analisis-breadcrumb" class="breadcrumb"></div>
          <div id="analisis-dominios"></div>
        </div>
      </div>

      <div class="chart-tab-pair" id="pair-comparativo">
        <div class="chart-card" style="grid-column: 1 / -1;">
          <p class="chart-card-title">Riesgo General por evaluación</p>
          <div id="comparativo-status" style="font-size:13px;color:#94a3b8;"></div>
          <div id="comparativo-chart" class="compare-chart"></div>
        </div>
        <div class="chart-card" style="grid-column: 1 / -1;">
          <p class="chart-card-title" id="comparativo-tabla-titulo">Cambio por dominio</p>
          <table class="compare-table" id="comparativo-tabla">
            <thead><tr id="comparativo-tabla-head"></tr></thead>
            <tbody id="comparativo-tabla-body"></tbody>
          </table>
        </div>
      </div>
```

Agregar en el bloque `<style>` del archivo (buscar dónde están definidas las clases `.chart-card`/`.chart-tabs`, agregar junto a ellas) las clases nuevas usadas por el mockup — tomar tal cual del mockup aprobado (adjunto en esta misma rama como referencia, archivo `mockup_fase3b_analisis.html` si Jorge te lo comparte, o replicar las clases `.cat-pills`, `.cat-pill`, `.cat-badge`, `.breadcrumb`, `.dom-row`, `.dom-row-head`, `.dom-row-left`, `.dom-chevron`, `.dom-name`, `.level-pill`, `.dim-list`, `.dim-item`, `.dim-name`, `.compare-chart`, `.compare-bar-col`, `.compare-bar`, `.compare-label`, `.compare-value`, `.compare-table`, `.trend`, `.trend.up`, `.trend.down`, `.trend.same` — usar variables CSS ya definidas en el archivo (`--primary`, `--border`, `--text-muted`, etc.), no colores hardcodeados nuevos salvo los 5 de nivel de riesgo ya usados en el resto del archivo (Nulo/Bajo/Medio/Alto/Muy alto) para mantener consistencia visual con el resto de la página).

**7.4 — JS**: quitar la inicialización de `myChart`, `myChart2`, `myChart3`, `myChart4`, `myChart5`, `myChart6` (líneas 510-515 actuales) y toda referencia a ellos dentro de `loadChart()` (líneas 545+ actuales — la función completa `loadChart()` deja de usarse y puede eliminarse junto con su invocación en la línea 819, ya que solo alimentaba las 3 pestañas retiradas). **Cuidado:** verificar antes de borrar que ninguna otra parte del archivo (ej. el selector `#dept_id` en línea 821, o el resize handler en 870-872) dependa de algo que no sea exclusivamente esas 3 pestañas — el `#dept_id` change handler debe seguir refrescando `loadRiesgoGeneral()` (que sigue existiendo, alimenta "Resumen") pero ya no `loadChart()`.

Agregar dos funciones JS nuevas, invocadas junto a `loadRiesgoGeneral()` en el `$(document).ready`:

```javascript
        function nivelColor(nivel){
            var colores = {0:'#9be5f7',1:'#6bf56e',2:'#eab308',3:'#ffc000',4:'#ff7070'};
            return colores[nivel] || '#e5e7eb';
        }

        var jerarquiaData = null;
        var catActiva = null;

        function renderJerarquia(){
            if (!jerarquiaData || !jerarquiaData.length) return;
            if (catActiva === null) catActiva = jerarquiaData[0].nombre;
            var cat = jerarquiaData.find(function(c){ return c.nombre === catActiva; });

            var pillsHtml = jerarquiaData.map(function(c){
                var activeCls = (c.nombre === catActiva) ? ' active' : '';
                return '<div class="cat-pill' + activeCls + '" data-cat="' + c.nombre + '">' +
                    '<span class="cat-badge" style="background:' + nivelColor(c.nivel) + '"></span>' + c.nombre + '</div>';
            }).join('');
            $('#analisis-cat-pills').html(pillsHtml);

            $('#analisis-breadcrumb').html(cat.nombre + ' <b>&rarr;</b> ' + cat.dominios.length + ' dominio(s) en esta categoría');

            var domHtml = cat.dominios.map(function(d, idx){
                var dimHtml = d.dimensiones.map(function(dim){
                    return '<div class="dim-item"><span class="dim-name">' + dim.nombre + '</span>' +
                        '<span style="font-size:11px;color:var(--text-muted);">' + dim.porcentaje + '% del máximo</span></div>';
                }).join('');
                return '<div class="dom-row' + (idx === 0 ? ' expanded' : '') + '" data-dom-idx="' + idx + '">' +
                    '<div class="dom-row-head">' +
                    '<div class="dom-row-left">' +
                    '<svg class="dom-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18l6-6-6-6"/></svg>' +
                    '<span class="dom-name">' + d.nombre + '</span></div>' +
                    '<span class="level-pill" style="background:' + nivelColor(d.nivel) + '">' + d.nivel_nombre + '</span>' +
                    '</div>' +
                    '<div class="dim-list">' + (dimHtml || '<div style="color:var(--text-muted);font-size:12px;">Sin dimensiones registradas.</div>') + '</div>' +
                    '</div>';
            }).join('');
            $('#analisis-dominios').html(domHtml);

            $('.cat-pill').off('click').on('click', function(){
                catActiva = $(this).data('cat');
                renderJerarquia();
            });
            $('.dom-row-head').off('click').on('click', function(){
                $(this).parent('.dom-row').toggleClass('expanded');
            });
        }

        function loadAnalisisJerarquico() {
            $.ajax({
                url: "{% url 'get_riesgo_general' %}",
                data: {"workplace_id":"{{workplace_id}}","evaluation":"{{evaluation}}"},
                dataType: 'json',
                success: function(data){
                    if (data.status === 'no_data'){
                        $('#analisis-status').text('No existen suficientes datos para este centro de trabajo.');
                        $('#analisis-cat-pills, #analisis-breadcrumb, #analisis-dominios').empty();
                        return;
                    }
                    $('#analisis-status').empty();
                    jerarquiaData = data.jerarquia;
                    catActiva = null;
                    renderJerarquia();
                },
                error:function(){ $('#analisis-status').text('Ocurrió un error al cargar el análisis.'); }
            });
        }

        function loadComparativo() {
            $.ajax({
                url: "{% url 'get_comparativo_evaluaciones' %}",
                data: {"workplace_id":"{{workplace_id}}"},
                dataType: 'json',
                success: function(data){
                    if (data.status === 'no_data'){
                        $('#comparativo-status').text('Aún no hay evaluaciones finalizadas con datos suficientes para comparar.');
                        $('#comparativo-chart, #comparativo-tabla-head, #comparativo-tabla-body').empty();
                        return;
                    }
                    $('#comparativo-status').empty();
                    var maxProm = Math.max.apply(null, data.evaluaciones.map(function(e){ return e.promedio; }).concat([1]));
                    var barsHtml = data.evaluaciones.map(function(e){
                        var alturaPx = Math.max(4, Math.round((e.promedio / maxProm) * 100));
                        return '<div class="compare-bar-col">' +
                            '<span class="compare-value">' + e.promedio + '</span>' +
                            '<div class="compare-bar" style="height:' + alturaPx + 'px; background:' + nivelColor(e.nivel) + ';"></div>' +
                            '<span class="compare-label">' + e.etiqueta + '<br>' + e.nivel_nombre + '</span>' +
                            '</div>';
                    }).join('');
                    $('#comparativo-chart').html(barsHtml);

                    if (data.cambio_dominios && data.cambio_dominios.length){
                        $('#comparativo-tabla-titulo').text('Cambio por dominio — ' + data.etiqueta_anterior + ' vs ' + data.etiqueta_actual);
                        $('#comparativo-tabla-head').html('<th>Dominio</th><th>' + data.etiqueta_anterior + '</th><th>' + data.etiqueta_actual + '</th><th>Cambio</th>');
                        var filasHtml = data.cambio_dominios.map(function(c){
                            var trendCls = c.tendencia === 'empeoro' ? 'up' : (c.tendencia === 'mejoro' ? 'down' : 'same');
                            var trendTxt = c.tendencia === 'empeoro' ? '&uarr; Empeoró' : (c.tendencia === 'mejoro' ? '&darr; Mejoró' : '= Sin cambio');
                            return '<tr><td>' + c.nombre + '</td><td>' + c.nivel_anterior + '</td><td>' + c.nivel_actual + '</td>' +
                                '<td class="trend ' + trendCls + '">' + trendTxt + '</td></tr>';
                        }).join('');
                        $('#comparativo-tabla-body').html(filasHtml);
                    } else {
                        $('#comparativo-tabla-titulo').text('Cambio por dominio');
                        $('#comparativo-tabla-head').empty();
                        $('#comparativo-tabla-body').html('<tr><td style="color:var(--text-muted);">Se necesitan al menos 2 evaluaciones finalizadas para comparar dominios.</td></tr>');
                    }
                },
                error:function(){ $('#comparativo-status').text('Ocurrió un error al cargar el comparativo.'); }
            });
        }
```

Invocar ambas junto a `loadRiesgoGeneral()` (donde hoy están las líneas 819-820):

```javascript
        loadRiesgoGeneral();
        loadAnalisisJerarquico();
        loadComparativo();
```

En el `#dept_id` change handler (línea 821 actual): **no** agregar `loadAnalisisJerarquico()`/`loadComparativo()` ahí — el análisis jerárquico y el comparativo son a nivel de centro de trabajo completo (igual que "Resumen"), no se filtran por departamento (`get_riesgo_general` y `get_comparativo_evaluaciones` no reciben `dept_id`, a diferencia de `get_chart_data`). Confirmar que el handler solo sigue llamando a lo que ya llamaba antes menos `loadChart()`.

Quitar del resize handler (líneas 870-872 actuales) las referencias a `myChart`...`myChart6` — ya no existen esos elementos.

## Validación requerida

1. `python -m py_compile surveys/views.py` y `python -m py_compile surveys/models.py`.
2. `python manage.py makemigrations --check --dry-run` (no debe generar migraciones pendientes fuera de la `0043` ya creada) y `python manage.py check`.
3. `python manage.py migrate` local sin errores.
4. Prueba con datos reales (usar un centro de trabajo con empleados que ya respondieron encuesta, Guía II y Guía III si es posible):
   - `get_riesgo_general` sigue devolviendo exactamente las mismas claves que antes (`status`, `guia`, `riesgo_general`, `recomendacion_general`, `dominios`) más la nueva `jerarquia` — no debe romper "Resumen".
   - `jerarquia` tiene 4 categorías (Guía II) o 5 (Guía III), cada una con sus dominios anidados correctamente (usar el mapeo de esta especificación), y cada dominio con sus dimensiones (cada dimensión debe tener `porcentaje` entre 0 y 100, sin campo `nivel` ni `color`).
   - Verificar manualmente que la suma total de dimensiones por dominio coincide con el conteo esperado (Guía II: 20 dimensiones en total repartidas en 8 dominios; Guía III: 25 dimensiones en 10 dominios).
5. Probar `EndEvaluation`: llamar el endpoint sobre un centro de prueba (no demo), confirmar que se crea un registro `EvaluationHistory` con `numero_evaluacion` igual al valor de `evaluation` ANTES del incremento, y que `workplace.evaluation` se incrementa como antes.
6. Probar `get_comparativo_evaluaciones` con un centro que tenga al menos 2 evaluaciones (una finalizada + la actual en curso): confirmar etiquetas correctas (`fecha_finalizacion` formateada para la finalizada, `"Actual (en curso)"` para la actual), y que `cambio_dominios` compara exactamente las últimas 2.
7. Probar con un centro que solo tenga 1 evaluación (nunca finalizada): `cambio_dominios` debe venir vacío, sin error.
8. Probar con un centro sin ningún empleado con encuesta respondida: debe devolver `{'status':'no_data'}` igual que antes (no debe romperse por los cálculos nuevos).
9. Prueba visual en navegador real (`workplace_results.html`): pestaña "Análisis por dominio" muestra pills de categoría clicables, clic en una categoría cambia el breadcrumb y los dominios mostrados, clic en un dominio expande/colapsa sus dimensiones, cada dimensión muestra solo el % (sin badge de color). Pestaña "Comparativo" muestra las barras con las evaluaciones finalizadas + la actual, y la tabla de cambio por dominio entre las 2 más recientes.
10. Confirmar que las pestañas "Categoría"/"Dominio"/"Dimensión" y sus heatmaps ECharts ya no aparecen en la página, y que no hay errores de JS en consola por referencias a elementos `#chart`...`#chart6` eliminados.
11. Confirmar que "Resumen" sigue funcionando exactamente igual que antes de este cambio (no debe haber regresión).

## Fuera de alcance

- No se toca `get_chart_data` (se deja de invocar desde el template, pero la función permanece intacta en el backend).
- No se agrega backfill de `fecha_finalizacion` para evaluaciones históricas ya finalizadas antes de este despliegue.
- No se agrega gráfica de tendencia histórica de dominios/categorías a lo largo de todas las evaluaciones (solo Riesgo General general + comparación de dominios entre las 2 evaluaciones más recientes). Documentado como pendiente v2.0 en `ESTADO.md`.
- No se agrega exportación (PDF/Excel) del comparativo ni del análisis jerárquico.
- No se modifica el cálculo ni la clasificación de Cfinal ni de Dominio (ya correctos desde fases anteriores) — solo se agregan Categoría (clasificado con umbrales oficiales) y Dimensión (neutral, sin clasificación).
