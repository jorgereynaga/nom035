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
