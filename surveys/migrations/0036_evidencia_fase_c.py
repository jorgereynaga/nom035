from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0035_alter_demo_credits_default"),
    ]

    operations = [
        migrations.CreateModel(
            name="EvidenciaFaseC",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("canalizacion", "Canalizacion Guia I (traumas severos)"), ("examen_medico", "Examen medico/evaluacion psicologica"), ("medida_control", "Medida de control/Programa de intervencion"), ("difusion", "Evidencia de difusion de la politica")], max_length=30, verbose_name="Tipo de evidencia")),
                ("archivo", models.FileField(upload_to="evidencias_fase_c/%Y/%m/", verbose_name="Archivo")),
                ("notas", models.TextField(blank=True, verbose_name="Notas")),
                ("fecha_carga", models.DateTimeField(auto_now_add=True)),
                ("workplace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="evidencias_fase_c", to="surveys.workplace", verbose_name="Centro de trabajo")),
            ],
        ),
    ]
