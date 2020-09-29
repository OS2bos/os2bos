from core.utils import generate_payment_date_exclusion_dates

from django.db import migrations


def populate_payment_date_exclusions(apps, schema_editor):
    PaymentDateExclusion = apps.get_model("core", "PaymentDateExclusion")

    dates = generate_payment_date_exclusion_dates(years=[2020, 2021, 2022])

    for date in dates:
        PaymentDateExclusion.objects.get_or_create(date=date)


class Migration(migrations.Migration):

    dependencies = [("core", "0072_paymentdateexclusion")]

    operations = [migrations.RunPython(populate_payment_date_exclusions)]
