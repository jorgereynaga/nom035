from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0037_protected_file_storage"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="risksurveya",
            unique_together={("employee", "evaluation")},
        ),
        migrations.AlterUniqueTogether(
            name="traumasurvey",
            unique_together={("employee", "evaluation")},
        ),
        migrations.AlterUniqueTogether(
            name="risksurveyb",
            unique_together={("employee", "evaluation")},
        ),
    ]
