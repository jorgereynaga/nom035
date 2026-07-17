# ESTADO NormaIA — Actualizado 8 Jul 2026 (sesión 10)

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: prueba/TestIhes2026! | jorge.reynaga.j@gmail.com (usuario con datos demo)
- URLs: nom035-production.up.railway.app / 035.ihes.mx
- Repo: github.com/jorgereynaga/nom035
- Local: C:\Users\JorgeAlbertoReynagaJ\Documents\nom 035\nom035\
- Editor: Sublime Text, terminal Git Bash en Windows

## IMPORTANTE — Flujo de trabajo con dos cuentas Claude
- Jorge alterna entre dos cuentas de Claude para no detenerse si una llega al límite de uso
- Por esto: ESTADO.md se actualiza y sube a git (commit+push) DESPUES DE CADA COMMIT DE CODIGO, no solo al final de la sesión — así la otra cuenta puede retomar el contexto sin pérdida

## Reglas de trabajo (no negociables)
- Migraciones SIEMPRE manuales (.py escrito a mano), nunca makemigrations — no hay Postgres local
- Deploy SOLO via git push origin main — nunca tocar Railway ni BD directamente
- Python: models.py y views.py usan TABS; forms.py y cargar_datos_demo.py usan ESPACIOS (4) — respetar el estilo de cada archivo
- Editar Python/HTML con python -c usando readlines() + indices de linea (lines[n]=/lines.insert()) — NUNCA str.replace() en bloques largos de HTML/JS sin antes verificar content.count(marcador)==1
- Cuando bash entra en estado raro (prompt >, error "event not found" por el signo ! en comentarios HTML <!--), usar heredoc python3 << 'PYEOF' ... PYEOF en vez de python -c "..."
- Verificar con sed -n antes y despues de cada edicion
- python -m py_compile archivo.py antes de cualquier commit de Python
- Jorge hace commit/push, Claude nunca actua directo — solo da el comando exacto
- Jorge pega logs de Railway despues de cada deploy para confirmar. Warnings W042 (DEFAULT_AUTO_FIELD) son preexistentes, se ignoran siempre

## COMPLETADO Y PROBADO EN PRODUCCION

### Portafolio de Evidencias NOM-035 — completo end-to-end ✅
(sin cambios respecto a sesión anterior — ver detalle histórico si se necesita)

### Reportes de resultados NOM-035 (workplace_results.html) — arreglado sesión 9 ✅
(sin cambios respecto a sesión anterior)

### Psicometría — reporte unificado ✅
(sin cambios respecto a sesión anterior)

### Branding: IHES → NormaIA ✅
(sin cambios respecto a sesión anterior)

### Catálogo de Instrumentos Psicométricos — COMPLETADO Y DESPLEGADO ✅ (sesión 10)
- Nueva vista `InstrumentosCatalogoView` (surveys/psico_views.py): lista instrumentos activos + candidatos del usuario, para asignar pruebas sin duplicar el link "Candidatos" del sidebar
- URL: `path('psico/instrumentos/', InstrumentosCatalogoView.as_view(), name='instrumentos_catalogo')` en nom035/urls.py
- Template `surveys/templates/psico_instrumentos.html`: tarjetas de instrumentos con botón "Asignar a candidato" → abre modal → selecciona candidato → genera link vía AssignTestView existente (no se tocó AssignTestView, solo se reutiliza)
- Modal reescrito desde cero (ya no tiene código heredado de psico_candidato_detalle.html):
  - `abrirModalAsignar(instId, instNombre)` — función nueva, fija el instrumento vía variable global `instrumento_actual_id`, limpia el modal cada vez que se abre
  - `<select id="sel_candidato">` con opciones de `candidatos` (ya no hay `<select id="sel_instrumento">`, el instrumento ya viene fijo del botón de la tarjeta)
  - JS del botón `btnAsignar` construye la URL dinámicamente: `"/psico/asignar/" + candidate_id + "/"` (ya no usa `{% url %}` con valor fijo inexistente)
- **BUG que rompió el primer deploy (ya resuelto):** `InstrumentosCatalogoView` se creó en psico_views.py pero no se agregó al import explícito en nom035/urls.py (línea 24-27, `from surveys.psico_views import (...)`) → NameError en Railway al arrancar (migrate/gunicorn crasheaban en loop). Fix: agregar `InstrumentosCatalogoView` a esa lista de imports. Commit y push separados, deploy confirmado exitoso (gunicorn arriba, sin errores)
- **Nota técnica:** el log de Railway mostró advertencia "models in app(s) 'surveys' have changes not yet reflected in a migration" — viene de agregar 2 choices nuevos ('competencias', 'comercial') a PsychoInstrument.TIPOS. Como es un CharField con choices (no cambia tipo/tamaño de columna), no debería requerir migración real, pero queda pendiente confirmar/generar la migración manual si se decide ser estrictos con esto

### Sidebar — link "Evaluaciones" corregido en todos los templates — COMPLETADO Y DESPLEGADO ✅ (sesión 10, parte 2)
- Antes: "Evaluaciones" apuntaba a `{% url 'candidatos' %}` (duplicado con "Candidatos") en index.html, o a `href="#"` (no hacía nada) en psico_candidatos.html, psico_candidato_detalle.html y psico_instrumentos.html
- Fix aplicado en los 4 templates via content.replace() con marcadores verificados (content.count()==1 antes de escribir):
  - index.html linea 647: ahora `{% url 'instrumentos_catalogo' %}`
  - psico_candidatos.html linea 256: ahora `{% url 'instrumentos_catalogo' %}`
  - psico_candidato_detalle.html linea 329: ahora `{% url 'instrumentos_catalogo' %}`
  - psico_instrumentos.html linea 329: ahora `{% url 'instrumentos_catalogo' %}` + clase `active` movida de "Candidatos" a "Evaluaciones" (es la pagina donde se esta parado)
- Deploy confirmado exitoso en Railway (gunicorn arriba, sin errores nuevos)
- `index_backup_original.html` NO se toco (respaldo viejo sin usar, decision explicita de sesiones previas)
- `landing.html` y `stripe_planes.html` tienen la palabra "Evaluaciones" pero es copy de marketing, no link de sidebar — se descartaron correctamente, no se tocaron

### Instrumentos psicométricos nuevos: Competencias Laborales y Perfil Comercial — CARGADOS Y BUG CRITICO RESUELTO (sesión 10, parte 7)
- Los JSON de 40 reactivos (8 dimensiones x 5) de ambos instrumentos ya se generaron y cargaron a PsychoItem via management commands cargar_competencias y cargar_comercial
- BUG CRITICO encontrado y resuelto: el template psico_test.html renderiza segun instrumento.tipo: disc/zavic usan botones Mas/Menos; cualquier otro tipo (incluye competencias/comercial) usa formato multiple choice que exige que cada opcion tenga los campos letra (A/B/C/D/E) y valor (texto visible) - el JS usa letra como el valor que se guarda y se envia al backend
  - El JSON original usaba texto+valor(numerico 1-5)+dimension SIN letra -> opciones casi vacias, boton Siguiente nunca se habilitaba, test bloqueado en la primera pregunta
  - FIX: opciones reestructuradas a letra+valor(texto visible)+dimension+peso(numero 1-5 para scoring, renombrado de valor)
  - _calcular_scores (TestCompleteView, surveys/psico_views.py) corregido: el frontend envia r.respuesta como la letra seleccionada (string plano) - ahora busca en item.opciones la opcion cuya letra coincide y toma peso+dimension de ahi
  - Los 40+40 reactivos viejos fueron borrados de PsychoItem en produccion y recargados desde cero - confirmado 40 en ambos con formato correcto
  - Deploy confirmado exitoso en Railway
- IMPORTANTE: TestSession de pruebas anteriores a este fix quedaron con referencias a PsychoItem ya borrados/recreados (IDs nuevos). Para volver a probar, generar un link NUEVO desde /psico/instrumentos/, no reusar links viejos

### Bugs preexistentes identificados (root cause encontrada) pero NO resueltos aun
- Zavic: template linea 123 agrupa zavic con la logica de DISC, usando botones Mas/Menos por dimension - conceptualmente incorrecto, Zavic deberia usar logica de distribuir 5 puntos entre 4 opciones (su propio tipo='distribute'), no seleccion binaria de opuestos
- Moss: sus opciones usan campos texto+puntos (sin letra ni valor) - mismo tipo de incompatibilidad que tenian Competencias/Comercial antes del fix de hoy. Requiere agregar letra+valor, renombrar puntos a peso o similar, y verificar que _calcular_scores lea el campo correcto para moss
- Ninguno de los dos se toco esta sesion, quedan listos para atacar cuando Jorge lo indique

## EN PROGRESO / PENDIENTE INMEDIATO

1. Probar en navegador con un candidato REAL (link NUEVO, no reusar uno viejo) que Competencias Laborales y Perfil Comercial ahora si permiten completar el test de principio a fin y generan reporte correcto
2. Decidir si se arregla Zavic y Moss en esta sesion o se deja para otra (root cause ya identificada arriba)
3. Extender ReporteUnificadoView/GenerarPerfilNarrativoView (surveys/psico_views.py) para que interpreten los tipos competencias y comercial en el calculo de scores/narrativa (verificar si ya quedo cubierto con el fix de _calcular_scores o si falta algo mas alla en esas vistas)

## Pendientes menores acumulados (no bloqueantes, de sesiones previas)
1. Mensajes claros de "se actualizara automaticamente" en los 3 documentos de Fase A del Portafolio cuando esten en estado pendiente
2. Boton "Descargar" explicito ademas de "Ver archivo" en evidencias de Fase C
3. Limite de NUMERO de archivos por tipo/workplace en Fase C (hoy solo hay limite de tamano individual de 10MB, no de cantidad)

## Notas tecnicas clave (para no repetir errores ya resueltos)
- **Imports explícitos en urls.py**: nom035/urls.py importa `surveys.views` con wildcard (`from surveys.views import *`) pero `surveys.psico_views` con import explícito por nombre — CUALQUIER vista nueva en psico_views.py debe agregarse manualmente a esa lista de imports en urls.py, o Railway crashea con NameError en el arranque (migrate check falla antes de levantar gunicorn)
- get_chart_data(request) en views.py (~500 lineas): cat=[], domains=[], dimensions=[] deben inicializarse ANTES del if not employees y del loop principal
- Django Response/JsonResponse con status='error' puede devolver HTTP 200 igual — revisar data.status explicitamente en callbacks de AJAX
- EndEvaluation: incrementa evaluation+1, pone paid=False. Bloqueado para workplace.es_demo=True
- userapp.nom035_demo/psico_demo = creditos gratis. Workplace.es_demo=True = si el CENTRO es de datos ficticios. Conceptos relacionados pero independientes
- Sistema de diseño NormaIA: .form-group, .form-label, .form-control, .section-card, .btn/.btn-primary/.btn-outline-primary, var(--bg-base), var(--border), var(--text-primary/secondary), var(--radius-md/lg), var(--shadow-sm)
- Templates psico_*.html son STANDALONE (su propio <html>, sidebar y CSS hardcodeados) — NO extienden index.html, no hay {% include %}
- imports en views.py son wildcard; cargar_datos_demo.py usa import explicito, hay que agregar cada modelo nuevo a la lista manualmente

### BUG RESUELTO — Moss (Supervision y Liderazgo) no mostraba opciones ni avanzaba (sesión 10, parte 8)
Misma causa raiz que Competencias/Comercial: cargar_moss.py usaba opciones con campos `texto`+`puntos`, incompatibles con el template psico_test.html que espera `letra`+`valor` para el formato "multiple choice".

FIX aplicado (mismo patron que Competencias/Comercial):
1. Transformadas las opciones de cargar_moss.py: `{"texto": X, "puntos": Y}` -> `{"letra": "A-D", "valor": X, "peso": Y}`
2. CUIDADO TECNICO: cargar_moss.py (como cargar_zavic.py) usa TABS para indentacion, no espacios. El primer intento de transformacion con python3 heredoc uso espacios para la linea "for s in situaciones:", causando TabError al compilar. Fix: reemplazar explicitamente por tabs (`\t\t`) en vez de espacios al insertar texto nuevo en archivos que usan tabs. LECCION para futuros archivos con tabs: verificar con `cat -A` el estilo de indentacion ANTES de insertar texto nuevo por concatenacion de strings, no asumir espacios.
3. _calcular_scores (dentro de TestCompleteView, linea ~215): bloque moss corregido para leer `letra = r.respuesta` (string plano enviado por el frontend) y buscar en item.opciones la opcion con esa letra, sumando su `peso` al total — antes intentaba `respuesta.get('puntos', 0)` asumiendo que r.respuesta era un diccionario, lo cual hubiera crasheado (AttributeError) si algun candidato hubiera logrado completar el test
4. Confirmado que las otras 3 vistas que manejan moss (TestResultView, GenerarPerfilNarrativoView, ReporteUnificadoView) NO necesitaron cambios porque solo leen el diccionario `scores` ya calculado (ej. scores.get('total', 0)), no las respuestas crudas
5. Los 30 items viejos de Moss fueron borrados y recargados en produccion: "Moss cargado: 30 situaciones creadas." confirmado

### HALLAZGO IMPORTANTE SIN RESOLVER — posible bug identico latente en Raven
Durante la investigacion de Moss se detecto que el bloque `elif tipo == 'raven':` en _calcular_scores tiene el MISMO problema de diseño: usa `respuesta.get('seleccion')` asumiendo que r.respuesta es un diccionario, pero por la arquitectura confirmada de TestCompleteView.post(), para CUALQUIER item tipo 'multiple' (que incluye raven), r.respuesta se guarda como la letra en texto plano, NO como diccionario. Esto significa que si un candidato completara Raven, el calculo de scores probablemente crashearia con AttributeError.
- Jorge no reporto a Raven como roto en las pruebas de esta sesion, posiblemente porque no lo probo de principio a fin (solo problemas visibles al TOMAR el test, no necesariamente llego a completarlo y generar el reporte)
- PENDIENTE: probar Raven end-to-end (completar el test con un candidato real) para confirmar si este bug realmente se manifiesta, y aplicar el mismo tipo de fix si es necesario (leer letra=r.respuesta directo y comparar contra item.respuesta_correcta, ya que Raven no necesita buscar en opciones, solo comparar la letra seleccionada)

## Pendiente inmediato actualizado
1. Probar Moss en navegador con candidato real (link nuevo) para confirmar que ya funciona de principio a fin
2. Arreglar Zavic: causa raiz ya identificada (template linea 123 agrupa zavic incorrectamente con la logica Mas/Menos de DISC, deberia tener su propia logica de distribuir 5 puntos entre 4 opciones)
3. Probar Raven end-to-end para confirmar si tiene el mismo bug latente que tenia Moss (ver hallazgo arriba)
4. Pendiente menor sin resolver: warning de Railway sobre migracion no reflejada (choices nuevos en PsychoInstrument.TIPOS)

### Moss CONFIRMADO FUNCIONANDO end-to-end en produccion ✅ (sesión 10, parte 8, cierre)
Jorge probo con candidato real: cuestionario completo, avanza correctamente entre las 30 preguntas, y el envio final ("Enviar evaluación") se completo con exito. Hubo un error transitorio "Error al enviar: intenta de nuevo" en el primer intento, pero al repetir el envio funciono correctamente — parece haber sido un problema de red/timeout puntual, no relacionado con el fix de codigo (no se detecto traceback de Django en los logs revisados). Si el error "Error al enviar" vuelve a aparecer de forma consistente, revisar logs de Railway en el momento exacto del fallo para descartar causa real en el backend.

