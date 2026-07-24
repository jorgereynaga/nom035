# Fase 2-C — Ficha de centro de trabajo: badges de Riesgo y Cumplimiento + enlaces a Evidencias/Clima Laboral

## ⚠️ Dependencia — orden de implementación obligatorio
Este lote **consume datos de los otros dos lotes de Fase 2** y no se puede probar de principio a fin sin ellos:
1. Primero: `FASE2_A_especificacion_riesgo_general_recomendaciones.md` (agrega el endpoint `get_riesgo_general`).
2. Segundo: `FASE2_B_especificacion_cumplimiento_documental.md` (agrega el campo `porcentaje_cumplimiento` a la respuesta de `get_portafolio_status`).
3. Tercero: este lote (Fase 2-C).

Si por alguna razón A o B no están listos todavía, este lote se puede implementar igual (el JS simplemente no encontrará esos campos en la respuesta) pero **no se debe dar por terminado/probado** hasta que los 3 estén integrados y se pueda confirmar visualmente con datos reales.

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local` (o la rama de Fase 2-A/2-B si ya están mergeadas a una rama intermedia — confirmar con Jorge cuál es la base correcta en el momento de implementar)
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/fase2-c-ficha-centro-badges`
- Este lote es 100% frontend (`surveys/templates/workplace_detail.html`) — no toca `views.py`, `models.py` ni requiere migración.
- `python -m py_compile` no aplica aquí (no hay cambios de Python), pero sí correr un `django-admin check` o levantar el servidor local para confirmar que el template renderiza sin errores de sintaxis Django.

## Contexto

Mockup aprobado por Jorge el 23 jul 2026 (ver conversación — ficha de detalle del centro con 2 tarjetas nuevas en el header: "Riesgo psicosocial" y "Cumplimiento documental", más 2 botones nuevos: "Ver evidencias" y "Ver clima laboral"). **La tabla de empleados que hoy vive debajo del header (`#list`, DataTable, líneas 420+) NO se toca, se queda exactamente igual.** Este lote es exclusivamente sobre el header (`detail-header-card`, líneas 333-418).

Los 2 badges nuevos se llenan vía AJAX al cargar la página (mismo patrón que ya usa la tabla de empleados con `$.ajax`/DataTables), consumiendo los 2 endpoints existentes/nuevos:
- `get_riesgo_general` (nuevo, de Fase 2-A) → da el nivel de Riesgo psicosocial.
- `get_portafolio_status` (ya existe, extendido en Fase 2-B) → da `porcentaje_cumplimiento`.

## Cambios requeridos

### 1. surveys/templates/workplace_detail.html — CSS (dentro de `{% block style %}`, después de la línea 296 `.dataTables_wrapper ul, .dataTables_wrapper li {...}`, antes de `{% endblock %}` línea 299)

```css
.meta-nuevo { position: relative; }
.risk-chip { display: flex; align-items: center; gap: 7px; }
.risk-dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
.risk-dot.nivel-0 { background: #9be5f7; }
.risk-dot.nivel-1 { background: #6bf56e; }
.risk-dot.nivel-2 { background: #eab308; }
.risk-dot.nivel-3 { background: #ffc000; }
.risk-dot.nivel-4 { background: #ff7070; }
.compliance-bar-track { width: 100%; height: 6px; border-radius: 999px; background: rgba(255,255,255,.16); margin-top: 4px; overflow: hidden; }
.compliance-bar-fill { height: 100%; background: #fff; border-radius: 999px; transition: width .3s ease; }
```

Estos 5 colores de `.risk-dot.nivel-N` son los mismos oficiales ya usados en el diccionario `col` de `get_chart_data` (`surveys/views.py:1430`) — no inventar colores nuevos, reutilizar exactamente estos hex.

### 2. surveys/templates/workplace_detail.html — HTML (dentro de `.detail-meta-row`, líneas 355-368)

Agregar, después del tercer `.detail-meta-item` (Total empleados, línea 364-367) y antes del cierre de `.detail-meta-row` (línea 368):

```html
    <div class="detail-meta-item meta-nuevo" id="badge-riesgo" style="display:none;">
      <span class="detail-meta-label">Riesgo psicosocial</span>
      <span class="detail-meta-value risk-chip">
        <span class="risk-dot" id="riesgo-dot"></span>
        <span id="riesgo-nivel">—</span>
      </span>
    </div>
    <div class="detail-meta-item meta-nuevo" id="badge-cumplimiento" style="display:none;">
      <span class="detail-meta-label">Cumplimiento documental</span>
      <span class="detail-meta-value"><span id="cumplimiento-pct">—</span>%</span>
      <div class="compliance-bar-track"><div class="compliance-bar-fill" id="cumplimiento-bar" style="width:0%"></div></div>
    </div>
```

