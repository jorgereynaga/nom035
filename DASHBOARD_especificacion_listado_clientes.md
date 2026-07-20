# Dashboard de métricas — Listado de clientes (v3)

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b feature/dashboard-listado-clientes`
- Si la rama `feature/dashboard-timeline-suscripciones` (lote anterior, línea de tiempo de suscripciones) ya está mergeada a `auditoria-local` cuando empieces este lote, parte de ahí. Si no, parte de `auditoria-local` tal cual y que Jorge decida el orden de merge.
- `surveys/dashboard_views.py` usa 4 espacios.
- Templates `dashboard_*.html` son STANDALONE (su propio `<html>`, sidebar y `<style>` hardcodeados, sin `{% extends %}`) — mismo patrón ya usado en todo el proyecto para vistas de este tipo (ver `psico_*.html`). El archivo nuevo debe duplicar el `<head>`/`<style>`/sidebar de `dashboard_metricas.html`, no inventar un sistema de diseño distinto ni intentar compartir un template base.
- No se requiere migración nueva.
- `python -m py_compile surveys/dashboard_views.py` antes de dar el lote por bueno.

## Contexto y objetivo

Jorge pidió poder ver, además de las métricas agregadas, un **listado de clientes individuales**: quiénes son, si están activos o no, qué plan contrataron, y si llegaron a cancelar. El sidebar del dashboard (rediseñado con Replit) ya tiene un link "Clientes" apuntando a `href="#"` — hay que darle una vista real.

De paso, quitar el link "Reportes" del sidebar (Jorge confirmó que no se necesita por ahora) y conectar los links "Métricas"/"Clientes" a sus URLs reales en vez de `#`.

## Decisiones de diseño (para no repetir la investigación)

**Tres estados posibles por cliente, no solo activo/inactivo:**
- **Activo**: `Userapp.stripe_plan_key` no está vacío ahora mismo.
- **Cancelado**: tiene al menos un `PlanPurchaseEvent` (compró alguna vez) pero `stripe_plan_key` está vacío ahora — es decir, canceló. Esto es una inferencia a partir de los datos existentes (no hay un evento de cancelación con fecha propia, ver limitación conocida más abajo), pero es correcta con el modelo de datos actual.
- **Nunca compró**: no tiene ningún `PlanPurchaseEvent`.

**"Plan contratado" a mostrar:**
- Si está Activo: el plan actual (`Userapp.stripe_plan_key`, resuelto a nombre legible vía `PLANS`).
- Si está Cancelado: el plan de su `PlanPurchaseEvent` más reciente (el último que contrató antes de cancelar).
- Si Nunca compró: sin plan (mostrar `—`).

**Limitación conocida, no se resuelve aquí**: si un cliente cancela y vuelve a comprar un plan distinto, y luego cancela otra vez, este listado solo puede mostrar su plan más reciente, no el historial completo de cambios de plan. Ver el historial completo requeriría una vista de detalle por cliente (fuera de alcance, ver sección de "fuera de alcance").

## Cambios requeridos

### 1. surveys/dashboard_views.py — extraer mixin compartido + nueva vista

Ambas vistas (`DashboardMetricasView` ya existente, y la nueva `ClientesListView`) necesitan exactamente la misma protección (superusuario). Extraer esa lógica a un mixin para no duplicarla:

```python
class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/login/'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # redirige a login_url
        raise PermissionDenied  # logueado pero no superuser -> 403 real
```

Y cambiar `class DashboardMetricasView(LoginRequiredMixin, UserPassesTestMixin, View):` por `class DashboardMetricasView(SuperuserRequiredMixin, View):`, quitando de ahí los métodos `test_func`/`handle_no_permission`/`login_url` que ya quedan en el mixin (comportamiento idéntico, solo se mueve el código).

Nueva vista, en el mismo archivo:

```python
class ClientesListView(SuperuserRequiredMixin, View):
    def get(self, request):
        usuarios_qs = User.objects.filter(
            is_staff=False, is_superuser=False,
        ).select_related('userapp').prefetch_related('plan_purchase_events').order_by('-date_joined')

        clientes = []
        for user in usuarios_qs:
            userapp = getattr(user, 'userapp', None)
            stripe_plan_key = userapp.stripe_plan_key if userapp else ''
            activo = bool(stripe_plan_key)
            eventos = sorted(user.plan_purchase_events.all(), key=lambda e: e.record_create, reverse=True)
            compro_alguna_vez = len(eventos) > 0

            if activo:
                plan_nombre = PLANS.get(stripe_plan_key, {}).get('name', stripe_plan_key)
                estado = 'activo'
            elif compro_alguna_vez:
                plan_nombre = PLANS.get(eventos[0].plan_key, {}).get('name', eventos[0].plan_key)
                estado = 'cancelado'
            else:
                plan_nombre = '—'
                estado = 'nunca_compro'

            clientes.append({
                'usuario': user.username,
                'email': user.email,
                'fecha_registro': user.date_joined.strftime('%d/%m/%Y'),
                'estado': estado,
                'plan': plan_nombre,
            })

        return render(request, 'dashboard_clientes.html', {'clientes': clientes})
```