## INSTRUMENTOS FUNCIONANDO END-TO-END CONFIRMADO: Competencias Laborales, Perfil Comercial, Moss ✅
## PENDIENTE: Zavic (bug identificado, fix no aplicado) y Raven (posible bug latente identico a Moss, sin confirmar)

### BUG RESUELTO — Zavic no permitia avanzar (usaba logica incorrecta de DISC) ✅ (sesión 10, parte 9, cierre)
CAUSA RAIZ: el template psico_test.html agrupaba Zavic con DISC (`{% if instrumento.tipo == 'disc' or instrumento.tipo == 'zavic' %}`), usando botones binarios "+ Mas" / "- Menos" por dimension. Pero las instrucciones del propio instrumento (visibles al candidato) piden "distribuir 5 puntos entre las 4 opciones" — una mecanica de asignacion de puntos, no de seleccion de opuestos. El backend (_calcular_scores, bloque zavic) YA esperaba el formato correcto (`respuesta.get('distribucion', {})`) desde antes de esta sesion — es decir, Zavic nunca tuvo una interfaz que generara ese formato, probablemente nunca funciono correctamente desde su implementacion original.

FIX aplicado en surveys/templates/psico_test.html (SOLO frontend, backend NO se toco):
1. CSS nuevo: contador circular con botones +/- (`.btn-zavic-mas`, `.btn-zavic-menos`, `.zavic-contador`, `.zavic-total`)
2. HTML: separada la rama `{% if instrumento.tipo == 'disc' %}` de una nueva `{% elif instrumento.tipo == 'zavic' %}` — cada opcion muestra un contador (0-5) con botones +1/-1, y un indicador de "Puntos asignados: X / 5" por grupo de pregunta
3. JS nuevo: funciones `zavicIncrementar(itemId, escala)` / `zavicDecrementar(itemId, escala)` — construyen `respuestas[itemId].distribucion = {escala: puntos}`, bloquean incrementar si la suma ya es 5
4. `grupoCompleto()`: separada la validacion de disc (igual que antes) de una nueva rama zavic que valida `suma === 5` exactamente
5. `enviar()`: separado el payload de disc (`{mas, menos}`, sin cambios) del de zavic (`{distribucion: {...}}`) — coincide exactamente con lo que _calcular_scores ya esperaba, cero cambios de backend necesarios
6. NO fue necesario borrar/recargar reactivos de Zavic en produccion (no se toco cargar_zavic.py, solo la interfaz de captura de respuestas)
7. CONFIRMADO por Jorge: evaluacion Zavic completada exitosamente end-to-end en produccion

## RESUMEN FINAL DE LA SESION — TODOS LOS BUGS DE INSTRUMENTOS RESUELTOS ✅
Los 4 problemas reportados por Jorge al probar los instrumentos en produccion quedaron resueltos y confirmados funcionando end-to-end:
1. Competencias Laborales ✅
2. Perfil Comercial y Servicio al Cliente ✅
3. Zavic ✅
4. Moss ✅

TODOS los instrumentos psicometricos de la plataforma (DISC, Raven, Moss, Zavic, Competencias Laborales, Perfil Comercial) estan ahora operativos para candidatos reales.

## Pendiente inmediato actualizado
1. Probar Raven end-to-end (completar el test con un candidato real) para confirmar si tiene el mismo bug latente que tenia Moss antes del fix (ver hallazgo de sesion anterior: _calcular_scores bloque raven usa `respuesta.get('seleccion')` asumiendo diccionario, pero el formato real guardado es la letra en texto plano — mismo problema que tenia moss). Si se confirma el bug, aplicar mismo tipo de fix (leer letra=r.respuesta directo y comparar contra item.respuesta_correcta)
2. Pendiente menor sin resolver: warning de Railway sobre migracion no reflejada (choices nuevos en PsychoInstrument.TIPOS)

### Raven CONFIRMADO FUNCIONANDO end-to-end en produccion ✅ (sesión 10, parte 10, cierre)
Jorge confirmo: evaluacion completada exitosamente tras el fix.

## SESION 10 CERRADA — TODOS los instrumentos psicometricos operativos y confirmados en produccion ✅
1. DISC — sin cambios, funcionando desde antes
2. Raven — bug de scoring (respuesta como dict vs string) corregido y confirmado ✅
3. Moss — bug de formato de opciones (letra/valor/peso) corregido y confirmado ✅
4. Zavic — bug de interfaz (usaba logica de DISC en vez de distribucion de puntos) corregido y confirmado ✅
5. Competencias Laborales — instrumento nuevo construido de cero, bug de formato corregido, confirmado ✅
6. Perfil Comercial y Servicio al Cliente — instrumento nuevo construido de cero, bug de formato corregido, confirmado ✅

## Pendiente inmediato actualizado (unico pendiente activo)
1. Pendiente menor sin resolver: warning de Railway sobre migracion no reflejada (choices nuevos 'competencias'/'comercial' en PsychoInstrument.TIPOS) — confirmar si requiere migracion manual con python manage.py makemigrations o se puede ignorar de forma segura (es un CharField con choices, no deberia cambiar la columna de BD)

## NUEVOS HALLAZGOS — pruebas continuas de Jorge (sesión 10, parte 11)
Jorge sigue probando la plataforma y encontro 4 pendientes nuevos, sin investigar aun:

1. **BUG: paginacion rota en "Ver resultados"** — URL de ejemplo: https://nom035-production.up.railway.app/workplace_result/19/1/. NOTA IMPORTANTE: esto ya se habia arreglado en la sesion 9 (fix de tooltip condicional en DataTables, documentado arriba). Posible regresion, o un problema distinto de paginacion esta vez. Requiere investigacion desde cero para no asumir que es el mismo bug.

2. **BUG: menu lateral incompleto en "Clima Laboral" y "Mi plan"** — comparado con el resto de las paginas (Dashboard, Portafolio de evidencias, Evaluaciones, Candidatos, Configuracion), el sidebar en estas 2 vistas no muestra todos los links esperados. Recordar: los templates NO usan {% include %} para el sidebar, cada uno lo trae hardcodeado completo — es probable que estos 2 templates especificos tengan una version vieja/incompleta del sidebar sin actualizar cuando se agregaron nuevos links (ej. cuando se agrego "Evaluaciones").

3. **Cambio simple de texto**: en el sidebar, renombrar el link "Mi plan" a "Planes" (cambio cosmetico, bajo riesgo).

4. **Rediseño de la vista Evaluaciones** (catalogo de instrumentos, psico_instrumentos.html): Jorge no esta conforme con el diseño actual. Quiere pedirle a Replit (otra herramienta de IA) un diseño con tarjetas — 4 arriba y 4 abajo, o separadas por tipo de evaluacion, cada tarjeta con nombre e descripcion breve del instrumento. Plan: escribir un prompt de diseño para Replit (mismo patron que se uso con ChatGPT para los reactivos), no implementar el diseño directamente en esta sesion.

Screenshot de referencia adjuntado por Jorge mostrando el sidebar actual completo (Dashboard, Centros de Trabajo, Añadir un Centro, Portafolio de evidencias, Evaluaciones, Candidatos, Mi plan, Configuracion) — este es el sidebar "correcto" contra el cual comparar Clima Laboral y Mi plan.

### Sidebar tambien incompleto en Evaluaciones y Candidatos — CAUSA RAIZ DISTINTA, TAMBIEN RESUELTA (sesión 10, parte 13)
Jorge confirmo que el fix anterior (Clima Laboral, Planes) funciono, pero reporto el MISMO SINTOMA en 2 vistas mas: Evaluaciones (psico_instrumentos.html) y Candidatos (psico_candidatos.html).

CAUSA DISTINTA a la de Clima Laboral/Planes: estos 2 templates son STANDALONE (sidebar hardcodeado propio, no heredan de index.html via {% extends %}). Investigando se encontro que NUNCA tuvieron el link "Clima Laboral" ni el loop de centros de trabajo individuales en su seccion NOM-035 — no es que la variable de contexto faltara (como en Clima Laboral/Planes), sino que el HTML mismo del sidebar copiado nunca incluyo esos elementos, probablemente porque se copio de una version antigua de index.html anterior a que existiera Clima Laboral.

Descubrimiento adicional: los 2 templates usan convenciones CSS DIFERENTES entre si:
- psico_candidatos.html usa `.nav-item-link` / `.nav-section-label` (igual que index.html)
- psico_instrumentos.html usa `.sidebar-link` / `.sidebar-section-label` (nomenclatura distinta)

FIX aplicado:
1. surveys/psico_views.py: agregado `Workplace` al import explicito, y `workplaces: Workplace.objects.filter(user=request.user)` al contexto de CandidateListView y InstrumentosCatalogoView
2. psico_candidatos.html: agregado `{% for item in workplaces %}` (centros individuales bajo NOM-035, usando clases .nav-item-link) + loop de Clima Laboral, replicando estructura de index.html
3. psico_instrumentos.html: mismo fix pero adaptado a sus propias clases .sidebar-link (para mantener consistencia visual con el resto del archivo)
4. LECCION TECNICA: al hacer content.replace() en estos templates, el primer intento en ambos archivos fallo por asserts — causa: habia una linea en blanco entre bloques que no se incluyo en el marcador de busqueda. Verificar SIEMPRE con `cat -A` el bloque completo (incluyendo lineas vacias) antes de armar el marcador de texto para reemplazo, no asumir que sed -n sin cat -A muestra todo con precision

PENDIENTE: confirmar visualmente tras el deploy que Evaluaciones y Candidatos ya muestran sidebar completo.

## Pendiente inmediato actualizado
1. Confirmar visualmente el fix de sidebar en Evaluaciones y Candidatos tras el deploy
2. Rediseno de la vista Evaluaciones (psico_instrumentos.html) con tarjetas — prompt para Replit pendiente de escribir
3. Pendiente menor sin resolver: warning de Railway sobre migracion no reflejada (choices nuevos en PsychoInstrument.TIPOS)
4. Pendiente menor sin resolver: `page=(start/length)+1` en employees_dt usa division float en vez de entera

