# Reglas de comision para socios comerciales (partners/referidos), confirmadas con Jorge 2026-08-03,
# porcentajes ajustados 2026-08-03 (15/7.5 -> 10/5).
# - Psicometria Starter no genera comision (ingreso muy bajo para justificarla).
# - Planes de entrada (< $3,000): comision fija de $300, igual en venta y renovacion.
# - Planes grandes: 10% en la primera venta, 5% en cada renovacion.

COMMISSION_EXCLUDED_PLANS = {'psico_starter'}
COMMISSION_FIXED_PLANS = {'nom035_micro', 'nom035_pyme', 'nom035_empresarial', 'psico_ilimitado_mensual'}
COMMISSION_FIXED_AMOUNT = 300
COMMISSION_PCT_VENTA = 10
COMMISSION_PCT_RENOVACION = 5


def calcular_comision_partner(plan_key, monto_plan, es_renovacion=False):
    """Devuelve el monto de comision (MXN) para un partner segun el plan comprado."""
    if plan_key in COMMISSION_EXCLUDED_PLANS:
        return 0
    if plan_key in COMMISSION_FIXED_PLANS:
        return COMMISSION_FIXED_AMOUNT
    pct = COMMISSION_PCT_RENOVACION if es_renovacion else COMMISSION_PCT_VENTA
    return round(float(monto_plan or 0) * pct / 100, 2)
