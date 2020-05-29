from django.db import migrations


def delete_duplicate_section_infos(apps, schema_editor):
    # Ensures possibly duplicate section infos are deleted before
    # enforcing a unique constraint.
    SectionInfo = apps.get_model("core", "SectionInfo")
    all_section_infos = SectionInfo.objects.all()
    # Find distinct section infos on section and activity_details.
    distinct_section_info_pks = (
        SectionInfo.objects.all()
        .distinct("section", "activity_details")
        .values_list("pk", flat=True)
    )
    # Exclude distinct section infos from all to get duplicates.
    duplicate_section_infos = all_section_infos.exclude(
        pk__in=distinct_section_info_pks
    )
    # Delete the duplicates.
    duplicate_section_infos.delete()


class Migration(migrations.Migration):

    dependencies = [("core", "0055_target_group_set_required_fields")]

    operations = [migrations.RunPython(delete_duplicate_section_infos)]