## Rediseño visual con Replit — en progreso (sesión 10, parte 14)
Jorge decidio usar Replit para rediseñar (SOLO visual, sin tocar funcionalidad) varias vistas clave. Flujo de trabajo establecido:
1. Claude escribe un prompt de diseño para Replit, especificando: ruta exacta del archivo en el repo publico de GitHub, que elementos funcionales NO se deben tocar (ids, v-model, {% url %}, JS, modales), libertad total de creatividad visual dentro de la identidad de marca (color primario #4f46e5, sidebar oscuro #0f172a, tipografia Inter/Plus Jakarta Sans)
2. Jorge pega el prompt en Replit, descarga el archivo resultante a su carpeta de Descargas
3. Claude revisa el archivo completo via view tool antes de integrarlo: verifica balanceo de tags Django ({% if %}/{% endif %}, {% for %}/{% endfor %}, {% block %}/{% endblock %}) y presencia de todos los elementos funcionales criticos (ids, v-model, endpoints)
4. Se hace backup del archivo original (ej. `evidence_backup_pre_replit.html`) antes de sobreescribir
5. Jorge copia el archivo con `cp` desde su carpeta de Descargas al repo, se verifica, se hace commit y push

### Vista 1: Catalogo de Instrumentos (psico_instrumentos.html) — COMPLETADO Y CONFIRMADO ✅
Rediseño con tarjetas: hero con gradiente de marca, contador de instrumentos disponibles, tarjetas con color de acento distinto por tipo de instrumento (disc, raven, moss, zavic, competencias, comercial) + fallback generico, cada tarjeta con icono, tag, tiempo estimado, descripcion y boton "Asignar a candidato". Sidebar (incluye workplaces loop y Clima Laboral que habiamos arreglado antes) y modal de asignacion preservados intactos. Confirmado funcionando en produccion por Jorge via screenshot.

### Vista 2: Portafolio de Evidencias (evidence.html) — COMPLETADO Y CONFIRMADO ✅ (con 1 ajuste menor)
Rediseño: banner de cumplimiento NOM-035 con gradiente, checklist transformado en tarjetas con badge circular de estado (✓ verde/⚠ ambar), borde lateral de color segun estado, pill "Completo"/"Pendiente". Seccion de resultados separada visualmente. TODA la logica Vue.js preservada intacta: `new Vue({...})`, data (workplace, results, portafolio_status), methods (on_workplace_change, get_portafolio_status, get_results), v-model, v-for, v-if, v-select2, ids del modal (modal_evidence, evidence_form, add_evidence, evidence_btn, users, workplace, result_type, image), todos los {% url %} de Django.
- NOTA: el archivo SI usa `{% extends 'index.html' %}` (mi prompt original decia erroneamente que era standalone como los psico_*.html — Replit trabajo correctamente sobre el archivo real del repo, ignorando esa imprecision mia)
- AJUSTE POST-DEPLOY: el selector de centro de trabajo (select2) se veia "plano y feo" segun Jorge — mejorado con mas altura (46px vs 38px), sombra sutil, tipografia mas marcada (font-weight 600), ancho contenido a 420px en vez de 100%. Solo cambio de CSS, cero logica tocada.
- Confirmado funcionando en produccion por Jorge via screenshot.

## PENDIENTE: 2 vistas mas por rediseñar con el mismo flujo
1. Clima Laboral (clima_resultados.html) — prompt aun no escrito, siguiente en la fila
2. Vista de empresa (probablemente workplace_detail.html o similar, la vista de /workplaces/<id>/ que muestra info del centro + tabla de empleados) — prompt aun no escrito

## Pendiente inmediato actualizado
1. Escribir prompt para Replit: Clima Laboral (clima_resultados.html)
2. Escribir prompt para Replit: Vista de empresa (confirmar archivo exacto primero)
3. Pendiente menor sin resolver: warning de Railway sobre migracion no reflejada (choices nuevos en PsychoInstrument.TIPOS)
4. Pendiente menor sin resolver: `page=(start/length)+1` en employees_dt usa division float en vez de entera

### Vista 3: Clima Laboral (clima_resultados.html) — COMPLETADO Y CONFIRMADO ✅ (sesión 10, parte 15)
Rediseño: hero con gradiente oscuro-morado, stats destacados (respuestas recibidas, dimensiones evaluadas), tarjeta de link para compartir con boton copiar, filas de dimension con barra de progreso + score + nivel de riesgo con color, leyenda de criterios de interpretacion (Critico/En riesgo/Adecuado/Favorable).
- BUG DETECTADO Y CORREGIDO ANTES DE INTEGRAR: Replit dejo el numero "8" hardcodeado en la tarjeta de "Dimensiones evaluadas" en vez de usar una variable dinamica. Corregido a `{{ dimensiones|length }}` antes del commit.
- Elementos funcionales preservados: `id="clima-url"`, el `onclick` exacto del boton copiar (`navigator.clipboard.writeText(...)`), variables de contexto `workplace`, `total`, `dimensiones`, `access_url`
- Confirmado funcionando perfecto en produccion por Jorge

## PENDIENTE: 1 vista mas por rediseñar (vista de empresa)
Aun no se ha confirmado el archivo/vista exacta — probablemente sea la vista de detalle del centro de trabajo (/workplaces/<id>/, la que muestra nombre de empresa, direccion, empleados registrados, evaluacion activa, tabla de empleados). Falta identificar el archivo real antes de escribir el prompt.

## RESUMEN COMPLETO DE LA SESION — para retomar en otra cuenta de Claude (8 Jul 2026, sesión 10 completa)

### 1. Instrumentos psicometricos nuevos — COMPLETADOS Y FUNCIONANDO ✅
- Competencias Laborales (40 reactivos, 8 dimensiones) y Perfil Comercial y Servicio al Cliente (40 reactivos, 8 dimensiones) construidos de cero, cargados en produccion, con scoring y perfil narrativo IA funcionando.

### 2. Bugs de instrumentos preexistentes — TODOS RESUELTOS Y CONFIRMADOS ✅
- Moss: opciones sin campo letra/valor correcto — corregido, formato letra/valor/peso
- Zavic: usaba logica de DISC (Mas/Menos) en vez de distribuir 5 puntos — nueva interfaz de contador +/- construida
- Raven: _calcular_scores comparaba respuesta como diccionario cuando era string plano — corregido
- Los 6 instrumentos (DISC, Raven, Moss, Zavic, Competencias, Comercial) confirmados funcionando end-to-end por Jorge

### 3. Bugs de sidebar y navegacion — TODOS RESUELTOS ✅
- Rename "Mi plan" -> "Planes" en 4 templates
- Sidebar incompleto en Clima Laboral y Planes: faltaba variable `workplaces` en contexto de ClimaResultadosView y StripePlansView — agregada
- Sidebar incompleto en Evaluaciones y Candidatos: el HTML nunca tuvo el loop de centros de trabajo ni el link de Clima Laboral (bug distinto, no de contexto sino de HTML faltante) — agregado
- Paginacion rota en tabla "Resultados por empleado" (workplace_results.html): CSS de `.dataTables_paginate` sin `display:flex` — corregido
- Boton "Ver opciones" en alerta de limite de empleados (workplace_detail.html) apuntaba a `/payments` en vez de a Planes — corregido a `{% url 'stripe_planes' %}`

### 4. Rediseño visual con Replit — 5 VISTAS COMPLETADAS ✅
Flujo establecido: Claude escribe prompt de diseño (ruta del archivo en GitHub, elementos funcionales a NO tocar, libertad creativa de diseño dentro de la identidad de marca), Jorge lo pega en Replit, descarga el archivo, Claude lo revisa (balanceo de tags Django, elementos funcionales) antes de integrar, se hace backup del original, se reemplaza, commit, push.
1. Catalogo de Instrumentos (psico_instrumentos.html) ✅
2. Portafolio de Evidencias (evidence.html) ✅ (ver seccion 5 abajo, tuvo un bug largo)
3. Clima Laboral (clima_resultados.html) ✅ — tuvo un bug de "8" hardcodeado en vez de `{{ dimensiones|length }}`, corregido antes de integrar
4. Vista de Empresa (workplace_detail.html) ✅
5. Ver Resultados (workplace_results.html) ✅ — la mas compleja, tuvo un bug critico de fondo invisible (ver LECCION TECNICA abajo)

### LECCION TECNICA CRITICA — Django `{% block %}` anidado dentro de `<style>` del layout base
En `index.html`, el `{% block style %}{% endblock %}` esta colocado DENTRO de la etiqueta `<style>` que el layout abre antes y cierra despues (linea ~591). Esto genera 2 bugs distintos posibles en templates hijos que usan `{% extends 'index.html' %}`:

**Bug A — corrupcion de parseo CSS**: si un template hijo pone `<link rel="stylesheet">` ANTES de su propio `<style>` dentro del `{% block style %}`, el navegador (ya en "modo CSS") trata el `<link>` como texto invalido, busca la primera `{` para "cerrar" esa regla basura — y esa `{` resulta ser la del primer selector CSS real del archivo, absorbiendo y descartando esa primera regla completa. Sintoma: la PRIMERA regla CSS del archivo se pierde silenciosamente (ej. el fondo de un hero card), el resto de reglas funcionan normal.

**Bug B — contenido descartado por Django (el mas grave, encontrado en Portafolio de Evidencias)**: si se mueve el `<link>` a DESPUES de `{% endblock %}` del block style pero ANTES del siguiente `{% block %}` (ej. `{% block dashboard %}`), ese contenido queda FUERA de cualquier bloque reconocido. Django, en templates que usan `{% extends %}`, DESCARTA SILENCIOSAMENTE cualquier contenido que no este dentro de un `{% block %}` que exista en el padre — el `<link>` nunca se renderiza en el HTML final, ni siquiera corrupto, simplemente no existe en la pagina. Esto causo que select2.css nunca cargara en Portafolio de Evidencias, dejando el `<select>` nativo sin ocultar correctamente (bug del "doble selector").

**FIX CORRECTO Y DEFINITIVO**: cualquier `<link rel="stylesheet">` que un template hijo necesite cargar DEBE ir DENTRO de un `{% block %}` que exista en el padre y que SI se renderice — la opcion mas simple es ponerlo como primera linea dentro de `{% block dashboard %}` (los navegadores procesan `<link>` en `<body>` sin problema). NUNCA dejarlo suelto entre bloques, y NUNCA antes del `<style>` propio dentro de `{% block style %}`.

**Nota sobre workplace_detail.html y workplace_results.html**: estas 2 vistas tenian el mismo patron de `<link>` fuera de bloques (Bug B) pero Jorge no reporto problemas visibles graves ahi — posiblemente porque datatables.min.css/select2.css no son tan criticos para esas paginas especificas, o el problema esta presente pero es menos notorio. PENDIENTE revisar si conviene aplicar el mismo fix (mover el link dentro de block dashboard) preventivamente en esas 2 vistas tambien.

### 5. Portafolio de Evidencias — saga completa del bug del doble selector (RESUELTO, pendiente de confirmacion final)
Jorge reporto que el selector "Centro de trabajo" se veia como si hubiera 2 selectores mezclados (uno bonito arriba, uno feo/nativo abajo que se desplegaba al hacer clic). Investigacion larga:
1. Primero se sospecho que era el mismo bug de Ver Resultados (Bug A) — se aplico fix de reordenar el link, pero el bug persistio
2. Jorge sugirio que podria ser un bug heredado de antes de cualquier cambio — se probo revirtiendo a la version 100% original (pre-Replit) y el bug SEGUIA presente, confirmando que es preexistente, no causado por el rediseño
3. Se encontro la causa raiz real: Bug B (arriba) — el link estaba fuera de cualquier block, Django lo descartaba, select2.css nunca cargaba
4. FIX APLICADO: link movido a dentro de `{% block dashboard %}`. Tambien se restauro la mejora visual del label con icono (`ws-label`) que se habia perdido durante las pruebas de diagnostico
5. **INCIDENTE OPERATIVO**: durante el diagnostico, un commit de "restaurar version mejorada" se dio como instruccion pero Jorge no lo ejecuto (solo corrio el comando de investigacion siguiente), causando confusion sobre que version estaba realmente en produccion. LECCION: verificar siempre con `git log --oneline -5` y `git status` cuando haya duda de que se ejecuto, no asumir.
6. Estado actual: el fix definitivo (commit mas reciente) fue pusheado. **PENDIENTE: Jorge aun no ha confirmado visualmente en produccion tras este ultimo push si el selector ya se ve correcto sin duplicados.**

## PENDIENTES ACTIVOS PARA LA OTRA CUENTA
1. **INMEDIATO**: confirmar visualmente que el fix definitivo del selector de Portafolio de Evidencias funciono (hard refresh en /evidence/, verificar que no hay selector duplicado y que se ve el label con icono azul)
2. Revisar si workplace_detail.html y workplace_results.html tienen el mismo Bug B (link fuera de bloques) y si vale la pena aplicar el mismo fix preventivamente aunque no den problemas visibles hoy
3. Pendiente menor sin resolver: warning de Railway sobre migracion no reflejada (choices nuevos en PsychoInstrument.TIPOS)
4. Pendiente menor sin resolver: `page=(start/length)+1` en employees_dt usa division float en vez de entera
5. Recordatorio permanente: NUNCA incluir el caracter `!` en mensajes de commit (error "event not found" en Git Bash Windows)
6. Recordatorio permanente: cuando haya dudas sobre si un comando se ejecuto, usar `git log --oneline -5` y `git status` para confirmar antes de asumir

## ARCHIVOS DE BACKUP CREADOS ESTA SESION (por si se necesita revertir algo)
- psico_instrumentos_backup_pre_replit.html
- evidence_backup_pre_replit.html
- evidence_con_bug_doble_selector.html (snapshot intermedio, ya no necesario pero se dejo por si acaso)
- clima_resultados_backup_pre_replit.html
- workplace_detail_backup_pre_replit.html
- workplace_results_backup_pre_replit.html
- workplace_results_backup_pre_replit_v2.html

### Portafolio de Evidencias — SELECTOR DUPLICADO CONFIRMADO RESUELTO ✅ (cierre definitivo)
Jorge confirmo visualmente en produccion: el selector "Centro de trabajo" ya se ve correcto, sin duplicados, con el label e icono aplicados. La saga completa (Bug B: link fuera de bloques Django, descartado silenciosamente) queda cerrada.

## SESION 10 CERRADA POR COMPLETO — TODO CONFIRMADO EN PRODUCCION ✅
Ningun pendiente activo de bugs visuales o funcionales conocidos. Los unicos pendientes restantes son menores (migracion Railway, division float en employees_dt) y la revision preventiva opcional de workplace_detail.html/workplace_results.html por el mismo patron de Bug B (no urgente, no hay sintomas reportados ahi).

# ============================================================
# LOTE A (IDOR NOM-035) — INVESTIGACION EN CURSO (sesion 12)
# Fecha: 14 Jul 2026
# ============================================================

## N35-SEC-001 CONFIRMADO EN CODIGO REAL
Archivo: surveys/views.py, clase WorkplaceResultView (linea 636), metodo get() linea 639.
Linea exacta del bug: linea 644 -> `wk=Workplace.objects.filter(id=kwargs['workplace_id']).last()` -- NO filtra por user=request.user.
URLs afectadas (nom035/urls.py lineas 77-78): `workplace_result` y `workplace_result2`.

**HALLAZGO IMPORTANTE:** el control de ownership correcto SI fue escrito en su momento pero quedo COMENTADO deliberadamente (lineas 657-658):
Esto no es una omision de diseno, es una regresion -- alguien desactivo la proteccion (probablemente durante debugging) y nunca se reactivo. Referencia para el fix: reactivar esta logica (ajustando el nombre del related_name si `workplaces` no es el correcto, verificar en el modelo).

## HALLAZGO NUEVO — NO ESTABA EN LOS 22 DE LA AUDITORIA ORIGINAL

### Llave AES hardcodeada (CWE-798)
surveys/views.py lineas 667-676, funciones encript()/decript():
key="test1234test1234"
Se usa para generar/validar codigos de verificacion de email y recuperacion de contrasena (formato user.id<->timestamp<->record_create_timestamp cifrado con AES-CBC). Cualquiera con acceso al codigo fuente puede forjar codigos validos para cualquier usuario.

### CRITICO — Posible bypass completo de recuperacion de contrasena (severidad: CRITICA, mayor que N35-SEC-001)
Archivo: surveys/views.py, clase PasswordRecover (linea 729, endpoint PUBLICO, sin LoginRequiredMixin).
Metodo post() tiene 2 bloques:
1. Primer bloque (if email != ""): solicita el link de recuperacion, genera codigo cifrado, envia por correo. Este bloque esta bien.
2. Segundo bloque (elif "new_password1" in request.POST...): cambia la contrasena real via SetPasswordForm(user, request.POST), usando email = request.POST.get('user-email', '') tomado DIRECTO del POST -- sin verificar en ningun momento que el codigo de recuperacion (code/iv) haya sido validado. El flag valid_code que se calcula en el GET solo controla que se muestra en el template, no viaja como token de sesion ni se revalida en este POST.

Implicacion: si esto se confirma (pendiente de verificar el template password_recover.html para descartar que el codigo viaje oculto en el form y se revise en otro punto no visto aun), cualquiera podria hacer POST directo a este endpoint con user-email=<email de la victima> + nueva contrasena, y tomar control total de cualquier cuenta SIN necesitar el codigo de verificacion ni acceso al correo de la victima.

IMPORTANTE - aclaracion de Jorge: el sistema hoy no tiene SMTP configurado ni dominio publico real (sigue en desarrollo). PERO este bug NO depende de que SMTP funcione -- el endpoint vulnerable no necesita que el correo se haya enviado, se puede explotar posteando directo a la URL sin pasar nunca por el flujo de correo. Es decir, es explotable HOY MISMO si alguien tiene acceso a la URL del ambiente de staging/produccion actual, independientemente del estado de SMTP.

DECISION DE JORGE: no corregir ahora mismo (no bloquea el trabajo actual del Lote A), pero se registra como PENDIENTE BLOQUEANTE ANTES DE SALIR A PRODUCCION REAL CON DOMINIO Y CLIENTES, sin importar si SMTP esta configurado o no para ese momento.

## PENDIENTE INMEDIATO DE INVESTIGACION (antes de escribir la especificacion de correccion)
1. Verificar surveys/templates/password_recover.html: grep -n "code\|iv\|token" surveys/templates/password_recover.html -- confirmar si el codigo/iv viaja oculto en el form y se revisa en otro punto de la vista no visto aun, o si el hallazgo de bypass de contrasena queda confirmado al 100%
2. Confirmar el related_name correcto en el modelo Workplace para reactivar el ownership check comentado (verificar si es request.user.workplaces o algun otro nombre)
3. Ubicar TODOS los demas usos de .filter(id=...) sin user= en surveys/views.py (patron sistemico, no exclusivo de WorkplaceResultView) -- probablemente EmployeeList, WorkplaceList, y otras vistas mencionadas en el roadmap (get_results, get_chart_data, employees_dt)
4. Confirmar alcance completo del IDOR antes de escribir la especificacion final del Lote A (tal como establecio el plan: "antes de ampliar la bateria, conviene identificar el alcance de la vulnerabilidad en modo lectura")

## HALLAZGOS NUEVOS A AGREGAR A LA MATRIZ FORMAL (fuera de los 22 originales)
- Llave AES hardcodeada en surveys/views.py (CWE-798) - severidad ALTA
- Posible bypass total de autenticacion via PasswordRecover sin verificacion de codigo - severidad CRITICA, pendiente de confirmar con el template antes de darlo por cerrado, pero con evidencia fuerte de codigo Python ya revisada

## ACTUALIZACION: PasswordRecover bypass — CONFIRMADO AL 100% (ya no es hipotesis)
Se verifico surveys/templates/password_recover.html lineas 90-113: el formulario de "cambiar contrasena" (mostrado solo cuando valid_code==True, proteccion de frontend unicamente) envia UNICAMENTE user-email (hidden), new_password1, new_password2 -- NO existe ningun campo con el codigo/iv de verificacion. Confirmado en el Python (surveys/views.py, PasswordRecover.post(), bloque elif "new_password1" in request.POST) que jamas se revalida el codigo en este punto.

CONFIRMADO EXPLOTABLE: un POST directo a la URL de PasswordRecover con user-email=<victima> + new_password1/new_password2 cambia la contrasena de cualquier cuenta sin necesitar codigo de verificacion, sin acceso al correo de la victima, y sin importar si SMTP esta configurado. No requiere autenticacion previa (vista publica).

Sigue siendo PENDIENTE BLOQUEANTE ANTES DE PRODUCCION REAL (decision de Jorge), no se corrige en esta sesion, pero el hallazgo ya no tiene ninguna duda pendiente de verificacion -- es hallazgo confirmado, severidad CRITICA, listo para entrar al roadmap de remediacion (Fase 0) en cuanto se decida atacarlo.

## MAPEO COMPLETO DEL ALCANCE DEL IDOR (N35-SEC-001 y mas alla) — sesion 12, cont.

Se completo el mapeo de TODAS las vistas relacionadas con el patron IDOR mencionado en el roadmap. Hallazgo mucho mas amplio y grave de lo reportado originalmente en la auditoria de 22 hallazgos.

### Vistas CBV afectadas (surveys/views.py)
- WorkplaceResultView (linea 636): ownership check COMENTADO (lineas 657-658). Requiere login (LoginRequiredMixin) pero cualquier usuario autenticado accede a cualquier workplace. Related_name correcto confirmado: request.user.workplaces
- WorkplaceDetailView (linea 607): ownership check SI ACTIVO (linea 627) -- esta vista es el patron de referencia correcto, sirve de plantilla para el fix
- EmployeeList (DRF, linea 2062): si se pasa workplace_id, no valida dueno (linea 2069). MAS GRAVE: si NO se pasa workplace_id, devuelve Employee.objects.all() (linea 2071) -- CUALQUIER usuario autenticado obtiene la lista COMPLETA de empleados de TODAS las empresas de la plataforma, no solo cruzando una cuenta especifica
- WorkplaceList (DRF, linea 2005): esta SI filtra correctamente por user_id=self.request.user.id (linea 2010) -- control efectivo, no tocar

### Vistas function-based SIN NINGUNA PROTECCION DE LOGIN (mas grave que N35-SEC-001 original)
Confirmado que NINGUNA de estas 5 funciones tiene @login_required ni proteccion equivalente, Y sus URLs en nom035/urls.py son path() planos sin middleware de proteccion:
- employees_dt (linea 1154, urls.py linea 83-84) -- recibe workplace_id de la URL, sin validar dueno, SIN LOGIN REQUERIDO
- get_results (linea 1244, urls.py linea 88) -- recibe workplace_id de GET, sin validar dueno, SIN LOGIN REQUERIDO
- get_workplaces (linea 1252, urls.py linea 90) -- recibe user_id DIRECTO del GET (linea 1253), permite ENUMERAR los centros de trabajo de CUALQUIER usuario con solo cambiar el user_id, SIN LOGIN REQUERIDO
- get_departments (linea 1259, urls.py linea 81) -- recibe workplace_id de GET, sin validar dueno, SIN LOGIN REQUERIDO
- get_chart_data (linea 1329, urls.py linea 87) -- recibe workplace_id de GET, sin validar dueno, SIN LOGIN REQUERIDO. Esta es la vista que calcula todos los niveles de riesgo psicosocial (dimensionA, etc.) -- expone el detalle completo de riesgo NOM-035 de cualquier empresa

CONCLUSION DEL MAPEO: el problema es sistemico y MAS GRAVE que N35-SEC-001 tal como se reporto originalmente. No es solo "un usuario autenticado puede ver datos de otro usuario" -- son 5 endpoints COMPLETAMENTE PUBLICOS (sin necesidad de cuenta ni login) que exponen: lista completa de empleados de toda la plataforma (sin filtro), datos de riesgo psicosocial NOM-035 completos por empresa, y permiten enumerar que centros de trabajo tiene cualquier usuario. Se recomienda elevar la severidad reportada y ampliar el hallazgo original en la matriz formal de la auditoria.

### Patron de referencia para el fix (ya existe en el codigo, usar como plantilla)
WorkplaceDetailView (linea 607-627) tiene el patron correcto:
if not request.user.workplaces.filter(id=kwargs['workplace_id']).exists():
        return HttpResponseRedirect(reverse_lazy('workplaces'))

Para las vistas function-based (que no son parte de una clase con LoginRequiredMixin), el fix debe: (1) agregar @login_required como decorador, (2) agregar el filtro de ownership equivalente (Workplace.objects.filter(id=workplace_id, user=request.user) en vez de solo id=workplace_id) antes de usar el dato.

## SIGUIENTE PASO
Con el alcance completo ya mapeado, el siguiente paso es escribir la especificacion de correccion del Lote A completa (todas las vistas listadas arriba), para que Codex la implemente. Se debe seguir el patron: no mezclar en el mismo lote autorizacion con otros temas (llave AES, PasswordRecover, archivos de /media/, etc. van en lotes separados segun el plan original).

# ============================================================
# LOTE A (IDOR NOM-035) — IMPLEMENTADO Y VALIDADO EN STAGING (sesion 13)
# Fecha: 15 Jul 2026
# ============================================================

## RESULTADO: LOTE A COMPLETAMENTE VALIDADO EN STAGING

Rama: fix/lote-a-idor-nom035 (a partir de auditoria-local), implementada por Codex siguiendo la especificacion LOTE_A_especificacion_IDOR.md.

### Cambios implementados (surveys/views.py + nom035/settings.py)
1. WorkplaceResultView: ownership check descomentado (lineas 657-658)
2. EmployeeList.get_queryset(): ambas ramas (con/sin workplace_id) ahora filtran por workplace__user=self.request.user; eliminado el Employee.objects.all() sin filtro
3. employees_dt: agregado @login_required + validacion de ownership
4. get_results: agregado @login_required + validacion de ownership
5. get_workplaces: eliminada dependencia de user_id externo, ahora usa request.user.id directo; quitada linea de debug p_.error(data)
6. get_departments: agregado @login_required + validacion de ownership
7. get_chart_data: agregado @login_required + validacion de ownership, sin tocar la inicializacion de cat/domains/dimensions
8. AGREGADO (no estaba en la spec original, encontrado durante pruebas): LOGIN_URL = 'login' en nom035/settings.py -- sin esto, @login_required redirigia al default de Django /accounts/login/, que no existe en este proyecto (causaba 404 tras la redireccion). Ahora redirige correctamente a /login/ (name="login" en urls.py)

### Validacion completa en ambiente de staging (con 2 cuentas sinteticas)
Se crearon 2 usuarios de prueba en staging (pruebaA@test.com / pruebaB@test.com, password Prueba2026!), cada uno con 1 Workplace y 1 Employee sintetico. Se confirmaron las 7 vistas corregidas + comportamiento sin sesion (redirige a login, HTTP 302), todas con resultado correcto. Ningun caso de exposicion cruzada detectado tras el fix.

### Commits en la rama fix/lote-a-idor-nom035
1. "Fix IDOR: ownership en WorkplaceResultView, EmployeeList, employees_dt, get_results, get_workplaces, get_departments, get_chart_data"
2. "Fix IDOR Lote A: agregar LOGIN_URL para que @login_required redirija correctamente"

## HALLAZGOS NUEVOS ENCONTRADOS DURANTE EL PROCESO (fuera de los 22 originales, para agregar a la matriz)

1. Llave AES hardcodeada en encript()/decript() (surveys/views.py ~667-676): key="test1234test1234" -- severidad ALTA, usada para codigos de verificacion de email y recuperacion de contrasena
2. CRITICO CONFIRMADO -- bypass total de PasswordRecover: el endpoint publico que cambia la contrasena (surveys/views.py, clase PasswordRecover, bloque elif "new_password1" in request.POST) nunca revalida el codigo de verificacion -- confirmado 100% contra el template (password_recover.html no incluye campo hidden de codigo/iv). Explotable HOY MISMO independientemente de si SMTP esta configurado. PENDIENTE BLOQUEANTE ANTES DE PRODUCCION REAL (decision de Jorge, no corregido en esta sesion)
3. Secret key de reCAPTCHA hardcodeada (surveys/views.py linea ~1873): secret_key="6Le3XCEtAAAAAFDF0__aZfnj9DQjwe6lkzdylREY" -- mismo patron CWE-798 que la llave AES. Encontrado al intentar registrar cuentas de prueba en staging (el site key tambien esta hardcodeado en auth-register.html, sin usar variables de entorno)
4. CSRF_TRUSTED_ORIGINS y CORS_ALLOWED_ORIGINS hardcodeados en nom035/settings.py (no usan variable de entorno, a diferencia de ALLOWED_HOSTS que si la usa) -- inconsistencia de patron, mismo tipo de deuda tecnica ya documentada. CORS_ALLOWED_ORIGINS ademas tiene un dominio placeholder sin usar ("https://tu-frontend.com") que deberia limpiarse
5. Procfile confirmado una vez mas (DEP-002): no incluye cargar_competencias ni cargar_comercial en el arranque automatico

## PROCEDIMIENTO OPERATIVO CONSOLIDADO (para repetir en lotes futuros)
1. Crear rama nueva desde auditoria-local: git checkout auditoria-local && git pull && git checkout -b fix/lote-X
2. Escribir especificacion de correccion como archivo .md, con seccion de instrucciones operativas al inicio (repo, rama, venv, que NO hacer)
3. Pasarsela a Codex con instruccion EXPLICITA de "implementa la especificacion completa" (Codex no asume la accion solo con recibir el archivo)
4. Revisar git diff (git status + git diff, usar git --no-pager diff para evitar que el pager corte la salida)
5. Cambiar el Source/Branch del servicio de staging en Railway a la rama del lote (Settings -> Source -> seleccionar rama)
6. Si hace falta correr comandos directos contra la DB de staging (crear superusuario, datos de prueba, etc.): reactivar TCP Proxy en Postgres de staging (Settings -> Networking -> "+ New"), ESPERAR 1-2 MINUTOS a que propague (los intentos inmediatos fallan con "server closed the connection unexpectedly"), usar DATABASE_URL sobreescrita en el comando (nunca railway run, que usa el host interno no resoluble desde la maquina local). ELIMINAR el proxy despues de cada uso
7. Variables de entorno especificas de staging que pueden requerir ajuste temporal para pruebas: ALLOWED_HOSTS (agregar dominio de staging), CSRF_TRUSTED_ORIGINS (hardcodeado en settings.py, requiere cambio de codigo temporal sin commit final, o commit temporal a revertir)
8. Para acelerar creacion de usuarios/datos de prueba: pasarle a Codex el comando completo con DATABASE_URL ya armada, evitando ida y vuelta -- Codex puede ejecutar python manage.py shell con scripts de creacion de datos directamente
9. Una vez validado en staging, hacer merge de la rama del lote a auditoria-local, y decidir si se aplica a produccion real

## PENDIENTE INMEDIATO
1. Confirmar con Jorge si se hace merge de fix/lote-a-idor-nom035 a auditoria-local ahora, o se espera a acumular mas lotes
2. Revertir el Source del servicio de staging en Railway de vuelta a auditoria-local (o a la rama que se decida) despues del merge
3. Definir el siguiente lote a atacar: llave AES + secret key de reCAPTCHA hardcodeadas (mismo patron CWE-798, podrian ir juntas en un lote), o el bypass critico de PasswordRecover (mas grave pero Jorge decidio dejarlo para antes de produccion real, no ahora)
4. Seguir pendiente: EVI-SEC-001 (archivos /media/ sin autenticacion), aun no investigado en codigo real

# ============================================================
# LOTE C (EVI-SEC-001 — archivos /media/ sin autenticacion) — INVESTIGACION (sesion 14)
# Fecha: 15 Jul 2026
# ============================================================

## MAPEO COMPLETO DEL PROBLEMA

### Causa raiz confirmada
nom035/urls.py linea 128: urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) -- sirve TODO el contenido de MEDIA_ROOT (carpeta media/) directo del disco, sin ninguna vista intermedia, sin autenticacion, sin validacion de ownership. Cualquiera con la URL exacta (o que adivine la ruta) descarga el archivo.