**Notas para quien implemente:**
- `getattr(user, 'userapp', None)` es defensivo por si algún usuario no tiene `Userapp` (no debería pasar para clientes reales, pero evita un `RelatedObjectDoesNotExist` si acaso).
- `sorted(..., reverse=True)` en Python sobre `user.plan_purchase_events.all()` (ya prefetcheado) evita una query extra por usuario — no usar `.order_by('-record_create').first()` aquí porque rompería el prefetch y generaría una query nueva por cada usuario en el loop (N+1).
- Sin paginación por ahora — la base de usuarios es chica (etapa temprana del producto). Si la lista crece mucho en el futuro, agregar paginación es una mejora aparte, no bloqueante hoy.

### 2. nom035/urls.py

Agregar al import existente de `dashboard_views`:
```python
from surveys.dashboard_views import DashboardMetricasView, ClientesListView
```
Y una ruta nueva junto a `metricas/`:
```python
path('metricas/clientes/', ClientesListView.as_view(), name='dashboard_clientes'),
```

### 3. surveys/templates/dashboard_clientes.html — archivo nuevo

Duplicar el `<head>` completo (variables CSS, `<style>`, fuentes) y el `<aside class="sidebar">` de `dashboard_metricas.html` tal cual, para mantener consistencia visual. Cambios respecto a ese sidebar duplicado:
- El link "Métricas" pierde la clase `active` y gana `href="{% url 'dashboard_metricas' %}"`.
- El link "Clientes" gana la clase `active` y `href="{% url 'dashboard_clientes' %}"`.
- El link "Reportes" se elimina por completo (ver sección 4 abajo, aplica también aquí).

Cuerpo de la página — una tabla simple con el mismo lenguaje visual que las tablas de `dashboard_metricas.html` (`.section-card`, `.table-wrap`, clases de badge tipo `.plan-badge` para el estado):

```html
<div class="page-body">
  <div class="section-title">
    <span class="title-dot"></span> Clientes
  </div>
  <div class="section-card">
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Email</th>
            <th>Fecha de registro</th>
            <th>Estado</th>
            <th>Plan</th>
          </tr>
        </thead>
        <tbody>
          {% for cliente in clientes %}
          <tr>
            <td><strong>{{ cliente.usuario }}</strong></td>
            <td class="td-muted">{{ cliente.email }}</td>
            <td>{{ cliente.fecha_registro }}</td>
            <td>
              <span class="plan-badge {% if cliente.estado == 'activo' %}starter{% elif cliente.estado == 'cancelado' %}enterprise{% else %}default{% endif %}">
                {% if cliente.estado == 'activo' %}Activo{% elif cliente.estado == 'cancelado' %}Cancelado{% else %}Nunca compró{% endif %}
              </span>
            </td>
            <td>{{ cliente.plan }}</td>
          </tr>
          {% empty %}
          <tr><td colspan="5" class="td-empty">No hay usuarios registrados.</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
```

(El uso de las clases de color `starter`/`enterprise`/`default` de `.plan-badge` es solo para reusar los colores ya definidos — verde para "Activo", ámbar para "Cancelado", gris para "Nunca compró" — ajustar si al ver el resultado visual no calza bien, usar buen criterio, esto no es una vista rediseñada por Replit todavía.)

### 4. surveys/templates/dashboard_metricas.html — actualizar sidebar

En el sidebar de este archivo (el mismo bloque que se duplica en el archivo nuevo):
- Eliminar por completo el `<a href="#">...Reportes</a>` (bloque con el ícono de barras).
- Cambiar `<a href="#" class="active">...Métricas</a>` a `<a href="{% url 'dashboard_metricas' %}" class="active">`.
- Cambiar `<a href="#">...Clientes</a>` a `<a href="{% url 'dashboard_clientes' %}">` (sin `class="active"` aquí, porque en esta página la sección activa es Métricas).

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/dashboard_views.py nom035/urls.py` sin errores.
2. Probar `/metricas/clientes/` en staging con los mismos 3 casos de siempre: anónimo → redirige a login; autenticado no-superuser → 403; superuser → 200.
3. Confirmar visualmente en staging, con los usuarios de prueba ya existentes (`pruebaB@test.com`, etc.), que:
   - Un usuario con `stripe_plan_key` activo aparece como "Activo" con su plan correcto
   - Un usuario que tuvo un `PlanPurchaseEvent` pero ya no tiene plan activo aparece como "Cancelado" con el plan que había contratado
   - Un usuario sin ningún `PlanPurchaseEvent` aparece como "Nunca compró", sin plan
4. Confirmar que los links "Métricas" y "Clientes" del sidebar navegan correctamente entre ambas vistas en los dos templates, y que "Reportes" ya no aparece en ninguno de los dos.

## Fuera de alcance de este lote
- Vista de detalle por cliente (historial completo de cada `PlanPurchaseEvent`, no solo el más reciente) — posible v4 si Jorge lo pide.
- Búsqueda/filtro/paginación en el listado — innecesario hoy por el tamaño de la base de usuarios.
- La sección "Reportes" — Jorge confirmó que no hace falta por ahora, simplemente se quita el link.
- Cualquier cambio a `DashboardMetricasView.get()` más allá de mover `test_func`/`handle_no_permission` al mixin nuevo — la lógica de métricas (KPIs, distribución de planes, profundidad de uso, línea de tiempo si ya está mergeada) queda exactamente igual.
