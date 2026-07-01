from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0031_add_es_demo_risksurveya"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkEnvironmentSurvey",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("department", models.CharField(blank=True, max_length=150, verbose_name="Departamento/Area")),
                ("periodo", models.CharField(blank=True, max_length=50, verbose_name="Periodo")),
                ("cl_p1", models.IntegerField(blank=True, null=True)),
                ("cl_p2", models.IntegerField(blank=True, null=True)),
                ("cl_p3", models.IntegerField(blank=True, null=True)),
                ("cl_p4", models.IntegerField(blank=True, null=True)),
                ("cl_p5", models.IntegerField(blank=True, null=True)),
                ("cl_p6", models.IntegerField(blank=True, null=True)),
                ("cl_p7", models.IntegerField(blank=True, null=True)),
                ("cl_p8", models.IntegerField(blank=True, null=True)),
                ("cl_p9", models.IntegerField(blank=True, null=True)),
                ("cl_p10", models.IntegerField(blank=True, null=True)),
                ("cl_p11", models.IntegerField(blank=True, null=True)),
                ("cl_p12", models.IntegerField(blank=True, null=True)),
                ("cl_p13", models.IntegerField(blank=True, null=True)),
                ("cl_p14", models.IntegerField(blank=True, null=True)),
                ("cl_p15", models.IntegerField(blank=True, null=True)),
                ("cl_p16", models.IntegerField(blank=True, null=True)),
                ("cl_p17", models.IntegerField(blank=True, null=True)),
                ("cl_p18", models.IntegerField(blank=True, null=True)),
                ("cl_p19", models.IntegerField(blank=True, null=True)),
                ("cl_p20", models.IntegerField(blank=True, null=True)),
                ("cl_p21", models.IntegerField(blank=True, null=True)),
                ("cl_p22", models.IntegerField(blank=True, null=True)),
                ("cl_p23", models.IntegerField(blank=True, null=True)),
                ("cl_p24", models.IntegerField(blank=True, null=True)),
                ("cl_p25", models.IntegerField(blank=True, null=True)),
                ("cl_p26", models.IntegerField(blank=True, null=True)),
                ("cl_p27", models.IntegerField(blank=True, null=True)),
                ("cl_p28", models.IntegerField(blank=True, null=True)),
                ("cl_p29", models.IntegerField(blank=True, null=True)),
                ("cl_p30", models.IntegerField(blank=True, null=True)),
                ("cl_p31", models.IntegerField(blank=True, null=True)),
                ("cl_p32", models.IntegerField(blank=True, null=True)),
                ("cl_p33", models.IntegerField(blank=True, null=True)),
                ("cl_p34", models.IntegerField(blank=True, null=True)),
                ("cl_p35", models.IntegerField(blank=True, null=True)),
                ("cl_p36", models.IntegerField(blank=True, null=True)),
                ("cl_p37", models.IntegerField(blank=True, null=True)),
                ("cl_p38", models.IntegerField(blank=True, null=True)),
                ("cl_p39", models.IntegerField(blank=True, null=True)),
                ("cl_p40", models.IntegerField(blank=True, null=True)),
                ("es_demo", models.BooleanField(default=False)),
                ("record_create", models.DateTimeField(auto_now_add=True)),
                ("workplace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="climate_surveys", to="surveys.workplace", verbose_name="Centro de trabajo")),
            ],
            options={"verbose_name": "Encuesta de Clima Laboral", "verbose_name_plural": "Encuestas de Clima Laboral"},
        ),
    ]
