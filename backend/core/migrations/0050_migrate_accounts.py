from django.db import migrations


def migrate_accounts(apps, schema_editor):
    Account = apps.get_model("core", "Account")
    SectionInfo = apps.get_model("core", "SectionInfo")

    main_activity_accounts = Account.objects.filter(
        supplementary_activity__isnull=True
    )

    for account in main_activity_accounts:
        section_info = SectionInfo.objects.filter(
            activity_details=account.main_activity, section=account.section
        ).first()
        if not section_info:
            continue

        section_info.main_activity_main_account_number = (
            account.main_account_number
        )
        section_info.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0049_auto_20200514_1046")]

    operations = [migrations.RunPython(migrate_accounts)]
