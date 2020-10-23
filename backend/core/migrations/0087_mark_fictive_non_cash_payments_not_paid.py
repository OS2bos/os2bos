from django.db import migrations, models
from django.db.models import Q

def mark_fictive_non_cash_payments_not_paid(apps, schema_editor):
    Payment = apps.get_model("core", "Payment")

    payments = Payment.objects.filter(
        Q(payment_method="INVOICE")|Q(payment_method="INTERNAL"),
        payment_schedule__fictive=True,
        paid=True,
    )

    for payment in payments:
        print(f"Marking payment with id: {payment.id} not paid")
        payment.paid = False
        payment.paid_date = None
        payment.paid_amount = None
        payment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0086_auto_20200918_1106'),
    ]

    operations = [migrations.RunPython(mark_fictive_non_cash_payments_not_paid)]
