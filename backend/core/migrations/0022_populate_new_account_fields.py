from django.db import migrations


def populate_account_fields(apps, schema_editor):
    Account = apps.get_model("core", "Account")
    for account in Account.objects.all():
        number_split = account.number.split("-")
        account.main_account_number = number_split[0]
        account.activity_numer = number_split[1]
        account.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0021_auto_20191118_1017")]

    operations = [migrations.RunPython(populate_account_fields)]
