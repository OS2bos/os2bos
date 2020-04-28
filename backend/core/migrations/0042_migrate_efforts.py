from django.db import migrations


def migrate_efforts(apps, schema_editor):
    Case = apps.get_model("core", "Case")
    Effort = apps.get_model("core", "Effort")
    TargetGroup = apps.get_model("core", "TargetGroup")

    integration_effort, _ = Effort.objects.get_or_create(
        name="Integrationsindsatsen"
    )
    youth_effort, _ = Effort.objects.get_or_create(
        name="Tværgående ungeindsats"
    )

    all_target_groups = TargetGroup.objects.all()

    integration_effort.allowed_for_target_groups.add(*all_target_groups)
    youth_effort.allowed_for_target_groups.add(*all_target_groups)

    refugee_cases = Case.objects.filter(refugee_integration=True)
    youth_cases = Case.objects.filter(cross_department_measure=True)

    for case in refugee_cases:
        case.efforts.add(integration_effort)
    for case in youth_cases:
        case.efforts.add(youth_effort)


class Migration(migrations.Migration):

    dependencies = [("core", "0041_auto_20200428_1526")]

    operations = [migrations.RunPython(migrate_efforts)]
