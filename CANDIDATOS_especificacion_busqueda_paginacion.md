# Candidatos — búsqueda instantánea, filtro por tipo y paginación real

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b fix/candidatos-busqueda-instantanea-paginacion`
- `surveys/psico_views.py` — verificar estilo de indentación existente con `cat -A` antes de editar (no asumir TABS o espacios).
- `surveys/templates/psico_candidatos.html` es HTML/JS estándar (jQuery ya cargado globalmente vía el layout, igual que en `employeeform.html`).
- **CRÍTICO — no olvidar:** `nom035/urls.py` importa `surveys.psico_views` con lista **explícita** (línea 24-29 actual), a diferencia de `surveys.views` que usa wildcard. La nueva vista `candidates_dt` **debe** agregarse a esa lista de imports, o el arranque del servidor truena con `NameError` (ya pasó antes con `InstrumentosCatalogoView`, documentado en `ESTADO.md`).
- No se agrega ningún modelo ni migración nueva — se reutiliza `Candidate` tal cual.
- `python -m py_compile surveys/psico_views.py` antes de cualquier commit.
- `python manage.py check` antes de cualquier commit.

## Contexto

Jorge detectó que la vista "Candidatos" (`psico_candidatos.html`) trae **todos** los candidatos del usuario sin límite (`CandidateListView.get()`, `surveys/psico_views.py`), y el template no tiene buscador, filtro ni paginación — con una cuenta que maneje muchas evaluaciones, la lista se volvería interminable.

Jorge aprobó un mockup con: buscador (nombre/puesto/correo), filtro por tipo (Todos/Candidato externo/Empleado actual), y paginación real del lado del servidor — **y pidió que la búsqueda sea instantánea, sin recargar la página** (no un simple submit de formulario).

**Diseño de la solución (para no meter DataTables en una página que hoy no lo usa, y mantener el diseño de tarjetas ya existente en vez de forzarlo a una tabla):**
- Nueva vista JSON `candidates_dt` (mismo patrón ya usado en `employees_dt`, `surveys/views.py` línea 1663 actual, para consistencia con el resto del proyecto): recibe `search`, `tipo`, `page` por GET, devuelve los candidatos de esa página + metadatos de paginación.
- El primer render (carga inicial de la página, sin JS) sigue siendo server-side vía `CandidateListView.get()`, ahora paginado también (para que funcione igual sin JavaScript y la primera carga sea rápida).
- El JS del template hace una petición AJAX a `candidates_dt` cada vez que el usuario escribe en el buscador (con debounce de 300ms para no disparar una petición por cada tecla), cambia el filtro de tipo, o hace clic en un link de paginación — y re-renderiza solo la lista de tarjetas y la barra de paginación, sin recargar la página completa.

## Cambios requeridos

### 1. `surveys/psico_views.py` — `CandidateListView.get()` (línea 19-31 actual)

Reemplazar el método completo:

```python
class CandidateListView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    PAGE_SIZE = 15

    def get(self, request):
        candidates_qs = Candidate.objects.filter(user=request.user).order_by('-record_create')
        total_candidatos = candidates_qs.count()
        paginator = Paginator(candidates_qs, self.PAGE_SIZE)
        page_obj = paginator.get_page(1)
        instrumentos = PsychoInstrument.objects.filter(activo=True)
        ctx = {
            'candidates': page_obj.object_list,
            'total_candidatos': total_candidatos,
            'total_paginas': paginator.num_pages,
            'instrumentos': instrumentos,
            'name': request.user.userapp.name,
            'workplaces': Workplace.objects.filter(user=request.user),
        }
        return render(request, 'psico_candidatos.html', ctx)
