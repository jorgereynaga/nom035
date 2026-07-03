# ESTADO NormaIA — Actualizado 3 Jul 2026

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: jorge.reynaga.j@gmail.com (usuario activo con datos demo)

## Completado
- Fix flujo completo NOM-035 (EndEvaluation, Ver resultados, reporte HTML)
- Modulo Clima Laboral completo con datos demo (8 respuestas, 8 dimensiones)
- Dashboard rediseñado 3 secciones con preview de dimensiones 4x2 con colores
- Candidatos demo aparecen en dashboard con nombre y estado correcto
- Registro y login redirigen al dashboard (no a planes)
- Bloqueo sin plan: nuevo centro, agregar empleados, agregar candidatos
- Modal "Plan requerido" al intentar funcion bloqueada
- Boton borrar datos demo (manual) + borrado automatico al contratar plan
- Reporte HTML profesional sin WeasyPrint
- Reporte unificado desbloqueado para usuarios demo
- psico_resultado.html rediseñado correctamente extendiendo index.html ✅
- NOM-035 dimension preview: promedio de todos los empleados ✅
- DEBUG=False en Railway ✅
- Nueva logica bloqueo encuestas: es_demo=True bloquea registro encuestas reales ✅
- Quitar nom035_demo del flujo de creditos ✅
- Restriccion clima laboral: enlace publico solo con plan activo ✅
- admin.py: nom035_creditos visible en UserAdmin ✅
- Fix phone max_length a 15 caracteres (migration 0033) ✅
- Revision completa NOM-035-STPS-2018 (texto oficial DOF) para diseño Portafolio de Evidencias ✅
- Definido alcance Portafolio de Evidencias: Fase A (auto), Fase C (carga manual), Fase B descartada ✅

## Estado actual (dashboard funcional)
- NOM-035: 100% cuestionarios, Completado, dimensiones 4x2 visibles ✅
- Clima Laboral: 8 respuestas, grid 4x2 con colores por nivel ✅
- Psicometria: 2 candidatos demo con evaluacion asignada ✅
- Borrar datos demo: FUNCIONA ✅
- Bloqueos sin plan: FUNCIONA ✅
- Reporte unificado: FUNCIONA ✅
- Dashboard carga correctamente ✅

## Pendientes
1. Portafolio de evidencias — Fase A: modelo PortafolioEvidencias + PortafolioStatusView (checklist) + GenerarPoliticaPDF + GenerarInformeResultadosPDF
2. Portafolio de evidencias — Fase C (despues de A): espacios de carga manual para canalizaciones Guia I, examenes medicos, medidas de control, evidencia de difusion
3. Pruebas finales: navegacion entre evaluaciones multiples

## Notas tecnicas
- views.py: mezcla tabs/espacios es el principal riesgo — siempre py_compile antes de push
- WeasyPrint: permanentemente bloqueado en Railway, usar HTML imprimible
- Migraciones: siempre manuales, ultima es 0033
- nom035_demo: campo en Userapp que ya no se usa en flujo principal
- Logica bloqueo: workplace.es_demo=True → 403 en registro de encuestas
- clima_sin_plan.html: template para enlace publico sin plan activo
- Editor: Sublime Text — siempre editar Python con python -c por indices de linea
- Portafolio Evidencias: NO usar boton unico "generar todo" — dashboard/checklist con
  generacion individual por documento, para evitar implicar que es paquete "certificado"
  ante autoridad (eso lo hacen Unidades de Verificacion, no la plataforma)
- Portafolio Evidencias Fase A usa tablas oficiales de la norma para niveles de riesgo
  (deterministico, sin IA generativa libre en conclusiones/recomendaciones)
