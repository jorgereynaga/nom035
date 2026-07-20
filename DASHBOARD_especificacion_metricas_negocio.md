# Dashboard interno de métricas de negocio — Especificación completa

## Instrucciones operativas
- Repo: nom035, rama base: `auditoria-local`
- Crear rama nueva: `git checkout auditoria-local && git pull && git checkout -b feature/dashboard-metricas-negocio`
- Entorno: usar el venv existente (`C:\NormaIA-Pruebas\nom035\venv`, Python 3.10)
- `surveys/models.py` usa **TABS** para indentación (confirmado con `cat -A`) — respetar al insertar el modelo nuevo.
- `surveys/stripe_views.py` usa **4 ESPACIOS** (confirmado) — respetar al insertar la línea nueva en `_handle_checkout_completed`.
- Archivo nuevo `surveys/dashboard_views.py`: no hereda estilo de ningún archivo existente, usar 4 espacios (PEP8 estándar).
- Última migración existente: `0039_perfil_narrativo_historial.py`. La migración de este lote es `0040_plan_purchase_event.py`, manual, dependencia `0039_perfil_narrativo_historial`. NO usar `makemigrations` real.
- `nom035/urls.py` importa `surveys.views` con wildcard, pero `surveys.stripe_views` y `surveys.psico_views` con import explícito por nombre (lista `from surveys.X import (...)`). **CUALQUIER vista nueva debe agregarse a un import explícito de este mismo tipo** — el bug histórico documentado en ESTADO.md (NameError en Railway al arrancar) fue exactamente por olvidar este paso con `InstrumentosCatalogoView`. Usar import explícito nuevo: `from surveys.dashboard_views import DashboardMetricasView`.
- `python -m py_compile` en cada archivo tocado antes de dar el lote por bueno.

## Contexto y objetivo

Vista interna, **solo para Jorge** (no para clientes/usuarios del sistema), que muestre — para un rango de fechas seleccionable — métricas de negocio: usuarios registrados, clientes históricos vs. activos, desglose y distribución de planes, MRR estimado, y profundidad de uso por cliente de pago.

Es una iniciativa nueva e independiente del trabajo de auditoría de seguridad en curso; no bloquea ni depende de ningún lote `fix/lote-X`. Sí toca `StripeWebhookView` (código que sirve a clientes reales), así que se trata con el mismo cuidado: rama propia, validación en staging, sin tocar producción hasta aprobación explícita.

### Decisión ya tomada: se necesita historial, no solo snapshot
Hoy, cuando un cliente cancela, `_handle_subscription_change` (`surveys/stripe_views.py:240`) vacía `stripe_plan_key` — se pierde el rastro de que alguna vez fue cliente de pago. Se agrega una tabla nueva append-only que registra cada compra/activación, y que **nunca se modifica ni se borra** cuando el cliente cancela.

### Decisión ya tomada: no hace falta distinguir cuentas demo/prueba de clientes reales
No existe (ni se construye) un campo "cuenta de prueba". `Workplace.es_demo` / `Candidate.es_demo` marcan **contenido de muestra autogenerado**, no el tipo de cuenta — se excluyen esos registros de las métricas de *uso*, pero no de las métricas de *clientes* (todo usuario real cuenta).

### Decisión ya tomada: administradores no cuentan como "usuarios"
Las cuentas de staff/superusuario (ej. la cuenta admin de Jorge en `/ihes_admin/`) no son clientes y deben excluirse de "usuarios registrados" y de cualquier métrica derivada. El código ya tenía esta intención comentada (`surveys/views.py:1079`, `.filter(user__is_staff=False)` comentado) — aquí sí se aplica.

## Modelos y datos existentes relevantes (ya investigados, no repetir la investigación)

- `Userapp` (`surveys/models.py:58`): `user` (OneToOne a `User`), `stripe_customer_id`, `stripe_plan_key` (`''` si no tiene plan activo), `record_create`. Se crea junto con `User` en el registro (`UserappList.post`, `surveys/views.py:1849`) — toda cuenta real de cliente tiene `Userapp`, las cuentas de staff creadas por `createsuperuser` normalmente NO.
- `Workplace` (`surveys/models.py:88`): `user` FK, `es_demo`. Sin FK a plan — el plan vive en `Userapp`.
- `Candidate` (`surveys/models.py:527`): `user` FK, `es_demo`.
- `Result` (`surveys/models.py:128`): evaluación NOM-035 completada, FK a `Workplace` (no a `Userapp` directo — ir por `workplace.user`).
- `TestSession` (`surveys/models.py:561`): `status='completada'` = evaluación psicométrica completada, FK a `Candidate` (no a `Userapp` directo — ir por `candidate.user`, y filtrar demo por `candidate.es_demo`, `TestSession` no tiene su propio `es_demo`).
- `PLANS` (`surveys/stripe_plans.py`): dict en código, cada plan tiene `precio` (MXN), `periodo` (`'anual'`/`'mensual'`), `modulo` (`'nom035'`/`'psicometria'`/`'suite'`), `name`. Todos los planes actuales son suscripciones recurrentes de Stripe (anuales o mensuales) — no hay pagos únicos reales en `PLANS` hoy pese a que `StripeCheckoutView` contempla `periodo == 'unico'` como caso posible (código defensivo sin plan que lo use actualmente, no se toca).