### 3 campos de FileField que se sirven via /media/ sin proteccion (surveys/models.py)
1. Linea 45, Userapp: image (logo de empresa) -- upload_to=user_directory_path -> ruta logos/<user_id>/<filename>
2. Linea 81, ResultFiles (o modelo similar): image (archivo de resultados/evidencias) -- upload_to=result_directory_path -> ruta results/<workplace_id>/<evaluation>/<filename>
3. Linea 1040, EvidenciaFaseC: archivo (evidencias NOM-035 Fase C: canalizaciones de trauma, examenes medicos, medidas de control, difusion) -- upload_to='evidencias_fase_c/%Y/%m/' -- EL MAS SENSIBLE, contiene documentos de canalizacion de trauma severo y examenes medicos/psicologicos

### AGRAVANTE: las rutas usan IDs secuenciales predecibles (surveys/models.py lineas 15-18)
def user_directory_path(instance, filename):
        return 'logos/{0}/{1}'.format(instance.user.id, filename)
def result_directory_path(instance, filename):
        return 'results/{0}/{1}/{2}'.format(instance.workplace.id,instance.evaluation,filename)

Como user_id/workplace_id son autoincrementales desde 1, es trivial ITERAR secuencialmente (/media/results/1/1/..., /media/results/2/1/..., etc.) sin necesitar conocer ningun nombre de archivo real -- ampliacion del alcance de EVI-SEC-001 mas alla de lo reportado originalmente (que asumia "URL conocida", aqui ademas se puede enumerar sin conocerla).

## HALLAZGO NUEVO — bug adicional en el patron de "archivos protegidos" ya existente

El proyecto SI tiene un patron de archivos protegidos separado (PROTECTED_MEDIA_ROOT, carpeta files/ fuera de media/), con 2 vistas custom:
- download_file (surveys/views.py ~linea 60, URL files/tmp/<int:user_id>/<str:file_name>): CORRECTO, valida request.user.id != user_id cuando no hay token, bloquea con Http404
- download_file2 (surveys/views.py ~linea 85, URL files/charts/<int:workplace_id>/<str:evaluation>/<str:file_name>): BUG -- el bloque if "_-_Token " in file_name: NO TIENE rama else que valide ownership cuando NO hay token en el nombre de archivo. Si se accede sin token, la funcion continua SIN VALIDAR QUIEN ES EL USUARIO -- descarga directa del PDF de resultados generales de CUALQUIER empresa conociendo workplace_id/evaluation/file_name, sin sesion siquiera necesariamente (dependiendo si la vista tiene @login_required, verificar).

Este bug es de la MISMA FAMILIA que EVI-SEC-001 pero en el sistema de archivos "protegidos", no en /media/ -- se agrega al mismo lote por ser el mismo tipo de correccion (servir archivos con validacion de ownership).

## PENDIENTE ANTES DE ESCRIBIR LA ESPECIFICACION DEL LOTE C
1. Confirmar si download_file y download_file2 tienen @login_required o algun control de autenticacion a nivel de vista (ademas del check interno de ownership)
2. Decidir la estrategia de fix para /media/: la solucion robusta es reemplazar static() con vistas custom que validen ownership antes de servir cada tipo de archivo (siguiendo el patron ya usado en download_file), pero esto es un cambio de arquitectura mayor (cambiar como se generan los templates que referencian estas URLs, no solo el backend). Evaluar alternativa mas simple: mover estos 3 campos especificos a PROTECTED_MEDIA_ROOT y crear vistas de descarga dedicadas para cada uno, en vez de tocar el mecanismo general de /media/ (que podria tener otros usos no sensibles, ej. staticfiles del admin)
3. Confirmar que ningun otro campo/modelo use /media/ para contenido sensible que no hayamos mapeado (revisar todos los FileField/ImageField del proyecto completo, no solo surveys/models.py)

