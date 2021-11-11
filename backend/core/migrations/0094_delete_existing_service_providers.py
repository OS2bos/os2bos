from django.db import migrations, models
from django.db.models import Q

def delete_existing_service_providers(apps, schema_editor):
    ServiceProvider = apps.get_model("core", "ServiceProvider")
    ServiceProvider.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0093_auto_20210622_1511'),
    ]

    operations = [migrations.RunPython(delete_existing_service_providers)]
