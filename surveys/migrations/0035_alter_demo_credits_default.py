from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0034_portafolio_evidencias"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userapp",
            name="nom035_demo",
            field=models.IntegerField(default=0, verbose_name="Créditos demo NOM-035"),
        ),
        migrations.AlterField(
            model_name="userapp",
            name="psico_demo",
            field=models.IntegerField(default=0, verbose_name="Créditos demo psicometría"),
        ),
    ]
