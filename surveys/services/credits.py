from surveys.stripe_plans import PLANS as STRIPE_PLANS

def assign_nom035_credits(user, plan_key):
    plan = STRIPE_PLANS.get(plan_key)
    if not plan:
        print(f"⚠️ Plan no encontrado: {plan_key}")
        return

    modulo = plan.get("modulo")
    evaluaciones_mes = plan.get("evaluaciones_mes") or 0
    evaluaciones_total = plan.get("evaluaciones_total") or 0

    if modulo == "nom035":
        # Creditos a nivel usuario, compartidos entre todos sus workplaces
        if evaluaciones_total == -1:
            creditos = 999999  # ilimitado
        else:
            creditos = evaluaciones_total or 0
        try:
            userapp = user.userapp
            userapp.nom035_creditos += creditos
            userapp.save()
            print(f"✅ {creditos} creditos NOM-035 asignados a {userapp.name}")
        except Exception as e:
            print(f"⚠️ Error asignando nom035: {e}")

    elif modulo == "psicometria":
        if evaluaciones_mes == -1:
            creditos = 999999  # ilimitado
        elif evaluaciones_total:
            creditos = evaluaciones_total
        else:
            creditos = evaluaciones_mes or 0
        try:
            userapp = user.userapp
            userapp.psico_evaluaciones_disponibles += creditos
            userapp.save()
            print(f"✅ {creditos} creditos psico asignados a {userapp.name}")
        except Exception as e:
            print(f"⚠️ Error asignando psico: {e}")

    elif modulo == "suite":
        # NOM-035 a nivel usuario
        if evaluaciones_total == -1:
            creditos_nom = 999999
        else:
            creditos_nom = evaluaciones_total or 0
        # Psico ilimitado
        creditos_psico = 999999 if evaluaciones_mes == -1 else (evaluaciones_mes or 0)
        try:
            userapp = user.userapp
            userapp.nom035_creditos += creditos_nom
            userapp.psico_evaluaciones_disponibles += creditos_psico
            userapp.save()
            print(f"✅ Suite: {creditos_nom} NOM-035 + {creditos_psico} psico asignados a {userapp.name}")
        except Exception as e:
            print(f"⚠️ Error asignando suite: {e}")

    else:
        print(f"⚠️ Modulo no manejado: {modulo}")
