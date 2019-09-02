from django.db import migrations
from django.db.models import F


def delete_end_before_start_activities(apps, schema_editor):
    Activity = apps.get_model("core", "Activity")
    Activity.objects.filter(end_date__lt=F("start_date")).delete()


class Migration(migrations.Migration):

    dependencies = [("core", "0001_initial")]

    operations = [migrations.RunPython(delete_end_before_start_activities)]
