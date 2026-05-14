from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0020_remove_stripe_plan_key'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE surveys_userapp
                ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(100) NULL,
                ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(100) NULL,
                ADD COLUMN IF NOT EXISTS stripe_plan_key VARCHAR(100) NOT NULL DEFAULT '',
                ADD COLUMN IF NOT EXISTS psico_evaluaciones_disponibles INTEGER NOT NULL DEFAULT 0;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]