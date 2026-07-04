# ESTADO NormaIA — Actualizado 4 Jul 2026

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: jorge.reynaga.j@gmail.com (usuario activo con datos demo)

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
- Form PoliticaPrevencionForm creado en surveys/forms.py ✅
- Vista GenerarPoliticaView creada en surveys/views.py (GET muestra form/imprime, POST guarda) ✅
- URL generar_politica/<int:workplace_id>/ agregada en nom035/urls.py ✅
- Template pdf/politica_prevencion.html (version imprimible, mismo estilo que riesgo_psicosocial.html) ✅
- Template politica_prevencion_form.html (formulario, extiende index.html block dashboard) ✅
- Import timezone agregado a surveys/views.py ✅
- PortafolioEvidencias demo se crea automaticamente en cargar_datos_demo.py con datos de ejemplo (responsable, representante legal, canal de quejas, etc.) ✅
- Creditos gratis eliminados: nom035_demo y psico_demo cambiados de default=1 a default=0 (migration 0035) — usuarios NUEVOS ya no reciben creditos gratis al registrarse. Usuarios existentes conservan los que ya tenian ✅

## Estado actual (dashboard funcional)
- NOM-035: 100% cuestionarios, Completado, dimensiones 4x2 visibles ✅
- Clima Laboral: 8 respuestas, grid 4x2 con colores por nivel ✅
- Psicometria: 2 candidatos demo con evaluacion asignada ✅
- Borrar datos demo: FUNCIONA ✅
- Bloqueos sin plan: FUNCIONA ✅
- Reporte unificado: FUNCIONA ✅
- Dashboard carga correctamente ✅
- Portafolio Evidencias - Politica de Prevencion: codigo completo y desplegado (modelo, form, vista, templates, datos demo). Accesible SOLO por URL directa /generar_politica/<workplace_id>/ — NO hay link visible en la UI todavia ⚠️

## Bugs activos / Pendientes de UI
1. **Portafolio de Evidencias sin link visible**: la pagina "Portafolio de evidencias" del sidebar (EvidenceView / evidence.html) es una vista PREEXISTENTE distinta (selector de workplace + lista de ResultFiles via Vue/AJAX con get_results), NO tiene ningun link hacia generar_politica. Se armo un bloque de codigo (tarjeta con link dinamico usando el v-model "workplace" de Vue) pero quedo a medio implementar — pendiente confirmar ocurrencia del marcador en evidence.html antes de escribir con python -c. Insertar antes de la seccion "<!-- Results -->" (linea ~199 aprox, verificar con sed antes de editar)
2. **Plataforma lenta durante prueba del 4 Jul**: reportado por Jorge durante prueba de generar_politica, no diagnosticado. Podria no estar relacionado a los cambios de hoy (una tabla nueva vacia no deberia impactar performance). Pendiente de reproducir/diagnosticar con mas contexto (¿lento en toda la plataforma o solo en una vista especifica?)

## Pendientes
1. Resolver bug activo #1 (link visible Portafolio de Evidencias en evidence.html)
2. Portafolio de evidencias — Fase A restante: GenerarInformeResultadosPDF (numeral 7.7 norma: datos centro, objetivo, actividades, metodo, resultados, conclusiones, recomendaciones, responsable) + CuestionariosAplicadosPDF (listado convocados, % participacion, fechas)
3. Portafolio de evidencias — PortafolioStatusView (checklist/dashboard de estado, NO boton unico "generar todo" — cada documento individual bajo demanda)
4. Portafolio de evidencias — Fase C (despues de A): espacios de carga manual para canalizaciones Guia I, examenes medicos, medidas de control, evidencia de difusion
5. Pruebas finales: navegacion entre evaluaciones multiples
6. Investigar reporte de lentitud del 4 Jul (bug activo #2)

## Notas tecnicas
- views.py: mezcla tabs/espacios es el principal riesgo — siempre py_compile antes de push
- WeasyPrint: permanentemente bloqueado en Railway (falla import de librerias externas en logs, confirmado 4 Jul). Patron real que SI funciona en produccion: render(request, 'pdf/plantilla.html', ctx) con print_mode=True, usuario exporta a PDF via Ctrl+P del navegador. pdf_reports_task en tasks.py sigue usando WeasyPrint pero probablemente falla silenciosamente en Railway — NO usar ese patron para nuevo codigo
- Migraciones: siempre manuales, ultima es 0035 (alter defaults nom035_demo/psico_demo)
- nom035_demo y psico_demo: ahora default=0 (antes default=1) — ver seccion Completado. assign_nom035_credits (surveys/services/credits.py) solo se llama tras evento de pago Stripe (linea 2624 de views.py), NO en registro ni en cargar_datos_demo — nunca fue la fuente de creditos gratis, el default del campo del modelo si lo era
- Logica bloqueo: workplace.es_demo=True → 403 en registro de encuestas
- clima_sin_plan.html: template para enlace publico sin plan activo
- Editor: Sublime Text — siempre editar Python con python -c por indices de linea (para archivos con tabs/espacios mezclados usar readlines()+insert(), NO string replace; solo se uso replace() puntual en views.py el 4 Jul por complejidad del marcador, con verificacion previa de content.count(marcador)==1 antes de escribir)
- surveys/forms.py usa espacios (4), surveys/models.py y surveys/views.py usan tabs, surveys/management/commands/cargar_datos_demo.py usa espacios (4) — respetar el estilo de cada archivo
- index.html usa block dashboard (NO block content) — templates que extienden index.html deben usar {% block dashboard %}
- Workplace vive en surveys/models.py:48 — campos reales: name, address, main_activity, employee_num (NO nombre/domicilio en español)
- Userapp tiene campos "Centros pagados A/B/C" (workplaces_available, workplaces_availableB, workplaces_availableC, default=0) editables desde admin para dar acceso manual sin pago — mecanismo real de acceso gratis manual, distinto de nom035_demo/psico_demo
- evidence.html usa Vue.js (v-model="workplace", v-for, AJAX a get_results/get_workplaces) — cualquier insercion ahi debe respetar la instancia Vue existente, no mezclar con Django template tags de forma que rompa el parseo
- Portafolio Evidencias: NO usar boton unico "generar todo" — dashboard/checklist con
  generacion individual por documento, para evitar implicar que es paquete "certificado"
  ante autoridad (eso lo hacen Unidades de Verificacion, no la plataforma)
- Portafolio Evidencias Fase A usa tablas oficiales de la norma para niveles de riesgo
  (deterministico, sin IA generativa libre en conclusiones/recomendaciones)
- imports en views.py son wildcard: from .models import * / from .forms import * — modelos y forms nuevos quedan disponibles automaticamente sin tocar imports. cargar_datos_demo.py usa import explicito, hay que agregar cada modelo nuevo a la lista manualmente
