# Estado del Proyecto NOM-035 / NormaIA
Ultima actualizacion: 19 Junio 2026

## Datos del Proyecto
- Repo: github.com/jorgereynaga/nom035
- Local: C:\Users\JorgeAlbertoReynagaJ\Documents\nom 035\nom035\
- Deploy: Railway via git push origin main
- URL produccion: nom035-production.up.railway.app
- Dominio: 035.ihes.mx (pendiente conectar a nueva landing)
- Admin: /ihes_admin/ admin / IhesAdmin2026!
- Test account: prueba / TestIhes2026!
- Stack: Django 3.2 + PostgreSQL + Stripe + Railway
- Branch respaldo UI original: backup-ui-original

## Completado reciente
- Descuento creditos NOM-035 al completar cuestionario
- Descuento creditos psicometricos al asignar prueba
- Sistema demo: nom035_demo=1 y psico_demo=1 en Userapp (migracion 0028)
- Bloqueo descarga PDF sin plan pagado (download_file, download_file2)
- Bloqueo reporte psicometrico sin plan pagado (ReporteUnificadoView)
- Validacion workplace obligatorio antes de crear candidato (CandidateCreateView)
- Landing page NormaIA integrada (surveys/templates/landing.html)
- Login y registro rediseñados estilo NormaIA
- Auto-login post registro con ApiLoginView en /api/login/
- reCAPTCHA v3 actualizado site key 6Le3XCEtAAAAAO-V0M9w9XaNgAtUHFj7TxrMJz0B
- REDISEÑO COMPLETO UI dashboard (Replit Agent):
  - index.html, workplace.html, workplace_detail.html, workplace_results.html
  - psico_candidatos.html, psico_candidato_detalle.html
  - employeeform.html, edit_profile.html, evidence.html
  - auth-login.html, auth-register.html
  - Sistema de variables CSS (--primary, --border, --radius, etc.)
  - Fuentes: Inter + Plus Jakarta Sans
  - Estilo: cards con border 1px solid #e2e8f0, border-radius 12px

## Pendiente inmediato
- stripe_planes.html no se actualizo con el nuevo diseño (es standalone, tiene CSS propio)

## Pendientes criticos
- DEBUG=False y variables de entorno en Railway (Fase 0 seguridad)
- Flujo crear Workplace para nuevo usuario post registro
- Pagina exito post compra
- Paginas 404 y 500
- Creditos demo ligados a cuenta no reseteable (Punto 3 socios)
- Conectar dominio 035.ihes.mx

## Pendientes futuros
- Rebranding IHES a NormaIA (pendiente aprobacion socios)
- Email bienvenida y recordatorios
- Terminos y condiciones
- Estrategia marketing y SEO

## Archivos clave
- surveys/views.py: Dashboard, registro, webhook, download_file, LandingView, ApiLoginView
- surveys/psico_views.py: CandidateCreateView, AssignTestView, ReporteUnificadoView
- surveys/models.py: Userapp (nom035_demo, psico_demo), CreditWallet
- nom035/urls.py: LandingView en '', WebIndex comentado, ApiLoginView en /api/login/
- surveys/migrations/0028_*.py: Campos demo en Userapp

## Notas tecnicas
- Sublime mezcla tabs/espacios usar python -c con encoding utf-8 para ediciones
- HTML inline en views.py usar comillas simples para evitar SyntaxError
- Test card Stripe: 4242 4242 4242 4242
- reCAPTCHA: probar en ventana incognito sin recargar
- Para revertir UI: git checkout backup-ui-original -- surveys/templates/
