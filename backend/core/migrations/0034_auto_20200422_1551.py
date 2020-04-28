# Generated by Django 2.2.9 on 2020-04-22 13:51

from django.db import migrations, models
from django.contrib.postgres.fields import ArrayField
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0033_rename_paymentschedule_related_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="TargetGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=128, verbose_name="navn"),
                ),
                (
                    "required_fields_for_case",
                    ArrayField(
                        models.CharField(max_length=128),
                        blank=True,
                        null=True,
                        verbose_name="påkrævede felter på sag",
                    ),
                ),
            ],
            options={
                "verbose_name": "målgruppe",
                "verbose_name_plural": "målgrupper",
            },
        ),
        migrations.AddField(
            model_name="case",
            name="target_group_model",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cases",
                to="core.TargetGroup",
                verbose_name="målgruppe",
            ),
        ),
        migrations.AddField(
            model_name="historicalcase",
            name="target_group_model",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="core.TargetGroup",
                verbose_name="målgruppe",
            ),
        ),
    ]
