from django.db import migrations


def set_targetgroup_required_fields(apps, schema_editor):
    TargetGroup = apps.get_model("core", "TargetGroup")
    all_target_groups = TargetGroup.objects.all()

    for target_group in all_target_groups:
        required_fields = target_group.required_fields_for_case
        if not required_fields:
            continue
        required_fields_list = required_fields.split(",")
        if "scaling_step" not in required_fields_list:
            required_fields_list.append("scaling_step")
        if "effort_step" not in required_fields_list:
            required_fields_list.append("effort_step")
        target_group.required_fields_for_case = ",".join(required_fields_list)
        target_group.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0054_auto_20200527_1016")]

    operations = [migrations.RunPython(set_targetgroup_required_fields)]
