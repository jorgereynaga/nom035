from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0039_perfil_narrativo_historial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanPurchaseEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_key', models.CharField(max_length=100, verbose_name='Plan')),
                ('modulo', models.CharField(max_length=20, verbose_name='Modulo')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio (snapshot MXN)')),
                ('periodo', models.CharField(max_length=20, verbose_name='Periodo')),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='Stripe Customer ID')),
                ('record_create', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plan_purchase_events', to='auth.user')),
            ],
        ),
    ]
