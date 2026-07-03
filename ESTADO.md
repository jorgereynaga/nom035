# ESTADO NormaIA — Actualizado 2 Jul 2026

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: jorge.reynaga.j@gmail.com

## Completado hoy
- Fix flujo completo NOM-035 (EndEvaluation, Ver resultados, reporte HTML)
- Modulo Clima Laboral completo con datos demo
- Dashboard rediseñado 3 secciones con preview de dimensiones 4x2
- Candidatos demo aparecen en dashboard
- Registro y login redirigen al dashboard (no a planes)
- Bloqueo sin plan: nuevo centro, agregar empleados, agregar candidatos
- Modal "Plan requerido" al intentar accionar bloqueado
- Boton borrar datos demo (manual)
- Borrado automatico de datos demo al contratar plan (webhook Stripe)
- CSS paginacion DataTable + selector de registros funciona
- Reporte HTML profesional sin WeasyPrint

## Estado actual demo (usuario nuevo)
- NOM-035: 100% cuestionarios, Completado, dimensiones visibles ✅
- Clima Laboral: 8 respuestas, grid 4x2 con colores ✅
- Psicometria: 2 candidatos demo con evaluacion asignada ✅
- Borrar datos demo: FUNCIONA ✅
- Bloqueos sin plan: FUNCIONA ✅

## Pendientes
1. Reporte unificado candidatos — desbloquear vista
2. Portafolio de evidencias automatico (pendiente revision norma)
3. admin.py: nom035_creditos visible
4. Fix phone max_length a 15
5. Restriccion clima laboral — acceso enlace publico sin plan
6. Pruebas finales: navegacion entre evaluaciones multiples
7. NOM-035 dimension preview — mostrar solo empleados con encuesta completada (no solo el primero)
