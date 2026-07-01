# ESTADO NormaIA — Actualizado 1 Jul 2026

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: prueba/TestIhes2026!

## Completado hoy
- Fix EndEvaluation: URL, workplace_id, slash inicial
- Fix WorkplaceResultView: permite ver resultados aunque paid=False
- Fix Ver resultados: apunta a evaluation-1, solo tras finalizar
- Mensaje informativo si aplicacion no finalizada
- Recarga automatica tras finalizar aplicacion
- Bootstrap JS en workplace_results.html para tooltip
- Fix survey3 solo para muestra_chart en PDFCreate
- Reporte HTML sin WeasyPrint (ReporteHTMLView + URL)
- Rediseno profesional template riesgo_psicosocial.html
- Candidatos demo: es_demo en modelo Candidate + admin
- CSS paginacion DataTable en workplace_detail y workplace_results
- Candidate registrado en admin

## Estado actual demo NOM-035
- Registro → datos demo auto (workplace + 6 empleados + 2 candidatos)
- Finalizar aplicacion: FUNCIONA + recarga pagina
- Ver resultados: FUNCIONA — muestra heatmap y tabla por empleado
- Descarga reporte HTML individual: FUNCIONA (nueva pestana, imprimible)
- Candidatos demo: FUNCIONA

## Pendientes
1. Portafolio de evidencias — generar ResultFiles al finalizar
2. Dashboard adaptivo NOM-035/Psicometria segun plan
3. Boton eliminar datos demo
4. Modulo Ambiente Laboral
5. admin.py: nom035_creditos visible
6. Fix phone max_length a 15
7. Paginacion empleados — mejorar diseno (bullets)
