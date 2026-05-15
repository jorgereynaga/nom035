from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0021_fix_stripe_columns'),
    ]

    operations = [
        migrations.CreateModel(
            name='PsychoInstrument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('tipo', models.CharField(choices=[('disc', 'DISC'), ('zavic', 'Valores e Intereses (Zavic)'), ('raven', 'Razonamiento (Raven)'), ('moss', 'Supervisión (Moss)')], max_length=20, verbose_name='Tipo')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('tiempo_limite', models.IntegerField(default=30, verbose_name='Tiempo límite (minutos)')),
                ('instrucciones', models.TextField(blank=True, verbose_name='Instrucciones para el evaluado')),
                ('record_create', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Instrumento Psicométrico', 'verbose_name_plural': 'Instrumentos Psicométricos'},
        ),
        migrations.CreateModel(
            name='PsychoItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField(verbose_name='Número de reactivo')),
                ('tipo', models.CharField(choices=[('disc_group', 'Grupo DISC (más/menos)'), ('distribute', 'Distribución de puntos'), ('multiple', 'Opción múltiple')], max_length=20, verbose_name='Tipo de reactivo')),
                ('texto', models.TextField(blank=True, verbose_name='Texto del reactivo')),
                ('dificultad', models.CharField(blank=True, choices=[('facil', 'Fácil'), ('medio', 'Medio'), ('dificil', 'Difícil')], max_length=10, verbose_name='Dificultad')),
                ('opciones', models.JSONField(default=list, verbose_name='Opciones (JSON)')),
                ('respuesta_correcta', models.CharField(blank=True, max_length=10, verbose_name='Respuesta correcta')),
                ('record_create', models.DateTimeField(auto_now_add=True)),
                ('instrumento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='surveys.psychoinstrument')),
            ],
            options={'verbose_name': 'Reactivo', 'verbose_name_plural': 'Reactivos', 'ordering': ['instrumento', 'numero']},
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, verbose_name='Nombre completo')),
                ('email', models.EmailField(blank=True, verbose_name='Correo electrónico')),
                ('puesto', models.CharField(blank=True, max_length=100, verbose_name='Puesto al que aplica')),
                ('tipo', models.CharField(choices=[('externo', 'Candidato externo'), ('empleado', 'Empleado actual')], default='externo', max_length=20, verbose_name='Tipo')),
                ('notas', models.TextField(blank=True, verbose_name='Notas')),
                ('record_create', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='psico_sessions', to='surveys.employee', verbose_name='Empleado relacionado')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidates', to='auth.user', verbose_name='Empresa RH')),
            ],
            options={'verbose_name': 'Candidato', 'verbose_name_plural': 'Candidatos', 'ordering': ['-record_create']},
        ),
        migrations.CreateModel(
            name='TestSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=64, unique=True, verbose_name='Token único')),
                ('status', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_proceso', 'En proceso'), ('completada', 'Completada'), ('expirada', 'Expirada')], default='pendiente', max_length=20, verbose_name='Estado')),
                ('fecha_envio', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')),
                ('fecha_inicio', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de inicio')),
                ('fecha_completado', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de completado')),
                ('expira_en', models.DateTimeField(blank=True, null=True, verbose_name='Expira en')),
                ('record_create', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='surveys.candidate')),
                ('instrumento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sessions', to='surveys.psychoinstrument')),
            ],
            options={'verbose_name': 'Sesión de Evaluación', 'verbose_name_plural': 'Sesiones de Evaluación', 'ordering': ['-record_create']},
        ),
        migrations.CreateModel(
            name='TestResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respuesta', models.JSONField(default=dict, verbose_name='Respuesta (JSON)')),
                ('record_create', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='responses', to='surveys.psychoitem')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='surveys.testsession')),
            ],
            options={'verbose_name': 'Respuesta', 'verbose_name_plural': 'Respuestas', 'ordering': ['session', 'item']},
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scores', models.JSONField(default=dict, verbose_name='Puntuaciones (JSON)')),
                ('interpretacion', models.TextField(blank=True, verbose_name='Interpretación')),
                ('perfil_narrativo', models.TextField(blank=True, verbose_name='Perfil narrativo (IA)')),
                ('record_create', models.DateTimeField(auto_now_add=True)),
                ('session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='surveys.testsession')),
            ],
            options={'verbose_name': 'Resultado', 'verbose_name_plural': 'Resultados'},
        ),
    ]