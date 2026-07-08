# ESTADO NormaIA — Actualizado 5 Jul 2026 (sesion 2)

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: prueba/TestIhes2026! | jorge.reynaga.j@gmail.com (usuario con datos demo)
- URLs: nom035-production.up.railway.app / 035.ihes.mx

## Completado

### PORTAFOLIO DE EVIDENCIAS — FASE A COMPLETA (3/3 documentos) ✅
- Modelo PortafolioEvidencias en surveys/models.py (migration 0034) ✅
- Creditos gratis eliminados: nom035_demo y psico_demo default=1→0 (migration 0035) ✅
- **Documento 1 — Politica de Prevencion**: PoliticaPrevencionForm, GenerarPoliticaView, templates pdf/politica_prevencion.html + politica_prevencion_form.html, URL generar_politica/<workplace_id>/ ✅
- **Documento 2 — Informe de Resultados** (numeral 7.7 norma): GenerarInformeResultadosView, template pdf/informe_resultados.html, URL generar_informe_resultados/<workplace_id>/. Reutiliza get_chart_data() existente via RequestFactory interno ✅
- **Documento 3 — Cuestionarios Aplicados**: CuestionariosAplicadosView, template pdf/cuestionarios_aplicados.html, URL cuestionarios_aplicados/<workplace_id>/ ✅
- Las 3 tarjetas visibles en evidence.html (sidebar "Portafolio de evidencias") ✅
- PortafolioEvidencias demo se crea automaticamente en cargar_datos_demo.py ✅
- Empty-state de evidence.html corregido ✅

### MEJORAS DE UX EN PORTAFOLIO DE EVIDENCIAS (sesion 2, 5 Jul) ✅
- target="_blank" agregado a las 4 tarjetas/links de evidence.html (3 nuevas + 1 de ResultFiles existente) para que nunca abandonen la plataforma ✅
- Boton de imprimir/guardar PDF unificado con estilo consistente (.print-bar/.btn-print, igual que /reporte_html/) en los 3 documentos del Portafolio ✅
- **BUG CRITICO RESUELTO**: get_chart_data() (funcion usada por dashboard Y por Informe de Resultados) lanzaba UnboundLocalError: cannot access local variable 'dimensions' cuando ningun empleado habia completado su cuestionario para la evaluacion actual (dimensions solo se asignaba dentro del loop for emp in employees, nunca antes). Fix: se agrego dimensions=[] a las inicializaciones al inicio de la funcion (junto a cat=[], domains=[], data=[], etc.), linea ~1319. Este bug es PREEXISTENTE, no fue introducido por Fase A, probablemente afectaba tambien al dashboard original en el mismo caso (workplace sin respuestas aun) ✅
- Se detecto y corrigio ademas: el {% if not print_mode %} en los 3 templates PDF ocultaba el boton de imprimir SIEMPRE, porque las 3 vistas pasan print_mode=True fijo en el ctx (no hay modo "sin boton" real para estos documentos). Se quito la condicional, boton siempre visible ✅
- PROBADO EN PRODUCCION 5 Jul: los 3 documentos abren en nueva pestana, muestran boton de imprimir, Informe de Resultados ya no se cuelga (confirmado por Jorge) ✅

## Estado actual (dashboard funcional)
- NOM-035: 100% cuestionarios, Completado, dimensiones 4x2 visibles ✅
- Clima Laboral: 8 respuestas, grid 4x2 con colores por nivel ✅
- Psicometria: 2 candidatos demo con evaluacion asignada ✅
- Borrar datos demo: FUNCIONA ✅
- Bloqueos sin plan: FUNCIONA ✅
- Reporte unificado: FUNCIONA ✅
- Dashboard carga correctamente ✅
- Portafolio de Evidencias — Fase A completa + UX pulida: FUNCIONA COMPLETO, probado en produccion ✅

## Pendientes
1. Portafolio de evidencias — considerar construir PortafolioStatusView como checklist mas robusto dentro de evidence.html en vez de seguir agregando tarjetas sueltas una por una (discutido, no decidido — por ahora funciona bien con 3 tarjetas individuales)
2. Portafolio de evidencias — Fase C (carga manual): espacios para canalizaciones Guia I, examenes medicos, medidas de control, evidencia de difusion. Estos NO se generan automaticamente, la empresa los carga
3. Pruebas finales: navegacion entre evaluaciones multiples
4. Selector de "Centro de trabajo" en evidence.html se ve poco estilizado — deuda de diseño PREEXISTENTE confirmada por Jorge (sistema viejo, se esta modernizando), NO es bug introducido en estas sesiones. Mejora futura, no urgente
5. Reporte de lentitud de plataforma del 4 Jul — el bug de get_chart_data (dimensions sin inicializar) podria estar RELACIONADO a este reporte de lentitud, ya que un error no capturado en esa funcion podria haber causado comportamiento raro/lento en el dashboard en ciertos workplaces antes de este fix. Vale la pena verificar si la lentitud reportada ya no ocurre despues de este fix
6. Revisar si get_chart_data tiene otros bugs similares de variables no inicializadas en todas las ramas (no se audito exhaustivamente, solo se corrigio el caso que causo el error reportado)

