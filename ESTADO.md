# Estado del Proyecto NOM-035 / NormaIA
Ultima actualizacion: 18-19 Junio 2026

## Datos del Proyecto
- Repo: github.com/jorgereynaga/nom035
- Local: C:\Users\JorgeAlbertoReynagaJ\Documents\nom 035\nom035\
- Deploy: Railway via git push origin main
- URL produccion: nom035-production.up.railway.app
- Dominio: 035.ihes.mx (pendiente conectar a nueva landing)
- Admin: /ihes_admin/ admin / IhesAdmin2026!
- Test account: prueba / TestIhes2026!
- Stack: Django 3.2 + PostgreSQL + Stripe + Railway

## Completado reciente
- Descuento creditos NOM-035 al completar cuestionario
- Descuento creditos psicometricos al asignar prueba
- Sistema demo: nom035_demo=1 y psico_demo=1 en Userapp (migracion 0028)
- Bloqueo descarga PDF sin plan pagado
- Bloqueo reporte psicometrico sin plan pagado
- Validacion workplace obligatorio antes de crear candidato
- Landing page NormaIA integrada
- Login y registro rediseñados estilo NormaIA
- Auto-login post registro con ApiLoginView en /api/login/
- reCAPTCHA v3 actualizado site key 6Le3XCEtAAAAAO-V0M9w9XaNgAtUHFj7TxrMJz0B

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

## Notas tecnicas
- Sublime mezcla tabs/espacios usar python -c con encoding utf-8 para ediciones
- HTML inline en views.py usar comillas simples para evitar SyntaxError
- Test card Stripe: 4242 4242 4242 4242
- reCAPTCHA: probar en ventana incognito sin recargar
