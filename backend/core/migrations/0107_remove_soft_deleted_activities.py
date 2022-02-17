from django.db import migrations


def remove_soft_deleted_activities(apps, schema_editor):
    Activity = apps.get_model("core", "Activity")
    Activity.objects.filter(status="DELETED").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0106_auto_20220217_0820"),
    ]

    operations = [
        migrations.RunPython(remove_soft_deleted_activities, elidable=True)
    ]
