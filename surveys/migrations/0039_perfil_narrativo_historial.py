from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0038_unique_survey_per_evaluation"),
    ]

    operations = [
        migrations.AddField(
            model_name="testresult",
            name="perfil_narrativo_historial",
            field=models.JSONField(
                default=list,
                verbose_name="Historial de perfiles narrativos (IA)",
            ),
        ),
    ]
