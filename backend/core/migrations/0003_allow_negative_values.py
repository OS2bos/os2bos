# Generated by Django 2.2.1 on 2019-10-14 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0002_auto_20191015_1404")]

    operations = [
        migrations.AlterField(
            model_name="paymentschedule",
            name="payment_amount",
            field=models.DecimalField(
                decimal_places=2, max_digits=14, verbose_name="beløb"
            ),
        )
    ]
