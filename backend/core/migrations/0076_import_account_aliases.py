from django.db import migrations


def import_account_aliases(apps, schema_editor):
    AccountAlias = apps.get_model("core", "AccountAlias")


class Migration(migrations.Migration):

    dependencies = [("core", "0075_auto_20200629_1154")]

    operations = [migrations.RunPython(import_account_aliases)]
