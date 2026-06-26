# ============================================================
# STRIPE PLANS — IHES NOM-035
# Actualizados Jun 2026
# ============================================================

PLANS = {
    # ── NOM-035 (pago unico, vigencia 1 año) ─────────────────
    # nom035_micro oculto por ahora
    "nom035_micro": {
        "price_id": "price_PENDIENTE_MICRO",
        "name": "NOM-035 Micro",
        "descripcion": "15 evaluaciones con vigencia de un año",
        "precio": 599,
        "periodo": "anual",
        "modulo": "nom035",
        "evaluaciones_total": 15,
        "visible": False,
    },
    "nom035_pyme": {
        "price_id": "price_1TmbFUKv0IwwlafKNdHPKxmL",
        "name": "NOM-035 PyME",
        "descripcion": "50 evaluaciones con vigencia de un año",
        "precio": 1190,
        "periodo": "anual",
        "modulo": "nom035",
        "evaluaciones_total": 50,
        "visible": True,
    },
    "nom035_empresarial": {
        "price_id": "price_1TmbWAKv0IwwlafKLkizNhJ7",
        "name": "NOM-035 Empresarial",
        "descripcion": "100 evaluaciones con vigencia de un año",
        "precio": 2400,
        "periodo": "anual",
        "modulo": "nom035",
        "evaluaciones_total": 100,
        "visible": True,
    },
    "nom035_ilimitado": {
        "price_id": "price_1TmbWlKv0IwwlafKRMeC838m",
        "name": "NOM-035 Ilimitado",
        "descripcion": "Evaluaciones ilimitadas con vigencia de un año",
        "precio": 12000,
        "periodo": "anual",
        "modulo": "nom035",
        "evaluaciones_total": -1,
        "visible": True,
    },

    # ── PSICOMETRIA ───────────────────────────────────────────
    "psico_starter": {
        "price_id": "price_1TmbXWKv0IwwlafKplaxn3fI",
        "name": "Psicometría Starter",
        "descripcion": "20 evaluaciones por mes, se renuevan cada mes",
        "precio": 390,
        "periodo": "mensual",
        "modulo": "psicometria",
        "evaluaciones_mes": 20,
        "evaluaciones_total": None,
        "visible": True,
    },
    "psico_ilimitado_mensual": {
        "price_id": "price_1TmbYNKv0IwwlafKU3K8usO2",
        "name": "Psicometría Ilimitado Mensual",
        "descripcion": "Evaluaciones ilimitadas, pago mensual",
        "precio": 1500,
        "periodo": "mensual",
        "modulo": "psicometria",
        "evaluaciones_mes": -1,
        "evaluaciones_total": None,
        "visible": True,
    },
    "psico_ilimitado_anual": {
        "price_id": "price_1TmcFcKv0IwwlafKyuCJiBCw",
        "name": "Psicometría Ilimitado Anual",
        "descripcion": "Evaluaciones ilimitadas, pago anual",
        "precio": 12500,
        "periodo": "anual",
        "modulo": "psicometria",
        "evaluaciones_mes": -1,
        "evaluaciones_total": None,
        "visible": True,
    },

    # ── SUITE EMPRESARIAL (anual) ─────────────────────────────
    "suite_pro_50": {
        "price_id": "price_1TmcHEKv0IwwlafKcUaYDZCv",
        "name": "Suite Pro 50",
        "descripcion": "50 evaluaciones NOM-035 + psicometría ilimitada — anual",
        "precio": 13000,
        "periodo": "anual",
        "modulo": "suite",
        "evaluaciones_total": 50,
        "evaluaciones_mes": -1,
        "visible": True,
    },
    "suite_pro_100": {
        "price_id": "price_1TmcJ7Kv0IwwlafKxcy9ZHWB",
        "name": "Suite Pro 100",
        "descripcion": "100 evaluaciones NOM-035 + psicometría ilimitada — anual",
        "precio": 13800,
        "periodo": "anual",
        "modulo": "suite",
        "evaluaciones_total": 100,
        "evaluaciones_mes": -1,
        "visible": True,
    },
    "suite_pro_ilimitado": {
        "price_id": "price_1TmcL3Kv0IwwlafK4YTtbibt",
        "name": "Suite Pro Ilimitado",
        "descripcion": "NOM-035 ilimitado + psicometría ilimitada — anual",
        "precio": 16000,
        "periodo": "anual",
        "modulo": "suite",
        "evaluaciones_total": -1,
        "evaluaciones_mes": -1,
        "visible": True,
    },
}

# Indice inverso: price_id -> plan_key (util en webhooks)
PRICE_ID_TO_PLAN = {v["price_id"]: k for k, v in PLANS.items()}