# ============================================================
# LOTE C1 (download_file2) — IMPLEMENTADO Y VALIDADO (sesion 14, cont.)
# Fecha: 15 Jul 2026
# ============================================================

## RESULTADO: LOTE C1 COMPLETO

Rama: fix/lote-c1-download-file2 (a partir de auditoria-local con Lote A ya incluido). Fusionada a auditoria-local.

### Cambios implementados en download_file2 (surveys/views.py)
1. Agregada la rama else faltante (cuando NO hay token en file_name): valida request.user.is_authenticated y Workplace.objects.filter(id=workplace_id, user=request.user).exists(), lanza Http404 si falla cualquiera de las dos
2. BUG PREEXISTENTE encontrado y corregido de paso (no relacionado con seguridad): habia un from django.http import HttpResponse LOCAL dentro de la funcion (en el bloque de "modo demo"), que hacia que Python tratara HttpResponse como variable local a TODA la funcion -- esto causaba UnboundLocalError en el flujo de descarga EXITOSA (cuando el usuario si es dueno), es decir, esta funcion probablemente nunca funciono correctamente para descargas legitimas. Se elimino el import local redundante (HttpResponse ya estaba importado globalmente al inicio del archivo)

### Validacion (con RequestFactory, sin necesitar contenedor de Railway)
Se uso django.test.RequestFactory para simular 3 peticiones directas a la funcion (con archivo dummy creado en PROTECTED_MEDIA_ROOT/charts/<workplace_id>/<evaluation>/ via DATABASE_URL sobreescrita + TCP proxy temporal):
- Usuario A (propietario) -> PASS, HTTP 200 con el PDF
- Usuario B (no propietario) -> PASS, Http404
- Usuario anonimo -> PASS, Http404

### Commits en fix/lote-c1-download-file2
1. "Fix: agregar validacion de ownership faltante en download_file2 (rama sin token)"
2. "Fix: eliminar import local redundante de HttpResponse en download_file2 (causaba UnboundLocalError en descargas exitosas)"

## TECNICA NUEVA DE VALIDACION (util para futuros lotes que involucren archivos)
Cuando el fix requiere probar contra archivos en el filesystem del contenedor (PROTECTED_MEDIA_ROOT, MEDIA_ROOT), no hace falta desplegar y navegar manualmente -- se puede usar django.test.RequestFactory en un script temporal corrido localmente (con DATABASE_URL apuntando al proxy de staging), crear el archivo dummy directo en el filesystem LOCAL (ya que RequestFactory ejecuta la vista en el proceso local, no en el contenedor remoto), simular las peticiones con distintos request.user, y borrar todo al terminar. Mas rapido que desplegar y probar por navegador para validar solo la logica de autorizacion de una vista.

## SIGUIENTE PASO
Continuar con Lote C2: proteger los 3 campos de FileField que se sirven sin autenticacion via /media/ (logos de empresa, resultados/evidencias, EvidenciaFaseC). Requiere: crear vistas de descarga protegidas + actualizar templates que hoy enlazan directo a /media/... . Cambio de arquitectura mas grande que C1, pendiente de escribir la especificacion.

# ============================================================
# LOTE C2 (EVI-SEC-001 — archivos /media/) — IMPLEMENTADO Y VALIDADO (sesion 14, cont.)
# Fecha: 15 Jul 2026
# ============================================================

## RESULTADO: LOTE C2 COMPLETO Y VALIDADO EN STAGING

Rama: fix/lote-c2-media-protegido (a partir de auditoria-local, incluye Lote A + C1).

### Cambios implementados
1. surveys/models.py: agregado protected_storage = FileSystemStorage(location=settings.PROTECTED_MEDIA_ROOT). Los 3 campos afectados (Userapp.image, ResultFiles.image, EvidenciaFaseC.archivo) ahora usan storage=protected_storage -- las funciones user_directory_path/result_directory_path NO cambiaron (siguen devolviendo rutas relativas, el storage custom es quien las resuelve fuera de MEDIA_ROOT)
2. CONFIRMADO EXPERIMENTALMENTE (por Codex, antes de implementar): en Django 3.2.25 upload_to con ruta absoluta NO funciona (lanza SuspiciousFileOperation) -- FileSystemStorage personalizado es la unica via correcta, confirmado antes de tocar codigo real
3. Migracion manual 0037_protected_file_storage.py: AlterField en los 3 campos, solo cambia storage, dependencia correcta a 0036
4. 3 vistas nuevas en surveys/views.py: download_logo, download_result_image, download_evidencia_fase_c -- las 3 con @login_required + validacion de ownership (Workplace/EvidenciaFaseC filtrados por request.user), usando FileResponse (no HttpResponse con content_type invalido -- ver leccion abajo)
5. 3 rutas nuevas en nom035/urls.py: /descargar/logo/, /descargar/resultado/<workplace_id>/<result_id>/, /descargar/evidencia/<evidencia_id>/
6. Templates actualizados (edit_profile.html x2, index.html, evidencia_fase_c_form.html) para usar {% url %} de las nuevas vistas en vez de /media/... directo
7. get_results (views.py) actualizado: el JSON ahora devuelve reverse('download_result_image', ...) en vez de item.image.url

### LECCION TECNICA: bug de content_type invalido encontrado durante implementacion
Primera version de las 3 vistas nuevas uso HttpResponse(fh.read(), content_type="image/*") -- "image/*" NO es un content-type valido (los navegadores esperan algo especifico como image/jpeg). Corregido reemplazando por FileResponse(open(path, 'rb')), que detecta el tipo correctamente y es ademas mas eficiente que leer todo el archivo con .read(). Patron a preferir en futuras vistas de descarga de archivos.

### Validacion en staging
- Logo: subido por Cuenta A, se muestra correctamente via /descargar/logo/. Confirmado que la ruta VIEJA /media/logos/1/logo.jpg ahora da 404 (el archivo ya NO esta en MEDIA_ROOT)
- EvidenciaFaseC: Cuenta A subio evidencia, la vio correctamente. Cuenta B intento /descargar/evidencia/<id>/ de la evidencia de A -> BLOQUEADO (no pudo verla). Fix de seguridad CONFIRMADO funcionando

### Ajuste temporal para pruebas (mismo patron que en lotes anteriores)
CSRF_TRUSTED_ORIGINS necesito agregar temporalmente el dominio de staging (no depende de variable de entorno, hardcodeado en settings.py) -- se hizo como commit temporal en esta rama, DEBE REVERTIRSE antes de mergear a auditoria-local (recordatorio explicito, ya paso una vez que se olvido en un lote anterior -- Lote A tambien tuvo este mismo ajuste temporal y si se revirtio correctamente)

## HALLAZGO NUEVO DE ARQUITECTURA (importante, no es bug de codigo sino de infraestructura Railway)

El servicio de staging (y probablemente produccion tambien) NO tiene ningun Volume persistente asignado. Confirmado revisando Settings del servicio -- no existe seccion de Volumes configurada. Esto significa:
- Cualquier archivo guardado en MEDIA_ROOT o PROTECTED_MEDIA_ROOT (disco local del contenedor) SE PIERDE en cada redeploy
- Esto aplica a TODOS los archivos subidos por usuarios: logos, evidencias NOM-035, resultados -- no solo los que tocamos en el Lote C2
- Se confirmo en vivo durante esta sesion: un logo/evidencia subidos antes de un redeploy (disparado por el commit temporal de CSRF) ya no estaban disponibles despues del redeploy

Implicacion para produccion real: antes de operar con clientes reales, el proyecto DEBE resolver esto -- ya sea con un Volume persistente de Railway, o (mejor practica a largo plazo) migrando el almacenamiento de archivos a un servicio tipo S3/object storage, que ademas resolveria de forma mas robusta el problema de servir archivos protegidos (URLs firmadas con expiracion, en vez de vistas Django leyendo del disco local).

PENDIENTE: agregar este hallazgo a la matriz formal de la auditoria -- no estaba en los 22 originales ni en los encontrados en sesiones anteriores. Severidad: ALTA para produccion (perdida de datos), aunque no es una vulnerabilidad de seguridad per se.

## EVENTO OBSERVADO SIN CONFIRMAR CAUSA RAIZ (vigilar, no bloqueante)
Durante las pruebas de este lote, una subida de archivo tardo varios minutos y mostro "upstream error" antes de eventualmente completarse exitosamente. Se investigo con Codex:
- Descartado: creacion de carpetas faltantes en PROTECTED_MEDIA_ROOT (Django 3.2 las crea automaticamente via os.makedirs en FileSystemStorage._save(), sin reintentos por esta causa)
- Descartado: "Serverless" (scale to zero) en Railway -- confirmado DESACTIVADO en el servicio de staging
- Hipotesis mas probable, sin confirmar 100%: efecto del redeploy reciente (arranque en frio + reconexion de Postgres) coincidiendo con el intento de subida, no un bug del codigo de este lote
- El problema NO se repitio en intentos posteriores inmediatos
- PENDIENTE: si se repite en sesiones futuras, investigar con mas profundidad (revisar metricas de CPU/memoria del contenedor en el momento exacto, o revisar si el filesystem efimero de Railway tiene latencia de I/O variable)

## SIGUIENTE PASO
Lote C2 listo para merge a auditoria-local -- PERO PRIMERO revertir el cambio temporal de CSRF_TRUSTED_ORIGINS (confirmar que no quede en el commit final, igual que se hizo correctamente en el Lote A).

# ============================================================
# LOTE D (llaves hardcodeadas) — IMPLEMENTADO Y FUSIONADO (sesion 14, cierre)
# Fecha: 15 Jul 2026
# ============================================================

## RESULTADO: LOTE D COMPLETO

Rama fix/lote-d-llaves-hardcodeadas fusionada a auditoria-local.

### Cambios
1. nom035/settings.py: 3 variables nuevas via config() (python-decouple, mismo patron ya usado para SECRET_KEY/ALLOWED_HOSTS): AES_ENCRYPTION_KEY, RECAPTCHA_SECRET_KEY, RECAPTCHA_SITE_KEY -- todas con default= al valor actual (NO se roto ningun valor real, solo se movio la fuente)
2. surveys/views.py: encript()/decript() usan settings.AES_ENCRYPTION_KEY; UserappList (verificacion recaptcha backend) usa settings.RECAPTCHA_SECRET_KEY; NewUserView pasa recaptcha_site_key al contexto del template
3. surveys/templates/auth-register.html: las 2 ocurrencias hardcodeadas de la site key reemplazadas por {{ recaptcha_site_key }}

### Validacion
Probado en staging: la pagina /newuser/ sigue mostrando el mismo error de reCAPTCHA que YA CONOCIAMOS de sesiones anteriores (dominio de staging no autorizado en la consola de Google para esa site key) -- esto CONFIRMA que el fix funciona correctamente (el valor real se esta leyendo bien desde la variable), no es un bug nuevo. Comportamiento identico al de antes del lote, que es exactamente el objetivo (mover sin alterar comportamiento).

### PENDIENTE (no bloqueante, anotado para cuando se vaya a produccion real)
Jorge debe configurar las 3 variables de entorno reales en Railway (produccion Y staging) en algun momento. Mientras no se configuren, el sistema sigue funcionando igual que antes (usa los default= que son los valores viejos). Rotar la llave AES a un valor nuevo (distinto del actual) invalidara cualquier link de verificacion de email o recuperacion de contrasena ya emitido y no usado -- hacerlo con cuidado, idealmente en una ventana de mantenimiento.

## RESUMEN COMPLETO DE LA SESION 14 (para continuidad)

4 lotes completados y fusionados a auditoria-local en esta sesion:
- Lote A: IDOR NOM-035 (7 vistas)
- Lote C1: download_file2 (ownership + bug UnboundLocalError)
- Lote C2: archivos /media/ protegidos (logos, resultados, evidencias Fase C) + hallazgo critico de Volume persistente faltante en Railway
- Lote D: llaves hardcodeadas (AES + reCAPTCHA) movidas a variables de entorno

Documento de continuidad creado: MATRIZ_CONSOLIDADA_POST_REMEDIACION.md (en la raiz del repo, rama auditoria-local) -- consolida el estado de los 22 hallazgos originales + 12 hallazgos nuevos encontrados durante la remediacion.

## PENDIENTES PARA LA SIGUIENTE SESION
1. INFRA-001 (Volume persistente en Railway) -- resolver directamente en el dashboard de Railway, no requiere lote de Codex, puede hacerse en paralelo sin bloquear
2. Definir siguiente lote de seguridad: N35-INT-001/002/003 (creditos y duplicados NOM-035), EVI-SEC-002 (archivos EXE aceptados), o PSI-VAL-001 a 006 (validacion backend de los 6 instrumentos psicometricos)
3. SEC-006 (PasswordRecover bypass) sigue como ULTIMO PASO antes de produccion real, decision ya tomada por Jorge
4. Recordar SIEMPRE: revertir CSRF_TRUSTED_ORIGINS temporal antes de mergear cualquier lote que requiera probar formularios POST en staging

# ============================================================
# LOTE E (N35-INT-001, creditos NOM-035) — IMPLEMENTADO Y VALIDADO (sesion 14, cont.)
# Fecha: 15 Jul 2026
# ============================================================

## RESULTADO: LOTE E COMPLETO Y FUSIONADO

Rama fix/lote-e-creditos-nom035, fusionada a auditoria-local.

### Cambio implementado en SaveAnswers.post() (surveys/views.py)
- Antes: serializer.save() ocurria PRIMERO, la validacion de es_demo/creditos ocurria DESPUES (con try/except que silenciaba errores con solo un print) -- si fallaba la validacion, el registro ya se habia guardado en BD a pesar de responder 403
- Ahora: para las ramas risksurveya/risksurveyb/traumasurvey, se valida es_demo y nom035_creditos<=0 ANTES de guardar nada; el guardado + descuento de credito quedan dentro de transaction.atomic(); se elimino el try/except que silenciaba errores
- Import agregado: from django.db import IntegrityError, transaction

### Validacion en staging (con Cuenta A, workplace_id=1)
- Sin creditos (forzado a 0): HTTP 403, CERO registros RiskSurveyA creados -- CONFIRMADO que ya no persiste nada indebido
- Con creditos (restaurados a 5): HTTP 201, 1 registro creado, creditos bajaron correctamente a 4
- Rama form=='employee' no se toco en el diff, riesgo de regresion minimo

## RESUMEN ACTUALIZADO DE LOTES COMPLETADOS (sesion 14)
A (IDOR), C1 (download_file2), C2 (media protegido), D (llaves hardcodeadas), E (creditos NOM-035 atomicos) -- 5 lotes en una sola sesion, todos validados en staging y fusionados a auditoria-local.

## PENDIENTES ACTUALIZADOS PARA SIGUIENTE SESION
1. INFRA-001 (Volume persistente Railway) -- sigue sin resolver, no bloquea nada
2. Candidatos para siguiente lote: N35-INT-002 (duplicados/consumo repetido, relacionado con lo que ya se toco en Lote E), N35-INT-003 (.last() silencioso), EVI-SEC-002 (archivos EXE aceptados), PSI-VAL-001 a 006 (validacion backend de los 6 instrumentos)
3. SEC-006 (PasswordRecover bypass) sigue como ULTIMO PASO antes de produccion real
4. Actualizar MATRIZ_CONSOLIDADA_POST_REMEDIACION.md con el cierre de Lote E (agregar fila N35-INT-001 como CORREGIDO)

