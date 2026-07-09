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
