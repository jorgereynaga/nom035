from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import migrations, models

import surveys.models


protected_storage = FileSystemStorage(location=settings.PROTECTED_MEDIA_ROOT)


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0036_evidencia_fase_c"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evidenciafasec",
            name="archivo",
            field=models.FileField(
                storage=protected_storage,
                upload_to="evidencias_fase_c/%Y/%m/",
                verbose_name="Archivo",
            ),
        ),
        migrations.AlterField(
            model_name="resultfiles",
            name="image",
            field=models.FileField(
                blank=True,
                null=True,
                storage=protected_storage,
                upload_to=surveys.models.result_directory_path,
                verbose_name="Archivo",
            ),
        ),
        migrations.AlterField(
            model_name="userapp",
            name="image",
            field=models.FileField(
                blank=True,
                null=True,
                storage=protected_storage,
                upload_to=surveys.models.user_directory_path,
                validators=[surveys.models.validate_file_extension],
                verbose_name="Logo de la empresa",
            ),
        ),
    ]
