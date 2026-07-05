# ESTADO NormaIA — Actualizado 5 Jul 2026

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: prueba/TestIhes2026! | jorge.reynaga.j@gmail.com (usuario con datos demo)
- URLs: nom035-production.up.railway.app / 035.ihes.mx

## Completado
- Fix flujo completo NOM-035 (EndEvaluation, Ver resultados, reporte HTML)
- Modulo Clima Laboral completo con datos demo (8 respuestas, 8 dimensiones)
- Dashboard rediseñado 3 secciones con preview de dimensiones 4x2 con colores
- Candidatos demo aparecen en dashboard con nombre y estado correcto
- Registro y login redirigen al dashboard (no a planes)
- Bloqueo sin plan: nuevo centro, agregar empleados, agregar candidatos
- Modal "Plan requerido" al intentar funcion bloqueada
- Boton borrar datos demo (manual) + borrado automatico al contratar plan
- Reporte HTML profesional sin WeasyPrint
- Reporte unificado desbloqueado para usuarios demo
- psico_resultado.html rediseñado correctamente extendiendo index.html ✅
- NOM-035 dimension preview: promedio de todos los empleados ✅
- DEBUG=False en Railway ✅
- Nueva logica bloqueo encuestas: es_demo=True bloquea registro encuestas reales ✅
- Quitar nom035_demo del flujo de creditos ✅
- Restriccion clima laboral: enlace publico solo con plan activo ✅
- admin.py: nom035_creditos visible en UserAdmin ✅
- Fix phone max_length a 15 caracteres (migration 0033) ✅
- Revision completa NOM-035-STPS-2018 (texto oficial DOF) para diseño Portafolio de Evidencias ✅
- Definido alcance Portafolio de Evidencias: Fase A (auto), Fase C (carga manual), Fase B descartada ✅
- Modelo PortafolioEvidencias creado en surveys/models.py (migration 0034) ✅
- Form PoliticaPrevencionForm creado en surveys/forms.py (widgets form-control, sin duplicados) ✅
- Vista GenerarPoliticaView (surveys/views.py) — GET muestra form/imprime, POST guarda ✅
- URL generar_politica/<int:workplace_id>/ ✅
- Templates pdf/politica_prevencion.html + politica_prevencion_form.html (estilo NormaIA real) ✅
- PortafolioEvidencias demo se crea automaticamente en cargar_datos_demo.py ✅
- Creditos gratis eliminados: nom035_demo y psico_demo default=1→0 (migration 0035) — solo afecta usuarios NUEVOS ✅
- Vista GenerarInformeResultadosView — Informe de Resultados NOM-035 numeral 7.7, reutiliza get_chart_data() via RequestFactory interno (sin duplicar calculo de niveles de riesgo) ✅
- URL generar_informe_resultados/<int:workplace_id>/ ✅
- Template pdf/informe_resultados.html (datos centro, objetivo, actividades, metodo, tabla de resultados por dimension con nivel predominante, conclusiones, recomendaciones, responsable) ✅
- Tarjetas visibles en evidence.html (Portafolio de evidencias, sidebar): Politica de Prevencion + Informe de Resultados, cada una con boton "Abrir" y href dinamico via v-model workplace de Vue ✅
- Empty-state de evidence.html corregido: distingue "sin workplace" de "sin resultados" ✅
- PROBADO EN PRODUCCION 5 Jul: /generar_politica/13/ y /generar_informe_resultados/13/ funcionan correctamente, ambas tarjetas visibles en Portafolio de evidencias (confirmado por Jorge) ✅

## Estado actual (dashboard funcional)
- NOM-035: 100% cuestionarios, Completado, dimensiones 4x2 visibles ✅
- Clima Laboral: 8 respuestas, grid 4x2 con colores por nivel ✅
- Psicometria: 2 candidatos demo con evaluacion asignada ✅
- Borrar datos demo: FUNCIONA ✅
- Bloqueos sin plan: FUNCIONA ✅
- Reporte unificado: FUNCIONA ✅
- Dashboard carga correctamente ✅
- Portafolio Evidencias — Politica de Prevencion: FUNCIONA COMPLETO, visible en UI, probado en produccion ✅
- Portafolio Evidencias — Informe de Resultados: FUNCIONA COMPLETO, visible en UI, probado en produccion ✅

## Pendientes
1. Portafolio de evidencias — Fase A restante: CuestionariosAplicadosPDF (listado convocados, % participacion, fechas de aplicacion)
2. Portafolio de evidencias — considerar construir PortafolioStatusView como checklist mas robusto dentro de evidence.html en vez de seguir agregando tarjetas sueltas una por una (discutido, no decidido aun — por ahora funciona bien con tarjetas individuales)
3. Portafolio de evidencias — Fase C (despues de A completa): espacios de carga manual para canalizaciones Guia I, examenes medicos, medidas de control, evidencia de difusion
4. Pruebas finales: navegacion entre evaluaciones multiples
5. Selector de "Centro de trabajo" en evidence.html se ve poco estilizado — deuda de diseño PREEXISTENTE confirmada por Jorge (sistema viejo, se esta modernizando), NO es bug introducido en estas sesiones. Mejora futura, no urgente
6. Reporte de lentitud de plataforma del 4 Jul — no diagnosticado ni reproducido de nuevo, posiblemente no relacionado a los cambios de estas sesiones