# ============================================================
# LOTE F (N35-INT-002, duplicados NOM-035) — IMPLEMENTADO Y VALIDADO (sesion 14, cont.)
# Fecha: 15 Jul 2026
# ============================================================

## RESULTADO: LOTE F COMPLETO Y VALIDADO

Rama fix/lote-f-duplicados-nom035, lista para merge a auditoria-local.

### Cambios
1. surveys/models.py: unique_together = ('employee', 'evaluation') agregado a la Meta existente de RiskSurveyA, TraumaSurvey, RiskSurveyB
2. Migracion manual 0038_unique_survey_per_evaluation.py: 3x AlterUniqueTogether, dependencia correcta a 0037
3. surveys/views.py, SaveAnswers.post(): doble proteccion contra duplicados --
   - El try/except alrededor del transaction.atomic() (ya existente del Lote E) ahora captura IntegrityError especificamente (condicion de carrera / colision concurrente), responde 409
   - ADEMAS (hallazgo de Codex durante implementacion): DRF ModelSerializer genera automaticamente un validador de unique_together, asi que el caso MAS COMUN de duplicado se detecta antes, en serializer.is_valid()==False -- se agrego un chequeo explicito despues del if serializer.is_valid() para responder 409 en vez del 400 generico en ese caso tambien

### Validacion en staging
- Migracion 0038 aplicada correctamente durante el deploy
- Intento de duplicado (mismo employee+evaluation que ya tenia 1 RiskSurveyA del Lote E): respuesta 409, conteo de RiskSurveyA se mantuvo en 1 (no subio a 2), creditos se mantuvieron en 4 (no bajaron de nuevo)

## PENDIENTE IMPORTANTE ANTES DE PRODUCCION REAL
Esta migracion (0038) NO debe aplicarse contra una base de datos con datos reales sin antes auditar y resolver duplicados existentes (employee+evaluation repetidos) -- si existieran, la migracion fallaria al no poder crear la restriccion de unicidad sobre datos que ya la violan. Como el proyecto aun no tiene datos reales de produccion, esto no es bloqueante hoy, pero DEBE recordarse antes de cualquier paso a produccion real con datos existentes.

## RESUMEN ACTUALIZADO DE LOTES DE LA SESION 14
A, C1, C2, D, E, F -- 6 lotes completados, validados en staging, y fusionados a auditoria-local en una sola sesion.

## PENDIENTES PARA SIGUIENTE SESION
1. INFRA-001 (Volume persistente Railway) -- sin resolver
2. Candidatos siguiente lote: N35-INT-003 (.last() silencioso), EVI-SEC-002 (archivos EXE), PSI-VAL-001 a 006 (validacion backend instrumentos psicometricos)
3. SEC-006 (PasswordRecover bypass) -- ULTIMO PASO antes de produccion real
4. Actualizar MATRIZ_CONSOLIDADA_POST_REMEDIACION.md: agregar N35-INT-002 como CORREGIDO
5. Recordar: auditar duplicados existentes antes de aplicar migracion 0038 en cualquier BD con datos reales

# ============================================================
# LOTE G (PSI-VAL-001 a 006, validacion psicometrica) — COMPLETADO Y FUSIONADO (sesion 14, cont.)
# Fecha: 15 Jul 2026
# ============================================================

## RESULTADO: LOTE G COMPLETO, FUSIONADO A auditoria-local

Rama fix/lote-g-validacion-psicometrica. Merge fast-forward, sin conflictos.

### Cambio implementado en TestCompleteView.post() (surveys/psico_views.py)
Reestructurado en 2 pasadas:
1. Primera pasada: valida CADA respuesta (formato + coherencia) SIN guardar nada en BD. Si algo es invalido, responde 400 inmediatamente, la sesion permanece en su estado original (pendiente/en_proceso), CERO TestResponse creados
2. Segunda pasada (solo si TODO paso la validacion): guarda todas las TestResponse, marca sesion completada, calcula scores (via _calcular_scores, sin cambios)

Nuevo metodo _validar_respuesta(self, item, respuesta) con reglas especificas por tipo de instrumento:
- disc: respuesta debe ser dict con 'mas'/'menos', ambos deben ser dimensiones validas presentes en item.opciones, y mas != menos
- moss/competencias/comercial/raven: respuesta debe ser string no vacio, debe existir como 'letra' en item.opciones
- zavic: respuesta debe ser dict con 'distribucion' (dict), cada escala debe ser valida para ese item, cada valor debe ser entero >=0 (type(puntos) is not int para excluir booleanos), y la SUMA debe ser exactamente 5

Tambien se agrego: verificacion de completitud (numero de respuestas validas debe igualar el total de items del instrumento) y validaciones defensivas de tipo (respuestas debe ser lista, cada item debe ser dict).

### Validacion (RequestFactory, aislado, sin necesitar contenedor)
Los 6 instrumentos probados con 3 escenarios cada uno (18 verificaciones total):
- Envio completo y valido -> 200, guarda correctamente (sin regresion)
- Envio incompleto -> 400, CERO TestResponse guardados, sesion no completada
- Formato invalido especifico del tipo (DISC mas==menos, Zavic suma!=5, letra inexistente en Moss/Raven/Competencias/Comercial) -> 400, CERO guardados

Todos los 18 casos PASS.

## RESUMEN FINAL DE LA SESION 14 — 7 LOTES COMPLETADOS

A (IDOR NOM-035), C1 (download_file2), C2 (media protegido), D (llaves hardcodeadas), E (creditos NOM-035 atomicos), F (duplicados NOM-035), G (validacion psicometrica 6 instrumentos) -- todos implementados, validados en staging o con RequestFactory aislado, y fusionados a auditoria-local.

## PENDIENTES PARA SIGUIENTE SESION
1. INFRA-001 (Volume persistente Railway) -- sin resolver, no bloqueante
2. Candidatos siguiente lote: N35-INT-003 (.last() silencioso), EVI-SEC-002 (archivos EXE en evidencias), DEP-001/002 (fix definitivo de migraciones/Procfile, ya mitigados manualmente)
3. Hallazgos "Media/Baja" pendientes: CLM-INT-001 (Clima Laboral reenvios), PN-01 a PN-06 (Perfil Narrativo, IA aun no conectada realmente), CONFIG-001/002, SEC-008 (llaves Conekta comentadas)
4. SEC-006 (PasswordRecover bypass) -- ULTIMO PASO antes de produccion real, decision ya tomada
5. Actualizar MATRIZ_CONSOLIDADA_POST_REMEDIACION.md: agregar PSI-VAL-001 a 006 como CORREGIDOS (6 filas), y corregir el conteo total de hallazgos (revisar bien SEC-005/007 que ya se movieron a Lote D, evitar doble conteo)

# ============================================================
# LOTE H (EVI-SEC-002, validacion de contenido de archivos) — COMPLETADO Y FUSIONADO
# Fecha: 15 Jul 2026 (sesion 15)
# ============================================================

## RESULTADO: LOTE H COMPLETO, FUSIONADO A auditoria-local

Rama fix/lote-h-validacion-archivos. Merge fast-forward, sin conflictos.

### Cambios
1. surveys/models.py: nueva funcion validar_contenido_archivo(archivo, extensiones_permitidas) -- valida magic bytes reales (PDF: %PDF-, JPG: \xff\xd8\xff, PNG: \x89PNG\r\n\x1a\n) contra la extension declarada, mas validacion adicional con Pillow para JPG/PNG (Image.open().verify()). Deja el puntero del archivo en posicion 0 al terminar
2. validate_file_extension (usado por Userapp.image, el logo) reescrito para usar la funcion nueva -- IMPORTANTE: el primer intento de Codex perdio la validacion de tamano de 2.5MB que tenia la funcion original, se detecto en revision de diff y se corrigio antes de comitear (ahora conserva ambas: limite de tamano Y validacion de contenido)
3. surveys/forms.py: EvidenciaFaseCForm.clean_archivo ahora llama a validar_contenido_archivo despues de las validaciones existentes (tamano 10MB, extension)
4. Sin dependencias nuevas -- solo se uso Pillow (ya instalado) y verificacion manual de magic bytes, evitando requerir python-magic/libmagic en el build de Railway

### Validacion (local, sin necesitar staging)
Probado con SimpleUploadedFile: PDF falso rechazado, PDF minimo valido aceptado, JPG real aceptado, PNG real aceptado, JPG falso rechazado, formulario completo con PDF falso rechazado, formulario con PDF valido aceptado. Todos los casos PASS.

## LECCION: revisar diffs de refactors con cuidado especial cuando reemplazan una funcion completa
Al reescribir validate_file_extension de cero, el primer intento omitio silenciosamente la validacion de tamano de 2.5MB que ya existia. Cuando se pide reescribir/refactorizar una funcion existente (no solo agregar codigo nuevo), revisar el diff linea por linea contra el ORIGINAL para confirmar que ningun comportamiento previo se perdio, no solo que el nuevo comportamiento funcione.

## RESUMEN ACTUALIZADO: 8 LOTES COMPLETADOS (sesiones 14-15)
A, C1, C2, D, E, F, G, H -- todos fusionados a auditoria-local.

## PENDIENTES PARA SIGUIENTE SESION
1. INFRA-001 (Volume persistente Railway) -- sin resolver
2. Candidatos siguiente lote: N35-INT-003 (.last() silencioso), DEP-001/002 (fix definitivo migraciones/Procfile)
3. Hallazgos Media/Baja pendientes: CLM-INT-001, PN-01 a 06, CONFIG-001/002, SEC-008
4. SEC-006 (PasswordRecover bypass) -- ULTIMO PASO antes de produccion real
5. Actualizar MATRIZ_CONSOLIDADA_POST_REMEDIACION.md: agregar EVI-SEC-002 como CORREGIDO

# ============================================================
# LOTE I (N35-INT-003, .last() sin filtro de evaluation) — COMPLETADO Y FUSIONADO
# Fecha: 15 Jul 2026 (sesion 15, cont.)
# ============================================================

## RESULTADO: LOTE I COMPLETO, FUSIONADO A auditoria-local

Rama fix/lote-i-evaluacion-actual. Merge fast-forward, sin conflictos.

### Cambio implementado en EmployeeList.get() (surveys/views.py, ~linea 2135)
emp.surveyB.last() / emp.surveyA.last() (SIN filtro de evaluation, inconsistente con el resto del archivo que si filtra) ahora filtran por emp.workplace.evaluation antes de .last(), guardando el resultado en variables survey_b_actual/survey_a_actual reutilizadas (evita doble consulta ademas de corregir el bug).

### Decision de diseno confirmada
Se evaluo si debia usarse el patron eval_to_check (usado en Portafolio de Evidencias para el "ultimo ciclo cerrado") en vez de emp.workplace.evaluation directo. Se confirmo que NO aplica aqui: esta vista (EmployeeList) representa el ESTADO OPERATIVO DEL CICLO VIGENTE (ya usaba emp.workplace.evaluation para el chequeo de trauma en la misma vista), mientras que eval_to_check es especifico para mostrar resultados de una evaluacion ya finalizada en el Portafolio. Contextos distintos, decision correcta de mantener consistencia con el resto de la vista.

### Alcance de N35-INT-003 en el proyecto (hallazgo importante)
Se investigo el patron completo de .last() en surveys/views.py (mas de 25 ocurrencias). La gran mayoria (filter(evaluation=X).last()) YA quedaron mitigadas indirectamente por el Lote F (unique_together employee+evaluation en RiskSurveyA/TraumaSurvey/RiskSurveyB) -- como ya no pueden existir duplicados por empleado+evaluacion, esos .last() ya no "eligen entre varios" registros, solo devuelven el unico posible. El UNICO caso genuinamente problematico (sin filtro de evaluation) era el corregido en este lote. N35-INT-003 se considera CERRADO para el modulo NOM-035.

## RESUMEN: 9 LOTES COMPLETADOS (sesiones 14-15)
A, C1, C2, D, E, F, G, H, I -- todos fusionados a auditoria-local.

## PENDIENTES PARA SIGUIENTE SESION
1. INFRA-001 (Volume persistente Railway) -- sin resolver
2. DEP-001/002 (fix definitivo de migraciones 0022/0023 y Procfile) -- unicos hallazgos "Alta" originales que faltan por atacar con codigo real (ya mitigados manualmente, falta el fix definitivo)
3. Hallazgos Media/Baja pendientes: CLM-INT-001, PN-01 a 06, CONFIG-001/002, SEC-008
4. SEC-006 (PasswordRecover bypass) -- ULTIMO PASO antes de produccion real
5. Actualizar MATRIZ_CONSOLIDADA_POST_REMEDIACION.md: agregar N35-INT-003 como CORREGIDO, y EVI-SEC-002 (Lote H) que quedo pendiente de sesion anterior
6. Nota menor: git detecto nombre/email de commit automaticamente en esta maquina -- no urgente, configurar con git config --global si Jorge quiere

# ============================================================
# LOTE J (DEP-001/DEP-002, fix definitivo migraciones+Procfile) — COMPLETADO Y FUSIONADO
# Fecha: 15 Jul 2026 (sesion 15, cont.)
# ============================================================

## RESULTADO: LOTE J COMPLETO, FUSIONADO A auditoria-local, DEPLOY LIMPIO CONFIRMADO

Rama fix/lote-j-migraciones-procfile.

### Cambios
1. surveys/migrations/0023_perfil_narrativo.py: vaciada de operaciones (quedo operations = []), conserva dependencia a 0022_psicometria. El campo perfil_narrativo ya lo crea 0022 (confirmado leyendo su codigo -- el CreateModel de TestResult ya incluye el campo)
2. Procfile: agregados cargar_competencias y cargar_comercial a la cadena de comandos del arranque, antes de gunicorn

### Validacion — LA MAS FUERTE DE TODA LA SESION
Codex probo una INSTALACION 100% LIMPIA con PostgreSQL LOCAL (no staging, base nueva de verdad):
- Las 38 migraciones (0001 a 0038) se aplicaron TODAS sin error y SIN NECESITAR --fake en ningun punto
- Los 6 instrumentos (disc, moss, raven, zavic, competencias, comercial) se cargaron automaticamente en el primer arranque, sin intervencion manual
- makemigrations --check --dry-run solo senala el pendiente YA CONOCIDO y ajeno a este lote: PsychoInstrument.tipo sin migracion formal para los choices 'competencias'/'comercial' (documentado desde sesiones anteriores, no bloqueante, de baja prioridad)

DEP-001 y DEP-002 quedan CERRADOS DEFINITIVAMENTE -- ya no son solo "mitigados manualmente", tienen el fix de codigo real, probado desde cero.

## RESUMEN: 10 LOTES COMPLETADOS (sesiones 14-15)
A, C1, C2, D, E, F, G, H, I, J -- todos fusionados a auditoria-local. Deploy en staging confirmado limpio tras el Lote J.

