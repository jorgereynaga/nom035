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

### Link "¿Olvidaste tu contraseña?" en auth-login.html — COMPLETADO ✅ (rama auditoria-local)
- `surveys/templates/auth-login.html` línea 207: `href="/forgot-password/"` (URL inexistente en nom035/urls.py, 404) → `href="{% url 'password_recover' %}"`, que resuelve a la ruta real `path('password_recover', PasswordRecover.as_view(), name='password_recover')`
- Confirmado visualmente con servidor local: clic en el link ya no da 404, carga correctamente la página "Recuperar contraseña" (formulario de email + botón "Enviar correo de recuperación")
- No requirió tocar views.py ni urls.py, cambio de una sola línea en el template

### Venv local reconstruido (worktree C:\NormaIA-Pruebas\nom035) — para no repetir la investigación
- Problema encontrado: `venv/Scripts/` existía pero estaba vacío (sin python.exe, pip.exe, activate) — venv corrupto, imposible levantar el servidor Django para pruebas visuales
- El sistema tiene Python 3.14 instalado (además del stub roto de Microsoft Store), pero Django 3.2 NO es compatible con Python 3.14 — hay que usar 3.10
- Solución: `py -3.10 -m venv venv` (lanzador `py` de Windows, seleccionando explícitamente 3.10.11) en vez de `python -m venv venv` a secas, que habría tomado la versión equivocada
- Después de recrear el venv, Git Bash seguía apuntando al python.exe viejo (cacheado) — hubo que correr `hash -r` para que bash resolviera de nuevo la ruta y encontrara el binario nuevo
- Ruta final correcta del intérprete: `C:\NormaIA-Pruebas\nom035\venv\Scripts\python.exe`
- `requirements.txt` se instaló limpio sin errores en el venv reconstruido; se confirmó que ya no incluye `conekta` (retirado en el Lote L)

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

# ============================================================
# LOTE P (credenciales SMTP hardcodeadas) — IMPLEMENTADO Y VALIDADO (sesion 18, cont.)
# Fecha: 17 Jul 2026
# ============================================================

## RESULTADO: LOTE P COMPLETO Y VALIDADO EN STAGING

Rama fix/lote-p-smtp-env-vars (a partir de auditoria-local, ya incluye el fix del link
roto de "Olvidaste tu contrasena" hecho en tarea aparte), implementada por Codex
siguiendo LOTE_P_especificacion_smtp_hardcoded.md.

### Contexto del hallazgo
Al intentar validar el flujo legitimo de PasswordRecover (Lote O) via correo real,
Jorge confirmo que el envio de correo en staging falla (error "no pudimos enviarte un
correo de confirmacion"). Diagnostico de Claude: la credencial de Gmail hardcodeada en
nom035/settings.py (EMAIL_HOST_USER/EMAIL_HOST_PASSWORD) SI es valida -- un login SMTP
de prueba contra smtp.gmail.com con esa credencial exacta funciono correctamente desde
fuera de Railway (LOGIN_OK). Esto descarta credencial revocada/incorrecta y apunta a
algo especifico del entorno de Railway (Google bloqueando la IP de Railway como inicio
de sesion sospechoso, o limite de Gmail SMTP para envio servidor-a-servidor) -- PENDIENTE
de que Jorge lo investigue por separado (revisar alertas de seguridad en la bandeja de
n035.ihes@gmail.com), fuera de alcance de este lote.

De paso se encontro que EMAIL_HOST_USER y EMAIL_HOST_PASSWORD (contrasena de aplicacion
real de Gmail) estaban hardcodeados en texto plano en el codigo fuente -- mismo patron
CWE-798 que AES_ENCRYPTION_KEY/RECAPTCHA_SECRET_KEY ya corregido en el Lote D, que
quedo fuera en ese momento.

### Cambio implementado
nom035/settings.py lineas 183-188: EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER,
EMAIL_HOST_PASSWORD, EMAIL_USE_TLS movidos a config() (python-decouple), mismo patron
exacto ya usado para AES_ENCRYPTION_KEY/RECAPTCHA_SECRET_KEY, con default= identico al
valor hardcodeado anterior -- CERO cambio de comportamiento mientras Railway no tenga
las variables de entorno configuradas.

### Validacion en staging
- Deploy limpio, gunicorn arriba sin errores
- Pagina de login renderiza normal (confirmado por Claude via navegador embebido) --
  sin regresion, tal como se esperaba de un cambio que solo mueve el origen del valor
- No se repitieron pruebas de envio de correo (ya se sabe que sigue fallando por la
  causa externa a Railway, sin relacion con este lote)

## PENDIENTE DE INFRAESTRUCTURA ACTUALIZADO
1. Jorge debe revisar alertas de seguridad en n035.ihes@gmail.com (posible bloqueo de
   Google al inicio de sesion desde la IP de Railway) -- si se resuelve, considerar
   configurar EMAIL_HOST_USER/EMAIL_HOST_PASSWORD reales en Railway (staging y
   produccion) usando las variables de entorno que ya existen desde este lote
2. Evaluar a futuro migrar a un proveedor de email transaccional dedicado (SendGrid,
   Mailgun, SES) si Gmail SMTP sigue siendo poco confiable -- no urgente
3. INFRA-001 (Volume persistente Railway) -- sigue sin resolver
4. PN-01 a 06 -- bloqueado, falta conectar proveedor de IA real

## LOTE P: COMPLETADO Y VALIDADO EN STAGING -- LISTO PARA MERGE A auditoria-local

# ============================================================
# LOTE Q (remitente SMTP hardcodeado + observabilidad) — IMPLEMENTADO Y VALIDADO (sesion 18, cont.)
# Fecha: 17 Jul 2026
# ============================================================

## RESULTADO: LOTE Q COMPLETO -- Y REVELO LA CAUSA REAL DE QUE SMTP NO FUNCIONE

Rama fix/lote-q-smtp-from-y-logging (a partir de auditoria-local), implementada por
Codex siguiendo LOTE_Q_especificacion_smtp_from_y_logging.md.

### Cambios implementados
1. nom035/settings.py: agregado DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL',
   default=EMAIL_HOST_USER) -- el remitente por default ahora siempre coincide con la
   cuenta que autentica, sin importar cual sea
2. surveys/views.py, send_mail(): from_email hardcodeado a 'IHES <n035.ihes@gmail.com>'
   (la cuenta VIEJA) reemplazado por f'NormaIA <{settings.DEFAULT_FROM_EMAIL}>' -- esto
   corrige el mismatch que causaba que Gmail rechazara el envio tras cambiar de cuenta
   en el Lote P (proteccion anti-spoofing de Gmail: remitente debe coincidir con quien
   autentica)
3. surveys/views.py: agregado logging real (p_.error(), logger ya existente en el
   archivo) en los 2 except: desnudos que envuelven especificamente las llamadas a
   send_mail() -- EmailVerification.post() (linea ~703) y PasswordRecover.post() (linea
   ~761, SOLO ese, no el que valida el codigo de recuperacion en la misma clase, ese
   sigue intacto sin loguear nada, es logica de seguridad del Lote O sin relacion)
   Antes: except: silencioso, CERO rastro en logs. Ahora: except Exception as e:
   p_.error(f"...: {e}") antes de mostrar el mismo mensaje generico al usuario

### VALIDACION EN STAGING -- HALLAZGO CRITICO DE INFRAESTRUCTURA CONFIRMADO
Al probar el flujo real de recuperacion de contrasena en staging (POST a
/password_recover con pruebaA@test.com), el request se quedo COLGADO ~2 minutos 20
segundos (sin responder), y el log de Railway (gracias al logging nuevo de este mismo
lote) finalmente mostro:

    Error enviando correo de recuperacion a pruebaA@test.com: [Errno 101] Network is unreachable

ESTO CAMBIA EL DIAGNOSTICO POR COMPLETO. NO es un problema de credenciales invalidas,
NI del remitente (aunque ese fix seguia siendo necesario y correcto de todas formas).
Es un error de RED A NIVEL DE SISTEMA OPERATIVO: Railway no puede establecer conexion
saliente hacia smtp.gmail.com:587 en absoluto. La prueba anterior de Claude (sesion
17) que dio "LOGIN_OK" fue ejecutada desde el sandbox local de Claude, CON salida a
internet sin restricciones -- NO representativa de la red real de Railway. Se descarta
la hipotesis de "Google bloqueo la IP de Railway como sospechosa".