## Notas tecnicas
- views.py: mezcla tabs/espacios es el principal riesgo — siempre py_compile antes de push
- WeasyPrint: permanentemente bloqueado en Railway. Patron real que SI funciona: render(request, 'pdf/plantilla.html', ctx) con print_mode=True, usuario exporta a PDF via Ctrl+P del navegador. pdf_reports_task en tasks.py sigue usando WeasyPrint pero probablemente falla silenciosamente — NO usar ese patron para nuevo codigo
- Migraciones: siempre manuales, ultima es 0035 (alter defaults nom035_demo/psico_demo)
- get_chart_data(request) en views.py: funcion grande (~500 lineas) que calcula niveles de riesgo por dominio/categoria/dimension para TODOS los empleados de un workplace, usando las tablas oficiales de rangos de la Guia II y III de la norma (confirmado que coinciden exactamente con el PDF oficial DOF). Devuelve JsonResponse con: status, count, data, total_level, total_cat, data2, total_dim, data5, employees, cat, dimensions, domains. total_dim es lista de {"value":[indice_dimension, nivel_0a4, cantidad_empleados], "itemStyle":{...}} — para "nivel predominante por dimension" agrupar por indice y tomar el nivel con mayor conteo (moda). dimensions es lista de nombres en mismo orden que indices, con \n incrustado (usar chr(10) para reemplazar si se esta dentro de string anidado)
- Para reusar get_chart_data() sin request HTTP real: usar django.test.RequestFactory, construir fake_request con factory.get() pasando workplace_id/evaluation como querystring, asignar fake_request.user = request.user, llamar get_chart_data(fake_request) directo. Evita duplicar/reimplementar el calculo
- nom035_demo y psico_demo: ahora default=0 (antes default=1). assign_nom035_credits (surveys/services/credits.py) solo se llama tras evento de pago Stripe (linea 2624 de views.py), NO en registro ni en cargar_datos_demo
- Logica bloqueo: workplace.es_demo=True → 403 en registro de encuestas
- clima_sin_plan.html: template para enlace publico sin plan activo
- Editor: Sublime Text — siempre editar Python con python -c por indices de linea (readlines()+insert()/lines[n]=...). Al insertar MULTIPLES lineas por indice en una sola pasada, insertar de indice mas alto a mas bajo para no desfasar posiciones. Para bloques largos de texto (HTML/templates) usar content.replace() con marcador CORTO (2-4 lineas, no bloques largos) y verificacion previa de content.count(marcador)==1 antes de escribir — bloques de marcador muy largos con caracteres especiales (comillas anidadas, guiones em-dash) pueden causar que la terminal Git Bash reinserte texto de comandos anteriores del historial al pegar, dando falsos "0 ocurrencias" aunque el archivo este bien. Si esto pasa, verificar el archivo real con grep/sed simple primero (sin pegar bloques largos) antes de asumir que hay corrupcion
- surveys/forms.py usa espacios (4), surveys/models.py y surveys/views.py usan tabs, surveys/management/commands/cargar_datos_demo.py usa espacios (4) — respetar el estilo de cada archivo
- index.html usa block dashboard (NO block content) — templates que extienden index.html deben usar {% block dashboard %}
- Sistema de diseño NormaIA real (confirmado en evidence.html): .form-group, .form-label, .form-control, .section-card, .section-card-header, .section-card-title, .section-card-body, .btn/.btn-primary/.btn-outline-primary, variables CSS var(--bg-base), var(--border), var(--text-primary), var(--text-secondary), var(--radius-md/lg), var(--shadow-sm). Templates nuevos que extienden index.html deben usar estas clases
- Workplace vive en surveys/models.py:48 — campos reales: name, address, main_activity, employee_num, evaluation, survey_type() (metodo, Django templates lo invocan sin parentesis)
- Userapp tiene campos "Centros pagados A/B/C" (workplaces_available, workplaces_availableB, workplaces_availableC, default=0) editables desde admin para dar acceso manual sin pago
- evidence.html usa Vue.js (v-model="workplace", v-for, AJAX a get_results/get_workplaces) — cualquier insercion ahi debe respetar la instancia Vue existente. El selector SI usa select2 aunque se vea con estilo basico (deuda preexistente)
- Portafolio Evidencias: NO usar boton unico "generar todo" — dashboard/checklist con generacion individual por documento, para evitar implicar que es paquete "certificado" ante autoridad (eso lo hacen Unidades de Verificacion, no la plataforma)
- Portafolio Evidencias Fase A usa tablas oficiales de la norma para niveles de riesgo (deterministico, sin IA generativa libre en conclusiones/recomendaciones — texto fijo/generico en informe_resultados.html)
- imports en views.py son wildcard: from .models import * / from .forms import * — modelos y forms nuevos quedan disponibles automaticamente. cargar_datos_demo.py usa import explicito, hay que agregar cada modelo nuevo a la lista manualmente
