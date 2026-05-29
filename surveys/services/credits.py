from surveys.stripe_plans import STRIPE_PLANS
from surveys.models import CreditWallet


def assign_nom035_credits(workplace, plan_key):
    plan = STRIPE_PLANS.get(plan_key)
    if not plan:
        print(f"⚠️ Plan no encontrado: {plan_key}")
        return

    modulo = plan.get('modulo')
    empleados_max = plan.get('empleados_max', 0)
    periodo = plan.get('periodo', 'mensual')

    wallet, created = CreditWallet.objects.get_or_create(workplace=workplace)

    if modulo == 'nom035':
        # Créditos según periodo
        if periodo == 'mensual':
            creditos = empleados_max
        elif periodo == 'semestral':
            creditos = empleados_max * 6
        elif periodo == 'anual':
            creditos = empleados_max * 12
        else:
            creditos = empleados_max

        wallet.nom035_total += creditos
        wallet.save()
        print(f"✅ {creditos} créditos NOM-035 asignados a {workplace.name}")

    else:
        print(f"⚠️ Módulo no manejado aún: {modulo}")
