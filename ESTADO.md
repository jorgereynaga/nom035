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
- PortafolioEvidencias demo se crea automaticamente en cargar_datos_demo.py con datos de ejemplo ✅
- Creditos gratis eliminados: nom035_demo y psico_demo cambiados de default=1 a default=0 (migration 0035) — usuarios NUEVOS ya no reciben creditos gratis. Usuarios existentes conservan los que ya tenian ✅
- Link visible a Politica de Prevencion agregado en evidence.html (tarjeta con href dinamico basado en v-model workplace de Vue) ✅
- Eliminado duplicado de PoliticaPrevencionForm en forms.py (estaba definido 2 veces identicas) ✅
- Formulario politica_prevencion_form.html rediseñado con estilo NormaIA real (.form-group, .form-label, .form-control, .section-card, .btn-primary) en vez de HTML plano ✅
- Widgets form-control agregados a todos los campos de PoliticaPrevencionForm (antes se veian sin estilo, tipo "Word") ✅
- Corregido empty-state de evidence.html: ahora distingue "sin workplace seleccionado" (v-if=\"!workplace\") de "sin resultados generados" (v-else-if=\"!results.length\") — antes mostraba el mensaje erroneo aunque ya hubiera un workplace seleccionado y la tarjeta de Politica visible ✅

## Estado actual (dashboard funcional)
- NOM-035: 100% cuestionarios, Completado, dimensiones 4x2 visibles ✅
- Clima Laboral: 8 respuestas, grid 4x2 con colores por nivel ✅
- Psicometria: 2 candidatos demo con evaluacion asignada ✅
- Borrar datos demo: FUNCIONA ✅
- Bloqueos sin plan: FUNCIONA ✅
- Reporte unificado: FUNCIONA ✅
- Dashboard carga correctamente ✅
- Portafolio Evidencias - Politica de Prevencion: FUNCIONA COMPLETO — visible desde sidebar > Portafolio de evidencias > seleccionar centro > tarjeta "Politica de Prevencion" > Abrir > formulario con estilo correcto > Generar Politica > version imprimible. Probado y confirmado por Jorge el 4 Jul (capturas de pantalla) ✅

## Pendientes
1. Portafolio de evidencias — Fase A restante: GenerarInformeResultadosPDF (numeral 7.7 norma: datos centro, objetivo, actividades, metodo, resultados, conclusiones, recomendaciones, responsable) + CuestionariosAplicadosPDF (listado convocados, % participacion, fechas)
2. Portafolio de evidencias — falta mostrar en evidence.html las DEMAS evidencias ademas de la Politica (Informe de Resultados, Cuestionarios Aplicados) una vez esten construidas en el pendiente #1. Actualmente solo se ve la tarjeta de Politica
3. Portafolio de evidencias — considerar construir PortafolioStatusView como checklist mas robusto dentro de evidence.html en vez de seguir agregando tarjetas sueltas una por una (discutido, no decidido aun)
4. Portafolio de evidencias — Fase C (despues de A): espacios de carga manual para canalizaciones Guia I, examenes medicos, medidas de control, evidencia de difusion
5. Pruebas finales: navegacion entre evaluaciones multiples
6. Selector de "Centro de trabajo" en evidence.html se ve poco estilizado — Jorge confirmo que esto es deuda de diseño PREEXISTENTE (sistema viejo que solo funcionaba para NOM-035, se esta modernizando), NO fue introducido por los cambios de esta sesion. Mejora de diseño futura, no urgente
7. Reporte de lentitud de plataforma del 4 Jul — no diagnosticado, no reproducido de nuevo, posiblemente no relacionado a los cambios de esta sesion (una tabla nueva vacia no deberia impactar performance)

## Notas tecnicas
- views.py: mezcla tabs/espacios es el principal riesgo — siempre py_compile antes de push
- WeasyPrint: permanentemente bloqueado en Railway (falla import de librerias externas en logs). Patron real que SI funciona en produccion: render(request, 'pdf/plantilla.html', ctx) con print_mode=True, usuario exporta a PDF via Ctrl+P del navegador. pdf_reports_task en tasks.py sigue usando WeasyPrint pero probablemente falla silenciosamente en Railway — NO usar ese patron para nuevo codigo
- Migraciones: siempre manuales, ultima es 0035 (alter defaults nom035_demo/psico_demo)
- nom035_demo y psico_demo: ahora default=0 (antes default=1). assign_nom035_credits (surveys/services/credits.py) solo se llama tras evento de pago Stripe (linea 2624 de views.py), NO en registro ni en cargar_datos_demo
- Logica bloqueo: workplace.es_demo=True → 403 en registro de encuestas
- clima_sin_plan.html: template para enlace publico sin plan activo
- Editor: Sublime Text — siempre editar Python con python -c por indices de linea (readlines()+insert()/lines[n]=...). Al insertar MULTIPLES lineas por indice en una sola pasada, insertar de indice mas alto a mas bajo para no desfasar posiciones. Para archivos HTML/templates usar el mismo enfoque con verificacion previa de content.count(marcador)==1 antes de cualquier replace() de bloque, y SIEMPRE verificar con sed/cat despues de escribir — un replace() puede fallar silenciosamente en pegar mal las lineas de apertura de un bloque (paso 4-jul: se perdieron 2 divs de apertura en un primer intento sobre evidence.html, se detecto con sed y se corrigio por indice de linea)
- surveys/forms.py usa espacios (4), surveys/models.py y surveys/views.py usan tabs, surveys/management/commands/cargar_datos_demo.py usa espacios (4) — respetar el estilo de cada archivo
- index.html usa block dashboard (NO block content) — templates que extienden index.html deben usar {% block dashboard %}
- Sistema de diseño NormaIA real (clases confirmadas en evidence.html): .form-group, .form-label, .form-control (con :focus usando var(--primary)), .section-card, .section-card-header, .section-card-title, .section-card-body, .btn/.btn-primary/.btn-outline-primary, variables CSS var(--bg-base), var(--border), var(--text-primary), var(--text-secondary), var(--radius-md/lg), var(--shadow-sm). Cualquier template nuevo que extienda index.html debe usar estas clases, NO estilos inline improvisados
- Workplace vive en surveys/models.py:48 — campos reales: name, address, main_activity, employee_num (NO nombre/domicilio en español)
- Userapp tiene campos "Centros pagados A/B/C" (workplaces_available, workplaces_availableB, workplaces_availableC, default=0) editables desde admin para dar acceso manual sin pago — mecanismo real de acceso gratis manual, distinto de nom035_demo/psico_demo
- evidence.html usa Vue.js (v-model="workplace", v-for, AJAX a get_results/get_workplaces) — cualquier insercion ahi debe respetar la instancia Vue existente. El selector de workplace SI usa select2 (v-select2) aunque se vea con estilo basico — es deuda de diseño preexistente, no bug introducido
- Portafolio Evidencias: NO usar boton unico "generar todo" — dashboard/checklist con
  generacion individual por documento, para evitar implicar que es paquete "certificado"
  ante autoridad (eso lo hacen Unidades de Verificacion, no la plataforma)
- Portafolio Evidencias Fase A usa tablas oficiales de la norma para niveles de riesgo
  (deterministico, sin IA generativa libre en conclusiones/recomendaciones)
- imports en views.py son wildcard: from .models import * / from .forms import * — modelos y forms nuevos quedan disponibles automaticamente. cargar_datos_demo.py usa import explicito, hay que agregar cada modelo nuevo a la lista manualmente