## ESTADO DE LOS HALLAZGOS "ALTA" ORIGINALES: TODOS CERRADOS
De los 12 hallazgos "Alta" de la auditoria original (22 totales), los que aplicaban a codigo real (N35-INT-001, N35-INT-002, N35-INT-003, PSI-VAL-001 a 006, EVI-SEC-002, DEP-001, DEP-002) estan TODOS corregidos. Los 2 "Critica" tambien estan corregidos (N35-SEC-001, EVI-SEC-001).

## PENDIENTES PARA SIGUIENTE SESION
1. INFRA-001 (Volume persistente Railway) -- sin resolver, infraestructura no codigo
2. Hallazgos Media/Baja restantes de la auditoria original: CLM-INT-001 (Clima Laboral reenvios ilimitados), PN-01 a PN-06 (Perfil Narrativo, modulo de IA aun sin proveedor real conectado)
3. Hallazgos nuevos menores: CONFIG-001/002 (CSRF/CORS hardcodeados, dominio placeholder), SEC-008 (llaves Conekta comentadas en codigo)
4. SEC-006 (PasswordRecover bypass) -- ULTIMO PASO antes de produccion real, sigue siendo la unica pieza critica pendiente, decision ya tomada por Jorge de dejarla para el final
5. Pendiente menor conocido: PsychoInstrument.tipo sin migracion formal para choices 'competencias'/'comercial' (bajo riesgo, Django detecta la diferencia pero no rompe nada)
6. Actualizar MATRIZ_CONSOLIDADA_POST_REMEDIACION.md con el cierre completo: agregar DEP-001, DEP-002, N35-INT-003, EVI-SEC-002 como CORREGIDOS -- consolidar conteo final

# ============================================================
# LOTE K (CONFIG-001/002, SEC-008) — COMPLETADO Y FUSIONADO
# Fecha: 16 Jul 2026 (sesion 16)
# ============================================================

## RESULTADO: LOTE K COMPLETO, FUSIONADO A auditoria-local

Rama fix/lote-k-config-limpieza.

### Cambios
1. nom035/settings.py: CORS_ALLOWED_ORIGINS y CSRF_TRUSTED_ORIGINS movidos a variables de entorno via config(), mismo patron que ALLOWED_HOSTS, con default = valores actuales de produccion. El dominio placeholder "https://tu-frontend.com" desaparecio (CONFIG-002 resuelto como efecto secundario)
2. surveys/views.py: eliminadas 4 lineas de comentarios con llaves de Conekta (3 originales "pulica"/"publica" de prueba + 1 encontrada durante la revision, la de "produccion" sin calificar)

### MEJORA DE PROCESO IMPORTANTE
Con CORS_ALLOWED_ORIGINS/CSRF_TRUSTED_ORIGINS ahora via variable de entorno, YA NO sera necesario hacer el ajuste temporal de codigo (commit temporal + revertir) que tuvimos que hacer en varios lotes anteriores (A, C2) para poder probar formularios POST en staging -- de aqui en adelante basta con agregar el dominio de staging a la variable de entorno en Railway, sin tocar codigo.

## HALLAZGO NUEVO IMPORTANTE — Conekta activo y con llave privada expuesta (para Lote L futuro)

Durante la limpieza de comentarios de Conekta, Codex encontro que la integracion de Conekta NO es solo codigo muerto comentado -- esta ACTIVA:
- conekta.api_key = "key_qfCtN8NqwJRTTJR23wdcqA" HARDCODEADA Y ACTIVA en surveys/views.py linea ~43 (llave privada de PRODUCCION, no de pruebas)
- Vistas activas PaymentList y AddCardList (surveys/views.py) usan el SDK de Conekta para crear/buscar clientes, crear ordenes, manejar tarjetas
- 2 templates (edit_profile.html, payments.html) cargan el SDK de Conekta y tokenizan tarjetas con una llave PUBLICA de pruebas (esta si esta bien que sea publica, no es el problema)
- Dependencia conekta==6.0.4 en requirements.txt
- Campo Userapp.client_id en models.py (historico, relacionado a Conekta)
- Webhook comentado en models.py
- Referencias en migraciones 0001 y 0010 (estas SI deben conservarse, no tocar historial de migraciones)

CONTEXTO DE JORGE: Conekta era el proveedor de pagos ANTES de que el sistema fuera solo NOM-035; ya NO se va a usar, Stripe es el proveedor definitivo de aqui en adelante. Jorge NO tiene acceso a la cuenta de Conekta para revocar la llave desde su lado.

RIESGO: la llave privada de produccion sigue expuesta en el codigo Y funcionalmente activa (el SDK realmente se usa). Como no se puede revocar desde Conekta (sin acceso a la cuenta), la unica mitigacion posible por ahora es eliminar el codigo que la usa y quitarla del repositorio -- aunque la llave en si podria seguir siendo valida en el lado de Conekta indefinidamente si nadie la revoca ahi.

## PENDIENTE INMEDIATO — LOTE L (nuevo, alta prioridad)
Limpieza completa de Conekta: eliminar llave hardcodeada, deshabilitar/eliminar PaymentList y AddCardList (o las partes que dependen de Conekta especificamente), quitar SDK de los 2 templates, remover dependencia de requirements.txt, decidir que hacer con Userapp.client_id (deprecar el campo o dejarlo por compatibilidad historica sin usarlo), NO tocar migraciones 0001/0010 (historial). Requiere mas cuidado que un lote tipico porque toca flujo de pagos -- confirmar con Jorge si PaymentList/AddCardList tienen alguna otra funcion ademas de Conekta antes de eliminarlas o si son 100% especificas de ese proveedor.

## RESUMEN: 11 LOTES COMPLETADOS (sesiones 14-16)
A, C1, C2, D, E, F, G, H, I, J, K -- todos fusionados a auditoria-local.

## PENDIENTES PARA SIGUIENTE SESION
1. LOTE L (Conekta completo) -- nueva prioridad alta, llave privada de produccion expuesta y activa
2. INFRA-001 (Volume persistente Railway) -- CONFIRMADO que sigue sin resolver (Jorge reviso, no aparece seccion de Volumes)
3. CLM-INT-001, PN-01 a 06 -- pendientes Media/Baja
4. SEC-006 (PasswordRecover bypass) -- ULTIMO PASO antes de produccion real
5. Actualizar MATRIZ_CONSOLIDADA_POST_REMEDIACION.md: agregar CONFIG-001/002 y SEC-008 como CORREGIDOS, agregar el hallazgo nuevo de Conekta activo (severidad ALTA/CRITICA a definir) como pendiente para Lote L

# ============================================================
# LOTE L (eliminacion de Conekta) — INCIDENTE DE SEGURIDAD Y REINICIO LIMPIO (sesion 16, cont.)
# Fecha: 16 Jul 2026
# ============================================================

## INCIDENTE DE SEGURIDAD OCURRIDO Y RESUELTO — LEER ANTES DE CONTINUAR

Durante la primera implementacion del Lote L, se uso `git add -A` para el commit final. Esto agrego accidentalmente al repo (PUBLICO en ese momento) una gran cantidad de archivos ajenos al lote que estaban sueltos sin trackear en el working directory de Jorge:
- `db_test.sqlite3` (base de datos de prueba completa)
- Archivos de evidencia de pruebas de seguridad con nombres reveladores (`...traversal.png`, `...extension.exe`, `...contenido-invalido.pdf`) dentro de `media/results/27/1/`
- La carpeta `qa_tests/` COMPLETA — un framework de pruebas QA/auditoria de Jorge con reportes que incluyen `INFORME_EJECUTIVO_NORMAIA_QA.md`, `MATRIZ_FINAL_HALLAZGOS.md`, `ROADMAP_REMEDIACION.md` — documentos que detallan vulnerabilidades de seguridad del sistema, incluyendo (potencialmente) el detalle de SEC-006 (bypass de PasswordRecover) que **sigue sin corregir**

Esto se subio a `github.com/jorgereynaga/nom035`, que en ese momento era PUBLICO. Riesgo: cualquiera pudo haber visto documentacion detallada de una vulnerabilidad critica activa y explotable.

### Acciones de remediacion ya ejecutadas (en orden)
1. Repo cambiado a PRIVADO en GitHub Settings (Jorge confirmo el cambio) — esto es lo mas importante, corta el acceso publico de inmediato
2. Rama remota `fix/lote-l-conekta` eliminada (`git push origin --delete`)
3. Rama local eliminada tambien (`git branch -D`)
4. Rama recreada limpia desde `auditoria-local` (que NUNCA tuvo estos archivos, el problema fue exclusivo del commit de Lote L)
5. `.gitignore` actualizado agregando `qa_tests/` explicitamente (commit `bcb6ded9`, ya pusheado, limpio, solo 3 lineas)
6. NO fue necesario usar `git filter-repo` — como el commit contaminado era el UNICO commit exclusivo de esa rama por encima de `auditoria-local`, simplemente borrar y recrear la rama fue suficiente y mas simple

### PENDIENTE DE ESTE INCIDENTE (importante, no cerrar hasta hacer esto)
1. **Confirmar que `media/` y `db_test.sqlite3` ya estan en `.gitignore` de forma robusta** — al revisar el `git status` post-limpieza, estos NO aparecieron como untracked (sugiere que ya estaban ignorados), pero vale la pena confirmarlo explicitamente con `cat .gitignore` para asegurar que el patron cubre bien todas las subcarpetas de media/ y no fue una coincidencia
2. **Evaluar con Jorge si se contacta a soporte de GitHub** para solicitud de purga de cache/indices de contenido sensible, dado que el repo estuvo publico con esos archivos por un tiempo indeterminado (breve, pero no confirmado con certeza que nadie accedio — "0 stars/watchers" no es garantia de que nadie vio archivos por URL directa)
3. **Considerar adelantar la prioridad de SEC-006** (bypass de PasswordRecover) dado que su documentacion pudo haber estado expuesta publicamente, aunque sea brevemente — ya no se siente tan seguro dejarlo como "ultimo paso antes de produccion", el nivel de riesgo pudo haber cambiado
4. **Regla nueva OBLIGATORIA para todos los commits futuros de cualquier lote**: NUNCA usar `git add -A` ni `git add .` — siempre agregar archivos EXPLICITAMENTE por nombre (`git add archivo1.py archivo2.html`). Revisar `git status` ANTES de cada `git add` para confirmar que no aparezca nada inesperado (carpetas de pruebas, bases de datos locales, archivos sueltos de trabajo)

## ESTADO ACTUAL DE LA RAMA fix/lote-l-conekta (limpia, lista para reimplementar)
- Rama creada limpia desde auditoria-local, con SOLO el commit del .gitignore (bcb6ded9)
- El codigo de Conekta ESTA DE VUELTA en su estado original (se revirtio al recrear la rama) — confirmado: `grep -c "conekta" surveys/views.py` = 16, `surveys/templates/payments.html` sigue existiendo
- El archivo `LOTE_L_especificacion_conekta.md` SI sigue presente (viene de auditoria-local, nunca se toco)
- PENDIENTE: pedirle a Codex que reimplemente la especificacion completa desde cero en esta rama (el trabajo que ya habia hecho una vez, con buena calidad segun el diff revisado, se perdio al descartar la rama contaminada — hay que rehacerlo, pero la especificacion ya esta escrita y no cambia)
- Cuando Codex termine: NO usar `git add -A`, agregar archivos explicitos: `nom035/urls.py`, `requirements.txt`, `surveys/models.py`, `surveys/stripe_views.py`, `surveys/templates/edit_profile.html`, `surveys/views.py`, y el `git rm surveys/templates/payments.html` para el archivo eliminado

## CAMBIO DE HERRAMIENTA: Jorge empieza a usar Claude Code
A partir de este punto, Jorge va a trabajar con Claude Code (la app de escritorio) apuntando directo a la carpeta del repo (`C:\NormaIA-Pruebas\nom035`), en vez de copiar/pegar comandos y resultados entre la terminal y el chat de Claude.ai. Esto deberia agilizar mucho el trabajo, especialmente revisar diffs completos y archivos grandes sin las limitaciones de copiar/pegar por chat.

El flujo de trabajo cambia ligeramente:
- Claude Code puede leer archivos, correr comandos, y ver resultados directamente sin que Jorge tenga que copiar/pegar
- Los principios siguen siendo los mismos: Jorge revisa y aprueba antes de cada commit/push, nunca se actua de forma completamente autonoma sin su confirmacion en pasos criticos (deploys, cambios de rama en Railway, merges)
- La regla de NUNCA usar git add -A aplica igual, sin importar la herramienta usada para ejecutar los comandos
- Verificar que Claude Code tambien tenga acceso de lectura a este ESTADO.md al iniciar, ya que es el puente de contexto entre sesiones (y ahora entre herramientas tambien)

## PENDIENTE INMEDIATO PARA RETOMAR (con Claude Code o la cuenta que continue)
1. Reimplementar Lote L en la rama limpia fix/lote-l-conekta (spec ya escrita, solo falta que Codex/Claude Code la aplique de nuevo)
2. Al commitear: SOLO archivos explicitos, jamas git add -A, revisar git status antes de cada add
3. Confirmar .gitignore cubre bien media/ y db_test.sqlite3 de forma robusta (no solo por casualidad)
4. Decidir con Jorge si se contacta a soporte de GitHub por el incidente de exposicion breve
5. Reevaluar prioridad de SEC-006 (PasswordRecover bypass) dado el incidente
6. Una vez reimplementado y validado en staging: merge de fix/lote-l-conekta a auditoria-local, cambiar Source de Railway de vuelta si se habia cambiado
7. INFRA-001 (Volume persistente Railway) sigue sin resolver
8. CLM-INT-001, PN-01 a 06 -- pendientes Media/Baja sin atacar aun

# ============================================================
# LOTE L (Eliminacion de Conekta) — IMPLEMENTADO EN RAMA (sesion 14)
# Fecha: 16 Jul 2026
# ============================================================

## RESULTADO: LOTE L COMPLETADO, PENDIENTE DE VALIDAR EN STAGING Y MERGE

Rama: fix/lote-l-conekta (a partir de auditoria-local, recreada limpia tras el
incidente de seguridad documentado en la sesion anterior). Implementado por
Codex siguiendo LOTE_L_especificacion_conekta.md. Commit: a80c3aef.

### Cambios implementados
1. surveys/stripe_views.py — StripePortalView.get() ahora crea el customer de
   Stripe al vuelo si userapp.stripe_customer_id esta vacio (mismo patron que
   StripeCheckoutView), guarda el id, y ya no redirige nunca a /payments/
   (ni en el flujo normal ni en el catch de error)
2. surveys/views.py — eliminado por completo: import conekta, la llave de
   API de PRODUCCION hardcodeada (key_qfCtN8NqwJRTTJR23wdcqA), get_price(),
   PaymentView, PaymentList, AddCardList
3. nom035/urls.py — eliminadas las rutas /payments/, /api/payments/,
   /api/addCard/ (stripe_portal no se toco, sigue igual)
4. surveys/templates/edit_profile.html — pestanas "Metodos de pago" y
   "Mis pagos" reemplazadas por mensaje + boton a {% url 'stripe_portal' %};
   eliminado el script de cdn.conekta.io y todos los handlers JS huerfanos
   (toggleAddCard, submit-card, delete-card)
5. surveys/templates/payments.html — archivo eliminado
6. surveys/models.py — Userapp.client_id conservado (sin migracion), marcado
   con comentario "# DEPRECATED - Conekta ya no se usa..."; eliminado el
   bloque comentado ConektaWebhook (codigo muerto)
