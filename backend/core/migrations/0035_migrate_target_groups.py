from django.db import migrations


def migrate_target_groups(apps, schema_editor):
    TargetGroup = apps.get_model("core", "TargetGroup")
    Case = apps.get_model("core", "Case")

    family_target_group, _ = TargetGroup.objects.get_or_create(
        name="familieafdelingen", required_fields_for_case="district"
    )
    disability_target_group, _ = TargetGroup.objects.get_or_create(
        name="handicapafdelingen"
    )

    family_dept_cases = Case.objects.filter(target_group="FAMILY_DEPT")
    disability_dept_cases = Case.objects.filter(target_group="DISABILITY_DEPT")

    family_dept_cases.update(target_group_model=family_target_group)
    disability_dept_cases.update(target_group_model=disability_target_group)


class Migration(migrations.Migration):

    dependencies = [("core", "0034_auto_20200422_1551")]

    operations = [migrations.RunPython(migrate_target_groups)]