Patron conocido: varias plataformas PaaS (Railway, Heroku, Render, etc.) bloquean por
defecto la salida por puertos SMTP crudos (25, 465, 587) como medida anti-spam,
mientras que la salida HTTPS (443) casi nunca se bloquea -- por eso los proveedores de
email transaccional (SendGrid, Mailgun, Postmark, SES, Resend) exponen API HTTPS en vez
de solo SMTP.

## DECISION DE JORGE
Dejar pendiente por ahora -- NO es bloqueante para el resto de la auditoria (SEC-006 ya
esta cerrado en el Lote O, independientemente de si el correo funciona). Cuando se
retome: opciones evaluadas fueron (1) migrar a proveedor de email transaccional via API
HTTPS -- la solucion mas probable de funcionar dado el error de red confirmado, pero
requiere mas trabajo (cuenta nueva, verificar dominio, adaptar send_mail() al
SDK/API del proveedor), o (2) confirmar con soporte/documentacion de Railway si el
egress SMTP se puede habilitar en el plan actual.

## PENDIENTE DE INFRAESTRUCTURA ACTUALIZADO
1. SMTP: confirmado que Railway bloquea o no puede alcanzar smtp.gmail.com:587 (Errno
   101, Network is unreachable) -- pendiente decidir entre migrar a proveedor via
   API HTTPS o gestionar habilitar el puerto con Railway
2. INFRA-001 (Volume persistente Railway) -- sigue sin resolver
3. PN-01 a 06 -- bloqueado, falta conectar proveedor de IA real

## LOTE Q: COMPLETADO Y VALIDADO EN STAGING (el logging cumplio su proposito de
## diagnostico exactamente como se penso) -- LISTO PARA MERGE A auditoria-local

# ============================================================
# LOTE R (PN-01 a PN-06, Perfil Narrativo IA) — IMPLEMENTADO Y VALIDADO (sesion 19)
# Fecha: 18 Jul 2026
# ============================================================

## RESULTADO: LOTE R COMPLETO Y VALIDADO EN STAGING CONTRA EL PROVEEDOR DE IA REAL

Rama fix/lote-r-perfil-narrativo (a partir de auditoria-local), implementada por Codex
siguiendo LOTE_R_especificacion_perfil_narrativo.md.

### Recuperacion de los hallazgos originales
Los 7 entregables originales de la auditoria (13 Jul 2026) se habian perdido del repo y
de su historial de git tras el incidente de seguridad. Se recuperaron los 6 hallazgos
PN-01 a PN-06 desde el registro local de sesiones de Codex
(~/.codex/sessions/2026/07/12/rollout-...jsonl), unica fuente que los conservaba
integros. El qa_tests/ local (scripts .py de las pruebas ya no existen, solo quedaron
.pyc compilados y JSON/capturas de resultados) sirvio como evidencia complementaria,
en particular un test de autorizacion horizontal sobre el perfil narrativo que resulto
INCONCLUSO (fallo de infraestructura del script, no revela vulnerabilidad) -- se
confirmo por separado que el ownership de GenerarPerfilNarrativoView SI esta bien
resuelto (candidate__user=request.user), no hay IDOR aqui.

### Cambios implementados (todos dentro de GenerarPerfilNarrativoView, surveys/psico_views.py)
1. PN-01 (respuesta vacia aceptada): se valida texto.strip() no vacio antes de guardar;
   si el proveedor devuelve vacio, error 502 controlado, perfil anterior no se toca
2. PN-02 (regeneracion sobrescribe sin historial) + PN-03 (sin timestamp): nuevo campo
   TestResult.perfil_narrativo_historial (JSONField, migracion manual 0039) -- cada
   generacion agrega una entrada con texto+timestamp+usuario_id+modelo, sin sobrescribir
   el historial; perfil_narrativo se mantiene como "el actual" para no romper
   psico_reporte.html
3. PN-04 (500 con texto de excepcion): logging real con p_.error() (logger nuevo en
   psico_views.py, mismo patron ya usado en views.py desde el Lote Q), respuesta al
   cliente generica sin str(e)
4. PN-05 (regeneraciones sin limite): tope duro de 5 regeneraciones por sesion +
   cooldown de 60 segundos entre generaciones, usando el mismo historial del punto 2
5. PN-06 (nombre del candidato en el prompt enviado al proveedor externo): quitado de
   las 5 variantes de prompt (disc/moss/raven/zavic/competencias-comercial), la
   variable candidato (linea 451 original) se elimino por completo, sin uso en ningun
   otro punto de la funcion

### Validacion en staging CONTRA EL PROVEEDOR DE IA REAL (Claude Haiku via Anthropic,
### ANTHROPIC_API_KEY configurada en Railway con credito)
No existe ningun boton/JS en ningun template que dispare esta vista -- se probo
posteando directo al endpoint. Se necesito un TestSession+TestResult sintetico (no
habia ninguno bajo las cuentas de prueba); se creo con Codex via TCP Proxy temporal de
Postgres de staging (mismo procedimiento ya documentado, con una cuenta nueva de Codex
por agotamiento de la anterior -- se le dieron instrucciones completas y autocontenidas
sin asumir contexto previo).
1. Generacion normal -> 200, texto real generado por Claude Haiku, CONFIRMADO que el
   texto no menciona el nombre del candidato en ningun punto (dice "el candidato"
   generico) -- PN-06 verificado con datos reales, no solo por inspeccion de codigo
2. Regeneracion inmediata (misma sesion, sin esperar) -> 429 "Espera un momento..." --
   cooldown de 60s confirmado
3. session_id inexistente (999999) -> 404 (tardo mas de lo normal por actividad del TCP
   proxy de Postgres activo en paralelo, pero resolvio correctamente, no hubo cuelgue
   real ni 500 -- confirmado revisando el network log despues de que la peticion
   completara en segundo plano)
4. Migracion 0039 aplicada limpio en el deploy de staging

## HALLAZGO NUEVO IMPORTANTE ENCONTRADO DURANTE ESTA VALIDACION (fuera de Lote R)
LoginView.post() (surveys/views.py, lineas 480-481) imprimia usuario Y CONTRASENA EN
TEXTO PLANO en cada intento de login exitoso -- confirmado en los logs de Railway
durante las pruebas de este lote (aparecieron las credenciales de pruebaA@test.com
literalmente en el log). CWE-532, presente desde siempre, sin relacion con este lote.
Corregido de inmediato por Claude (autorizado explicitamente por Jorge dado lo trivial
y de bajo riesgo del cambio: borrar 2 lineas print()) en rama aparte
fix/lote-s-credenciales-en-logs, pusheada, pendiente de merge.

## LOTE R: COMPLETADO Y VALIDADO EN STAGING CONTRA EL PROVEEDOR DE IA REAL -- LISTO
## PARA MERGE A auditoria-local

# ============================================================
# LOTE S (CWE-532, credenciales en logs) — IMPLEMENTADO Y VALIDADO (sesion 19, cont.)
# Fecha: 18 Jul 2026
# ============================================================

## RESULTADO: LOTE S COMPLETO Y VALIDADO EN STAGING

Rama fix/lote-s-credenciales-en-logs (a partir de auditoria-local). Fix implementado
directamente por Claude (autorizado explicitamente por Jorge dado lo trivial y de bajo
riesgo del cambio), no via Codex -- unico lote de esta sesion con esa excepcion.

### Hallazgo
Encontrado por accidente durante la validacion del Lote R: LoginView.post()
(surveys/views.py, lineas 480-481) imprimia usuario Y CONTRASENA EN TEXTO PLANO en cada
intento de login exitoso via print(us)/print(pw). Confirmado en los logs reales de
Railway durante las pruebas de este lote -- aparecieron las credenciales de
pruebaA@test.com literalmente. CWE-532, presente desde siempre en el codigo original,
sin relacion con ningun lote anterior. ApiLoginView (la otra vista de login) confirmada
limpia, sin el mismo problema.

