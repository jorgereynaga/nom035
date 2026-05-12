from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0018_purchasedproducts_workplace'),
    ]

    operations = [
        migrations.AddField(
            model_name='userapp',
            name='stripe_customer_id',
            field=models.CharField(
                blank=True, max_length=100, null=True,
                verbose_name='Stripe Customer ID'
            ),
        ),
        migrations.AddField(
            model_name='userapp',
            name='stripe_subscription_id',
            field=models.CharField(
                blank=True, max_length=100, null=True,
                verbose_name='Stripe Subscription ID'
            ),
        ),
        migrations.AddField(
            model_name='userapp',
            name='stripe_plan_key',
            field=models.CharField(
                blank=True, default='', max_length=100,
                verbose_name='Plan activo'
            ),
        ),
        migrations.AddField(
            model_name='userapp',
            name='psico_evaluaciones_disponibles',
            field=models.IntegerField(
                default=0,
                verbose_name='Evaluaciones psicométricas disponibles'
            ),
        ),
    ]
