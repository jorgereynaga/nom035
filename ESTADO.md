# ESTADO NormaIA — Actualizado 29 Jun 2026 (noche final)

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: prueba/TestIhes2026!
- Repo: github.com/jorgereynaga/nom035
- Local: C:\Users\JorgeAlbertoReynagaJ\Documents\nom 035\nom035\
- Editor: Sublime Text (tabs — editar Python con python -c por indice de linea)

## Ultimo deploy exitoso
- Migration 0031: es_demo en RiskSurveyA (resolvio error 500 en admin)
- demo: workplace paid=True para mostrar resultados
- auth-register: CSRF fix, errores arriba, llave JS corregida
- Registro funciona — datos demo se crean automaticamente

## Estado actual del demo (usuario nuevo)
- Workplace "Empresa Demo S.A. de C.V." se crea correctamente
- 6 empleados creados con paginacion (5 por pagina, 2 paginas)
- Todos los empleados muestran estado "Contestada" correctamente
- Filtro por departamento funciona (Administracion, Direccion, Logistica, Produccion, RH)
- Boton "Finalizar aplicacion" habilitado pero al hacer clic Aceptar no funciona
- Portafolio de evidencias vacio — requiere finalizar aplicacion primero
- Candidatos psicometricos no aparecen en seccion Candidatos

## Pendientes proxima sesion (en orden)
1. Fix boton "Aceptar" en modal Finalizar encuestas
   - grep -n "finalizar\|finalize\|Finalizar" surveys/templates/workplace_detail.html
2. Verificar que al finalizar se generan ResultFiles y aparecen en Portafolio
3. Fix candidatos demo — no aparecen en seccion Candidatos
4. Paginacion de empleados — mejorar diseno (anotado para despues)
5. Dashboard adaptivo NOM-035/Psicometria segun plan (Replit)
6. Boton "Eliminar datos de ejemplo"
7. admin.py: nom035_creditos visible
8. Fix phone max_length a 15

## Notas tecnicas
- workplace_detail.html tiene el modal de finalizar — revisar JS del boton Aceptar
- Portafolio usa ResultFiles model — se generan al finalizar aplicacion
- Candidatos: modelo Candidate existe con es_demo=True pero vista puede filtrar diferente
- Paginacion fea en lista de empleados — registros por pagina selector visible, mejorar CSS

## Completado en sesiones anteriores
- stripe_plans.py: 9 planes activos
- Migration 0029: nom035_creditos en Userapp
- Migration 0030: es_demo en Workplace, Employee, Candidate
- Migration 0031: es_demo en RiskSurveyA
- cargar_datos_demo.py: crea workplace + 6 empleados + RiskSurveyA/B + 2 candidatos
- views.py ~1658: call_command cargar_datos_demo post-registro
- workplaceform.html, employeeform.html: redisenos completados
- auth-register.html: CSRF fix, errores arriba

## MODULO AMBIENTE LABORAL — JSON recibido 29 Jun 2026
- 40 reactivos, escala Likert 1-5
- 8 dimensiones: liderazgo, comunicacion, trabajo_equipo, reconocimiento,
  condiciones_trabajo, carga_equilibrio, desarrollo_crecimiento, pertenencia
- Todos los reactivos directos (inverso=false) — sin recodificacion
- Calculo: promedio por dimension + promedio general
- Criterios: Critico(1-2.49), En riesgo(2.5-3.49), Adecuado(3.5-4.24), Favorable(4.25-5)
- Minimo 32 respuestas validas para reporte general, 4 por dimension
- Minimo 5 respuestas para reporte grupal (anonimato)
- Salida: por area, departamento, empresa — NO por colaborador individual

## Modelo Django sugerido para Ambiente Laboral
- WorkEnvironmentSurvey: FK Workplace, campo departamento (texto libre), 40 campos IntegerField
- WorkEnvironmentResult: FK Workplace, dimension, promedio, nivel (critico/riesgo/adecuado/favorable)
- URL publica anonima: /clima/{access_code}/ — sin login requerido
- Solo disponible en planes Suite o anuales

## Pendiente para implementar
1. Crear modelo WorkEnvironmentSurvey en models.py + migracion
2. Vista publica anonima para responder
3. Vista de resultados agregados por empresa/CT/area
4. Comando cargar_datos_demo — agregar respuestas demo de clima laboral
5. Dashboard — agregar seccion Clima Laboral
6. PDF de resultados por dimension
