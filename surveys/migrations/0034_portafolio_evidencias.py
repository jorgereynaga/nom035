from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0033_phone_max_length_15"),
    ]

    operations = [
        migrations.CreateModel(
            name="PortafolioEvidencias",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("periodo_evaluacion", models.CharField(max_length=20, verbose_name="Periodo de evaluación")),
                ("responsable_nombre", models.CharField(blank=True, max_length=200, verbose_name="Nombre del responsable")),
                ("responsable_puesto", models.CharField(blank=True, max_length=150, verbose_name="Puesto del responsable")),
                ("responsable_cedula", models.CharField(blank=True, max_length=50, verbose_name="Cédula profesional")),
                ("representante_legal_nombre", models.CharField(blank=True, max_length=200, verbose_name="Representante legal")),
                ("representante_legal_cargo", models.CharField(blank=True, max_length=150, verbose_name="Cargo del representante legal")),
                ("canal_quejas", models.CharField(blank=True, max_length=200, verbose_name="Canal de quejas")),
                ("responsable_quejas", models.CharField(blank=True, max_length=200, verbose_name="Responsable de atención de quejas")),
                ("correo_quejas", models.EmailField(blank=True, max_length=254, verbose_name="Correo de quejas")),
                ("tiempo_respuesta_quejas", models.CharField(blank=True, max_length=100, verbose_name="Tiempo estimado de respuesta")),
                ("version_politica", models.CharField(default="1.0", max_length=10, verbose_name="Versión de la política")),
                ("fecha_emision", models.DateField(blank=True, null=True, verbose_name="Fecha de emisión")),
                ("periodicidad_revision", models.CharField(default="Anual", max_length=50, verbose_name="Periodicidad de revisión")),
                ("fecha_proxima_revision", models.DateField(blank=True, null=True, verbose_name="Próxima fecha de revisión")),
                ("fecha_ultima_evaluacion", models.DateField(blank=True, null=True, verbose_name="Fecha de última evaluación")),
                ("record_create", models.DateTimeField(auto_now_add=True)),
                ("workplace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portafolio_evidencias", to="surveys.workplace", verbose_name="Centro de trabajo")),
            ],
        ),
    ]
