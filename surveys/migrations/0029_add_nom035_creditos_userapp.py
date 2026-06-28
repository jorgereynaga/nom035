from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0028_add_demo_credits_to_userapp"),
    ]

    operations = [
        migrations.AddField(
            model_name="userapp",
            name="nom035_creditos",
            field=models.IntegerField(default=0, verbose_name="Créditos NOM-035 disponibles"),
        ),
    ]