## Notas tecnicas
- views.py: mezcla tabs/espacios es el principal riesgo — siempre py_compile antes de push
- WeasyPrint: permanentemente bloqueado en Railway. Patron real que SI funciona: render(request, 'pdf/plantilla.html', ctx) con print_mode=True, usuario exporta a PDF via Ctrl+P del navegador. IMPORTANTE: en nuestros 3 templates print_mode ya NO controla visibilidad del boton de imprimir (ver arriba) — print_mode sigue pasandose en el ctx pero no tiene efecto en el template actualmente, es vestigial. Si se necesita un modo "sin boton" real en el futuro, hay que revisar esa logica
- Migraciones: siempre manuales, ultima es 0035 (alter defaults nom035_demo/psico_demo)
- get_chart_data(request) en views.py (~linea 1218): funcion grande (~500 lineas) que calcula niveles de riesgo por dominio/categoria/dimension para TODOS los empleados de un workplace. Variables cat=[], domains=[], dimensions=[] se inicializan en linea ~1316-1319 ANTES del if not employees y del loop principal — esto es CRITICO, cualquier variable nueva usada en el return final debe inicializarse ahi tambien, o se repite el mismo tipo de UnboundLocalError. dimensions/domains/cat solo se reasignan (con el valor real) dentro del loop for emp in employees, en las ramas if emp.surveyB... (Guia III) y elif emp.surveyA... (Guia II) — si NINGUN empleado cae en ninguna rama (ninguno respondio aun), se quedan como listas vacias en vez de fallar
- Para reusar get_chart_data() sin request HTTP real: usar django.test.RequestFactory con factory.get() pasando workplace_id/evaluation como STRINGS explicitos (str(workplace_id), str(workplace.evaluation)) en el querystring — no pasar enteros directos, aunque no era la causa raiz del bug encontrado hoy, es buena practica ya que request.GET siempre devuelve strings en un request real
- Tecnica de diagnostico usada hoy: envolver temporalmente una vista en try/except que retorne HttpResponse('<pre>'+traceback.format_exc()+'</pre>', status=500) para ver el traceback completo en el navegador cuando no se tiene acceso facil a logs de Railway en tiempo real. IMPORTANTE: quitar este diagnostico despues de usarlo, nunca dejarlo en produccion (expone informacion interna)
- nom035_demo y psico_demo: ahora default=0 (antes default=1)
- Logica bloqueo: workplace.es_demo=True → 403 en registro de encuestas
- Editor: Sublime Text — siempre editar Python con python -c por indices de linea (readlines()+insert()/lines[n]=...). Al insertar MULTIPLES lineas por indice en una sola pasada, insertar de indice mas alto a mas bajo para no desfasar posiciones. Para bloques de texto en HTML/templates usar content.replace() con marcador CORTO (2-4 lineas) y verificacion previa de content.count(marcador)==1
- surveys/forms.py usa espacios (4), surveys/models.py y surveys/views.py usan tabs, surveys/management/commands/cargar_datos_demo.py usa espacios (4)
- index.html usa block dashboard (NO block content)
- Sistema de diseño NormaIA real: .form-group, .form-label, .form-control, .section-card, .section-card-header, .section-card-title, .section-card-body, .btn/.btn-primary/.btn-outline-primary, variables CSS var(--bg-base), var(--border), var(--text-primary), var(--text-secondary), var(--radius-md/lg), var(--shadow-sm)
- Patron de boton imprimir/descargar consistente en toda la plataforma: .print-bar (contenedor) + .btn-print (boton azul #2563eb con hover #1d4ed8) + emoji 🖨️, visible SIEMPRE (sin condicional print_mode) en documentos standalone tipo pdf/*.html
- Workplace vive en surveys/models.py:48 — campos reales: name, address, main_activity, employee_num, evaluation, survey_type() (metodo)
- Userapp tiene campos "Centros pagados A/B/C" (workplaces_available, workplaces_availableB, workplaces_availableC, default=0) editables desde admin
- evidence.html usa Vue.js (v-model="workplace", v-for, AJAX a get_results/get_workplaces)
- Portafolio Evidencias: NO usar boton unico "generar todo" — dashboard/checklist con generacion individual por documento
- imports en views.py son wildcard: from .models import * / from .forms import *. cargar_datos_demo.py usa import explicito

## ACTUALIZACION 5 Jul 2026 (sesion 3) — Checklist de Portafolio de Evidencias

### PortafolioStatusView implementado (checklist real) ✅
- Decision de diseño: CONVIVE con las tarjetas existentes (checklist resumen arriba, tarjetas detalladas abajo) — no las reemplaza
- Decision de alcance: checklist muestra SOLO los 3 documentos existentes de Fase A. Items de Fase C (canalizaciones, examenes medicos, etc.) NO se muestran hasta que esten construidos de verdad
- Endpoint get_portafolio_status(request) en views.py: calcula estado real de los 3 documentos
  - Politica: completo si portafolio.responsable_nombre existe, detalle muestra version_politica
  - Informe de Resultados: completo si get_chart_data() devuelve status=ok (reutiliza RequestFactory, mismo patron que GenerarInformeResultadosView)
  - Cuestionarios Aplicados: completo si respondieron>0, detalle muestra "X de Y (Z%)"
- URL get_portafolio_status/ agregada
- evidence.html (Vue): agregado portafolio_status:[] a data(), metodo get_portafolio_status() (mismo patron AJAX que get_results()), metodo combinado on_workplace_change() que dispara ambos AJAX al cambiar selector (reemplazo el @change="get_results" original)
- HTML checklist: iconos ✓ verde (completo) / ⚠ ambar (pendiente), nombre + detalle + link "Ver" (target=_blank), insertado justo antes de las tarjetas existentes
- PROBADO EN PRODUCCION 5 Jul: checklist funciona correctamente, refleja estado real (ej. Cuestionarios muestra "0 de 6 (0%)" cuando nadie ha respondido), confirmado por Jorge con captura de pantalla ✅

### Nota sobre reporte de lentitud del 4 Jul
- Confirmado por Jorge: la lentitud reportada el 4 Jul ya NO ocurre. Probablemente fue temporal/no relacionado al bug de get_chart_data. Se cierra como no reproducible, no se seguira investigando salvo que reaparezca

## Notas tecnicas adicionales (sesion 3)
- Truco de terminal: cuando un bloque python -c con caracteres especiales (!, comillas anidadas) falla en Git Bash con errores tipo "event not found" (por expansion de historial de bash), usar heredoc en su lugar: python3 << 'PYEOF' ... PYEOF — las comillas simples alrededor de PYEOF evitan que bash interprete cualquier caracter especial dentro del bloque
- Patron para checklists/dashboards de estado: crear un endpoint AJAX que reutiliza la logica de calculo ya existente en las vistas de generacion (no duplicar), devolver JSON con lista de items {nombre, estado, detalle, url}, y consumir desde Vue con un metodo que se dispara junto a los metodos AJAX existentes en el mismo evento (@change combinado)
- Patron de marcador para content.replace() en HTML con Django templates: verificar SIEMPRE con sed + cat -A antes de asumir el contenido exacto — lineas en blanco entre bloques HTML son faciles de pasar por alto y causan "0 ocurrencias" con marcadores que se ven identicos a simple vista

## ACTUALIZACION 5 Jul 2026 (sesion 4) — Fusion de checklist + bugs de evaluacion/demo resueltos

### Fusion del checklist con las tarjetas ✅
- Se elimino la duplicacion visual: checklist con estado (✓/⚠) + tarjetas separadas → ahora es UNA sola lista generada dinamicamente desde portafolio_status
- v-for="item in portafolio_status" reemplaza las 3 tarjetas hardcodeadas de evidence.html
- Cada fila muestra: icono ✓ verde (completo) o ⚠ ambar (pendiente) + nombre + detalle de estado + boton "Abrir" unico
- PROBADO Y CONFIRMADO por Jorge: vista limpia, sin duplicacion

### BUG CRITICO RESUELTO: EndEvaluation no bloqueaba workplaces demo ✅
- Investigacion completa de flujo de evaluaciones (planes NOM-035: 50/100/ilimitadas evaluaciones, vigencia 1 año, 1 evaluacion = 1 credito):
  - EndEvaluation (views.py ~2485, endpoint /api/end_evaluation/) incrementa workplace.evaluation+1 y pone paid=False — es una accion MANUAL disparada por boton "Finalizar/Avanzar evaluacion" en workplace_detail.html, NO automatica
  - El workplace demo (id=13 en pruebas) fue avanzado a evaluacion=2 en algun momento (probablemente prueba anterior), pero las respuestas demo (RiskSurveyA) solo existen con evaluation=1 — causaba que Informe de Resultados y Cuestionarios Aplicados marcaran "pendiente" en el checklist aunque los datos demo SI existian y estaban completos
  - Esto confirmo que get_portafolio_status/GenerarInformeResultadosView/CuestionariosAplicadosView estaban funcionando CORRECTAMENTE (reflejando el estado real de evaluation actual), el problema era el ESTADO DE DATOS del workplace demo, no la logica
- FIX aplicado: EndEvaluation ahora verifica `if workplace.es_demo: return Response({'status':'error', ...})` ANTES de incrementar evaluation — bloquea que se pueda avanzar evaluacion en centros de trabajo demo
- Workplace demo roto (id=13) fue borrado por Jorge usando el boton "Borrar datos de prueba" existente (borra el Workplace completo, no solo resetea evaluation — confirmado revisando borrar_datos_demo.py management command)

### BUG RESUELTO: boton "Borrar datos de prueba" no desaparecia al no haber datos demo ✅
- Causa: el boton en index.html dependia de `{% if nom035_demo %}` que lee userapp.nom035_demo (campo de CREDITOS, cambiado a default=0 ayer pero usuarios existentes conservan su valor viejo=1) — esto es una variable de creditos, NO de existencia real de datos demo
- FIX: se agrego ctx['tiene_datos_demo'] = Workplace.objects.filter(user=request.user, es_demo=True).exists() en views.py (dashboard principal, linea ~225), calculado a partir de existencia REAL de workplace demo, no de creditos
- index.html actualizado: {% if nom035_demo %} → {% if tiene_datos_demo %} en el boton "Borrar datos de prueba"
- ctx['nom035_demo'] (el original) se dejo intacto porque se sigue usando para el calculo de creditos disponibles (nom035_disponibles) en otro punto del dashboard — no se toco esa logica
- PROBADO: tras borrar el workplace demo roto, pendiente confirmar en produccion que el boton ya no aparece (Jorge iba a verificar)

### Pendiente para verificar en la siguiente sesion
1. Confirmar que boton "Borrar datos de prueba" ya no aparece tras el fix + borrado del workplace roto
2. Considerar tambien ocultar/deshabilitar el boton "Finalizar/Avanzar evaluacion" en el FRONTEND (workplace_detail.html) cuando workplace.es_demo=True — hoy solo se bloqueo en backend (el usuario veria el boton pero recibiria error al hacer click). Bloqueo de backend es lo critico y ya esta resuelto; ocultar en frontend es mejora de UX, no urgente
3. Crear un usuario de prueba NUEVO para validar de punta a punta: registro → datos demo cargados en evaluacion 1 → checklist del Portafolio muestra los 3 documentos completos desde el primer momento → intentar avanzar evaluacion en ese demo debe fallar con el mensaje de error nuevo

## Notas tecnicas adicionales (sesion 4)
- IMPORTANTE: cuando bash entra en estado raro (prompt cambia a '>' esperando cierre de comilla/parentesis), usar Ctrl+C o escribir tres backticks para forzar abort y recuperar el prompt limpio antes de seguir
- Patron para diagnosticar sin logs de Railway en tiempo real: agregar campos de debug temporales a un JsonResponse existente (mas simple que try/except con traceback completo si el problema es de datos, no de excepcion) — ej. agregar 'debug': [...], 'workplace_evaluation': x, 'survey_type': y al return, ver el resultado accediendo al endpoint GET directo en el navegador, y LIMPIAR el debug inmediatamente despues de diagnosticar (nunca dejarlo en produccion)
- borrar_datos_demo (management command) hace DELETE completo del Workplace demo y relacionados — no existe un comando para "resetear evaluacion sin borrar todo". Si en el futuro se necesita resetear sin perder el workplace, habria que crear un comando nuevo
- Distincion importante confirmada: userapp.nom035_demo/psico_demo = creditos gratis (cuantas evaluaciones puede aplicar sin plan). Workplace.es_demo=True = si el CENTRO DE TRABAJO es de datos ficticios/demo. Son conceptos relacionados pero independientes — no asumir que uno implica el otro al escribir logica de UI condicional
- EndEvaluation (POST via boton en workplace_detail.html, no automatico): incrementa evaluation+1 y pone paid=False, lo que fuerza al usuario a re-confirmar plan/creditos para la siguiente evaluacion. Logico dado el modelo de negocio (planes con vigencia 1 año, credito=evaluacion). Ahora bloqueado para es_demo=True

## ACTUALIZACION 5 Jul 2026 (sesion 5) — Demo nace finalizado + fix de mensaje falso en EndEvaluation

### BUG RESUELTO: EndEvaluation bloqueado en demo creaba trampa de UX ✅
- Tras bloquear EndEvaluation para es_demo=True (sesion 4), el frontend (workplace_detail.html) seguia mostrando toastr.success falso porque el JS no revisaba data.status antes de asumir exito — la Response de Django devuelve status HTTP 200 incluso cuando el backend rechaza logicamente la operacion (status:'error' en el JSON, no un status code HTTP de error)
- FIX: agregado if (data.status === 'error') en el callback success del AJAX de end_evaluation — ahora muestra toastr.error con el mensaje real del backend y NO recarga la pagina si fallo
- Esto revelo una trampa de UX real: el demo pedia "finalizar evaluacion" para ver resultados, pero bloqueabamos finalizar por ser demo — el prospecto se quedaba sin poder ver resultados nunca

### FIX DE PRODUCTO: workplace demo nace ya finalizado ✅
- cargar_datos_demo.py: Workplace demo ahora se crea con paid=False y evaluation=2 explicito (antes: paid=True, evaluation=1 por default)
- Esto usa la misma convencion que ya tiene el sistema para evaluaciones reales finalizadas (paid=False + evaluation>1 → boton "Ver resultados" apunta a evaluation-1)
- Efecto: el prospecto ve resultados INMEDIATAMENTE al entrar al workplace demo, sin necesitar finalizar nada (que ademas esta bloqueado para demos)
- PROBADO Y CONFIRMADO por Jorge con usuario nuevo: funciona correctamente

### Contexto tecnico importante descubierto en esta sesion sobre el flujo de evaluaciones (aportado por Jorge, de una sesion anterior de arreglo de este mismo flujo)
Tabla de estados del sistema de evaluaciones NOM-035:
| Estado | paid | evaluation | Ver resultados | DataTable empleados |
|---|---|---|---|---|
| Activa (1ra) | True | 1 | Bloqueado ("debes finalizar") | evaluation=1 |
| Finalizada (1ra) | False | 2 | /workplace_result/{id}/1/ | evaluation=1 |
| Activa (2da) | True | 2 | Bloqueado | evaluation=2 |
| Finalizada (2da) | False | 3 | /workplace_result/{id}/2/ | evaluation=2 |

Puntos donde esta logica ya estaba implementada ANTES de esta sesion (confirmado, no se toco):
- workplace_detail.html: botones condicionales {% if not paid and evaluation > 1 %} / {% elif paid %} / {% else %}, DataTable ajax con {% if not paid %}{{evaluation|add:"-1"}}{% else %}{{evaluation}}{% endif %}
- WorkplaceResultView: redirect por wk.paid comentado (permite ver resultados de evaluaciones ya finalizadas)
- Index (dashboard): eval_to_check = item.evaluation if item.paid else max(1, item.evaluation - 1)
- AJAX end_evaluation ya usaba {{workplace_id}} correcto (no {{workplaceid}}) y url con slash inicial correcto, con setTimeout(location.reload(), 1500)

Estos fixes fueron aplicados en una sesion PREVIA no documentada en este ESTADO.md (Jorge trajo el contexto completo por escrito). Quedan confirmados como YA APLICADOS Y FUNCIONANDO, no se repitieron.

## Notas tecnicas adicionales (sesion 5)
- IMPORTANTE: Django Response/JsonResponse con status='error' en el body JSON puede seguir devolviendo HTTP 200 — cualquier callback de AJAX success() en el frontend DEBE revisar data.status explicitamente, no asumir que success() = operacion exitosa. Este patron aplica a CUALQUIER endpoint que devuelva {'status':'error', ...} sin usar status=4xx/5xx en el Response
- Patron de "evaluacion finalizada" para datos demo: si se necesita que un demo muestre resultados sin friccion desde el primer momento, crear el Workplace con paid=False y evaluation=N+1 donde N es la evaluacion real donde viven los datos de respuesta (evaluation=2 con datos en evaluation=1, replicando el patron real de "evaluacion recien finalizada")

## ACTUALIZACION 5 Jul 2026 (sesion 6) — Fix critico: eval_to_check faltaba en Portafolio de Evidencias

### BUG CRITICO RESUELTO: Portafolio de Evidencias no usaba eval_to_check ✅
- Tras el fix de sesion 5 (workplace demo nace con paid=False, evaluation=2), el dashboard normal (Index) y workplace_detail.html YA mostraban resultados correctamente porque ya usaban la logica eval_to_check = workplace.evaluation if workplace.paid else max(1, workplace.evaluation - 1)
- Pero las 3 vistas del Portafolio de Evidencias (construidas en sesiones anteriores, ANTES de que el demo naciera con paid=False) seguian usando workplace.evaluation directo — nunca se les aplico esta logica porque cuando se construyeron, el demo siempre nacia sincronizado (paid=True, evaluation=1, sin desfase)
- Esto causaba que Informe de Resultados y Cuestionarios Aplicados mostraran "pendiente"/"0 de 6" en TODO usuario nuevo creado despues del fix de sesion 5, aunque los datos demo estuvieran completos — confirmado con workplace_id=15 y con un usuario adicional creado despues
- FIX aplicado en las 3 vistas (surveys/views.py):
  - get_portafolio_status: eval_to_check agregado despues de portafolio=..., usado en factory.get() del Informe y en evaluation= de Cuestionarios
  - GenerarInformeResultadosView: eval_to_check agregado despues del if not workplace, usado en factory.get()
  - CuestionariosAplicadosView: evaluation = workplace.evaluation if workplace.paid else max(1, workplace.evaluation - 1) (mismo patron, una sola linea)
- PROBADO Y CONFIRMADO por Jorge: workplace 15 y un usuario nuevo adicional, ambos muestran los 3 documentos completos con datos reales ✅
- LECCION IMPORTANTE: cualquier vista NUEVA que se construya en el futuro y necesite buscar respuestas de encuestas por evaluation, DEBE usar eval_to_check (paid/evaluation-1), NUNCA workplace.evaluation directo — este es el patron correcto establecido en Index (dashboard) desde antes, que se le olvido replicar a las vistas del Portafolio cuando se construyeron

### Limpieza de UI en evidence.html ✅
- Eliminado el empty-state redundante "No hay resultados generados para este centro de trabajo" (ligado a la lista vieja de ResultFiles/results.length) — quedaba huerfano y confuso ahora que el checklist fusionado (portafolio_status) ya muestra su propio estado. Solo queda el empty-state "Selecciona un centro de trabajo para ver sus evidencias"

## Pendientes activos de esta sesion (continuar en la siguiente)
1. Fase C del Portafolio: agregar al checklist espacios de carga manual para: Canalizaciones Guia I (acontecimientos traumaticos severos), Examenes medicos/evaluaciones psicologicas, Medidas de control/Programa de intervencion, Evidencia de difusion de la politica. Estos NO se generan automaticamente, la empresa los debe cargar como archivo
2. Mensajes claros en los 3 documentos de Fase A cuando no hay datos: en vez de solo decir "pendiente"/"sin respuestas suficientes", agregar texto explicito tipo "Este documento se actualizara automaticamente cuando se completen las evaluaciones/cuestionarios correspondientes" — para que el usuario entienda que no es un error, es un estado transitorio esperado
3. Tema pendiente de sesion anterior, no resuelto aun: candidatos (psicometria) sin evaluaciones contestadas no pueden generar reporte unificado — hay que poner esas evaluaciones demo de esos 2 usuarios candidatos como resueltas

## ACTUALIZACION 6 Jul 2026 (sesion 7) — Fase C completa: carga manual de evidencias

### FASE C IMPLEMENTADA ✅
- Modelo generico EvidenciaFaseC (surveys/models.py, migration 0036): workplace FK, tipo (choices: canalizacion/examen_medico/medida_control/difusion), archivo (FileField), notas, fecha_carga
- Form EvidenciaFaseCForm (surveys/forms.py) con validacion:
  - Limite de tamano: 10 MB por archivo (decision de negocio para controlar costos de hosting)
  - Tipos permitidos: solo PDF, JPG, PNG (clean_archivo() valida size y extension)
- Vista SubirEvidenciaFaseCView (surveys/views.py): GET muestra form + lista de evidencias ya cargadas de ese tipo, POST guarda y redirige (permite subir multiples archivos del mismo tipo, ej. varias canalizaciones)
- URL subir_evidencia_fase_c/<workplace_id>/<tipo>/ (tipo es parametro string: canalizacion/examen_medico/medida_control/difusion)
- Template evidencia_fase_c_form.html: estilo NormaIA consistente (.form-group/.form-control/.section-card), muestra lista de archivos ya subidos con link "Ver archivo" y fecha, formulario de carga debajo
- get_portafolio_status actualizado: agrega 2-4 items de Fase C al checklist con VISIBILIDAD CONDICIONAL:
  - Canalizaciones Guia I: SIEMPRE visible (numeral 5.5 de la norma aplica a todos los centros)
  - Evidencia de Difusion: SIEMPRE visible (numeral 5.7 aplica a todos los centros)
  - Examenes Medicos/Evaluaciones Psicologicas: SOLO visible si el diagnostico (chart_data.total_dim) muestra nivel Medio(2)/Alto(3)/Muy alto(4) en alguna dimension — logica: itera total_dim buscando algun item con nivel>=2 y val>0
  - Medidas de Control/Programa de Intervencion: mismo criterio que examenes medicos
- PROBADO Y CONFIRMADO por Jorge en produccion: checklist muestra correctamente 5-7 items segun corresponda ✅

### Decisiones de producto tomadas en esta sesion
- Modelo GENERICO (EvidenciaFaseC con campo tipo) en vez de 4 modelos separados — mas simple de mantener, permite multiples archivos por tipo
- Carga = archivo real + notas (no solo checkbox de "completado")
- Limite de archivo 10MB, solo PDF/JPG/PNG — decision explicita de Jorge para controlar costos de storage en Railway
- Items de Fase C con visibilidad condicional (no todos siempre visibles) — mas fiel a lo que exige la norma segun el diagnostico real de cada centro de trabajo

## Con esto Portafolio de Evidencias queda COMPLETO end-to-end:
- Fase A (3 documentos automaticos): Politica, Informe de Resultados, Cuestionarios Aplicados — generados por la plataforma, usan eval_to_check correctamente
- Fase C (2-4 items de carga manual): Canalizaciones, Difusion siempre + Examenes/Medidas condicionales segun diagnostico
- Checklist unico fusionado en evidence.html, con estado ✓/⚠, detalle, y boton "Abrir"/link de accion por item
- Todos los bugs de sincronizacion de evaluacion (eval_to_check) resueltos en las 3 vistas de Fase A

## Pendientes para la siguiente sesion
1. Mensajes claros de "se actualizara automaticamente" en los 3 documentos de Fase A cuando esten en estado pendiente (mejora de copy, no bloqueante — quedo pendiente de sesiones anteriores)
2. Candidatos (psicometria) sin evaluaciones contestadas no pueden generar reporte unificado — poner evaluaciones demo de esos 2 usuarios candidatos como resueltas (pendiente de sesiones anteriores, no resuelto aun)
3. Considerar agregar boton "Descargar" (ademas de "Ver archivo") en evidencia_fase_c_form.html si los usuarios lo piden
4. Revisar si se necesita un limite de NUMERO de archivos por tipo/workplace (hoy no hay limite de cantidad, solo de tamano individual)

## ACTUALIZACION 7 Jul 2026 (sesion 8) — Reporte unificado psicometria + branding NormaIA

### BUG RESUELTO: candidatos demo sin evaluaciones contestadas ✅
- Problema: ReporteUnificadoView (surveys/psico_views.py:400) requiere TestSession con status='completada' + su TestResult asociado (via session.result). Los candidatos demo (Pedro Alvarado, Sofia Ramirez) se creaban con TestSession pero sin status explicito (quedaba en default 'pendiente') y SIN TestResult — por eso el reporte unificado mostraba "sin datos" (psico_reporte_sin_datos.html)
- FIX en cargar_datos_demo.py:
  - TestSession ahora se crea con status='completada', fecha_inicio y fecha_completado explicitos
  - Se agrega creacion de TestResult con scores coherentes segun PsychoInstrument.tipo:
    - disc: {'D':20,'I':15,'S':10,'C':8} (formato requerido por ReporteUnificadoView: max ~28 por letra)
    - moss: {'total':68} (formato: /90)
    - raven: {'porcentaje':75} (formato: 0-100)
    - zavic: {'M':40,'L':30,'I':20,'C':10} (formato: valores relativos, se normalizan a %)
  - Se agrego import de TestResult en cargar_datos_demo.py (import explicito, no wildcard)
- IMPORTANTE: este fix solo aplica a usuarios NUEVOS registrados despues del deploy — candidatos demo de usuarios ya existentes (creados antes de este fix) seguiran sin TestResult, no se corrigen retroactivamente
- PROBADO Y CONFIRMADO por Jorge con usuario nuevo: reporte unificado de Sofia Ramirez se genera correctamente con perfil DISC completo ✅

### Limpieza de branding: IHES → NormaIA ✅
- psico_reporte.html (reporte unificado psicometria): quitado header "IHES <span>NOM-035</span>" + "Plataforma de Evaluacion Psicometrica" (dejado vacio, consistente con reportes NOM-035 sin logo). Footer cambiado de "Reporte generado por IHES NOM-035" a "Reporte generado por NormaIA"
- Copyright actualizado de "IHES S.C." (o variantes: "IHES SA. de CV.", "Instituto Hispanoamericano de Estudios Superiores S.C.") a "NormaIA 2027" en 5 templates:
  - index.html (dashboard principal)
  - psico_candidatos.html
  - password_recover.html
  - survey.html (2 ocurrencias, ambas actualizadas)
  - valid_email.html
- NO se toco index_backup_original.html (decision explicita de Jorge: es un respaldo viejo sin usar)
- landing.html YA decia "NormaIA" correctamente, no requirio cambio

## Pendientes activos para continuar
1. Mensajes claros de "se actualizara automaticamente" en los 3 documentos de Fase A del Portafolio (Politica/Informe/Cuestionarios) cuando esten en estado pendiente — mejora de copy, no bloqueante, pendiente desde sesion 6
2. Considerar boton "Descargar" explicito ademas de "Ver archivo" en evidencias de Fase C (opcional)
3. Revisar limite de NUMERO de archivos por tipo/workplace en Fase C (hoy solo hay limite de tamano individual de 10MB, no de cantidad)
4. Jorge menciono que encontro "otros detalles" adicionales en esta sesion — pendiente de detallar

## ACTUALIZACION 7 Jul 2026 (sesion 8) — Reporte unificado psicometria + branding NormaIA

### BUG RESUELTO: candidatos demo sin evaluaciones contestadas ✅
- Problema: ReporteUnificadoView (surveys/psico_views.py:400) requiere TestSession con status='completada' + su TestResult asociado (via session.result). Los candidatos demo (Pedro Alvarado, Sofia Ramirez) se creaban con TestSession pero sin status explicito (quedaba en default 'pendiente') y SIN TestResult — por eso el reporte unificado mostraba "sin datos" (psico_reporte_sin_datos.html)
- FIX en cargar_datos_demo.py:
  - TestSession ahora se crea con status='completada', fecha_inicio y fecha_completado explicitos
  - Se agrega creacion de TestResult con scores coherentes segun PsychoInstrument.tipo:
    - disc: {'D':20,'I':15,'S':10,'C':8} (formato requerido por ReporteUnificadoView: max ~28 por letra)
    - moss: {'total':68} (formato: /90)
    - raven: {'porcentaje':75} (formato: 0-100)
    - zavic: {'M':40,'L':30,'I':20,'C':10} (formato: valores relativos, se normalizan a %)
  - Se agrego import de TestResult en cargar_datos_demo.py (import explicito, no wildcard)
- IMPORTANTE: este fix solo aplica a usuarios NUEVOS registrados despues del deploy — candidatos demo de usuarios ya existentes (creados antes de este fix) seguiran sin TestResult, no se corrigen retroactivamente
- PROBADO Y CONFIRMADO por Jorge con usuario nuevo: reporte unificado de Sofia Ramirez se genera correctamente con perfil DISC completo ✅

### Limpieza de branding: IHES → NormaIA ✅
- psico_reporte.html (reporte unificado psicometria): quitado header "IHES <span>NOM-035</span>" + "Plataforma de Evaluacion Psicometrica" (dejado vacio, consistente con reportes NOM-035 sin logo). Footer cambiado de "Reporte generado por IHES NOM-035" a "Reporte generado por NormaIA"
- Copyright actualizado de "IHES S.C." (o variantes: "IHES SA. de CV.", "Instituto Hispanoamericano de Estudios Superiores S.C.") a "NormaIA 2027" en 5 templates:
  - index.html (dashboard principal)
  - psico_candidatos.html
  - password_recover.html
  - survey.html (2 ocurrencias, ambas actualizadas)
  - valid_email.html
- NO se toco index_backup_original.html (decision explicita de Jorge: es un respaldo viejo sin usar)
- landing.html YA decia "NormaIA" correctamente, no requirio cambio

## Pendientes activos para continuar
1. Mensajes claros de "se actualizara automaticamente" en los 3 documentos de Fase A del Portafolio (Politica/Informe/Cuestionarios) cuando esten en estado pendiente — mejora de copy, no bloqueante, pendiente desde sesion 6
2. Considerar boton "Descargar" explicito ademas de "Ver archivo" en evidencias de Fase C (opcional)
3. Revisar limite de NUMERO de archivos por tipo/workplace en Fase C (hoy solo hay limite de tamano individual de 10MB, no de cantidad)
4. Jorge menciono que encontro "otros detalles" adicionales en esta sesion — pendiente de detallar

## PENDIENTE SIN RESOLVER — sesion 8 (cortada, continuar en la siguiente)

### Bugs reportados por Jorge en workplace_result (aun sin diagnosticar a fondo)
Ubicacion: https://nom035-production.up.railway.app/workplace_result/18/1/
Template: surveys/templates/workplace_results.html

1. **Paginacion incorrecta en resultados vs detalle**: en /workplaces/18/ (detalle del centro, lista de empleados) la paginacion funciona bien. En /workplace_result/18/1/ (ver resultados) la paginacion "ya no es correcta, y falla" — Jorge no especifico el error exacto, falta reproducir/ver el comportamiento real
2. **Boton "Descargar resultados" no funciona**: linea 250 de workplace_results.html. No descarga nada y muestra "un mensaje muy feo" (no se capturo el mensaje exacto). Opciones propuestas por Jorge: (a) quitar el boton porque los resultados ya estan en el Portafolio de Evidencias, o (b) hacer que si descargue un PDF con esos resultados
3. **Boton "Resultados adicionales" por empleado no funciona**: tabla de "Resultados por empleado", columna "Resultados adicionales" (linea 340). Boton feo, no descarga nada, no esta claro que deberia mostrar. Jorge no recuerda la funcion original — evaluar si se quita o se corrige

### Siguiente paso al retomar
Se iba a revisar:
```bash
sed -n '240,260p' surveys/templates/workplace_results.html
sed -n '335,360p' surveys/templates/workplace_results.html
```
para ver el codigo exacto de ambos botones (que endpoint/funcion JS intentan llamar) antes de decidir el fix — Jorge corto la sesion antes de correr estos comandos.

### Decision pendiente de tomar con Jorge
Para el boton "Descargar resultados": ¿eliminar (ya que Informe de Resultados del Portafolio de Evidencias cubre esta necesidad) o arreglar para que genere PDF real?
Para "Resultados adicionales" por empleado: confirmar que debia mostrar antes de decidir si se quita o se repara.

## Pendientes acumulados (no resueltos aun, de sesiones anteriores)
1. Mensajes claros de "se actualizara automaticamente" en los 3 documentos de Fase A del Portafolio cuando esten en estado pendiente
2. Boton "Descargar" explicito ademas de "Ver archivo" en evidencias de Fase C (opcional)
3. Limite de NUMERO de archivos por tipo/workplace en Fase C (hoy solo hay limite de tamano individual)
4. Los 3 bugs de workplace_result descritos arriba (nuevo, sesion 8)

## ACTUALIZACION 7 Jul 2026 (sesion 9) — Fixes en workplace_results.html

### BUG RESUELTO: Paginacion sin estilo en "Resultados por empleado" ✅
- Comparando /workplaces/18/ (Empleados del centro, paginacion bien estilizada) vs /workplace_result/18/1/ (Resultados por empleado, paginacion como lista con bullets sin estilo)
- Causa: workplace_results.html tenia el CSS base de .dataTables_paginate .paginate_button pero le faltaban 3 reglas que SI tenia workplace_detail.html:
  - .dataTables_wrapper .dataTables_paginate { list-style: none !important; padding-left: 0 !important; }
  - .dataTables_wrapper .dataTables_paginate span { list-style: none !important; }
  - .dataTables_wrapper ul, .dataTables_wrapper li { list-style: none !important; padding-left: 0 !important; }
- FIX: se agregaron las 3 reglas faltantes en workplace_results.html, en el mismo orden/lugar que workplace_detail.html
- PROBADO Y CONFIRMADO por Jorge ✅

### BUG RESUELTO: Boton "Descargar resultados" no funcionaba ✅
- El boton (header de workplace_results.html) llamaba a /api/save_chart/ (SaveCharts view) que a su vez usa pdf_reports_task.delay(...) — la MISMA tarea Celery con WeasyPrint que sabemos esta permanentemente rota en Railway
- Jorge confirmo: como el Informe de Resultados del Portafolio de Evidencias ya cubre esta necesidad (sin depender de WeasyPrint), se decidio ELIMINAR el boton en vez de arreglarlo
- FIX: se elimino el bloque <div class="results-actions"><button class="results">Descargar resultados</button></div> del template, y su handler JS huerfano $(".results").click(function(){...}) que llamaba a /api/save_chart/
- NOTA: SaveCharts (views.py:355) y la ruta /api/save_chart/ siguen existiendo en el codigo/urls.py, solo se quito el boton/handler que lo disparaba desde este template. No se borro la vista backend (podria estar en uso desde otro lugar, no se investigo)
- PROBADO Y CONFIRMADO por Jorge ✅

### MEJORA: Boton "Resultados adicionales" por empleado ✅
- Los botones existian y SI funcionaban (abren /reporte_html/{fileid}/{evaluation}/, mismo patron HTML imprimible que ya funciona), pero eran badges pequeños con SOLO icono, sin texto, dificiles de entender. Ademas tenian un typo: "Descargar resutados"
- Jorge eligio: un boton por tipo con texto claro (no un boton generico, no solo iconos con tooltip)
- FIX en employees_dt (views.py ~1225-1238): reemplazado el HTML de badges-solo-icono por <button> con texto: "Ver trauma" (para Guia I) y "Ver riesgo psicosocial" (para Guia II/III), corregido el typo "resutados"→"resultados"
- El campo `traumado` sigue llamandose asi en el codigo (variable interna), no fue necesario renombrarlo
- PROBADO Y CONFIRMADO por Jorge: "quedo perfecto" ✅

## Pendientes para la siguiente sesion
1. Mensajes claros de "se actualizara automaticamente" en los 3 documentos de Fase A del Portafolio cuando esten en estado pendiente (arrastrado de sesiones anteriores)
2. Mejorar la vista del selector "Centro de trabajo" en el Portafolio de Evidencias (evidence.html) — Jorge senalo que se ve muy simple/sin estilo (screenshot muestra solo un select basico sin la lista de opciones visible, se ve vacio/poco pulido). PENDIENTE DE INICIAR esta sesion
3. Boton "Descargar" explicito ademas de "Ver archivo" en evidencias de Fase C (opcional, no solicitado aun)
4. Limite de NUMERO de archivos por tipo/workplace en Fase C (hoy solo hay limite de tamano individual de 10MB)

## PENDIENTE SIN TERMINAR — sesion 9 (parte 2, cortada, continuar en la siguiente)

### En proceso: Catalogo de Instrumentos Psicometricos (nueva vista "Evaluaciones")

**Contexto de la decision:**
- El link "Evaluaciones" del sidebar apuntaba a la MISMA url que "Candidatos" ({% url 'candidatos' %} duplicado) — no servia para nada, confirmado por Jorge
- Se evaluaron 2 opciones: (A) catalogo de instrumentos con asignacion directa, (B) mini-dashboard de evaluaciones ya aplicadas
- Se eligio la OPCION A: catalogo de instrumentos psicometricos activos, con boton "Asignar a candidato" en cada tarjeta

**Instrumentos nuevos aprobados por Jorge (para agregar despues, la definicion del contenido/reactivos vino de una sesion con ChatGPT):**
1. Competencias Laborales — 8 dimensiones x 5 reactivos = 40 items, Likert 5 puntos (Comunicacion, Trabajo en equipo, Responsabilidad, Organizacion, Solucion de problemas, Adaptabilidad, Orientacion a resultados, Aprendizaje)
2. Perfil Comercial y Servicio al Cliente — mismo formato 8x5=40 items (Orientacion al cliente, Comunicacion comercial, Persuasion etica, Manejo de objeciones, Seguimiento y cierre, Tolerancia al rechazo, Solucion de problemas del cliente, Orientacion a metas)
- Observaciones de Claude sobre la propuesta de ChatGPT: cuidado con item PC_RECH_03 (carga valorativa fuerte, se acerca a rasgo de personalidad no competencia objetiva); los codigos de reactivo (CL_COM_01, PC_CLI_01) deben verificarse contra el patron real de PsychoItem/TestResponse antes de que ChatGPT genere el JSON final; la calificacion es suma simple sin ponderacion (aceptable para MVP)
- AUN NO SE HA CONSTRUIDO EL JSON DE REACTIVOS NI SE HAN CARGADO A PsychoItem — eso es el siguiente paso grande, pendiente

**Avance tecnico de esta sesion (Catalogo de Instrumentos):**
1. ✅ PsychoInstrument.TIPOS actualizado en models.py: agregados ('competencias', 'Competencias Laborales') y ('comercial', 'Perfil Comercial y Servicio al Cliente')
2. ✅ Vista InstrumentosCatalogoView creada en surveys/psico_views.py (al final del archivo): lista PsychoInstrument activos + Candidate del usuario, renderiza psico_instrumentos.html
3. ✅ URL agregada: path('psico/instrumentos/', InstrumentosCatalogoView.as_view(), name='instrumentos_catalogo') en nom035/urls.py, linea 119
4. ✅ Template psico_instrumentos.html creado (copia de psico_candidato_detalle.html, 559 lineas) — sidebar/topbar reutilizados tal cual, contenido central YA reemplazado con tarjetas de instrumentos (bloque "Instrumentos Psicometricos" con boton "Asignar a candidato" por tarjeta, funcion JS abrirModalAsignar(instId, instNombre) ya referenciada en el boton)
5. ⚠️ PENDIENTE INCOMPLETO: el MODAL de asignacion (al final del archivo, lineas ~415-490) TODAVIA tiene el codigo VIEJO de psico_candidato_detalle.html sin adaptar:
   - Linea 424: `<p class="modal-desc">Selecciona el instrumento a aplicar a candidate.nombre</p>` — candidate NO EXISTE en este contexto, hay que cambiar a un <strong id="nombre_instrumento_modal"> vacio que se llena por JS
   - Linea 428: `<select id="sel_instrumento">` con opciones de TODOS los instrumentos — hay que CAMBIAR a `<select id="sel_candidato">` con opciones de candidatos (el instrumento ya viene fijo del boton de la tarjeta, no se vuelve a elegir en el modal)
   - Linea 463-471: el JS del boton btnAsignar usa `document.getElementById('sel_instrumento').value` y `{% url 'asignar_test' candidate.id %}` (candidate.id no existe aqui) — hay que reemplazar por: usar una variable JS `instrumento_actual_id` seteada por `abrirModalAsignar()`, leer `sel_candidato` para el id del candidato, y armar la URL dinamicamente como `"/psico/asignar/" + candidate_id + "/"` en vez de usar {% url %} con valor fijo
6. NO SE HA HECHO COMMIT DE NADA DE ESTO TODAVIA (models.py, psico_views.py, urls.py, psico_instrumentos.html) — sigue solo en el filesystem local de Jorge, no en git ni desplegado

### Intentos fallidos de edicion (leccion aprendida)
- Se intento reemplazar el bloque del modal con content.replace() de bloques largos (heredoc python3 << 'PYEOF') pero las ocurrencias no coincidieron (probablemente diferencias de espacios/comillas) — el intento aborto correctamente SIN escribir nada (safety check de content.count()==1 funciono bien), asi que el archivo esta intacto pero sin el fix aplicado
- Se decidio cambiar de estrategia a edicion por INDICE DE LINEA con sed para confirmar rangos exactos antes de reemplazar — este es el enfoque mas confiable para este archivo, continuar asi en la siguiente sesion

### Siguiente paso exacto al retomar
```bash
sed -n '424,434p' surveys/templates/psico_instrumentos.html
```
para confirmar el rango completo del bloque modal-desc + form-group + select + su cierre </div>, y de ahi reemplazar por indice de linea (readlines() + lines[inicio:fin] = nuevo_bloque) los 3 puntos pendientes: (a) texto del modal-desc, (b) select de candidato en vez de instrumento, (c) JS del boton btnAsignar con la nueva logica de abrirModalAsignar + URL dinamica.

Despues de eso: py_compile no aplica a HTML pero SI verificar con grep/sed que no haya tags sin cerrar, luego commit de los 4 archivos juntos (models.py, psico_views.py, urls.py, psico_instrumentos.html), deploy, y probar /psico/instrumentos/ en el navegador.

## Pendientes acumulados (arrastrados de sesiones previas, aun no resueltos)
1. Mensajes claros de "se actualizara automaticamente" en los 3 documentos de Fase A del Portafolio cuando esten en estado pendiente
2. Boton "Descargar" explicito ademas de "Ver archivo" en evidencias de Fase C (opcional)
3. Limite de NUMERO de archivos por tipo/workplace en Fase C (hoy solo hay limite de tamano individual de 10MB)
4. Construir el JSON de reactivos para Competencias Laborales y Perfil Comercial (una vez el catalogo este terminado), cargarlos a PsychoInstrument/PsychoItem, y verificar que ReporteUnificadoView / GenerarPerfilNarrativoView sepan interpretar estos 2 tipos nuevos (hoy solo manejan disc/moss/raven/zavic en la logica de scores)
