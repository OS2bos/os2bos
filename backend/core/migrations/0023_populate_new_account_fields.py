from django.db import migrations


def populate_account_fields(apps, schema_editor):
    Account = apps.get_model("core", "Account")
    for account in Account.objects.all():
        number_split = account.number.split("-")
        account.main_account_number = number_split[0]
        if len(number_split) > 1:
            account.activity_number = number_split[1]
        else:
            account.activity_number = ""
        account.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0022_auto_20191118_1314")]

    operations = [migrations.RunPython(populate_account_fields)]
