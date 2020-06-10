from django.db import migrations


def migrate_to_new_auditmodelmixin(apps, schema_editor):
    Activity = apps.get_model("core", "Activity")
    Appropriation = apps.get_model("core", "Appropriation")
    Case = apps.get_model("core", "Case")
    RelatedPerson = apps.get_model("core", "RelatedPerson")

    for activity in Activity.objects.all():
        Activity.objects.filter(pk=activity.pk).update(
            created_new=activity.created, modified_new=activity.modified,
        )

    for appropriation in Appropriation.objects.all():
        Appropriation.objects.filter(pk=appropriation.pk).update(
            created_new=appropriation.created,
            modified_new=appropriation.modified,
        )

    for case in Case.objects.all():
        Case.objects.filter(pk=case.pk).update(
            created_new=case.created, modified_new=case.modified,
        )

    for related_person in RelatedPerson.objects.all():
        RelatedPerson.objects.filter(pk=related_person.pk).update(
            created_new=related_person.created,
            modified_new=related_person.modified,
        )


class Migration(migrations.Migration):

    dependencies = [("core", "0063_auto_20200602_1059")]

    operations = [migrations.RunPython(migrate_to_new_auditmodelmixin)]
