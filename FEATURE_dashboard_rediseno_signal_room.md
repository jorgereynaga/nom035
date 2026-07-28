# Rediseño visual del Dashboard — "Signal Room" (propuesta de Replit)

## Contexto

Jorge le paso el repo publico y la ruta `surveys/templates/index.html` a
Replit, con libertad total de diseno pero sin tocar datos ni funcionalidad,
pidiendo una propuesta visual agradable, facil de entender y llamativa para
un usuario no tecnico (responsable de RH/cumplimiento).

Replit entrego el archivo completo con su concepto "Signal Room" (estilo
Linear/Vercel: alta densidad de informacion, jerarquia clara, color
semantico). Antes de integrarlo se reviso exhaustivamente:

## Validacion realizada

1. **Diff de variables Django**: se extrajeron todos los `{{ }}` y `{% %}`
   del `index.html` original y de la propuesta y se compararon con
   `comm` -- **0 diferencias** en ambos sentidos. Ninguna variable de
   contexto fue renombrada, eliminada ni inventada.
2. **Render real**: se sustituyo temporalmente `index.html` por la
   propuesta y se renderizo via Django test client
   (`Client().get('/main')` con un usuario logueado) -- **200 OK**, sin
   tags sin resolver en el HTML final, valores de KPI reales visibles.
3. **Prueba en navegador**: servidor local levantado, login real, se
   confirmo el arbol de accesibilidad completo -- sidebar, topbar, KPIs,
   las 4 secciones (Centros en atencion, Acciones pendientes,
   Psicometria, Clima Laboral) y todos los links de navegacion
   funcionando. Sin errores en consola.
4. `python -m py_compile` no aplica (es un template, no Python), pero
   `manage.py check` no mostro nada nuevo (solo los warnings
   preexistentes de auto-created primary keys, ya conocidos).

## Hallazgo (no bloqueante, registrado como pendiente)

La propuesta incluye ~160 lineas de CSS para clases `.nom-wp-card` /
`.clima-wp-card` (tarjetas de listado por centro de trabajo) que **no se
usan en ningun elemento del HTML** -- el Dashboard actual ya no tiene esas
listas (viven en `workplace.html` desde el rediseno ejecutivo de una
sesion anterior); probablemente Replit genero estilos pensando en una
version anterior del archivo. No afecta funcionamiento, es CSS muerto.
Jorge decidio dejarlo para una limpieza posterior (ver ESTADO.md,
pendiente #8).

## Cambios

- `surveys/templates/index.html`: reemplazo completo del CSS/HTML de
  presentacion (sidebar, topbar, KPI cards, tarjetas de centros en
  atencion, acciones pendientes, seccion de psicometria, resumen de
  clima laboral). Misma logica de datos, mismo `{% block dashboard %}` y
  `{% block scripts %}`, mismas variables de contexto de
  `Index.get()` (`surveys/views.py`).