## Cambios requeridos

### 1. surveys/models.py — modelo nuevo `PlanPurchaseEvent`

Agregar al final del archivo:

```python
class PlanPurchaseEvent(models.Model):
	"""Registro historico append-only de cada activacion de plan. NUNCA se edita ni se borra."""
	user=models.ForeignKey(User,related_name="plan_purchase_events",on_delete=models.CASCADE)
	plan_key=models.CharField(u'Plan',max_length=100)
	modulo=models.CharField(u'Modulo',max_length=20)
	precio=models.DecimalField(u'Precio (snapshot MXN)',max_digits=10,decimal_places=2)
	periodo=models.CharField(u'Periodo',max_length=20)
	stripe_customer_id=models.CharField(u'Stripe Customer ID',max_length=100,blank=True,null=True)
	record_create=models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return f"{self.user.username} - {self.plan_key} ({self.record_create.date()})"
```

`precio` y `periodo` se guardan como snapshot (no se leen de `PLANS` en el momento de consultar el histórico) para que cambios futuros de precio no alteren retroactivamente el MRR histórico. Sin `record_update`, sin soft-delete: este modelo es append-only por diseño, no por convención de código — no agregar ningún método `.save()`/`.delete()` override ni admin action que permita editar/borrar filas.

Migración manual `surveys/migrations/0040_plan_purchase_event.py`:
```python
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0039_perfil_narrativo_historial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanPurchaseEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_key', models.CharField(max_length=100, verbose_name='Plan')),
                ('modulo', models.CharField(max_length=20, verbose_name='Modulo')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio (snapshot MXN)')),
                ('periodo', models.CharField(max_length=20, verbose_name='Periodo')),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='Stripe Customer ID')),
                ('record_create', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plan_purchase_events', to='auth.user')),
            ],
        ),
    ]
```
Verificar el nombre exacto de la app (`'auth.user'` vs `'auth.User'`, minúscula esperada por convención de Django) contra alguna migración existente del proyecto que también tenga FK a `User`, para no adivinar el formato.

### 2. surveys/stripe_views.py — un solo `create()` nuevo, cero cambios a lógica existente

En `_handle_checkout_completed` (línea 177), **después** de `userapp.save()` (línea 199) y **antes** del bloque `try` que borra datos demo (línea 202), agregar:

```python
            from .models import PlanPurchaseEvent
            PlanPurchaseEvent.objects.create(
                user=userapp.user,
                plan_key=plan_key,
                modulo=plan.get('modulo', ''),
                precio=plan.get('precio', 0),
                periodo=plan.get('periodo', ''),
                stripe_customer_id=userapp.stripe_customer_id,
            )
```

No se toca `_activate_plan`, `_handle_invoice_paid`, `_handle_payment_failed` ni `_handle_subscription_change` — el histórico de la compra inicial es suficiente para responder "compró alguna vez" y para el MRR (que se calcula sobre `Userapp.stripe_plan_key` **actual**, no sumando eventos). Las renovaciones (`invoice.paid`) NO generan un evento nuevo en esta versión — quedan fuera de alcance (ver sección de fuera de alcance) porque no son necesarias para ninguna de las métricas pedidas hoy.

### 3. surveys/dashboard_views.py — archivo nuevo