7. requirements.txt — eliminada la linea conekta==6.0.4

### Revision de diff (Claude, antes del commit)
- Confirmado con grep que solo quedan referencias a "conekta" en el
  comentario de deprecacion de models.py y en las migraciones historicas
  0001/0010 (correcto, no se tocan por especificacion)
- Tags Django balanceados en edit_profile.html (if/endif, block/endblock)
- Sin referencias colgantes a payments.html, PaymentView, PaymentList,
  AddCardList, /api/addCard/ en ningun otro archivo del repo
- python -m py_compile OK en los 4 archivos .py tocados (verificado dos
  veces, por Codex con Python 3.10 y de forma independiente por Claude)
- Detalle cosmetico no bloqueante: StripePortalView usa return_url con
  string hardcodeado "/edit_profile/" en el flujo normal pero
  reverse('edit_profile') en el catch de error — ambos resuelven al mismo
  lugar, es solo inconsistencia de estilo, no bug

### HALLAZGO NUEVO SIN RELACION AL LOTE (anotado, no corregido)
db.sqlite3 (raiz del repo) y toda la carpeta media/ (incluye PDFs reales de
resultados de clientes) estan TRACKEADOS en git desde antes de esta sesion,
y .gitignore no tiene *.sqlite3 ni media/. No es parte del incidente de
seguridad ya documentado (no aparecio en git status, no fue agregado ahora),
es contenido preexistente en el historial. PENDIENTE: decidir si se trata
como un lote de remediacion aparte (limpieza de historial de git, dato
sensible de clientes reales expuesto si el repo alguna vez fue o vuelve a
ser publico).

## PENDIENTE INMEDIATO
1. Validar en staging: iniciar sesion con cuenta SIN stripe_customer_id
   previo, click en "Metodos de pago", confirmar que crea el customer de
   Stripe al vuelo y redirige al Portal sin caer en 404 ni en /payments/
2. Confirmar visualmente que ambas pestanas de edit_profile.html se ven
   correctas sin resto visual del formulario viejo de tarjetas
3. Confirmar que /payments/, /api/payments/ y /api/addCard/ devuelven 404
4. Decidir si se hace merge de fix/lote-l-conekta a auditoria-local ahora
   o se espera a acumular mas lotes
5. Nuevo pendiente (no bloqueante para este lote): evaluar lote de limpieza
   para db.sqlite3/media/ trackeados en git (ver hallazgo arriba)

## VALIDACION EN STAGING COMPLETADA — LOTE L CERRADO (sesion 14, cont.)
Fecha: 17 Jul 2026

Validado por Claude en nom035-staging.up.railway.app con la cuenta pruebaB@test.com
(sin stripe_customer_id previo):

1. Deploy limpio tras git push origin fix/lote-l-conekta (commits a80c3aef, badc3558) --
   NOTA IMPORTANTE: el primer intento de validacion fallo porque se habia cambiado el
   Source de Railway a la rama SIN empujar los commits a GitHub primero -- Railway seguia
   sirviendo la version vieja (con Conekta activo). LECCION: siempre confirmar
   `git log origin/<rama>` coincide con local antes de asumir que un cambio de Source
   en Railway ya refleja el ultimo commit.
2. /payments/, /api/payments/, /api/addCard/ -- los 3 devuelven 404 (confirmado con
   fetch({redirect:'manual'/'follow'}) desde el navegador, no solo visualmente)
3. edit_profile.html -- pestanas "Metodos de pago" y "Mis pagos" confirmadas sin ningun
   resto visual del formulario viejo de tarjetas, ambas con link a stripe_portal
4. Flujo completo probado: login sin stripe_customer_id -> click "Metodos de pago" ->
   StripePortalView crea el customer de Stripe al vuelo -> redirige correctamente a
   billing.stripe.com con el Portal real (metodo de pago, datos de facturacion con el
   email correcto, historial de facturas) -- sin caer en 404 ni en /payments/

## LOTE L: COMPLETADO Y VALIDADO EN STAGING -- LISTO PARA MERGE A auditoria-local

# ============================================================
# LOTE M (CLM-INT-001, reenvios ilimitados Clima Laboral) — IMPLEMENTADO Y VALIDADO (sesion 17)
# Fecha: 17 Jul 2026
# ============================================================

## RESULTADO: LOTE M COMPLETO Y VALIDADO EN STAGING

Rama fix/lote-m-clima-reenvios (a partir de auditoria-local), implementada por Codex
siguiendo LOTE_M_especificacion_clima_reenvios.md. Commit: c531016f.

### Cambio implementado en ClimaLaboralView (surveys/views.py, ~linea 2733-2760)
Bloqueo de reenvios via sesion de Django (sin requerir login, la encuesta sigue siendo
anonima por diseno):
- POST: despues de validar que el workplace existe y tiene plan/creditos activos, se
  verifica request.session.get(f'clima_submitted_{wk.id}'); si ya existe, se devuelve
  clima_gracias.html sin crear un WorkEnvironmentSurvey nuevo. Si es la primera vez, se
  crea el registro y se marca request.session[f'clima_submitted_{wk.id}'] = True
- GET: mismo chequeo -- si la sesion ya envio, se muestra clima_gracias.html directo en
  vez del formulario vacio
- Se eligio bloqueo por SESION (no por IP) deliberadamente: varios empleados de un mismo
  centro de trabajo suelen compartir la misma IP de oficina (NAT), bloquear por IP
  afectaria a empleados legitimos distintos. Mitigacion proporcional a la severidad Media
  del hallazgo, consistente con que la encuesta es intencionalmente anonima
- Indentacion de 4 espacios de la clase (distinta al resto del archivo) respetada
- ClimaResultadosView (vista del empleador) sin cambios

### Validacion en staging (Claude, navegador embebido)
Con Workplace de pruebaA@test.com (4 creditos NOM-035 disponibles), access_code
203503421f294e83b2305e5d85a7ed53:
1. Envio completo valido (POST directo con los 40 campos vs fetch, csrftoken real) ->
   200, 1 WorkEnvironmentSurvey creado, confirmado via ClimaResultadosView (1 respuesta)
2. Reenvio inmediato desde la MISMA sesion -> 200 (misma plantilla gracias) pero CERO
   registros nuevos -- confirmado que el conteo se mantuvo en 1, no subio a 2
3. GET de vuelta al formulario en la misma sesion -> ya no muestra el formulario vacio,
   redirige directo a clima_gracias.html (titulo de pagina cambio a "Gracias")
4. Sesion distinta (logout de Django para forzar sesion nueva, request.session.flush())
   -> SI pudo enviar una respuesta nueva -- conteo subio correctamente a 2, promedio de
   las 8 dimensiones recalculado de 4.0 a 3.5 (consistente con valores 4 y 3 enviados)
5. NOTA METODOLOGICA: pestanas nuevas del mismo navegador comparten cookies (no son
   sesiones distintas) -- para probar el caso 4 hubo que forzar logout explicito, no
   bastaba con abrir una pestana nueva
6. ClimaResultadosView confirmada sin cambios de comportamiento (calculo de dimensiones
   correcto)

## LOTE M: COMPLETADO Y VALIDADO EN STAGING -- LISTO PARA MERGE A auditoria-local

# ============================================================
# LOTE N (N35-FUN-004, employees_dt devuelve 500 en casos limite) — IMPLEMENTADO Y VALIDADO (sesion 17, cont.)
# Fecha: 17 Jul 2026
# ============================================================

## RESULTADO: LOTE N COMPLETO Y VALIDADO EN STAGING

Rama fix/lote-n-employees-dt-500 (a partir de auditoria-local), implementada por Codex
siguiendo LOTE_N_especificacion_employees_dt_500.md. Commit: f4c76359.

### Causas raiz confirmadas (surveys/views.py, employees_dt, linea ~1139)
1. ZeroDivisionError: Paginator(query, length).page(page) con length=0 (controlable via
   query string) -- la excepcion no era ni PageNotAnInteger ni EmptyPage, se propagaba
   sin control -> 500
2. TypeError: int(request.GET.get('draw'/'start'/'length')) sin validar que el parametro
   existiera -> int(None) -> 500 si faltaba cualquiera de los 3 en la peticion
3. KeyError: el chequeo `if order>3: order=0` no cubria valores negativos de
   order[0][column] -- ordering[order] con order=-1 crasheaba (ordering es un dict con
   llaves 0-3, no una lista)
4. Menor: page=(start/length)+1 usaba division de punto flotante en vez de entera

### Cambio implementado
- draw/start/length/order[0][column] ahora se leen dentro de un try/except
  (TypeError, ValueError) -- si falta cualquiera o no es entero valido, responde 400
  con el mismo formato JSON vacio que ya usaba el 403 de ownership
- length<=0 se rechaza explicitamente con 400 (variante elegida: rechazar en vez de
  forzar un default)
- `if order>3: order=0` reemplazado por `if order not in ordering: order=0` -- cubre
  negativos y fuera de rango por arriba, sigue corrigiendo silenciosamente (no rechaza)
- page=(start//length)+1, division entera, solo ejecuta despues de garantizar length>0
- Ownership check y logica de negocio (armado de arr, badges, WhatsApp) sin cambios

### Validacion en staging (Claude, navegador embebido, fetch directo con sesion real)
Con pruebaA@test.com, workplace_id=1 (1 empleado registrado), endpoint
/employees_dt/1/0/1/:
- Peticion normal (draw/start/length/order completos) -> 200, datos correctos
- length=0 -> 400 (antes: 500 ZeroDivisionError)
- Falta draw -> 400 (antes: 500 TypeError)
- Falta start -> 400
- Falta length -> 400
- order[0][column]=-1 -> 200, corregido a columna 0 (antes: 500 KeyError)
- order[0][column]=99 -> 200, corregido a columna 0 (comportamiento preexistente, sin
  regresion)
- DataTable real de workplace_detail.html confirmado renderizando correctamente en
  pantalla (1 empleado, paginacion "pagina 1 de 1")

## HALLAZGO MENOR ADICIONAL, ANOTADO PERO NO CORREGIDO EN ESTE LOTE
nom035/urls.py linea 81: path('employees_dt/<int:workplace_id>/<int:t>/', ...) sin
evaluation en la URL -- si se invoca directamente (nadie lo hace hoy, confirmado con
grep que ningun template usa esta variante de 2 segmentos) causaria
TypeError: missing 1 required positional argument: 'evaluation'. No explotable por el
flujo normal de la app, se deja anotado para decidir despues si se cierra (opcion mas
simple: agregar evaluation=0 como default en la firma de la funcion).

## LOTE N: COMPLETADO Y VALIDADO EN STAGING -- LISTO PARA MERGE A auditoria-local

# ============================================================
# LOTE O (SEC-006, bypass total de PasswordRecover) — IMPLEMENTADO Y VALIDADO (sesion 18)
# Fecha: 17 Jul 2026
# ============================================================

## RESULTADO: LOTE O COMPLETO -- HALLAZGO MAS GRAVE DE TODA LA AUDITORIA, CERRADO

Rama fix/lote-o-password-recover-bypass (a partir de auditoria-local), implementada
por Codex siguiendo LOTE_O_especificacion_password_recover_bypass.md. Commit de codigo:
fix aplicado exclusivamente en PasswordRecover.post() (surveys/views.py, ~linea 766).

### Cambio implementado
- Condicion de la rama de cambio de contrasena corregida: antes comprobaba
  "new_password1" dos veces (nunca comprobaba new_password2), ahora comprueba ambos
- El POST ahora exige 'code' e 'iv' en kwargs (la URL) -- estos ya viajaban ahi porque
  el <form method="POST"> de password_recover.html no tiene action, se somete a la
  misma URL /password_recover/<code>/<iv> desde donde se cargo, NO fue necesario tocar
  el template
- Se replica exactamente la misma logica de desencriptacion+validacion de 1 hora que ya
  usaba get() (mismo patron, mismo Userapp.objects.filter(user_id=..., record_create=...))
- El usuario a modificar se deriva del token desencriptado (userapp.user), el campo
  user-email del POST YA NO se usa para identidad en ningun punto
- Codigo ausente/invalido/expirado -> no se ejecuta SetPasswordForm, mensaje
  error_changing_pass, contrasena NO se toca
- ct["valid_code"] ahora refleja la validacion real (antes hardcodeado a True)

### Validacion en staging (Claude, navegador embebido)
1. ATAQUE ORIGINAL (debia fallar): POST directo a /password_recover (sin code/iv en la
   URL) con new_password1/new_password2 y user-email=pruebaB@test.com -> 200, pagina
   "No pudimos verificar tu cuenta", CONFIRMADO que la contrasena de pruebaB NO cambio
   (login posterior con la contrasena ORIGINAL de pruebaB exitoso)
2. ATAQUE CON CODE/IV FORJADOS: POST a /password_recover/AAAA/BBBB (valores inventados)
   con los mismos campos -> 200, misma pagina de rechazo, SIN 500 (excepcion de
   desencriptacion manejada con gracia)
3. FLUJO LEGITIMO: NO se pudo validar end-to-end porque el envio de correo (SMTP) no
   esta configurado en este ambiente -- CONFIRMADO POR JORGE que es una limitacion
   PREEXISTENTE del sistema original, sin relacion con este lote (el codigo de envio de
   correo, PasswordRecover.post() rama `if email!="":`, no se toco en este lote). Se
   confirmo en su lugar que solicitar el link no crashea (responde con gracia el mensaje
   "no pudimos enviarte un correo de confirmacion"), y se confirmo por revision de
   codigo que la logica de validacion nueva en post() es identica byte a byte al patron
   ya usado y probado en get() desde hace meses (mismo decript(), misma ventana de 1
   hora, misma consulta a Userapp)
4. Confirmado tambien: el campo "user-email" ya no tiene ningun efecto sobre que cuenta
   se modifica -- la unica fuente de verdad es el codigo desencriptado

## HALLAZGO MENOR NUEVO, FUERA DE ALCANCE, ANOTADO PARA OTRA SESION
Durante la validacion se encontro que el link "¿Olvidaste tu contraseña?" en la pantalla
de login (surveys/templates/auth-login.html) apunta a href="/forgot-password/", una URL
que NUNCA existio en nom035/urls.py (la ruta real es 'password_recover'). Bug preexistente,
sin relacion con SEC-006. Se dejo una tarea aparte anotada (no parte de este lote).

## PENDIENTE DE INFRAESTRUCTURA (preexistente, confirmado por Jorge, no bloqueante para
## este lote pero SI bloqueante para que el flujo de recuperacion de contrasena funcione
## de verdad en cualquier ambiente)
SMTP no esta configurado (EMAIL_HOST/EMAIL_HOST_USER/EMAIL_HOST_PASSWORD en
nom035/settings.py apuntan a Gmail pero el envio real falla). Jorge menciono que hay
varias cosas por configurar, y que aparte ya se cambiaron RECAPTCHA_SITE_KEY y
RECAPTCHA_SECRET_KEY (variables de entorno relacionadas, movidas a env vars en el
Lote D). Configurar SMTP real es un prerequisito para que TANTO PasswordRecover como
EmailVerification funcionen end-to-end -- se sugiere agregarlo a la lista de pendientes
de infraestructura junto a INFRA-001 (Volume persistente Railway).

## LOTE O: COMPLETADO Y VALIDADO (dentro de lo verificable en este ambiente) -- LISTO
## PARA MERGE A auditoria-local