### Cambio implementado
Eliminadas las 2 lineas print(us)/print(pw) en LoginView.post(). Sin ningun otro
cambio -- el resto del flujo de autenticacion (authenticate(), login(), validacion de
email) queda identico.

### Validacion en staging
- Deploy limpio, gunicorn arriba sin errores
- Login confirmado funcionando exactamente igual que antes (POST a /login/ con
  pruebaA@test.com -> 200, redirige a /main) -- sin regresion de comportamiento
- grep confirmo que no queda ningun otro print() de credenciales en el resto del
  proyecto

## LOTE S: COMPLETADO Y VALIDADO EN STAGING -- LISTO PARA MERGE A auditoria-local

# ============================================================
# LOTE T (INFRA-001, Volume persistente Railway) — IMPLEMENTADO Y VALIDADO (sesion 20)
# Fecha: 18-19 Jul 2026
# ============================================================

## RESULTADO: LOTE T COMPLETO Y VALIDADO EN STAGING -- HALLAZGO INFRA-001 CERRADO

Rama fix/lote-t-infra001-volumen-persistente (a partir de auditoria-local). Fix
implementado directamente por Claude (mismo criterio que el Lote S: cambio chico,
mismo patron config()+default= ya usado en Lotes D/P/Q), coordinado en tiempo real
con Jorge mientras configuraba el Volume en el dashboard de Railway.

### Contexto
Railway solo permitio adjuntar UN volumen por servicio via el flujo de "clic derecho
en canvas -> New -> Volume" (el menu de creacion rapida no vuelve a ofrecer "Volume"
como tipo despues del primero). Esto obligo a resolver como acomodar dos rutas
distintas (MEDIA_ROOT publico y PROTECTED_MEDIA_ROOT protegido, separados
deliberadamente desde el Lote C2 para cerrar EVI-SEC-001) dentro de un solo punto de
montaje, SIN reintroducir la vulnerabilidad de archivos protegidos servidos sin
autenticacion. Se confirmo antes de tocar nada: MEDIA_ROOT se sirve publico y sin auth
via urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
(nom035/urls.py linea 128, sin guard de DEBUG), mientras PROTECTED_MEDIA_ROOT nunca
tiene URL publica, solo se accede via las 3 vistas @login_required del Lote C2.

### Cambio implementado
nom035/settings.py: nueva variable PERSISTENT_STORAGE_ROOT = config('PERSISTENT_STORAGE_ROOT',
default=BASE_DIR) -- MEDIA_ROOT y PROTECTED_MEDIA_ROOT ahora son subcarpetas
(media/ y files/ respectivamente) DENTRO de ese unico punto de montaje, preservando
la separacion logica y de seguridad exacta que ya existia (siguen siendo carpetas
distintas, solo que ahora ambas viven sobre el mismo volumen fisico). Default=BASE_DIR
preserva el comportamiento actual en cualquier ambiente sin la variable configurada
(mismo patron ya usado en Lotes D/P/Q).

### Configuracion de infraestructura (Jorge, en Railway)
1. Volume creado y adjuntado al servicio nom035 (staging), Mount Path = /data
2. Variable de entorno PERSISTENT_STORAGE_ROOT=/data agregada en el servicio nom035
3. Deploy de la rama fix/lote-t-infra001-volumen-persistente

### Validacion en staging -- PRUEBA REAL DE PERSISTENCIA ANTE REDEPLOY
1. Deploy inicial: log confirma "Mounting volume on: /var/lib/containers/.../vol_hbp4g9magfmavzjr",
   gunicorn arranca limpio
2. Subida de archivo de prueba (logo, PNG de 70 bytes) via POST directo a /edit_profile/
   (login via fetch con pruebaA@test.com) -> 200
3. Descarga confirmada via /descargar/logo/ (vista protegida del Lote C2) -> 200,
   image/png, 70 bytes exactos
4. REDEPLOY manual disparado en Railway (mismo codigo, sin push nuevo) -- log confirma
   mismo volumen montado (mismo ID vol_hbp4g9magfmavzjr), gunicorn arranca limpio
5. Descarga repetida DESPUES del redeploy -> 200, mismos 70 bytes exactos -- CONFIRMADO
   que el archivo sobrevivio el redeploy, la causa raiz de INFRA-001 (perdida de
   archivos en cada redeploy) esta resuelta

## PENDIENTE ACTUALIZADO
1. Repetir el mismo Volume + variable de entorno en el servicio de PRODUCCION cuando
   se decida llevar el proyecto a produccion real (este lote y su validacion fueron
   unicamente en staging, como el resto de la auditoria)
2. SMTP -- sigue pendiente, bloqueo de red Railway->Gmail, decision de Jorge de dejarlo
   pendiente
3. PN-01 a 06 -- ya resueltos (Lote R), no hay pendiente activo de Perfil Narrativo
4. Limpiar el archivo de prueba subido (test_volumen.png) en algun momento -- no es
   sensible, es solo un pixel de prueba, no urgente

## LOTE T: COMPLETADO Y VALIDADO EN STAGING (persistencia ante redeploy confirmada con
## prueba real) -- LISTO PARA MERGE A auditoria-local

# ============================================================
# DESPLIEGUE A PRODUCCION — REMEDIACION COMPLETA DE AUDITORIA APLICADA (sesion 20, cierre)
# Fecha: 19 Jul 2026
# ============================================================

## RESULTADO: auditoria-local FUSIONADA A main Y DESPLEGADA A PRODUCCION (Railway) --
## VALIDADA EN VIVO

### Merge a main
1. Confirmado antes de tocar nada: el auto-deploy del servicio `production` en Railway
   estaba pausado manualmente por Jorge -- el push a main no iba a disparar deploy
   automatico
2. git checkout main && git pull && git merge auditoria-local -- SIN CONFLICTOS (main
   no tenia ningun commit propio, 70 commits de diferencia, todos de auditoria-local)
3. Push a origin/main confirmado (379861da..4e975431)
4. Verificado que los commits de todos los lotes (A a T, incluyendo el fix critico de
   PasswordRecover del Lote O y la eliminacion de Conekta del Lote L) estan presentes
   en main

### Deploy manual a produccion (Jorge, deliberado)
1. Primer deploy: migraciones 0037/0038/0039 aplicadas por primera vez en la base de
   datos de produccion (nunca habian corrido ahi), gunicorn arranco limpio
2. Variables de entorno configuradas en el servicio `production` de Railway:
   - AES_ENCRYPTION_KEY: nueva llave aleatoria de 32 caracteres (AES-256) generada por
     Claude con secrets.choice, distinta a la de prueba/staging
   - RECAPTCHA_SITE_KEY / RECAPTCHA_SECRET_KEY: nuevas, generadas por Jorge en la
     consola de reCAPTCHA para el dominio de produccion (035.ihes.mx)
   - EMAIL_HOST_USER=normaia.sistemas@gmail.com, EMAIL_HOST_PASSWORD= App Password de
     Gmail (cuenta con 2FA activado, contraseña de aplicacion generada especificamente)
   - ANTHROPIC_API_KEY: misma llave que staging (decision de Jorge, reusar en vez de
     separar, credito compartido entre ambos ambientes)
   - PENDIENTE: PERSISTENT_STORAGE_ROOT + Volume en produccion -- Jorge planea migrar
     produccion real a un VPS de DigitalOcean pronto, en un VPS tradicional (git pull +
     reiniciar proceso) el disco es persistente por defecto y este Volume de Railway
     NO hace falta ahi -- se decidio no configurar Volume en Railway production dado
     que es una situacion temporal antes de la migracion a DO
3. Segundo deploy (para recoger las variables nuevas): limpio, sin migraciones nuevas
   (ya aplicadas), gunicorn arranco sin errores

### Validacion en produccion real (Codex + Jorge)
1. Codex intento registrar una cuenta de prueba via automatizacion en
   https://nom035-production.up.railway.app/newuser/ -> fallo con "Solicitud denegada"
   -- diagnosticado por Claude leyendo el codigo real (UserappList.post()): ese mensaje
   especifico solo ocurre cuando reCAPTCHA responde success=true pero score<=0.5 (NO es
   el mensaje de llaves mal configuradas, que seria "El captcha no es valido") --
   comportamiento esperado de reCAPTCHA v3 detectando trafico de navegador automatizado,
   no un bug de la configuracion nueva