```python
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from .models import Userapp, Workplace, Candidate, Result, TestSession, PlanPurchaseEvent
from .stripe_plans import PLANS


class DashboardMetricasView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    raise_exception = True  # 403 en vez de redirect si esta logueado pero no es superuser

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        fecha_fin = self._parse_fecha(request.GET.get('fecha_fin')) or timezone.now()
        fecha_inicio = self._parse_fecha(request.GET.get('fecha_inicio')) or (fecha_fin - timedelta(days=30))

        usuarios_qs = User.objects.filter(
            is_staff=False, is_superuser=False,
            date_joined__gte=fecha_inicio, date_joined__lte=fecha_fin,
        )
        total_usuarios = usuarios_qs.count()

        usuarios_con_compra_historica = usuarios_qs.filter(
            plan_purchase_events__isnull=False
        ).distinct().count()

        # Snapshot actual, no depende del rango de fechas
        clientes_activos_qs = Userapp.objects.filter(
            user__is_staff=False, user__is_superuser=False,
        ).exclude(stripe_plan_key='')
        clientes_activos = clientes_activos_qs.count()

        desglose_planes = {}
        for ua in clientes_activos_qs.select_related('user'):
            plan_info = PLANS.get(ua.stripe_plan_key, {})
            nombre_plan = plan_info.get('name', ua.stripe_plan_key)
            desglose_planes.setdefault(nombre_plan, 0)
            desglose_planes[nombre_plan] += 1

        distribucion_planes = []
        for nombre_plan, count in desglose_planes.items():
            pct = round((count / clientes_activos) * 100, 1) if clientes_activos else 0
            distribucion_planes.append({'plan': nombre_plan, 'clientes': count, 'pct': pct})

        mrr = Decimal('0')
        for ua in clientes_activos_qs:
            plan_info = PLANS.get(ua.stripe_plan_key)
            if not plan_info:
                continue
            precio = Decimal(str(plan_info['precio']))
            if plan_info['periodo'] == 'anual':
                mrr += precio / Decimal('12')
            else:
                mrr += precio

        profundidad_uso = []
        for ua in clientes_activos_qs.select_related('user'):
            centros_activos = Workplace.objects.filter(user=ua.user, es_demo=False).count()
            evaluaciones_nom035 = Result.objects.filter(
                workplace__user=ua.user, workplace__es_demo=False
            ).count()
            evaluaciones_psico = TestSession.objects.filter(
                candidate__user=ua.user, candidate__es_demo=False, status='completada'
            ).count()
            profundidad_uso.append({
                'usuario': ua.user.username,
                'email': ua.user.email,
                'plan': PLANS.get(ua.stripe_plan_key, {}).get('name', ua.stripe_plan_key),
                'centros_activos': centros_activos,
                'evaluaciones_nom035': evaluaciones_nom035,
                'evaluaciones_psico': evaluaciones_psico,
            })

        return render(request, 'dashboard_metricas.html', {
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'total_usuarios': total_usuarios,
            'usuarios_con_compra_historica': usuarios_con_compra_historica,
            'clientes_activos': clientes_activos,
            'distribucion_planes': distribucion_planes,
            'mrr': round(mrr, 2),
            'profundidad_uso': profundidad_uso,
        })

    def _parse_fecha(self, valor):
        if not valor:
            return None
        try:
            return timezone.make_aware(datetime.strptime(valor, '%Y-%m-%d'))
        except ValueError:
            return None
```

Notas de diseño de la vista:
- `UserPassesTestMixin` + `test_func` sobre `is_superuser` es la verificación real pedida — no una URL oculta. `raise_exception = True` hace que un usuario autenticado pero no-superuser reciba 403 en vez de ser redirigido silenciosamente al login (lo cual sería confuso). Un usuario no autenticado sí es redirigido a `/login/` por `LoginRequiredMixin`, que corre primero en el MRO.
- "Usuarios registrados" y "compraron alguna vez" respetan el rango de fechas (filtran por `date_joined` del usuario). "Plan activo ahora", "distribución de planes", "MRR" y "profundidad de uso" son snapshots del momento actual — no tendría sentido histórico filtrarlos por fecha de registro del usuario (un cliente activo hoy pudo haberse registrado hace 2 años, fuera del rango). Esto es una decisión de diseño explícita, no un descuido — confirmarla con Jorge al revisar el diff por si prefiere otro comportamiento.
- Fechas por defecto: últimos 30 días si no se pasan `fecha_inicio`/`fecha_fin` por querystring.

### 4. surveys/templates/dashboard_metricas.html — archivo nuevo

Template **standalone** (su propio `<html>`, sin `{% extends 'index.html' %}`), mismo patrón que los `psico_*.html`. Se evita así deliberadamente el bug de bloques Django documentado en ESTADO.md (`{% block style %}` anidado dentro de `<style>` del layout base causa que contenido fuera de bloques se descarte silenciosamente — ver sección "LECCION TECNICA CRITICA" de ESTADO.md). Al ser standalone no hereda ese riesgo.

