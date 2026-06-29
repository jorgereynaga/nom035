# ESTADO NormaIA — Actualizado 29 Jun 2026

## Último deploy exitoso
- Migration 0030: es_demo en Workplace, Employee, Candidate

## Completado en sesiones recientes
- stripe_plans.py: 9 nuevos planes (NOM-035, Psico, Suite)
- Migration 0029: nom035_creditos en Userapp
- credits.py: lógica user-scoped para NOM-035 y Suite
- views.py: descuento nom035_creditos + dashboard muestra creditos correctos
- stripe_planes.html: nuevos planes, campo visible, evaluaciones_total
- workplaceform.html: rediseño NormaIA
- employeeform.html: Select2 con opcion crear nueva area
- psico_test.html: soporte multiple choice Raven/Moss, fix exclusividad Mas/Menos
- Dashboard: seccion informativa NOM-035 eliminada
- Migration 0030: es_demo en Workplace, Employee, Candidate

## Pendientes proxima sesion
1. Comando cargar_datos_demo (workplace + empleados + cuestionarios + candidatos psico)
2. Signal post-registro para disparar datos demo automaticamente
3. Dashboard adaptivo NOM-035/Psicometria segun plan (con Replit)
4. Boton "Eliminar datos de ejemplo"
5. admin.py: agregar nom035_creditos visible
6. Fix campo phone max_length a 15

## Arquitectura creditos NOM-035
- nom035_creditos en Userapp (user-scoped, compartido entre workplaces)
- Descuento en views.py al guardar risksurveya/b/traumasurvey
- Demo: nom035_demo en Userapp (1 credito, no se resetea)

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: prueba/TestIhes2026!
