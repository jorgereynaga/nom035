from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0029_add_nom035_creditos_userapp"),
    ]

    operations = [
        migrations.AddField(
            model_name="workplace",
            name="es_demo",
            field=models.BooleanField(default=False, verbose_name="Datos de ejemplo"),
        ),
        migrations.AddField(
            model_name="employee",
            name="es_demo",
            field=models.BooleanField(default=False, verbose_name="Datos de ejemplo"),
        ),
        migrations.AddField(
            model_name="candidate",
            name="es_demo",
            field=models.BooleanField(default=False, verbose_name="Datos de ejemplo"),
        ),
    ]
