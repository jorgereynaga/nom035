# ESTADO NormaIA — Actualizado 29 Jun 2026 (noche)

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: prueba/TestIhes2026!
- Repo: github.com/jorgereynaga/nom035
- Local: C:\Users\JorgeAlbertoReynagaJ\Documents\nom 035\nom035\
- Editor: Sublime Text (tabs — editar Python con python -c por indice de linea)

## Ultimo deploy exitoso
- auth-register: fix llave extra JS, CSRF cookie, errores arriba
- Registro funciona — datos demo se crean automaticamente al registrar
- Migration 0030: es_demo en Workplace, Employee, Candidate

## Bugs activos en datos demo (PRIORIDAD)
1. Empleados: vista muestra solo 1 de 6 — probablemente filtro por evaluation o paginacion
2. Empleados: dice "no contestó encuesta" aunque RiskSurveyA/B fueron creados
3. Portafolio de evidencias: no muestra reportes del centro demo
4. Candidatos: aparecen 0 aunque se crearon 2 — vista puede filtrar diferente
5. Candidatos: no tienen sesiones psicometricas asignadas (TestSession) ni respuestas

## Para investigar en proxima sesion
- Ver como views.py filtra empleados en la vista de centro de trabajo
- Ver como views.py detecta si empleado contestó encuesta
- Ver modelo TestSession y como asignar evaluaciones a candidatos demo
- grep -n "surveyA\|survey_a\|contestado\|completed" surveys/views.py

## Completado
- stripe_plans.py: 9 planes activos
- Migration 0029: nom035_creditos en Userapp
- Migration 0030: es_demo en Workplace, Employee, Candidate
- cargar_datos_demo.py: crea workplace + 6 empleados + RiskSurveyA/B + 2 candidatos
- views.py ~1658: call_command cargar_datos_demo post-registro
- workplaceform.html, employeeform.html, psico_test.html: rediseños completados
- auth-register.html: CSRF fix, errores arriba, llave JS extra corregida

## Pendientes generales
1. Fix datos demo (ver bugs arriba)
2. Dashboard adaptivo NOM-035/Psicometria segun plan (Replit)
3. Boton "Eliminar datos de ejemplo"
4. admin.py: nom035_creditos visible
5. Fix phone max_length a 15
