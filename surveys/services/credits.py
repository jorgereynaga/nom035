from surveys.stripe_plans import PLANS as STRIPE_PLANS
from surveys.models import CreditWallet


def assign_nom035_credits(user, plan_key):
    plan = STRIPE_PLANS.get(plan_key)
    if not plan:
        print(f"⚠️ Plan no encontrado: {plan_key}")
        return

    modulo = plan.get('modulo')
    empleados_max = plan.get('empleados_max') or 0
    evaluaciones_mes = plan.get('evaluaciones_mes') or 0
    evaluaciones_total = plan.get('evaluaciones_total') or 0
    periodo = plan.get('periodo', 'mensual')

    if modulo == 'nom035':
        workplace = user.workplaces.first()
        if not workplace:
            print(f"⚠️ Usuario sin workplace: {user.email}")
            return
        if periodo == 'mensual':
            creditos = empleados_max
        elif periodo == 'semestral':
            creditos = empleados_max * 6
        elif periodo == 'anual':
            creditos = empleados_max * 12
        else:
            creditos = empleados_max
        wallet, created = CreditWallet.objects.get_or_create(workplace=workplace)
        wallet.nom035_total += creditos
        wallet.save()
        print(f"✅ {creditos} créditos NOM-035 asignados a {workplace.name}")

    elif modulo == 'psicometria':
        if evaluaciones_total:
            creditos = evaluaciones_total
        elif evaluaciones_mes:
            if periodo == 'mensual':
                creditos = evaluaciones_mes
            elif periodo == 'semestral':
                creditos = evaluaciones_mes * 6
            elif periodo == 'anual':
                creditos = evaluaciones_mes * 12
            else:
                creditos = evaluaciones_mes
        else:
            creditos = 0
        try:
            userapp = user.userapp
            userapp.psico_evaluaciones_disponibles += creditos
            userapp.save()
            print(f"✅ {creditos} créditos psicometría asignados a {userapp.name}")
        except Exception as e:
            print(f"⚠️ Error asignando psico: {e}")

    else:
        print(f"⚠️ Módulo no manejado: {modulo}")