# Generated by Django 2.2.1 on 2019-10-23 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0010_payment_note")]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="saved_account_string",
            field=models.CharField(
                blank=True, max_length=128, verbose_name="gemt kontostreng"
            ),
        )
    ]