2. Jorge probo el mismo registro manualmente (navegador humano normal) -> EXITOSO,
   cuenta creada sin problema -- CONFIRMA que las llaves de reCAPTCHA nuevas de
   produccion estan correctamente configuradas y funcionando

## ESTADO FINAL: PRODUCCION (Railway, dominio 035.ihes.mx / nom035-production.up.railway.app)
## CORRIENDO LA REMEDIACION COMPLETA DE LA AUDITORIA, CON VARIABLES DE ENTORNO REALES,
## VALIDADA CON REGISTRO DE USUARIO REAL EXITOSO

## PENDIENTES RESTANTES
1. SMTP en produccion: mismo riesgo que en staging (posible bloqueo de puerto 587 en
   Railway) -- AUN NO PROBADO en produccion end-to-end (recuperacion de contrasena /
   verificacion de correo reales). Jorge planea migrar a un VPS de DigitalOcean donde
   este problema probablemente no exista (los VPS tradicionales no suelen bloquear
   SMTP saliente) -- pendiente confirmar una vez ahi
2. Migracion futura a VPS de DigitalOcean: cuando este listo, replicar las mismas
   variables de entorno (pueden reusarse los mismos valores) en el nuevo .env, ajustar
   DATABASE_URL y ALLOWED_HOSTS al nuevo host -- PERSISTENT_STORAGE_ROOT no necesario
   ahi (disco persistente por defecto en VPS tradicional)
3. Decision pendiente sin resolver: db.sqlite3 y carpeta media/ trackeados en el
   historial de git (contienen PDFs reales de clientes de prueba) -- hallazgo anotado
   hace varias sesiones, nunca atacado, sigue ahi
4. Considerar generar RECAPTCHA_SECRET_KEY/SITE_KEY separadas para staging tambien (hoy
   staging sigue usando las llaves viejas por default, que ya estaban expuestas
   publicamente en el codigo original) -- no urgente, staging no es produccion real

# ============================================================
# LOTE U (contraste de texto en tarjetas de dimension, dashboard) — IMPLEMENTADO Y VALIDADO (sesion 20, cont.)
# Fecha: 19 Jul 2026
# ============================================================

## RESULTADO: LOTE U COMPLETO Y VALIDADO -- FIX VISUAL, SIN RELACION CON LA AUDITORIA

Rama fix/lote-u-contraste-dashboard (a partir de auditoria-local). Hallazgo reportado
por Jorge (screenshot), no parte de los hallazgos de seguridad.

### Hallazgo
En surveys/templates/index.html, las tarjetas de "Dimensiones de riesgo" (dashboard
NOM-035) y "Dimensiones de clima" (Clima Laboral) usaban el mismo color saturado del
nivel de riesgo tanto para el fondo/borde de la tarjeta COMO para el texto del valor y
la etiqueta -- para el nivel "Medio" ese color es #ffff00 (amarillo puro), casi
ilegible sobre el fondo claro tintado al 20%.

### Cambio implementado
- Quitados los estilos inline style="color:{{dim.color}}" de .dim-card-val y .dim-badge
  en los 2 bloques (dimensions_preview y climate_dimensions_preview)
- Agregado color: var(--text-primary) (#0f172a, mismo color ya usado en el resto del
  dashboard) a ambas clases CSS
- El fondo tintado (background-color:{{dim.color}}33) y el borde izquierdo
  (border-left-color:{{dim.color}}) del .dim-card NO se tocaron -- siguen codificando
  visualmente el nivel de riesgo, solo el texto encima se volvio siempre legible

### LECCION TECNICA -- bug detectado en revision de diff antes de aprobar
El primer intento de Codex agrego correctamente color: var(--text-primary) a
.dim-card-val, pero en .dim-badge la regla CSS YA TENIA una linea color: inherit;
preexistente MAS ABAJO en el mismo bloque -- en CSS, cuando hay 2 declaraciones color
en la misma regla, gana la que aparece despues en el codigo, asi que color: inherit
anulaba silenciosamente el fix nuevo. Antes no importaba porque el style inline (mayor
especificidad) siempre ganaba sobre cualquier CSS de clase; al quitar el inline, el
conflicto preexistente salio a la luz. Se le pidio a Codex un segundo pase para
eliminar esa linea color: inherit; sobrante -- confirmado con grep que la regla quedo
con una sola declaracion de color.

