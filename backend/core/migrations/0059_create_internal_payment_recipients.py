from django.db import migrations


def create_internal_payment_recipients(apps, schema_editor):
    InternalPaymentRecipient = apps.get_model(
        "core", "InternalPaymentRecipient"
    )

    InternalPaymentRecipient.objects.get_or_create(
        name="Ungdomspensionen (DUT)"
    )
    InternalPaymentRecipient.objects.get_or_create(name="Familiehuset")


class Migration(migrations.Migration):

    dependencies = [("core", "0058_internalpaymentrecipient")]

    operations = [migrations.RunPython(create_internal_payment_recipients)]
