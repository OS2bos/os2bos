from django.db import migrations


def migrate_sections(apps, schema_editor):
    TargetGroup = apps.get_model("core", "TargetGroup")
    Section = apps.get_model("core", "Section")

    family_target_group, _ = TargetGroup.objects.get_or_create(
        name="Familieafdelingen", required_fields_for_case=["district"]
    )
    disability_target_group, _ = TargetGroup.objects.get_or_create(
        name="Handicapafdelingen"
    )

    family_sections = Section.objects.filter(
        allowed_for_family_target_group=True
    )
    disability_sections = Section.objects.filter(
        allowed_for_disability_target_group=True
    )

    for section in family_sections:
        section.allowed_for_target_groups.add(family_target_group)

    for section in disability_sections:
        section.allowed_for_target_groups.add(disability_target_group)


class Migration(migrations.Migration):

    dependencies = [("core", "0038_section_allowed_for_target_groups")]

    operations = [migrations.RunPython(migrate_sections)]