Ambos empiezan con `display:none` y el JS los muestra (`display:flex` o el valor que use `.detail-meta-item` — confirmar el `display` real de esa clase antes de escribir el JS) solo cuando llega una respuesta válida, para no mostrar guiones/vacíos mientras carga o si el centro no tiene datos suficientes (`status: no_data`).

### 3. surveys/templates/workplace_detail.html — HTML (dentro de `.action-row`, después del botón "Ver resultados", antes del cierre `</div>` de la línea 416)

```html
    <a href="{% url 'evidence' %}" class="btn btn-outline btn-sm">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z"/></svg>
      Ver evidencias
    </a>
    <a href="{% url 'clima_resultados' workplace_id %}" class="btn btn-outline btn-sm">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
      Ver clima laboral
    </a>
```

Nota: `{% url 'evidence' %}` no lleva `workplace_id` como argumento (esa vista, `EvidenceView`, no lo acepta en la URL — el usuario selecciona el centro con un combo dentro de `/evidence/`, confirmado en `nom035/urls.py:93`). `{% url 'clima_resultados' workplace_id %}` sí lo requiere y ya está confirmado que funciona con esa variable de contexto (mismo patrón usado en `index.html:1398`).

### 4. surveys/templates/workplace_detail.html — JS (dentro de `{% block scripts %}`, dentro del mismo `$(document).ready(function(){...})` que ya arranca la línea 458, agregar después de la inicialización del DataTable)

```javascript
  $.ajax({
    url: "{% url 'get_riesgo_general' %}",
    data: {"workplace_id": "{{workplace_id}}", "evaluation": "{{evaluation}}"},
    dataType: 'json',
    success: function(data){
      if (data.status === 'ok') {
        var nivel = data.riesgo_general.nivel;
        $("#riesgo-dot").removeClass().addClass("risk-dot nivel-" + nivel);
        $("#riesgo-nivel").text(data.riesgo_general.nivel_nombre);
        $("#badge-riesgo").show();
      }
    }
  });

  $.ajax({
    url: "{% url 'get_portafolio_status' %}",
    data: {"workplace_id": "{{workplace_id}}"},
    dataType: 'json',
    success: function(data){
      if (typeof data.porcentaje_cumplimiento !== 'undefined') {
        $("#cumplimiento-pct").text(data.porcentaje_cumplimiento);
        $("#cumplimiento-bar").css("width", data.porcentaje_cumplimiento + "%");
        $("#badge-cumplimiento").show();
      }
    }
  });
```

Confirmado: `nom035/urls.py:98` tiene `path('get_portafolio_status/', get_portafolio_status, name='get_portafolio_status')`, y `evidence.html:481` ya la invoca con `{% url 'get_portafolio_status' %}` — usar exactamente esa misma forma aquí, sin cambios.

## Validación requerida antes de dar el lote por terminado
1. Con los 3 lotes de Fase 2 (A, B, C) integrados, abrir `/workplaces/<id>/` de un centro de prueba con empleados y encuestas completas:
   - Los 2 badges nuevos aparecen con datos reales (nivel de riesgo con su color correcto, % de cumplimiento con su barra).
   - El botón "Ver evidencias" lleva a `/evidence/` y el usuario puede seleccionar el mismo centro desde el combo ahí.
   - El botón "Ver clima laboral" lleva a `/clima/resultados/<id>/` del centro correcto.
2. Con un centro SIN datos suficientes (sin encuestas contestadas): los 2 badges nuevos deben quedar ocultos (no mostrar "—" ni "0%" engañoso), sin romper el resto del header.
3. Confirmar que la tabla de empleados debajo del header sigue funcionando exactamente igual que antes (sin regresión) — paginación, búsqueda, columnas.
4. Confirmar visualmente que los 2 botones nuevos no rompen el `flex-wrap` de `.action-row` en pantallas angostas (probar en una ventana reducida).

## Fuera de alcance de este lote (no tocar)
- La tabla de empleados (`#list`, DataTable) — se queda exactamente igual, ni una línea de esa sección se toca.
- Cualquier cambio a `WorkplaceDetailView` en `views.py` — este lote es 100% template/JS, consumiendo endpoints que ya existen o que agregan los otros 2 lotes.
- El rediseño de la lista de "Centros de Trabajo" (`workplaces.html` o el template que corresponda) — Jorge decidió explícitamente posponerlo (23 jul 2026), no incluir en este lote.
- Cualquier cambio a `workplace_results.html` (pestaña "Resumen") — es contenido de `FASE2_A_especificacion_riesgo_general_recomendaciones.md`, lote aparte.
