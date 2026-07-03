# ESTADO NormaIA — Actualizado 2 Jul 2026

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: jorge.reynaga.j@gmail.com (usuario activo con datos demo)

## Completado hoy
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
- Mensaje sin evaluaciones cuando candidato no tiene sesiones completadas
- Fix: related_name sessions (no test_sessions) en candidatos dashboard
- Fix: tabs/espacios en BorrarDemoView y candidates en views.py

## Estado actual (dashboard funcional)
- NOM-035: 100% cuestionarios, Completado, dimensiones 4x2 visibles ✅
- Clima Laboral: 8 respuestas, grid 4x2 con colores por nivel ✅
- Psicometria: 2 candidatos demo con evaluacion asignada ✅
- Borrar datos demo: FUNCIONA ✅
- Bloqueos sin plan: FUNCIONA ✅
- Reporte unificado: FUNCIONA (desbloqueado) ✅
- Dashboard carga correctamente ✅

## Pendientes
1. Rediseno psico_resultado.html — template de Replit causo crash, pendiente redisenar correctamente
2. Portafolio de evidencias automatico (pendiente revision norma)
3. admin.py: nom035_creditos visible
4. Fix phone max_length a 15
5. Restriccion clima laboral — acceso enlace publico solo con plan
6. Pruebas finales: navegacion entre evaluaciones multiples
7. NOM-035 dimension preview — promedio de todos los empleados, no solo el primero
8. DEBUG=True en Railway — CAMBIAR A FALSE antes de pruebas con clientes

## Notas tecnicas
- psico_resultado.html: template original restaurado (diseno viejo), pendiente rediseno
- views.py: mezcla tabs/espacios es el principal riesgo — siempre verificar con py_compile antes de push
- WeasyPrint: permanentemente bloqueado en Railway, usar HTML imprimible
- Migraciones: siempre manuales, ultima es 0032
