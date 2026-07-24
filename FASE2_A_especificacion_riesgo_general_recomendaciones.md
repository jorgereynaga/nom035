# Fase 2-A — Riesgo General, conteo de dominios y recomendaciones automáticas

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/fase2-a-riesgo-general`
- Entorno: usar el venv existente (Python 3.10)
- `surveys/views.py` y `surveys/models.py` usan **TABS** para indentación (confirmado con `cat -A`). `surveys/templates/*.html` no aplica esta regla (es HTML/JS). Verificar con `cat -A` antes de insertar líneas nuevas en `views.py`.
- Migraciones SIEMPRE manuales, nunca `makemigrations` real. Este lote **no requiere migración** (no toca modelos).
- `python -m py_compile surveys/views.py` antes de cualquier commit.
- No tocar `get_chart_data` (`surveys/views.py:1340-1842`) — es código ya corregido y sensible (bugs de Raven/Moss/Zavic resueltos ahí en sesiones previas). Todo lo nuevo va en una función separada, con sus propias copias de los diccionarios `domainsA`/`domainsB` que necesite, para no arriesgar una regresión en el reporte "Resultados completos" ya confirmado funcionando en producción.

## Contexto

Los socios pidieron un indicador de riesgo general del centro de trabajo, un conteo de cuántos dominios caen en cada nivel, y recomendaciones automáticas de intervención. La propuesta fue documentada, revisada externamente (incluye una revisión con ChatGPT) y aprobada por Jorge — ver `SOCIOS_feedback_correcciones.md` hallazgo 5.2/5.3 y el documento `Propuesta_Fase2_NOM035_v2.docx` compartido con los socios (no está en el repo, es solo contexto de la decisión).

**Principio no negociable**: esta pantalla muestra **riesgo psicosocial**, no cumplimiento normativo. El cumplimiento documental es un indicador *separado* (ver Fase 2-B, `FASE2_B_especificacion_cumplimiento_documental.md`, lote aparte). En ningún texto de este lote debe aparecer la palabra "Cumplimiento" — usar siempre "Riesgo".

La norma (NOM-035-STPS-2018, Guías II y III) define `Cdom` (calificación por dominio), `Ccat` (por categoría) y `Cfinal` (calificación total del cuestionario) **por cuestionario individual**, no agregado entre empleados. No existe una fórmula oficial para agregar varios empleados en un solo número por centro. La decisión de producto (confirmada con los socios) es: **promediar** la suma cruda de cada empleado (por dominio y total) y clasificar ese promedio contra los rangos oficiales — mostrando SIEMPRE junto al promedio la distribución real (cuántos empleados cayeron en cada nivel), para no esconder casos individuales graves.

## Cambios requeridos

### 1. surveys/views.py — nueva función `get_riesgo_general(request)`

Agregar inmediatamente después del cierre de `get_chart_data` (después de la línea 1842, donde termina esa función, antes de la siguiente definición). Mismo patrón de ownership y de parámetros GET que `get_chart_data` (línea 1340-1343):

```python
def get_riesgo_general(request):
	workplace_id=request.GET.get('workplace_id',None)
	if not Workplace.objects.filter(id=workplace_id, user=request.user).exists():
		return JsonResponse({'error':'not_found'}, status=403)
	evaluation=request.GET.get('evaluation',None)
	wk=Workplace.objects.filter(id=workplace_id).last()
	if evaluation is None:
		evaluation=wk.evaluation
	employees=Employee.objects.filter(workplace_id=workplace_id)
	guia3 = wk.survey_type()==3
```

A partir de aquí, seguir estos pasos dentro de la misma función:

**1.1 — Copiar (no importar ni reutilizar) los diccionarios de dominios**, exactamente como están en `get_chart_data` líneas 1400-1419 (`domainsB` y `domainsA`), tal cual, sin modificarlos. Son ~20 líneas cada uno, cópienlas literal.

**1.2 — Constantes de umbrales oficiales** (agregar como diccionarios al inicio de la función, o como constantes de módulo antes de la función — usar juicio, pero si van a nivel de módulo, nombrarlas con prefijo claro para no chocar con nada existente):

```python
UMBRALES_DOMINIO_GUIA_II = {
	"Condiciones en el ambiente de trabajo": [3,5,7,9],
	"Carga de trabajo": [12,16,20,24],
	"Falta de control sobre el trabajo": [5,8,11,14],
	"Jornada de trabajo": [1,2,4,6],
	"Interferencia en la relación trabajo-familia": [1,2,4,6],
	"Liderazgo": [3,5,8,11],
	"Relaciones en el trabajo": [5,8,11,14],
	"Violencia": [7,10,13,16],
}
UMBRALES_DOMINIO_GUIA_III = {
	"Condiciones en el ambiente de trabajo": [5,9,11,14],
	"Carga de trabajo": [15,21,27,37],
	"Falta de control sobre el trabajo": [11,16,21,25],
	"Jornada de trabajo": [1,2,4,6],
	"Interferencia en la relación trabajo-familia": [4,6,8,10],
	"Liderazgo": [9,12,16,20],
	"Relaciones en el trabajo": [10,13,17,21],
	"Violencia": [7,10,13,16],
	"Reconocimiento del desempeño": [6,10,14,18],
	"Insuficiente sentido de pertenencia e inestabilidad": [4,6,8,10],
}
UMBRALES_CFINAL_GUIA_II = [20,45,70,90]
UMBRALES_CFINAL_GUIA_III = [50,75,99,140]
NIVEL_NOMBRE = {0:"Nulo",1:"Bajo",2:"Medio",3:"Alto",4:"Muy alto"}

def clasificar_nivel(valor, umbrales):
	if valor < umbrales[0]: return 0
	if valor < umbrales[1]: return 1
	if valor < umbrales[2]: return 2
	if valor < umbrales[3]: return 3
	return 4
```

Verificado línea por línea contra la Tabla 3 (Guía II) y Tabla 6 (Guía III) del DOF, 23/oct/2018. Estos umbrales ya coinciden con los que usa `get_chart_data` en sus bloques `if/elif` hardcodeados (ej. línea 1457: `color=0 if _sum<5 else (1 if _sum<9 else (2 if _sum<11 else (3 if _sum<14 else 4)))` para "Condiciones en el ambiente de trabajo" en Guía III — coincide con `[5,9,11,14]` arriba). No hace falta ni conviene tocar `get_chart_data` para que use esta función común; es una simple duplicación intencional de umbrales, ya justificada arriba.

**1.3 — Por cada empleado, calcular su Cfinal y sus sumas por dominio**, con la misma lógica de elegibilidad que ya usa `get_chart_data` (líneas 1449 y 1640: `surveyB` si `survey_type()==3`, si no `surveyA`):

```python
	domains_dict = domainsB if guia3 else domainsA
	umbrales_dominio = UMBRALES_DOMINIO_GUIA_III if guia3 else UMBRALES_DOMINIO_GUIA_II
	umbrales_cfinal = UMBRALES_CFINAL_GUIA_III if guia3 else UMBRALES_CFINAL_GUIA_II
	survey_model = RiskSurveyB if guia3 else RiskSurveyA

	cfinal_por_empleado = []
	sumas_por_dominio = {d: [] for d in domains_dict}

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
		cfinal_por_empleado.append(emp_cfinal)

	if not cfinal_por_empleado:
		return JsonResponse({'status': 'no_data'})
```

**1.4 — Riesgo General (promedio + distribución)**:

```python
	promedio_cfinal = sum(cfinal_por_empleado) / len(cfinal_por_empleado)
	nivel_general = clasificar_nivel(promedio_cfinal, umbrales_cfinal)
	distribucion = {0:0, 1:0, 2:0, 3:0, 4:0}
	for c in cfinal_por_empleado:
		distribucion[clasificar_nivel(c, umbrales_cfinal)] += 1
```

**1.5 — Conteo de dominios por nivel** (promedio por dominio, clasificado contra el umbral de ESE dominio):

```python
	dominios_detalle = []
	conteo_dominios_nivel = {0:0, 1:0, 2:0, 3:0, 4:0}
	for domain in domains_dict:
		valores = sumas_por_dominio[domain]
		promedio_dom = sum(valores) / len(valores) if valores else 0
		nivel_dom = clasificar_nivel(promedio_dom, umbrales_dominio[domain])
		conteo_dominios_nivel[nivel_dom] += 1
		dominios_detalle.append({'nombre': domain, 'nivel': nivel_dom, 'nivel_nombre': NIVEL_NOMBRE[nivel_dom]})
```

**1.6 — Capa 1: texto oficial por nivel de Riesgo General** (Tabla 4 de Guía II / Tabla 7 de Guía III — idénticas en contenido, un solo diccionario sirve para ambas guías):

```python
	RECOMENDACION_NIVEL_GENERAL = {
		4: "Se requiere realizar el análisis de cada categoría y dominio para establecer las acciones de intervención apropiadas, mediante un Programa de intervención que deberá incluir evaluaciones específicas, y contemplar campañas de sensibilización, revisar la política de prevención de riesgos psicosociales y programas para la prevención de los factores de riesgo psicosocial, la promoción de un entorno organizacional favorable y la prevención de la violencia laboral, así como reforzar su aplicación y difusión.",
		3: "Se requiere realizar un análisis de cada categoría y dominio, de manera que se puedan determinar las acciones de intervención apropiadas a través de un Programa de intervención, que podrá incluir una evaluación específica y deberá incluir una campaña de sensibilización, revisar la política de prevención de riesgos psicosociales y programas para la prevención de los factores de riesgo psicosocial, la promoción de un entorno organizacional favorable y la prevención de la violencia laboral, así como reforzar su aplicación y difusión.",
		2: "Se requiere revisar la política de prevención de riesgos psicosociales y programas para la prevención de los factores de riesgo psicosocial, la promoción de un entorno organizacional favorable y la prevención de la violencia laboral, así como reforzar su aplicación y difusión, mediante un Programa de intervención.",
		1: "Es necesario una mayor difusión de la política de prevención de riesgos psicosociales y programas para: la prevención de los factores de riesgo psicosocial, la promoción de un entorno organizacional favorable y la prevención de la violencia laboral.",
		0: "El riesgo resulta despreciable por lo que no se requiere medidas adicionales.",
	}
```
(Esta constante puede ir a nivel de módulo junto a las otras, no repetirla dentro de la función si se define arriba.)

**1.7 — Capa 2: catálogo de acciones del numeral 8.2, mapeado por dominio.** Solo se incluye en la respuesta para dominios con `nivel_dom >= 2` (Medio/Alto/Muy alto). Constante de módulo:

```python
RECOMENDACION_DOMINIO_82 = {
	"Condiciones en el ambiente de trabajo": "El numeral 8.2 de la norma no contempla un catálogo específico para este dominio (regula prevención psicosocial y violencia, no condiciones físicas del lugar de trabajo). Se recomienda revisar las condiciones de seguridad e higiene del centro conforme a la normatividad aplicable (ej. NOM-030-STPS).",
	"Carga de trabajo": "Numeral 8.2 b): revisión y supervisión de que la distribución de la carga de trabajo se realice de forma equitativa, considerando el número de trabajadores, actividades a desarrollar, alcance de la actividad y su capacitación; planificar el trabajo con las pausas o periodos necesarios de descanso y rotación de tareas para evitar ritmos acelerados; e instructivos o procedimientos que definan claramente las tareas y responsabilidades.",
	"Falta de control sobre el trabajo": "Numeral 8.2 c): involucrar a los trabajadores en la toma de decisiones sobre la organización de su trabajo y en la mejora de las condiciones de trabajo y la productividad; acordar y mejorar el margen de libertad y control sobre su trabajo, impulsando el desarrollo de nuevas competencias; y reuniones para abordar áreas de oportunidad y determinar soluciones.",
	"Jornada de trabajo": "Numeral 8.2 e), numeral 2): establecer lineamientos con medidas y límites que eviten las jornadas de trabajo superiores a las previstas en la Ley Federal del Trabajo.",
	"Interferencia en la relación trabajo-familia": "Numeral 8.2 e): involucrar a los trabajadores en la definición de los horarios de trabajo cuando las condiciones lo permitan; apoyos para atender emergencias familiares comprobables; y promoción de actividades de integración familiar previo acuerdo con los trabajadores.",
	"Liderazgo": "Numeral 8.2 a): acciones para el manejo de conflictos, distribución de tiempos y determinación de prioridades en el trabajo; lineamientos contra la discriminación que fomenten equidad y respeto; mecanismos de comunicación entre supervisores/gerentes y trabajadores; instrucciones claras para atender problemas que limiten el trabajo; y capacitación/sensibilización de directivos, gerentes y supervisores.",
	"Relaciones en el trabajo": "Numerales 8.2 a) y d): además de lo señalado para Liderazgo, fomentar el apoyo social — relaciones entre trabajadores, supervisores, gerentes y patrones; reuniones periódicas (semestrales o anuales) de seguimiento; promoción de la ayuda mutua e intercambio de experiencias; y fomento de actividades culturales y deportivas.",
	"Violencia": "Numeral 8.2 g): difundir información para sensibilizar sobre violencia laboral a trabajadores, directivos, gerentes y supervisores; establecer procedimientos de actuación y seguimiento capacitando al responsable de su implementación; e informar sobre cómo denunciar actos de violencia laboral.",
	"Reconocimiento del desempeño": "Numeral 8.2 f): reconocer el desempeño sobresaliente de los trabajadores, difundir sus logros y, en su caso, expresarles sus posibilidades de desarrollo.",
	"Insuficiente sentido de pertenencia e inestabilidad": "Numerales 8.2 h) y f): promover comunicación directa y frecuente sobre problemas que afecten el trabajo, difundir cambios en la organización, dar oportunidad a los trabajadores de expresar opiniones sobre mejoras, y reforzar el reconocimiento del desempeño (ver dominio Reconocimiento).",
}
```

**1.8 — Armar y devolver la respuesta**:

```python
	for d in dominios_detalle:
		if d['nivel'] >= 2:
			d['recomendacion'] = RECOMENDACION_DOMINIO_82.get(d['nombre'], '')

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
	})
```

### 2. nom035/urls.py — registrar la URL

Agregar cerca de la línea 86 (`path('get_chart_data/', get_chart_data, name='get_chart_data'),`):
```python
path('get_riesgo_general/', get_riesgo_general, name='get_riesgo_general'),
```
Confirmar que `get_riesgo_general` queda accesible según el patrón de import usado en `urls.py` para `views.py` (es wildcard `from surveys.views import *`, así que no requiere agregarse a ninguna lista explícita — a diferencia de `psico_views.py`, que sí lo requiere).

### 3. surveys/templates/workplace_results.html — nueva pestaña "Resumen"

**3.1 — CSS** (junto al bloque existente, líneas 190-195): agregar `tab-resumen` a las 3 reglas de selector múltiple:
```css
#tab-resumen:checked ~ .chart-tabs-body #pair-resumen,
#tab-cat:checked ~ .chart-tabs-body #pair-cat,
#tab-dom:checked ~ .chart-tabs-body #pair-dom,
#tab-dim:checked ~ .chart-tabs-body #pair-dim { display: flex; }
#tab-resumen:checked ~ .chart-tabs-nav label[for="tab-resumen"],
#tab-cat:checked ~ .chart-tabs-nav label[for="tab-cat"],
#tab-dom:checked ~ .chart-tabs-nav label[for="tab-dom"],
#tab-dim:checked ~ .chart-tabs-nav label[for="tab-dim"] { background: var(--primary); color: #fff; }
```
Agregar también estilos nuevos para las tarjetas del resumen (`.resumen-card`, `.resumen-riesgo-badge` con los 5 colores oficiales ya usados en `.risk-legend` línea 69 — reutilizar esa paleta, no inventar colores nuevos) y para `.dominio-recomendacion-item`.

**3.2 — HTML**: en el bloque de radios (líneas 358-360), agregar `<input type="radio" name="chart-tab" id="tab-resumen" checked>` **primero**, y quitar `checked` de `id="tab-cat"` (línea 358) para que "Resumen" sea la pestaña que abre por default. En `chart-tabs-nav` (después de línea 362), agregar el `<label for="tab-resumen">` primero, con un ícono simple (reutilizar el patrón SVG de los otros labels). En `chart-tabs-body` (después de línea 377), agregar `<div class="chart-tab-pair" id="pair-resumen">` primero, con placeholders vacíos que el JS llenará (ver 3.3): un contenedor para el badge de Riesgo General + distribución, uno para el conteo de dominios, uno para el texto de Capa 1, y una lista para Capa 2.

**3.3 — JS**: agregar una función `loadRiesgoGeneral()` con el mismo patrón `$.ajax` que `loadChart()` (línea 502-505), apuntando a `{% url 'get_riesgo_general' %}` con los mismos parámetros `workplace_id`/`evaluation` (sin `dept_id`, el Riesgo General es del centro completo, no por departamento). Llamarla junto con `loadChart()` al cargar la página. En el `success`, si `data.status == 'no_data'`, mostrar el mismo mensaje de "No existen suficientes datos" ya usado (línea 509) dentro de `#pair-resumen`; si `status == 'ok'`, renderizar:
- Badge grande con `data.riesgo_general.nivel_nombre` y color según nivel (mapear 0-4 a los mismos colores de `col` en el backend: `#9be5f7,#6bf56e,#ffff00,#ffc000,#ff7070`), más `data.riesgo_general.promedio` como dato secundario, más una leyenda de texto fijo: *"Este indicador resume el nivel de riesgo psicosocial detectado en las respuestas del cuestionario. El cumplimiento de la NOM-035 depende de las acciones documentales del Capítulo 5 (política, difusión, programa de intervención), no de este resultado."*
- Debajo, la distribución (`data.riesgo_general.distribucion`) como lista simple "X de Y empleados en [nivel]" por cada nivel con conteo > 0.
- `data.recomendacion_general` como párrafo, con encabezado tipo "Qué exige la norma en este nivel".
- El conteo de dominios (`data.dominios.conteo_por_nivel`) como lista "X dominios en [nivel]" por cada nivel con conteo > 0.
- La lista `data.dominios.detalle` filtrada a los que tengan `recomendacion` (o sea, `nivel >= 2`), cada uno con su nombre, nivel y el texto de `recomendacion`.

No es necesario usar ECharts para esta pestaña — es contenido de texto/badges, no gráficas, a diferencia de las otras 3 pestañas.

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/views.py` sin errores.
2. Confirmar visualmente en local (servidor de desarrollo) que la pestaña "Resumen" abre por default al entrar a `/workplace_result/<id>/`, con datos reales de un centro de prueba que ya tenga empleados con encuestas completas (Guía II y, si hay datos, un centro con Guía III también, para probar ambas ramas).
3. Confirmar que las otras 3 pestañas (Categoría/Dominio/Dimensión) siguen funcionando exactamente igual que antes (sin regresión) — clic en cada una, las gráficas ECharts se muestran y redimensionan correctamente.
4. Probar un centro sin datos suficientes (`status: no_data`) y confirmar que el mensaje se muestra sin errores de JS en consola.
5. Verificar manualmente 2-3 casos del cálculo con lápiz y papel contra un empleado de prueba conocido, comparando el Cfinal calculado por `get_riesgo_general` contra la suma manual de sus respuestas, para descartar un error de signo/índice en el bucle.
6. Confirmar que en ningún texto visible de la nueva pestaña aparece la palabra "Cumplimiento".

## Fuera de alcance de este lote (no tocar)
- El checklist de evidencias / cumplimiento documental — es el lote `FASE2_B_especificacion_cumplimiento_documental.md`, aparte.
- Enlaces a Evidencias/Clima Laboral desde `workplace_detail.html` — pendiente del backlog de Fase 2, no incluido aquí, se puede pedir como lote separado si Jorge lo prioriza.
- Cualquier cambio a `get_chart_data`, `EmployeeList`, u otras vistas de resultados existentes.
- Filtro por departamento (`dept_id`) en el Riesgo General — queda fuera, es siempre del centro completo.