```

(Agregar `from django.core.paginator import Paginator` a los imports de `surveys/psico_views.py` si no está ya presente — verificar primero con `grep -n "^from django.core.paginator" surveys/psico_views.py`.)

### 2. `surveys/psico_views.py` — nueva vista `candidates_dt`

Agregar justo después de la clase `CandidateListView`:

```python
def candidates_dt(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not_authenticated'}, status=401)
    search = request.GET.get('search', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    candidates_qs = Candidate.objects.filter(user=request.user).order_by('-record_create')
    if search:
        candidates_qs = candidates_qs.filter(
            Q(nombre__icontains=search) | Q(puesto__icontains=search) | Q(email__icontains=search)
        )
    if tipo in dict(Candidate.TIPOS):
        candidates_qs = candidates_qs.filter(tipo=tipo)

    total_candidatos = candidates_qs.count()
    paginator = Paginator(candidates_qs, CandidateListView.PAGE_SIZE)
    page_obj = paginator.get_page(page)

    data = [{
        'id': c.id,
        'nombre': c.nombre,
        'inicial': c.nombre[:1].upper() if c.nombre else '?',
        'puesto': c.puesto or 'Sin puesto asignado',
        'tipo': c.tipo,
        'tipo_display': c.get_tipo_display(),
        'sessions_count': c.sessions.count(),
    } for c in page_obj.object_list]

    return JsonResponse({
        'candidates': data,
        'total_candidatos': total_candidatos,
        'page': page_obj.number,
        'total_paginas': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    })
```

(Verificar que `Q` de `django.db.models` y `JsonResponse` ya estén importados en `surveys/psico_views.py` — si no, agregar `from django.db.models import Q` y `from django.http import JsonResponse` a los imports existentes.)

### 3. `nom035/urls.py` — agregar `candidates_dt` al import explícito y a las rutas

**3.1 —** Agregar `candidates_dt` a la lista de imports de `surveys.psico_views` (línea 24-29 actual):

```python
from surveys.psico_views import (
    CandidateListView, CandidateCreateView, CandidateDetailView,
    AssignTestView, TestSessionView, TestCompleteView, TestResultView,
    GenerarPerfilNarrativoView, ReporteUnificadoView,
    InstrumentosCatalogoView, candidates_dt,
)
```

**3.2 —** Agregar la ruta nueva, justo después de `path('psico/candidatos/', CandidateListView.as_view(), name='candidatos'),` (línea 127 actual):

```python
    path('psico/candidatos_dt/', candidates_dt, name='candidatos_dt'),
```

### 4. `surveys/templates/psico_candidatos.html` — CSS nuevo

Agregar junto a las reglas `.candidates-list`/`.candidate-card`/etc. ya existentes (después de la línea con `.candidate-sessions { ... }`):

```css
    /* ─── Buscador, filtro y paginacion ─────────────────────── */
    .filter-bar { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
    .filter-input { flex: 1; min-width: 220px; padding: 9px 14px; font-size: 13px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--bg-base); font-family: 'Inter', sans-serif; }
    .filter-input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37,99,235,.1); }
    .filter-select { padding: 9px 14px; font-size: 13px; border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--bg-base); color: var(--text-primary); font-family: 'Inter', sans-serif; }
    .filter-count { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }
    .pagination-bar { display: flex; align-items: center; justify-content: space-between; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border); flex-wrap: wrap; gap: 10px; }
    .pagination-info { font-size: 12.5px; color: var(--text-muted); }
    .pagination-links { display: flex; gap: 6px; align-items: center; }
    .page-link { display: flex; align-items: center; justify-content: center; min-width: 32px; height: 32px; padding: 0 8px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--bg-base); color: var(--text-primary); font-size: 12.5px; font-weight: 600; text-decoration: none; cursor: pointer; }
    .page-link:hover { background: var(--bg-surface); }
    .page-link.active { background: var(--primary); color: #fff; border-color: var(--primary); }
    .page-link.disabled { opacity: .4; cursor: not-allowed; pointer-events: none; }
```

### 5. `surveys/templates/psico_candidatos.html` — HTML (búsqueda + lista + paginación)

Reemplazar el bloque completo desde `{% if candidates %}` hasta el `{% endif %}` que le corresponde (líneas 328-364 actuales) por:

```html
    <div class="filter-bar">
      <input class="filter-input" type="text" id="candidato-search" placeholder="Buscar por nombre, puesto o correo...">
      <select class="filter-select" id="candidato-tipo-filter">
        <option value="">Todos los tipos</option>
        <option value="externo">Candidato externo</option>
        <option value="empleado">Empleado actual</option>
      </select>
    </div>
    <p class="filter-count" id="candidato-count">{{total_candidatos}} candidato{{total_candidatos|pluralize}} encontrado{{total_candidatos|pluralize}}</p>

    <div class="candidates-list" id="candidatos-list-container">
      {% for c in candidates %}
      <div class="candidate-card">
        <div class="candidate-card-left">
          <div class="candidate-avatar">{{ c.nombre|first|upper }}</div>
          <div>
            <p class="candidate-name">{{ c.nombre }}</p>
            <p class="candidate-role">{{ c.puesto|default:"Sin puesto asignado" }}</p>
          </div>
        </div>
        <div class="candidate-card-right">
          <span class="badge {% if c.tipo == 'externo' %}badge-externo{% else %}badge-empleado{% endif %}">
            {{ c.get_tipo_display }}
          </span>
          <span class="candidate-sessions">{{ c.sessions.count }} prueba{{ c.sessions.count|pluralize }}</span>
          <a href="{% url 'candidato_detalle' c.id %}" class="btn btn-outline btn-sm">
            Ver detalle
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>
        </div>
      </div>
      {% empty %}
      <div class="empty-state">
        <div class="empty-state-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <h3>Sin candidatos registrados</h3>
        <p>No tienes candidatos aún. Agrega el primero para comenzar a evaluar.</p>
        <button class="btn btn-primary" onclick="document.getElementById('modalNuevo').classList.add('activo')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>
          Agregar primer candidato
        </button>
      </div>
      {% endfor %}
    </div>

    <div class="pagination-bar" id="candidatos-pagination" {% if total_paginas <= 1 %}style="display:none;"{% endif %}>
      <span class="pagination-info" id="candidatos-pagination-info">Página 1 de {{total_paginas}}</span>
      <div class="pagination-links" id="candidatos-pagination-links"></div>
    </div>
```

**Nota:** el `{% empty %}` del `{% for %}` reemplaza el bloque `{% else %}` que existía en el `{% if candidates %}` original — comportamiento equivalente (se muestra cuando la lista está vacía), pero usando la sintaxis nativa de Django para loops vacíos en vez de un `if` envolvente, ya que ahora el conteo real de candidatos totales se maneja aparte con `total_candidatos` (para el texto "X encontrados", que debe reflejar el total sin filtrar en la carga inicial, no si la página actual tiene candidatos).

### 6. `surveys/templates/psico_candidatos.html` — JS (búsqueda instantánea + paginación AJAX)

Agregar antes del `</body>` de cierre (o dentro del bloque `<script>` ya existente al final del archivo, si lo hay — verificar con `grep -n "<script>" surveys/templates/psico_candidatos.html` y ubicar el lugar adecuado):

```javascript
<script>
(function(){
  var searchInput = document.getElementById('candidato-search');
  var tipoFilter = document.getElementById('candidato-tipo-filter');
  var listContainer = document.getElementById('candidatos-list-container');
  var countLabel = document.getElementById('candidato-count');
  var paginationBar = document.getElementById('candidatos-pagination');
  var paginationInfo = document.getElementById('candidatos-pagination-info');
  var paginationLinks = document.getElementById('candidatos-pagination-links');
  var currentPage = 1;
  var debounceTimer = null;

  function escapeHtml(str){
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function renderCard(c){
    var badgeClass = c.tipo === 'externo' ? 'badge-externo' : 'badge-empleado';
    return '<div class="candidate-card">' +
      '<div class="candidate-card-left">' +
        '<div class="candidate-avatar">' + escapeHtml(c.inicial) + '</div>' +
        '<div><p class="candidate-name">' + escapeHtml(c.nombre) + '</p><p class="candidate-role">' + escapeHtml(c.puesto) + '</p></div>' +
      '</div>' +
      '<div class="candidate-card-right">' +
        '<span class="badge ' + badgeClass + '">' + escapeHtml(c.tipo_display) + '</span>' +
        '<span class="candidate-sessions">' + c.sessions_count + (c.sessions_count === 1 ? ' prueba' : ' pruebas') + '</span>' +
        '<a href="/psico/candidatos/' + c.id + '/" class="btn btn-outline btn-sm">Ver detalle</a>' +
      '</div>' +
    '</div>';
  }

  function renderPagination(data){
    if (data.total_paginas <= 1){ paginationBar.style.display = 'none'; return; }
    paginationBar.style.display = 'flex';
    paginationInfo.textContent = 'Página ' + data.page + ' de ' + data.total_paginas;
    var html = '<a class="page-link' + (data.has_previous ? '' : ' disabled') + '" data-page="' + (data.page - 1) + '">‹ Anterior</a>';
    for (var p = 1; p <= data.total_paginas; p++){
      html += '<a class="page-link' + (p === data.page ? ' active' : '') + '" data-page="' + p + '">' + p + '</a>';
    }
    html += '<a class="page-link' + (data.has_next ? '' : ' disabled') + '" data-page="' + (data.page + 1) + '">Siguiente ›</a>';
    paginationLinks.innerHTML = html;
    paginationLinks.querySelectorAll('.page-link:not(.disabled)').forEach(function(link){
      link.addEventListener('click', function(){
        currentPage = parseInt(this.getAttribute('data-page'), 10);
        cargarCandidatos();
      });
    });
  }

  function cargarCandidatos(){
    $.ajax({
      url: "{% url 'candidatos_dt' %}",
      method: 'GET',
      data: {
        search: searchInput.value.trim(),
        tipo: tipoFilter.value,
        page: currentPage,
      },
      dataType: 'json',
      success: function(data){
        if (data.candidates.length === 0){
          listContainer.innerHTML = '<div class="empty-state"><h3>Sin resultados</h3><p>No se encontraron candidatos con esos criterios.</p></div>';
        } else {
          listContainer.innerHTML = data.candidates.map(renderCard).join('');
        }
        countLabel.textContent = data.total_candidatos + (data.total_candidatos === 1 ? ' candidato encontrado' : ' candidatos encontrados');
        renderPagination(data);
      }
    });
  }

  searchInput.addEventListener('input', function(){
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function(){
      currentPage = 1;
      cargarCandidatos();
    }, 300);
  });
  tipoFilter.addEventListener('change', function(){
    currentPage = 1;
    cargarCandidatos();
  });

  // Inicializar los links de paginacion ya renderizados por Django en la carga inicial
  renderPagination({
    total_paginas: {{total_paginas}},
    page: 1,
    has_previous: false,
    has_next: {{total_paginas}} > 1,
  });
})();
</script>
```

## Validación requerida

1. `python -m py_compile surveys/psico_views.py`.
2. `python manage.py check` (confirmar que no truena por el import faltante de `candidates_dt` en `nom035/urls.py`).
3. Crear (vía shell o admin) al menos 20 candidatos de prueba para un mismo usuario, con nombres/puestos variados y tipos mixtos (externo/empleado).
4. Cargar `/psico/candidatos/`: confirmar que solo se muestran los primeros 15 (o el `PAGE_SIZE` definido), con la barra de paginación visible mostrando el total de páginas correcto.
5. Escribir en el buscador (ej. parte de un nombre): confirmar que la lista se actualiza sola, sin recargar la página, en menos de ~300ms después de dejar de escribir — y que **no** se dispara una petición AJAX por cada tecla individual (debounce funcionando).
6. Cambiar el filtro de tipo: confirmar que la lista se actualiza sola y solo muestra candidatos de ese tipo.
7. Hacer clic en "Siguiente"/un número de página: confirmar que carga la página correspondiente sin recargar, y que "Anterior" se deshabilita en la página 1 y "Siguiente" en la última.
8. Combinar búsqueda + filtro + paginación al mismo tiempo: confirmar que los 3 criterios se aplican juntos correctamente.
9. Probar con un usuario que tenga 0 candidatos: debe mostrar el estado vacío original ("Sin candidatos registrados... Agregar primer candidato"), no el de "Sin resultados" (ese es solo para búsquedas sin coincidencias).
10. Probar con una búsqueda que no encuentre nada: debe mostrar "Sin resultados" sin errores.
11. Confirmar que `candidates_dt` no expone candidatos de otro usuario (filtra siempre por `user=request.user`).
12. Prueba visual en navegador real: sin errores de consola, la interacción se siente instantánea, "Ver detalle" en las tarjetas re-renderizadas por JS sigue llevando al candidato correcto.
13. Confirmar que el modal "Nuevo candidato" y el resto de la página (sidebar, header) siguen funcionando exactamente igual que antes.

## Fuera de alcance

- No se agrega ordenamiento por columna (nombre/fecha/tipo) — solo el orden por defecto (`-record_create`, más reciente primero).
- No se usa DataTables — se mantiene el diseño de tarjetas actual con una implementación AJAX ligera propia, consistente con otros patrones ya usados en el proyecto (`guardarEstadoChecklist`, etc.).
- No se cambia `CandidateDetailView` ni el modal de "Nuevo candidato".
- No se pulen visualmente los nuevos elementos (buscador, filtro, paginación) más allá de reutilizar el sistema de diseño ya existente en el archivo — eso se puede refinar después con Replit si Jorge lo decide.
