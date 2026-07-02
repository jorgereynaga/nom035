# ESTADO NormaIA — Actualizado 2 Jul 2026

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: jorge.reynaga.j@gmail.com (usuario activo con datos demo)

## Completado hoy
- Fix EndEvaluation: URL, workplace_id, slash inicial
- Fix WorkplaceResultView: permite ver resultados aunque paid=False
- Fix Ver resultados: apunta a evaluation-1, solo tras finalizar
- Mensaje informativo si aplicacion no finalizada
- Recarga automatica tras finalizar aplicacion
- Bootstrap JS en workplace_results.html y workplace_detail.html
- Tooltip condicional en workplace_detail.html
- Reporte HTML sin WeasyPrint (ReporteHTMLView)
- Rediseno profesional template riesgo_psicosocial.html
- Candidatos demo: es_demo en modelo Candidate + admin
- CSS paginacion DataTable — sin bullets, en fila, selector funciona
- DataTable usa evaluation-1 cuando aplicacion finalizada
- eval_to_check en dashboard para mostrar survey_completed correcto
- Modulo Clima Laboral completo:
  - Modelo WorkEnvironmentSurvey (migration 0032)
  - Vista publica anonima /clima/{access_code}/
  - Vista resultados /clima/resultados/{workplace_id}/
  - Templates clima_laboral.html, clima_gracias.html, clima_resultados.html
  - 8 respuestas demo en cargar_datos_demo
  - Enlace en sidebar de index.html
- Dashboard rediseñado con Replit (3 secciones: NOM-035, Psicometria, Clima)
- raw_access_code y climate_surveys_count en contexto del dashboard

## Estado actual demo
- NOM-035: 100% cuestionarios, Completado ✅
- Clima Laboral: 8 respuestas, resultados por dimension ✅
- Psicometria: candidatos demo NO aparecen en dashboard ❌

## Pendientes inmediatos
1. Fix psicometria dashboard — candidatos demo no aparecen
2. Preview dimensiones NOM-035 en espacio en blanco del dashboard
3. Preview dimensiones Clima Laboral en dashboard
4. Boton "Ver resultados completos" que mande a /workplace_result/{id}/{eval}/
5. Candidatos demo: verificar por que no aparecen en seccion psicometria

## Pendientes generales
6. Portafolio de evidencias automatico (pendiente revision norma)
7. Boton eliminar datos demo
8. admin.py: nom035_creditos visible
9. Fix phone max_length a 15
10. Pruebas finales: navegacion entre evaluaciones multiples
11. Restriccion clima laboral solo para usuarios con plan/pago
