from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0025_creditwallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditwallet',
            name='psico_total',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='creditwallet',
            name='psico_used',
            field=models.IntegerField(default=0),
        ),
    ]