Contenido mínimo (funcional, sin diseño — el diseño visual se hace después con Replit, prompt aparte):
- Formulario simple `GET` con 2 inputs `type="date"` (`fecha_inicio`, `fecha_fin`) y botón "Aplicar", que recarga la misma vista con querystring.
- Tarjetas con los números: `total_usuarios`, `usuarios_con_compra_historica`, `clientes_activos`, `mrr` (formateado como moneda MXN).
- Tabla o gráfica de pastel con `distribucion_planes` (plan, clientes, pct).
- Tabla con `profundidad_uso` (una fila por cliente activo: usuario, email, plan, centros activos, evaluaciones NOM-035, evaluaciones psicometría).
- Incluir Chart.js vía CDN (`<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`) para una gráfica de pastel de `distribucion_planes` — no hay librería de gráficas instalada en el proyecto hoy, y este es el patrón ya usado para otras dependencias JS (jQuery, toastr, DataTables se cargan igual, vía CDN directo en `index.html`).

No es necesario que este HTML se vea bien — es el "esqueleto funcional" que después se le manda a Replit con su propio prompt de diseño (fuera de alcance de este lote, lo escribo yo por separado cuando este esqueleto esté confirmado funcionando).

### 5. nom035/urls.py

Agregar el import explícito:
```python
from surveys.dashboard_views import DashboardMetricasView
```
Y una entrada en `urlpatterns` (junto a las rutas de `psico/`, por ejemplo):
```python
    path('metricas/', DashboardMetricasView.as_view(), name='dashboard_metricas'),
```
No colgar esta URL bajo `/ihes_admin/` — esa ruta ya está tomada por `admin.site.urls` (línea 61) y no debe interferir con el admin de Django.

## Validación requerida antes de dar el lote por terminado
1. `python -m py_compile surveys/models.py surveys/stripe_views.py surveys/dashboard_views.py nom035/urls.py` sin errores.
2. Confirmar que la migración `0040` aplica sin error sobre una base local/staging (`python manage.py migrate`), nunca contra producción.
3. Probar `/metricas/` con 3 tipos de usuario en staging:
   - No autenticado → redirige a `/login/`.
   - Autenticado, `is_superuser=False` → 403.
   - Autenticado, `is_superuser=True` (cuenta admin existente) → 200, ve la vista completa.
4. Simular una compra en staging (Stripe test mode) y confirmar que se crea exactamente 1 fila nueva en `PlanPurchaseEvent` con los datos correctos (`plan_key`, `precio`, `periodo`, `modulo` coinciden con el plan comprado), y que la activación del plan (`workplaces_available`, etc.) sigue funcionando exactamente igual que antes — este es el punto más sensible, confirmar que no se rompió nada de la lógica ya validada en producción.
5. Cancelar esa suscripción de prueba (o simular el webhook `customer.subscription.deleted`) y confirmar que `Userapp.stripe_plan_key` se vacía como siempre, PERO la fila en `PlanPurchaseEvent` sigue intacta (esto prueba que el histórico sobrevive a la cancelación, el objetivo central de este lote).
6. Confirmar visualmente que los números mostrados en `/metricas/` cuadran con lo que hay en la base de staging (contar manualmente vía Django admin o shell como sanity check, al menos para `total_usuarios` y `clientes_activos`).
7. Probar el filtro de fechas: cambiar `fecha_inicio`/`fecha_fin` en el form y confirmar que `total_usuarios` y `usuarios_con_compra_historica` cambian en consecuencia, mientras que `clientes_activos`, `mrr` y `distribucion_planes` NO cambian (son snapshot).

## Fuera de alcance de este lote (no tocar)
- Diseño visual de `dashboard_metricas.html` — se resuelve después con Replit, prompt separado.
- Registrar eventos de renovación (`invoice.paid`) en `PlanPurchaseEvent` — se puede agregar en un lote futuro si Jorge decide que hace falta para calcular churn con más precisión; no es necesario para ninguna métrica pedida hoy.
- Gráfica de tendencia histórica de MRR a lo largo del tiempo (requeriría snapshots periódicos, no solo eventos de compra) — posible v2.
- Cualquier cambio a `_activate_plan`, `_handle_invoice_paid`, `_handle_payment_failed`, `_handle_subscription_change` — sin cambios.
- Enlace/botón en el sidebar de `index.html` hacia `/metricas/` — decisión pendiente de Jorge (¿quiere un link visible aunque esté protegido, o prefiere navegar directo a la URL?); no se agrega en este lote salvo que lo pida explícitamente.
