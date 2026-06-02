from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0026_creditwallet_psico'),
    ]

    operations = [
        migrations.AddField(
            model_name='userapp',
            name='psico_plan_key',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Plan psicometría activo'),
        ),
    ]