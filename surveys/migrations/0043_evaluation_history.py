from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('surveys', '0042_evidencia_fase_c_estados_reetiquetados'),
	]

	operations = [
		migrations.CreateModel(
			name='EvaluationHistory',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('numero_evaluacion', models.IntegerField(verbose_name='Número de evaluación')),
				('guia', models.IntegerField(verbose_name='Guía aplicada (2 o 3)')),
				('fecha_finalizacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de finalización')),
				('workplace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluation_history', to='surveys.workplace')),
			],
			options={
				'ordering': ['numero_evaluacion'],
			},
		),
	]
