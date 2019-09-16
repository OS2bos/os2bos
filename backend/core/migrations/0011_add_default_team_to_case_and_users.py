from django.db import migrations


def add_default_team_for_case(apps, schema_editor):
    Team = apps.get_model("core", "Team")
    Case = apps.get_model("core", "Case")

    team = Team.objects.get(name="S-DIG")
    Case.objects.filter(team__isnull=True).update(team=team)


def add_default_team_for_user(apps, schema_editor):
    Team = apps.get_model("core", "Team")
    User = apps.get_model("core", "User")

    team = Team.objects.get(name="S-DIG")
    User.objects.filter(team__isnull=True).update(team=team)


class Migration(migrations.Migration):

    dependencies = [("core", "0010_auto_20190911_0929")]

    operations = [
        migrations.RunPython(add_default_team_for_case),
        migrations.RunPython(add_default_team_for_user),
    ]
