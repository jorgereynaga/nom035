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

## Estado actual (dashboard funcional)
- NOM-035: 100% cuestionarios, Completado, dimensiones 4x2 visibles ✅
- Clima Laboral: 8 respuestas, grid 4x2 con colores por nivel ✅
- Psicometria: 2 candidatos demo con evaluacion asignada ✅
- Borrar datos demo: FUNCIONA ✅
- Bloqueos sin plan: FUNCIONA ✅
- Reporte unificado: FUNCIONA ✅
- Dashboard carga correctamente ✅
- Portafolio Evidencias - Politica de Prevencion: codigo completo, pendiente de probar en navegador ⚠️

## Pendientes
1. PROBAR en navegador: https://035.ihes.mx/generar_politica/<workplace_id>/ (llenar form, verificar POST guarda en PortafolioEvidencias, verificar ?print=1 renderiza bien el PDF imprimible)
2. Portafolio de evidencias — Fase A restante: GenerarInformeResultadosPDF (numeral 7.7 norma: datos centro, objetivo, actividades, metodo, resultados, conclusiones, recomendaciones, responsable) + CuestionariosAplicadosPDF (listado convocados, % participacion, fechas)
3. Portafolio de evidencias — PortafolioStatusView (checklist/dashboard de estado, NO boton unico "generar todo" — cada documento individual bajo demanda)
4. Portafolio de evidencias — Fase C (despues de A): espacios de carga manual para canalizaciones Guia I, examenes medicos, medidas de control, evidencia de difusion
5. Pruebas finales: navegacion entre evaluaciones multiples

## Notas tecnicas
- views.py: mezcla tabs/espacios es el principal riesgo — siempre py_compile antes de push
- WeasyPrint: permanentemente bloqueado en Railway (falla import de librerias externas en logs, confirmado 4 Jul). Patron real que SI funciona en produccion: render(request, 'pdf/plantilla.html', ctx) con print_mode=True, usuario exporta a PDF via Ctrl+P del navegador. pdf_reports_task en tasks.py sigue usando WeasyPrint pero probablemente falla silenciosamente en Railway — NO usar ese patron para nuevo codigo
- Migraciones: siempre manuales, ultima es 0034 (PortafolioEvidencias)
- nom035_demo: campo en Userapp que ya no se usa en flujo principal
- Logica bloqueo: workplace.es_demo=True → 403 en registro de encuestas
- clima_sin_plan.html: template para enlace publico sin plan activo
- Editor: Sublime Text — siempre editar Python con python -c por indices de linea (para archivos con tabs/espacios mezclados usar readlines()+insert(), NO string replace; solo se uso replace() puntual en views.py el 4 Jul por complejidad del marcador, con verificacion previa de content.count(marcador)==1 antes de escribir)
- surveys/forms.py usa espacios (4), surveys/models.py y surveys/views.py usan tabs — respetar el estilo de cada archivo
- index.html usa block dashboard (NO block content) — templates que extienden index.html deben usar {% block dashboard %}
- Workplace vive en surveys/models.py:48 — campos reales: name, address, main_activity, employee_num (NO nombre/domicilio en español)
- Portafolio Evidencias: NO usar boton unico "generar todo" — dashboard/checklist con
  generacion individual por documento, para evitar implicar que es paquete "certificado"
  ante autoridad (eso lo hacen Unidades de Verificacion, no la plataforma)
- Portafolio Evidencias Fase A usa tablas oficiales de la norma para niveles de riesgo
  (deterministico, sin IA generativa libre en conclusiones/recomendaciones)
- imports en views.py son wildcard: from .models import * / from .forms import * — modelos y forms nuevos quedan disponibles automaticamente sin tocar imports