### Validacion en staging
Deploy limpio. Login via fetch + navegacion a /main confirmados. Estilos computados
verificados directo en el navegador (mas confiable que una captura visual): tanto
.dim-badge como .dim-card-val devuelven color: rgb(15, 23, 42) (#0f172a) de forma
incondicional, sin importar el nivel de riesgo mostrado -- confirma que el fix ya no
depende del color del nivel en absoluto.

## LOTE U: COMPLETADO Y VALIDADO EN STAGING -- LISTO PARA MERGE A auditoria-local

# ============================================================
# LOTE V (texto de botones Metodos de pago / Mis pagos) — IMPLEMENTADO Y VALIDADO (sesion 21)
# Fecha: 19 Jul 2026
# ============================================================

## RESULTADO: LOTE V COMPLETO Y VALIDADO -- CAMBIO DE TEXTO, SIN RELACION CON LA AUDITORIA

Rama fix/lote-v-texto-boton-pagos (a partir de auditoria-local). Pedido directo de
Jorge: el texto "en Stripe" en los botones de Configuracion -> Metodos de pago / Mis
pagos sobraba (aunque funcionalmente si va a Stripe).

### Cambio implementado
surveys/templates/edit_profile.html:
- "Administrar métodos de pago en Stripe" -> "Administrar métodos de pago"
- "Consultar pagos en Stripe" -> "Consultar pagos"
Solo el texto visible de los 2 botones, href intactos (siguen apuntando a
{% url 'stripe_portal' %}). Los subtitulos/parrafos descriptivos que tambien
mencionan "Stripe" arriba de los botones NO se tocaron (Jorge solo pidio el texto
de los botones).

### Validacion en staging
Deploy limpio. Confirmado con fetch directo al HTML real servido por
/edit_profile/ (logueado como pruebaA@test.com): los 2 botones muestran
exactamente "Administrar métodos de pago" y "Consultar pagos", con
href="/stripe/portal/" sin cambios.

## LOTE V: COMPLETADO Y VALIDADO EN STAGING -- LISTO PARA MERGE A auditoria-local

# ============================================================
# DASHBOARD DE METRICAS DE NEGOCIO — ESPECIFICACION COMPLETADA (sesion 15/16)
# Fecha: 19 Jul 2026
# ============================================================

## Iniciativa nueva, independiente del trabajo de auditoria — NO bloquea produccion

Vista interna protegida (is_superuser), solo para Jorge, con metricas de negocio:
usuarios registrados, clientes historicos vs activos, desglose/distribucion de
planes, MRR estimado, profundidad de uso (centros activos + evaluaciones
completadas por cliente de pago).

Investigacion completa hecha, especificacion escrita en
DASHBOARD_especificacion_metricas_negocio.md (raiz del repo, rama
feature/dashboard-metricas-negocio). Cubre:

1. Modelo nuevo PlanPurchaseEvent (append-only, precio/periodo como snapshot)
   + migracion manual 0040_plan_purchase_event.py (dependencia: 0039)
2. Un solo PlanPurchaseEvent.objects.create() nuevo dentro de
   _handle_checkout_completed (surveys/stripe_views.py) -- cero cambios a
   _activate_plan, _handle_invoice_paid, _handle_payment_failed,
   _handle_subscription_change. El objetivo es que el historico sobreviva a la
   cancelacion (hoy _handle_subscription_change vacia stripe_plan_key y se
   pierde el rastro)
3. DashboardMetricasView nueva (surveys/dashboard_views.py, archivo nuevo),
   UserPassesTestMixin + is_superuser (403 real, no URL oculta)
4. Template standalone dashboard_metricas.html (deliberadamente sin
   {% extends 'index.html' %} para evitar el bug de bloques Django ya
   documentado abajo en este archivo) + Chart.js via CDN (no habia libreria de
   graficas instalada en el proyecto)
5. URL /metricas/, import explicito nuevo en nom035/urls.py (mismo patron que
   psico_views, para no repetir el bug del NameError en Railway)

Decisiones de diseno explicitas (confirmar al revisar el diff):
- Se excluyen cuentas is_staff/is_superuser de todas las metricas de clientes
- El rango de fechas filtra "usuarios registrados" y "compraron alguna vez",
  pero NO "plan activo ahora"/MRR/distribucion de planes (son snapshot del
  momento actual)
- Renovaciones (invoice.paid) NO generan evento nuevo en esta version, fuera
  de alcance
- Sin link en el sidebar hacia /metricas/ salvo que Jorge lo pida

## PENDIENTE INMEDIATO
1. Pasarle DASHBOARD_especificacion_metricas_negocio.md a Codex con
   instruccion explicita de implementar (sobre esta misma rama o una nueva
   derivada, segun decida Jorge)
2. Revisar diff, probar en staging (Stripe test mode: simular compra,
   confirmar 1 fila nueva en PlanPurchaseEvent + activacion de plan sin
   cambios; simular cancelacion, confirmar que el historico sobrevive)
3. Diseño visual de dashboard_metricas.html con Replit -- prompt aun no
   escrito, pendiente hasta que el esqueleto funcional este confirmado

# ============================================================
# DASHBOARD DE METRICAS DE NEGOCIO — IMPLEMENTADO Y VALIDADO EN STAGING
# Fecha: 20 Jul 2026
# ============================================================

## NOTA DE PROCESO: Codex sin cuota hasta 26 Jul 2026 (ambas cuentas, solo este proyecto)
Este lote se implemento con Claude aplicando el codigo directamente (en vez de
Codex), con autorizacion explicita de Jorge como modo de trabajo temporal
mientras Codex no este disponible. El resto del flujo (Jorge revisa diff antes
de cada commit, validacion en staging antes de merge) se mantuvo sin cambios.

## Implementacion completa en feature/dashboard-metricas-negocio-impl
- surveys/models.py: PlanPurchaseEvent (append-only) + migracion manual 0040
- surveys/stripe_views.py: 1 solo create() nuevo en _handle_checkout_completed,
  cero cambios al resto de _activate_plan/_handle_invoice_paid/etc
- surveys/dashboard_views.py (nuevo): DashboardMetricasView, LoginRequiredMixin
  + UserPassesTestMixin (is_superuser)
- surveys/templates/dashboard_metricas.html (nuevo): standalone, Chart.js via CDN
- nom035/urls.py: import explicito + path('metricas/', ...)

## BUG encontrado y corregido durante validacion en staging
DashboardMetricasView tenia `raise_exception = True` a nivel de clase. Como
LoginRequiredMixin y UserPassesTestMixin comparten el atributo raise_exception
(ambos heredan de AccessMixin), esto causaba que un usuario ANONIMO recibiera
403 directo en vez de ser redirigido a /login/ -- confirmado en staging antes
del fix (GET /metricas/ -> 403 sin sesion).

FIX: se quito raise_exception de la clase y se sobreescribio handle_no_permission()
para diferenciar los 2 casos (no autenticado -> redirect normal a login_url,
autenticado pero no superuser -> PermissionDenied real). Confirmado en staging
despues del fix: GET /metricas/ sin sesion -> GET /login/?next=/metricas/ -> 200.

## Validacion completa en staging (nom035-staging.up.railway.app), 3 casos
1. Anonimo -> redirige a /login/?next=/metricas/ (corregido, ver bug arriba)
2. Autenticado, no-superuser (pruebaB@test.com) -> 403 correcto
3. Autenticado, superuser (admin) -> 200, datos correctos (3 usuarios
   registrados, 0 compraron/activos ya que staging no tiene compras Stripe
   reales todavia -- coherente con PlanPurchaseEvent vacio)

## HALLAZGO NUEVO, preexistente, NO corregido en este lote
Durante la validacion se encontro que `/login/` (LoginView.post(),
surveys/views.py:481) hace `user.userapp.validated_email` sin verificar que
el Userapp exista. Cualquier cuenta is_staff/is_superuser creada via
createsuperuser (sin pasar por el registro de clientes) no tiene Userapp,
y el login normal por /login/ truena con una excepcion no controlada en vez
de un error claro (se vio como que "se queda pensando"). Workaround usado
para probar como superuser: loguearse por /ihes_admin/ (no depende de
Userapp) y navegar directo a la URL protegida en la misma sesion. Pendiente
de decidir si se agrega a la matriz de hallazgos para un lote futuro.

## PENDIENTE INMEDIATO
1. Merge feature/dashboard-metricas-negocio-impl -> auditoria-local
2. Diseño visual de dashboard_metricas.html con Replit -- prompt aun no escrito
3. Decidir si el hallazgo de Userapp/login de superusuarios entra a la matriz
   de hallazgos como un lote futuro

# ============================================================
# HALLAZGO NUEVO, CRITICO: SEC-009 — Webhook de Stripe duplicado,
# la implementacion "correcta" nunca se ejecuta
# Fecha: 20 Jul 2026
# ============================================================

Encontrado durante el trabajo del dashboard de metricas de negocio (rama
auditoria-local), independiente de ese lote. Registrado tambien en
MATRIZ_CONSOLIDADA_POST_REMEDIACION.md como SEC-009. Confirmado en codigo
real, presente tambien en main (produccion). AUN NO CORREGIDO -- solo
diagnosticado, pendiente de decidir cuando atacarlo.

## El problema

nom035/urls.py registra la ruta /stripe/webhook/ TRES veces (lineas 39, 114,
136 al momento de este hallazgo). Django usa el primer patron que hace
match -- la linea 39, que apunta a una funcion stripe_webhook() en
surveys/views.py:2562. Esto significa que la clase StripeWebhookView completa
(surveys/stripe_views.py) NUNCA se ejecuta con un webhook real de Stripe --
es codigo muerto, a pesar de que parece la implementacion "oficial" (con
metodos separados para cada tipo de evento).

## Como se llego a este estado (investigacion de historial)

git log --oneline -- surveys/views.py filtrado por "webhook"/"credit"/"stripe":
- 12 may 2026: se integro Stripe con clases (stripe_views.py)
- 22-30 may 2026: sesion de depuracion (commits "force user for webhook test",
  "debug webhook completo", "fix: reescribir stripe_webhook limpio") que
  termino escribiendo una funcion nueva y paralela directo en views.py, con
  su propio sistema de creditos (assign_nom035_credits() en
  surveys/services/credits.py, usa nom035_creditos/psico_evaluaciones_disponibles)
  -- distinto al sistema que usa la clase muerta (workplaces_available/B/C)
- Esa funcion quedo registrada ANTES en urls.py y es la que corre en
  produccion hoy

## Problemas concretos de la funcion activa (surveys/views.py:2562)

1. Solo maneja checkout.session.completed. No maneja invoice.paid,
   invoice.payment_failed, ni customer.subscription.deleted/updated -- las
   cancelaciones de suscripcion probablemente nunca se procesan en
   produccion: un cliente que cancela en Stripe seguiria con su plan activo
   indefinidamente en el sistema.
2. Fallback peligroso: si no encuentra al usuario comprador
   (User.objects.get(id=user_id) o por email falla), hace
   user = User.objects.first() -- asignaria el plan pagado al PRIMER usuario
   cualquiera de toda la base de datos.
3. Tiene print() con emojis como unico logging (sin logger), leftover de
   depuracion.
4. Codigo duplicado/paralelo a StripeWebhookView, que ademas tiene un modelo
   de creditos distinto e incompatible (workplaces_available vs
   nom035_creditos) -- riesgo de confusion para cualquiera que edite
   stripe_views.py pensando que esta tocando codigo vivo.

## Nota importante -- que SI esta bien

El campo Userapp.stripe_plan_key/psico_plan_key SI se actualiza
correctamente en la funcion activa, asi que cualquier logica que dependa
solo de ese campo (ej. el dashboard de metricas de negocio, PlanPurchaseEvent)
NO se ve afectada. El problema es especifico a: cancelaciones sin procesar,
el fallback peligroso, y el hecho de que StripeWebhookView es enteramente
codigo muerto.

## Pendiente de decidir (para cuando se ataque este hallazgo)

Dos caminos posibles, requiere pensarlo con cuidado porque toca el webhook
que sirve compras reales:
(a) Eliminar StripeWebhookView y las 2 rutas duplicadas, migrando cualquier
    logica util (manejo de invoice.paid/payment_failed/cancelaciones) a la
    funcion activa en views.py
(b) Al reves: limpiar la funcion de views.py y hacer que las 3 rutas apunten
    unicamente a StripeWebhookView, migrando assign_nom035_credits y el
    fallback seguro ahi

Su propio lote, su propia rama, validacion completa en staging con Stripe
test mode antes de tocar main.

# ============================================================
# SEC-009 CORREGIDO Y VALIDADO EN STAGING (opcion a)
# Fecha: 20 Jul 2026
# ============================================================

## NOTA DE PROCESO
Igual que el lote del dashboard de metricas: Claude aplico el codigo
directamente (Codex sin cuota hasta 26 Jul 2026), con autorizacion explicita
de Jorge. Rama: fix/sec-009-stripe-webhook-duplicado, partiendo de
auditoria-local actualizada.

## Decision de diseno confirmada con Jorge antes de implementar
Se eligio la opcion (a): conservar y arreglar la funcion activa
stripe_webhook() en views.py (porque ya alimenta nom035_creditos/
psico_evaluaciones_disponibles, el sistema de creditos REALMENTE consumido
por la app -- confirmado revisando donde se LEE cada campo, no solo donde
se escribe: nom035_creditos se usa en surveys/views.py lineas 318, 802,
1062, 2761, 2777; workplaces_available solo se mostraba en contexto de
plantilla, su unico punto de decremento estaba comentado). Se elimino
StripeWebhookView (codigo muerto, usaba el sistema de creditos incorrecto/
no consumido) y las 2 rutas duplicadas en urls.py.

Sobre cancelaciones (customer.subscription.deleted/updated), Jorge eligio
explicitamente: solo limpiar stripe_plan_key/psico_plan_key (que deje de
verse como "con plan activo"), SIN tocar creditos ya otorgados -- el
cliente conserva lo que pago hasta agotarlo, pero no se le renueva.

## Cambios aplicados
- nom035/urls.py: eliminadas las 2 rutas duplicadas de /stripe/webhook/ y
  el import de StripeWebhookView; queda 1 sola ruta activa (linea 39)
- surveys/stripe_views.py: eliminada la clase StripeWebhookView completa
  (codigo muerto) + imports que quedaron sin uso (HttpResponse,
  method_decorator, csrf_exempt, PRICE_ID_TO_PLAN)
- surveys/views.py, stripe_webhook(): funcion dividida en helpers
  (_stripe_handle_checkout_completed, _stripe_handle_invoice_paid,
  _stripe_handle_payment_failed, _stripe_handle_subscription_change):
  - print() con emojis reemplazado por logging real (p_.info/warning/error)
  - Eliminado el fallback peligroso `User.objects.first()`: ahora si no se
    encuentra al comprador, se loguea con p_.error() y se ignora el evento
    (nadie recibe un plan que no compro)
  - invoice.paid: re-acredita SOLO si billing_reason=='subscription_cycle'
    (evita doble acreditacion en la factura inicial, que ya se acredito via
    checkout.session.completed)
  - invoice.payment_failed: logueado como warning, sin desactivar acceso
    (mismo comportamiento no-destructivo que tenia el codigo muerto)
  - customer.subscription.deleted/updated: si status en
    canceled/unpaid/past_due, limpia stripe_plan_key y psico_plan_key,
    creditos existentes intactos (decision de Jorge arriba)
  - Se incorporo tambien un cambio que ya estaba sin commitear en el
    working tree (PlanPurchaseEvent.objects.create() dentro de esta misma
    funcion, agregado en sesion anterior para que el dashboard de metricas
    reciba compras reales) -- se fusiono directo en la reescritura en vez
    de tratarlo aparte, avisado a Jorge antes de continuar
- Confirmado con grep: ningun template ni reverse() dependia del nombre de
  URL 'stripe_webhook' de la ruta eliminada -- Stripe llama la URL directo
  por path, no por nombre

## LIMITACION CONOCIDA, no resuelta en este lote (preexistente, heredada del diseno original)
Userapp solo trackea UN stripe_subscription_id/plan a la vez de forma
ambigua entre modulos: si un usuario tiene stripe_plan_key Y psico_plan_key
ambos activos (ej. compro NOM-035 Y psicometria por separado), una renovacion
(invoice.paid, subscription_cycle) solo puede re-acreditar uno de los dos
(se prioriza stripe_plan_key). Confirmado en pruebas: no se recreditó
psico_starter en el escenario de 2 planes simultaneos. El codigo muerto
(StripeWebhookView) tenia la MISMA limitacion (solo leia stripe_plan_key,
nunca psico_plan_key, en _handle_invoice_paid) -- no es una regresion de
este lote, es un limite del modelo de datos actual (un solo
stripe_subscription_id por Userapp). Pendiente de decidir si se rediseña
a futuro (ej. subscription_id separado por modulo) si Jorge empieza a
vender NOM-035 + psicometria como suscripciones independientes en vez de
via el plan "suite".

## Validacion completa en staging (Stripe test mode, sk_test_/whsec_ confirmados)
Deploy limpio en Railway (Source cambiado temporalmente a la rama del lote,
gunicorn arriba sin errores nuevos). Se creo un usuario de prueba con
Userapp (staging.test@normaia.mx, ver nota abajo) y se simularon 8 eventos
firmados criptograficamente igual que Stripe real (HMAC-SHA256 con el
STRIPE_WEBHOOK_SECRET real de staging), enviados directo al endpoint:

1. checkout.session.completed, usuario valido, plan nom035_pyme -> HTTP 200,
   +50 nom035_creditos, stripe_plan_key='nom035_pyme', stripe_customer_id y
   stripe_subscription_id guardados, PlanPurchaseEvent creado
2. checkout.session.completed, usuario INEXISTENTE (id y email invalidos)
   -> HTTP 200, evento ignorado, log p_.error() con el detalle, NINGUN
   usuario recibio credito (confirma que el fallback peligroso ya no existe)
3. checkout.session.completed, plan psico_starter -> HTTP 200,
   +20 psico_evaluaciones_disponibles, psico_plan_key='psico_starter'
4. invoice.paid, billing_reason=subscription_create -> HTTP 200, NO
   acredito (confirma que no hay doble acreditacion en la factura inicial)
5. invoice.paid, billing_reason=subscription_cycle -> HTTP 200, +50
   nom035_creditos adicionales (renovacion), confirmando el mecanismo de
   renovacion funciona (ver limitacion conocida arriba sobre cual plan
   se re-acredita cuando hay 2 activos)
6. invoice.payment_failed -> HTTP 200, logueado como warning, sin cambios
   de estado
7. customer.subscription.deleted, status=canceled -> HTTP 200,
   stripe_plan_key y psico_plan_key limpiados a '', nom035_creditos
   (100) y psico_evaluaciones_disponibles (20) INTACTOS -- exactamente el
   comportamiento que Jorge eligio
8. Firma invalida (secret incorrecto) -> HTTP 400, rechazado correctamente

Todos los resultados verificados directo en base de datos (no solo el
HTTP status), via TCP Proxy temporal en Postgres de staging (creado,
usado, eliminado). Usuario de prueba reseteado a estado neutro
(0 creditos, sin plan, sin customer_id) al terminar, para dejarlo limpio
para pruebas futuras de la otra sesion de Claude.

NOTA: se encontro que el usuario staging.test@normaia.mx (creado en sesion
anterior para pruebas manuales) no tenia Userapp asociado -- mismo patron
del hallazgo ya documentado sobre LoginView.post() y superusuarios sin
Userapp. Se le creo un Userapp minimo para poder correr estas pruebas.

## Commit local (aun NO pusheado a auditoria-local ni main)
Rama fix/sec-009-stripe-webhook-duplicado, 1 commit:
"Fix SEC-009: eliminar webhook de Stripe duplicado y codigo muerto"
(nom035/urls.py, surveys/stripe_views.py, surveys/views.py)

## PENDIENTE INMEDIATO
1. Jorge revisa el diff final del commit antes de decidir merge a
   auditoria-local
2. Actualizar MATRIZ_CONSOLIDADA_POST_REMEDIACION.md: SEC-009 pasa de
   Pendiente a Corregido (pendiente hasta que se confirme el merge)
3. Considerar si la limitacion conocida (renovacion con 2 planes
   simultaneos) amerita su propio hallazgo/lote a futuro

# ============================================================
# DASHBOARD DE METRICAS DE NEGOCIO — PROYECTO COMPLETO CERRADO EN PRODUCCION
# Fecha: 21 Jul 2026
# ============================================================

## Resumen ejecutivo
Iniciativa completa: vista interna `/metricas/` (protegida por is_superuser)
con KPIs de negocio, mas la vista hermana `/metricas/clientes/`. Ya esta
en produccion, mergeada y validada.

## Cronologia completa (para referencia futura)
1. v1 -- KPIs base: usuarios registrados, compraron alguna vez, clientes
   activos, MRR estimado, distribucion de planes, profundidad de uso
   (centros activos + evaluaciones NOM-035/psicometria por cliente activo).
   Requirio el modelo nuevo PlanPurchaseEvent (append-only) para poder medir
   "compro alguna vez" incluso despues de que el cliente cancela.
2. SEC-009 (hallazgo encontrado en el camino, no parte original del dashboard):
   /stripe/webhook/ estaba registrado 3 veces en urls.py, la implementacion
   "correcta" (StripeWebhookView) nunca se ejecutaba con webhooks reales.
   Diagnosticado, corregido (se elimino el codigo muerto y las rutas
   duplicadas, se limpio la funcion activa en views.py: logging real,
   fallback peligroso eliminado, manejo de invoice.paid/payment_failed/
   subscription_change agregado), validado con 8 eventos de Stripe test
   mode firmados criptograficamente contra la BD de staging.
3. v2 -- Linea de tiempo de suscripciones nuevas por periodo (granularidad
   automatica dia/semana segun el rango de fechas ya existente), usando
   PlanPurchaseEvent.record_create.
4. v3 -- Listado de clientes (/metricas/clientes/): todos los usuarios
   registrados con 3 estados (Activo/Cancelado/Nunca compro) + plan
   contratado (actual o el ultimo antes de cancelar) + busqueda/filtros
   en tiempo real (JS puro, sin backend). Se extrajo SuperuserRequiredMixin
   compartido entre las 2 vistas del dashboard.
5. Rediseño visual completo con Replit (2 pasadas): identidad NormaIA
   (sidebar oscuro, KPI cards, badges de color por estado/plan), gráfica
   de suscripciones con área degradada y tooltips pulidos, búsqueda/filtros
   con diseño completo en Clientes.

## BUGS DE CSS ENCONTRADOS Y CORREGIDOS DURANTE EL REDISEÑO (leccion tecnica)
Patron repetido 2 veces en `dashboard_clientes.html`: usar `flex: N M Xpx`
en un elemento hijo de un contenedor `flex-direction: column` hace que el
navegador interprete el `Xpx` del flex-basis como ALTURA, no como ancho
(el flex-basis siempre actua sobre el eje principal del contenedor, que en
una columna es vertical). Paso primero con el `<select>` de los filtros
(`.filter-bar select { flex: 0 1 180px }` dentro de `.filter-group`
columna -> altura de 177px en vez de 38px), luego con `.search-wrap`
(mismo patron, `flex: 1 1 220px`). Fix en ambos casos: reemplazar `flex:`
por `width:`/`max-width:` explicitos. LECCION para el futuro: si un
`<select>`/input/div dentro de un contenedor `flex-direction: column` se ve
con una altura rara, revisar primero si tiene una propiedad `flex:` con un
valor pensado para ancho.

## NOTA DE PROCESO
Todo el trabajo de v2/v3/rediseño se hizo con el flujo normal (Codex
implementa el codigo funcional, Replit hace el diseño visual, Claude
escribe specs y revisa cada diff antes de commit). El unico tramo con
Claude implementando directo fue SEC-009 y el v1 original, durante la
ventana en que Codex se quedo sin creditos (ya resuelto, ver memoria de
esa sesion).

## Estado final
- `auditoria-local` y `main` sincronizados, todo en produccion
  (`www.sireed.com.mx` / `nom035-production.up.railway.app`)
- Deploy de produccion confirmado limpio (gunicorn arriba, sin errores
  nuevos, solo warnings W042 preexistentes)
- Sin pendientes activos de este proyecto

## PENDIENTES QUE QUEDAN FUERA DE ESTE PROYECTO (no tocar aqui)
1. Vista de detalle por cliente (historial completo de cada
   PlanPurchaseEvent, no solo el mas reciente) -- posible v4 futura
2. "Clientes activos netos en el tiempo" (con cancelaciones restadas)
   -- requeriria un modelo hermano de eventos de cancelacion con fecha
3. Limitacion conocida de SEC-009: con 2 planes simultaneos (ej. NOM-035 +
   psicometria por separado), una renovacion solo puede re-acreditar uno
   de los dos (se prioriza stripe_plan_key) -- preexistente, no es
   regresion de este lote
4. Warning de Railway sobre migracion no reflejada (choices 'competencias'/
   'comercial' en PsychoInstrument.TIPOS) -- sigue pendiente de sesiones
   anteriores, sin relacion con este proyecto

# ============================================================
# NORMAIA DESPLEGADO EN VPS PROPIO — https://normaia.ihes.mx
# Fecha: 22 Jul 2026
# ============================================================

## Contexto importante descubierto en este proceso
`035.ihes.mx` (dominio que usan los clientes reales hoy) NO apuntaba a
Railway como se creia -- resuelve directo a un VPS compartido propio
(DigitalOcean, 104.236.46.73, Ubuntu 18.04.3 LTS fuera de soporte oficial),
sirviendo una instalacion OBSOLETA de nom035 (version anterior a
psicometria, Python 3.6.9, venv compartido con otros sitios, gunicorn+
supervisor+celery via RabbitMQ -- confirmado con Celery corriendo 334 dias,
WeasyPrint funcional ahi a diferencia de Railway). Decision de Jorge:
esa instalacion queda intacta y sin tocar, es obsoleta y no se usa
activamente aunque tecnicamente sirve trafico. El plan es reemplazarla
por NormaIA (este repo) bajo un dominio nuevo, y mover el dominio cuando
este listo.

## Despliegue completado
- Docker Engine 24.0.2 + Docker Compose v2.18.1 instalados en el VPS
  (el script oficial de Docker marca deprecation warning por Ubuntu 18.04,
  pero la instalacion funciono correctamente)
- Repo clonado en /webapps/NormaIA (carpeta nueva, separada de /webapps/nom35)
- Postgres propio en contenedor Docker (no el Postgres compartido del VPS)
- .env de produccion configurado: SECRET_KEY real, DATABASE_URL apuntando
  al servicio `db` del compose, ANTHROPIC_API_KEY real (key nueva
  "normaia-vps-api-key", sin vencimiento), SMTP real (Gmail con contraseña
  de aplicacion), Stripe en placeholder (pendiente activar modo test
  primero, luego modo live)
- nginx: archivo nuevo /etc/nginx/sites-available/normaia (separado del
  archivo "nom035" que en realidad contiene la config de muchos dominios
  distintos, no se toco), proxy_pass a http://127.0.0.1:8010
- DNS: registro A normaia.ihes.mx -> 104.236.46.73 creado y propagado
- SSL: certificado real de Let's Encrypt via certbot --nginx, redirect
  HTTP->HTTPS automatico configurado
- Validado end-to-end: https://normaia.ihes.mx/login/ responde 200 OK,
  migraciones y carga de instrumentos psicometricos corrieron limpias

## PENDIENTE
1. Activar Stripe: primero modo test para validar checkout/webhook en el
   VPS (crear webhook nuevo en Stripe apuntando a
   https://normaia.ihes.mx/stripe/webhook/), despues modo live cuando se
   decida cobrar de verdad
2. Probar el flujo completo de perfil narrativo con IA end-to-end (ya tiene
   la ANTHROPIC_API_KEY real cargada, falta probarlo con una evaluacion
   psicometrica real completa)
3. Decidir que hacer con 035.ihes.mx/nom35 viejo una vez NormaIA este
   validado (desactivarlo, o dejarlo corriendo indefinidamente)
4. Por higiene de seguridad: rotar SECRET_KEY, POSTGRES_PASSWORD, y la
   contraseña de aplicacion de Gmail del VPS -- quedaron visibles en el
   chat de la sesion donde se configuraron
5. Confirmar que el renovador automatico de certbot (ya activo para los
   demas dominios del VPS) tambien cubre normaia.ihes.mx (deberia ser
   automatico, mismo certbot global, pero no se confirmo explicitamente)
6. Pendiente nuevo, fuera de este despliegue: actualizar la landing page
   (pagina principal) con informacion real del sistema, precios de
   paquetes actuales, mencion del perfil narrativo con IA, y beneficios --
   se va a trabajar con Replit, en otra sesion

# ============================================================
# LANDING REDISENADA + STRIPE ACTIVADO + CORRECCIONES FASE 1
# Fecha: 23 Jul 2026 (sesion 22)
# ============================================================

## Local oficial a partir de ahora
`C:\NormaIA-Pruebas\nom035` -- reemplaza la ruta vieja de `Documents\nom 035\nom035`.
Venv Python 3.10 ya reconstruido ahi (ver sesion de VPS arriba).

## 1. Landing page -- rediseño completo en 2 rondas, ya en produccion (VPS)
- **Ronda 1**: precios reales (los de `stripe_plans.py`, no inventados),
  perfil narrativo con IA mencionado, 6 instrumentos correctos, Clima
  Laboral marcado como incluido solo en NOM-035/Suite (no en Psicometria
  sola -- verificado contra el codigo: el acceso depende de
  `stripe_plan_key`, no de `psico_plan_key`).
- **Ronda 2**: rediseño completo de 20 secciones (hero con mockup
  ilustrativo, demo gratuita explicada, seccion propia de Perfil
  Narrativo con IA + aviso de limites, seguridad y privacidad, FAQ con
  10 preguntas verificadas contra el comportamiento real del sistema,
  formulario de contacto conectado al endpoint real `/contact/`,
  eventos de analitica via `trackEvent()` stub). Sin testimonios ni
  logos de empresas ficticias mas alla de los ya existentes (se dejaron
  como placeholder por decision de Jorge).
- Ambas rondas se construyeron con prompts para Replit (mismo flujo que
  las vistas anteriores), revisadas por Claude antes de integrar
  (balance de tags, elementos funcionales, backups `_pre_*` creados).
- **Bug encontrado y corregido en el camino**: renombrar `Dockerfile` a
  `Dockerfile.vps` (+ actualizar `docker-compose.yml`) porque Railway
  auto-detectaba el Dockerfile e ignoraba `railway.json` (que fuerza
  NIXPACKS), causando "Application failed to respond" en Railway
  staging y en el servicio Railway "produccion" de pruebas (ninguno es
  la produccion real, que es el VPS). VPS no se vio afectado.

## 2. Stripe activado en modo test en el VPS
Llaves reales de Stripe test (`pk_test_`/`sk_test_`) y webhook
(`whsec_`, apuntando a `https://normaia.ihes.mx/stripe/webhook/`,
eventos: checkout.session.completed, invoice.paid,
invoice.payment_failed, customer.subscription.updated) configuradas en
el `.env` del VPS. Compra de prueba con tarjeta `4242 4242 4242 4242`
confirmada funcionando end-to-end por Jorge.

**Leccion tecnica importante**: `docker compose restart` NO relee el
`.env` -- hay que usar `docker compose up -d web` (recrea el
contenedor) para que tome variables de entorno nuevas. Aplica para
cualquier cambio futuro de `.env` en el VPS.

## 3. Documento nuevo: SOCIOS_feedback_correcciones.md
Documento vivo en la raiz del repo donde Jorge va acumulando
observaciones de los socios (screenshots, comentarios) conforme se las
comparten. Cada observacion se verifica contra el codigo real antes de
anotarla como confirmada. Incluye tambien un plan de 3 fases acordado
con Jorge para no atrasar el trabajo: Fase 1 = correcciones puntuales
(bugs), Fase 2 = indicador general + recomendaciones de solo lectura,
Fase 3 = rediseño visual completo + funcionalidad con estado. Revisar
ese archivo para la lista completa y detallada de hallazgos, incluyendo
varias propuestas de mejora importantes (ej. "Riesgo General" tipo
Cfinal de la norma, conteo de dominios por nivel, recomendaciones
automaticas basadas en el numeral 8.2 de la NOM-035 -- pendientes,
Fase 2/3).

## 4. Fase 1 completa -- correcciones desplegadas en VPS y confirmadas por Jorge
- Tarjeta "Dimensiones de riesgo" del Dashboard: calculaba el nivel con
  un porcentaje generico (20/40/60/80%) en vez de los umbrales
  oficiales por dominio de la Guia II de la norma (los mismos que ya
  usaba correctamente `get_chart_data`) -- corregido, ahora usa los
  umbrales reales de cada dominio.
- Etiqueta "Dimensiones de riesgo" -> "Dominios de riesgo" (son 8
  dominios, no dimensiones -- las dimensiones son 20, subdivisiones
  dentro de los dominios; observacion correcta de un socio).
- Insignia "Mas popular"/"Mejor valor" en `/planes/` aparecia en los 3
  planes de cada tab a la vez (la condicion comparaba `periodo`, que
  coincidia en los 3; en Psicometria la condicion nunca se cumplia,
  bug opuesto) -- corregido para comparar contra el `plan_key`
  especifico de cada tab.
- Correo muerto `n035.ihes@gmail.com` (cuenta inexistente/sin acceso)
  reemplazado por `normaia.sistemas@gmail.com` en 7 lugares del codigo,
  incluyendo el destino real del formulario de contacto de la landing
  (antes se perdian silenciosamente los mensajes).
- Correo de bienvenida al registro activado (estaba comentado): llega
  al usuario nuevo Y notificacion interna a
  normaia.sistemas@gmail.com.
- **Bug funcional serio encontrado y corregido**: el link de
  "Recuperar contraseña" del correo apuntaba a
  `/email_verification/<code>/<token>` (vista `EmailVerification`) en
  vez de `/password_recover/<code>/<token>` (vista `PasswordRecover`,
  la que muestra el formulario de contraseña nueva) -- por eso el
  usuario llegaba a la pantalla de "correo verificado" y la contraseña
  nunca se actualizaba. Confirmado corregido por Jorge en produccion.
- Links de verificacion/recuperacion en el correo apuntaban al dominio
  viejo `035.ihes.mx` en vez de `normaia.ihes.mx` -- corregido.
- Marca "IHES" -> "NormaIA" en title/meta de `register-template.html`.
- Copyright hardcodeado a "2027" -> dinamico (`{% now "Y" %}`) en
  `valid_email.html`, `password_recover.html`, `survey.html`. Typo
  "nuesra aplicacion movil" -> "nuestra aplicacion movil".
- Todo Fase 1 confirmado funcionando en produccion (VPS) por Jorge.

## PENDIENTE (para la proxima sesion)
1. Seguir recibiendo y registrando observaciones de los socios en
   `SOCIOS_feedback_correcciones.md` (Jorge las sigue mandando).
2. Fase 2 del plan: implementar el indicador "Riesgo General" (Cfinal,
   umbrales ya definidos por la norma), conteo/distribucion de
   dominios por nivel, recomendaciones de solo lectura basadas en el
   numeral 8.2 de la norma, y enlaces directos a Evidencias/Clima
   Laboral desde la ficha del centro de trabajo.
3. Logo viejo "NOM 035/IHES" (`static/app-assets/images/pages/login_nom035.png`,
   usado en `valid_email.html` y `password_recover.html`) -- pendiente
   de reemplazar por un asset con la marca NormaIA.
4. Railway staging sigue con el problema de Nixpacks/python no
   detectado correctamente (quedo pendiente de resolver, no bloqueante
   ya que la produccion real es el VPS).
5. Pendientes menores de sesiones previas siguen sin resolver: warning
   de migracion no reflejada (choices PsychoInstrument), division
   float en employees_dt, rotar credenciales del VPS por higiene.
