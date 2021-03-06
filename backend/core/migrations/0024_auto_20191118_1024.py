# Generated by Django 2.2.1 on 2019-11-18 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0023_populate_new_account_fields")]

    operations = [
        migrations.RemoveField(model_name="account", name="number"),
        migrations.AlterField(
            model_name="account",
            name="activity_number",
            field=models.CharField(
                blank=True, max_length=128, verbose_name="aktivitetsnummer"
            ),
        ),
        migrations.AlterField(
            model_name="account",
            name="main_account_number",
            field=models.CharField(
                max_length=128, verbose_name="hovedkontonummer"
            ),
        ),
    ]
