import os
import csv

from django.db import migrations
from django.db.models import Q


def import_account_aliases(apps, schema_editor):
    AccountAlias = apps.get_model("core", "AccountAlias")
    SectionInfo = apps.get_model("core", "SectionInfo")
    ActivityDetails = apps.get_model("core", "ActivityDetails")

    path = os.path.join(
        os.path.dirname(__file__), "..", "data", "account_aliases.csv",
    )
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]

        for row in rows[1:]:
            account_alias = row[0]
            mapping = row[2].rstrip("-")
            _, account_number, activity_id, _ = mapping.split("-")

            # Find the relevant SectionInfos.
            section_infos = SectionInfo.objects.filter(
                Q(main_activity_main_account_number=account_number)
                | Q(supplementary_activity_main_account_number=account_number)
            )
            if not section_infos.exists():
                print(
                    f"section info with main activity account number: "
                    f"{account_number} does not exist."
                )
                continue

            # Find the relevant ActivityDetails.
            activity_details = ActivityDetails.objects.filter(
                activity_id=activity_id
            )
            if not activity_details.exists():
                print(
                    f"activity details with activity_id: "
                    f"{activity_id} does not exist."
                )
                continue
            activity_details = activity_details.first()

            for section_info in section_infos:
                AccountAlias.objects.update_or_create(
                    section_info=section_info,
                    activity_details=activity_details,
                    defaults={"alias": account_alias},
                )


class Migration(migrations.Migration):

    dependencies = [("core", "0075_auto_20200629_1154")]

    operations = [migrations.RunPython(import_account_aliases)]
