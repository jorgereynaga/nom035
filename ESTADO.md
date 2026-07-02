# ESTADO NormaIA — Actualizado 2 Jul 2026

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: jorge.reynaga.j@gmail.com

## Completado hoy
- Fix EndEvaluation: URL, workplace_id, slash inicial
- Fix WorkplaceResultView: permite ver resultados aunque paid=False
- Fix Ver resultados: apunta a evaluation-1, solo tras finalizar
- Recarga automatica tras finalizar aplicacion
- Bootstrap JS y tooltip condicional en workplace_detail y workplace_results
- Reporte HTML sin WeasyPrint + rediseno profesional
- Candidatos demo: es_demo en modelo + admin
- CSS paginacion DataTable + selector de registros
- DataTable usa eval_to_check segun estado paid
- Modulo Clima Laboral completo (modelo, vistas, templates, datos demo)
- Dashboard rediseñado con 3 secciones (NOM-035/Psicometria/Clima)
- Mini-tarjetas dimensiones con color por nivel de riesgo, grid 4x2
- Boton Resultados completos con URL correcta
- Candidatos demo aparecen en dashboard con nombre correcto
- climate_dimensions_preview y dimensions_preview en contexto

## Estado actual demo
- NOM-035: 100% cuestionarios, Completado, dimensiones visibles ✅
- Clima Laboral: 8 respuestas, grid 4x2 con colores ✅
- Psicometria: 2 candidatos demo visibles, estado Pendiente ✅

## Pendientes
1. Asignar evaluaciones psicometricas a candidatos demo
2. Portafolio de evidencias automatico (pendiente revision norma)
3. Boton eliminar datos demo
4. admin.py: nom035_creditos visible
5. Fix phone max_length a 15
6. Restriccion clima laboral solo usuarios con plan/pago
7. Pruebas finales: navegacion entre evaluaciones multiples
