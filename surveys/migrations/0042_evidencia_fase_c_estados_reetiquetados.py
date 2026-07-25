from django.db import migrations, models


def remapear_estados(apps, schema_editor):
	EvidenciaFaseC = apps.get_model('surveys', 'EvidenciaFaseC')
	EvidenciaFaseC.objects.filter(estado='tienen').update(estado='completado')
	EvidenciaFaseC.objects.filter(estado__in=['trabajando', 'falta']).update(estado='en_proceso')


class Migration(migrations.Migration):

	dependencies = [
		('surveys', '0041_evidencia_fase_c_estado'),
	]

	operations = [
		migrations.RunPython(remapear_estados, migrations.RunPython.noop),
		migrations.AlterField(
			model_name='evidenciafasec',
			name='estado',
			field=models.CharField(choices=[('en_proceso', 'En proceso'), ('completado', 'Completado'), ('no_aplica', 'No aplica')], default='en_proceso', max_length=20, verbose_name='Estado'),
		),
	]
