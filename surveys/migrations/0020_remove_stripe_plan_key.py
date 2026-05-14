from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0019_stripe_fields'),
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
            reverse_sql="""
                ALTER TABLE surveys_userapp
                DROP COLUMN IF EXISTS stripe_customer_id,
                DROP COLUMN IF EXISTS stripe_subscription_id,
                DROP COLUMN IF EXISTS stripe_plan_key,
                DROP COLUMN IF EXISTS psico_evaluaciones_disponibles;
            """
        ),
    ]