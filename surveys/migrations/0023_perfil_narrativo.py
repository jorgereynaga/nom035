from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0022_psicometria'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='perfil_narrativo',
            field=models.TextField(blank=True, verbose_name='Perfil narrativo (IA)'),
        ),
    ]