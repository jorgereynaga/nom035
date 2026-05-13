from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0019_stripe_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userapp',
            name='stripe_plan_key',
        ),
    ]