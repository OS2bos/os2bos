# Generated by Django 2.2.13 on 2020-06-25 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0073_populate_payment_date_exclusions'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Account',
        ),
    ]
