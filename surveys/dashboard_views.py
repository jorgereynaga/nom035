from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from .models import Userapp, Workplace, Candidate, Result, TestSession, PlanPurchaseEvent
from .stripe_plans import PLANS


class DashboardMetricasView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()  # redirige a login_url
        raise PermissionDenied  # logueado pero no superuser -> 403 real

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
