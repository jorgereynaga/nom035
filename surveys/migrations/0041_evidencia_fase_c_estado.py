from django.db import migrations, models


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
	]
