from django.db import migrations


def add_default_team_for_case(apps, schema_editor):
    Team = apps.get_model("core", "Team")
    Case = apps.get_model("core", "Case")
    User = apps.get_model("core", "User")

    admin, created = User.objects.get_or_create(username="admin")
    team, created = Team.objects.get_or_create(
        name="S-DIG", defaults={"leader": admin}
    )
    Case.objects.filter(team__isnull=True).update(team=team)


def add_default_team_for_user(apps, schema_editor):
    Team = apps.get_model("core", "Team")
    User = apps.get_model("core", "User")

    admin, created = User.objects.get_or_create(username="admin")
    team, created = Team.objects.get_or_create(
        name="S-DIG", defaults={"leader": admin}
    )
    User.objects.filter(team__isnull=True).update(team=team)


class Migration(migrations.Migration):

    dependencies = [("core", "0010_auto_20190911_0929")]

    operations = [
        migrations.RunPython(add_default_team_for_case),
        migrations.RunPython(add_default_team_for_user),
    ]
