# ESTADO NormaIA — Actualizado 30 Jun 2026

## Stack
- Django 3.2 + PostgreSQL + Stripe + Railway
- Deploy: git push origin main
- Admin: /ihes_admin/ admin/IhesAdmin2026!
- Test: prueba/TestIhes2026!

## Completado hoy
- Fix EndEvaluation: query_params + slash inicial + workplace_id correcto
- Fix WorkplaceResultView: permite ver resultados aunque paid=False
- Fix Ver resultados: apunta a evaluacion anterior (evaluation-1)
- Fix Bootstrap JS en workplace_results.html para tooltip
- Fix survey3 solo para muestra_chart en PDFCreate
- Migration 0031: es_demo en RiskSurveyA

## Estado actual demo NOM-035
- Registro funciona, datos demo se crean automaticamente
- 6 empleados con estado "Contestada" correctamente
- Finalizar aplicacion: FUNCIONA
- Ver resultados: FUNCIONA — muestra heatmap y tabla por empleado
- Descarga PDF individual: FALLA 500 — WeasyPrint no puede generar PDFs en Railway
  - nixpacks.toml tiene gobject-introspection, pango, cairo, glib
  - WeasyPrint 62.3 en requirements.txt
  - Error: "could not import some external libraries"
  - Solucion pendiente: reemplazar con HTML imprimible o fix nixpacks

## Pendientes
1. Fix descarga PDF — WeasyPrint en Railway (nixpacks) o alternativa HTML
2. Portafolio de evidencias — generar ResultFiles al finalizar
3. Candidatos demo no aparecen en seccion Candidatos
4. Paginacion empleados — mejorar diseno
5. Dashboard adaptivo NOM-035/Psicometria segun plan
6. Boton eliminar datos demo
7. Modulo Ambiente Laboral (JSON recibido, modelo planificado)
8. admin.py: nom035_creditos visible
9. Fix phone max_length a 15
