from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0032_add_work_environment_survey"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userapp",
            name="phone",
            field=models.CharField(max_length=15, verbose_name="Teléfono"),
        ),
    ]
