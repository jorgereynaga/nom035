from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0030_add_es_demo_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="risksurveya",
            name="es_demo",
            field=models.BooleanField(default=False, verbose_name="Datos de ejemplo"),
        ),
    ]
