# ESTADO NormaIA — Actualizado 29 Jun 2026 (tarde)

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: prueba/TestIhes2026!
- Repo: github.com/jorgereynaga/nom035
- Local: C:\Users\JorgeAlbertoReynagaJ\Documents\nom 035\nom035\
- Editor: Sublime Text (tabs, no espacios — editar Python con python -c por indice de linea)

## Ultimo deploy exitoso
- Comando cargar_datos_demo + auto-trigger post-registro
- Fix CSRF en auth-register + errores arriba
- Migration 0030: es_demo en Workplace, Employee, Candidate

## BUG ACTIVO — auth-register.html
- SyntaxError JS en linea ~355: "missing ) after argument list"
- El formulario de registro no funciona
- Pendiente revisar sed -n '350,360p' surveys/templates/auth-register.html
- jQuery carga en linea 277, script en 281-360, cierre body 362
- Posible causa: caracter especial o Django template tag dentro del JS

## Completado en sesiones recientes
- stripe_plans.py: 9 nuevos planes (NOM-035, Psico, Suite)
- Migration 0029: nom035_creditos en Userapp
- credits.py: logica user-scoped para NOM-035 y Suite
- workplaceform.html: rediseno NormaIA
- employeeform.html: Select2 con opcion crear nueva area
- psico_test.html: soporte multiple choice Raven/Moss
- Dashboard: seccion informativa NOM-035 eliminada
- cargar_datos_demo.py: comando completo con 6 empleados + 2 candidatos
- views.py ~1658: call_command cargar_datos_demo post-registro

## Pendientes
1. FIX URGENTE: SyntaxError JS en auth-register.html linea ~355
2. Verificar que registro funciona y datos demo se crean
3. Dashboard adaptivo NOM-035/Psicometria segun plan (con Replit)
4. Boton "Eliminar datos de ejemplo"
5. admin.py: agregar nom035_creditos visible
6. Fix campo phone max_length a 15

## Arquitectura creditos NOM-035
- nom035_creditos en Userapp (user-scoped)
- Descuento en views.py al guardar risksurveya/b/traumasurvey
- Demo: nom035_demo=1, psico_demo=1 en Userapp
