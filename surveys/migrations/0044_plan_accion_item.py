from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('surveys', '0043_evaluation_history'),
	]

	operations = [
		migrations.CreateModel(
			name='PlanAccionItem',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('area_trabajadores', models.CharField(max_length=300, verbose_name='Área o trabajadores sujetos')),
				('tipo_accion', models.CharField(max_length=300, verbose_name='Tipo de acción')),
				('fecha_programada', models.DateField(verbose_name='Fecha programada')),
				('responsable', models.CharField(max_length=200, verbose_name='Responsable')),
				('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_proceso', 'En proceso'), ('completado', 'Completado')], default='pendiente', max_length=20, verbose_name='Estado')),
				('evaluacion_posterior', models.CharField(max_length=300, verbose_name='Evaluación posterior')),
				('record_create', models.DateTimeField(auto_now_add=True)),
				('record_update', models.DateTimeField(auto_now=True)),
				('workplace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plan_accion_items', to='surveys.workplace', verbose_name='Centro de trabajo')),
			],
			options={
				'ordering': ['fecha_programada'],
			},
		),
	]
