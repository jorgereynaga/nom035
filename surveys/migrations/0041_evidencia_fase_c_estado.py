from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import migrations, models

protected_storage = FileSystemStorage(location=settings.PROTECTED_MEDIA_ROOT)


def borrar_evidencias_fase_c(apps, schema_editor):
	EvidenciaFaseC = apps.get_model('surveys', 'EvidenciaFaseC')
	EvidenciaFaseC.objects.all().delete()


class Migration(migrations.Migration):

	dependencies = [
		('surveys', '0040_plan_purchase_event'),
	]

	operations = [
		migrations.RunPython(borrar_evidencias_fase_c, migrations.RunPython.noop),
		migrations.AddField(
			model_name='evidenciafasec',
			name='estado',
			field=models.CharField(choices=[('tienen', 'Tienen'), ('trabajando', 'Lo estan trabajando'), ('falta', 'Les falta')], default='falta', max_length=20, verbose_name='Estado'),
		),
		migrations.AddField(
			model_name='evidenciafasec',
			name='fecha_actualizacion',
			field=models.DateTimeField(auto_now=True),
		),
		migrations.AlterField(
			model_name='evidenciafasec',
			name='tipo',
			field=models.CharField(choices=[('canalizacion', 'Canalizacion Guia I (traumas severos)'), ('examen_medico', 'Examen medico/evaluacion psicologica'), ('medida_control', 'Medida de control/Programa de intervencion'), ('difusion', 'Evidencia de difusion de la politica'), ('registros', 'Registros de resultados y medidas de control'), ('mecanismos_queja', 'Mecanismos de queja/denuncia de violencia laboral')], max_length=30, verbose_name='Tipo de evidencia'),
		),
		migrations.AlterUniqueTogether(
			name='evidenciafasec',
			unique_together={('workplace', 'tipo')},
		),
		# El campo 'archivo' se comento en el modelo (Fase 2-B), pero la columna
		# de la BD seguia siendo NOT NULL desde la migracion 0037 -- sin esto,
		# cualquier fila nueva fallaria al insertarse porque el ORM ya no la
		# puebla. No se elimina la columna (se conserva por si se revierte el
		# cambio), solo se relaja la restriccion.
		migrations.AlterField(
			model_name='evidenciafasec',
			name='archivo',
			field=models.FileField(blank=True, null=True, storage=protected_storage, upload_to='evidencias_fase_c/%Y/%m/', verbose_name='Archivo'),
		),
	]
