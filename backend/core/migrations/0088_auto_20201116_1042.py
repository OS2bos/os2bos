# Generated by Django 2.2.16 on 2020-11-16 09:42

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0087_mark_fictive_non_cash_payments_not_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='modifies',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_by', to='core.Activity', verbose_name='justeres af aktivitet'),
        ),
        migrations.AlterField(
            model_name='paymentschedule',
            name='payment_day_of_month',
            field=models.IntegerField(blank=True, default=1, help_text='dette felt er obligatorisk for og angår kun månedlige betalinger', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(31)], verbose_name='betales d.'),
        ),
        migrations.AlterField(
            model_name='rate',
            name='needs_recalculation',
            field=models.BooleanField(default=False, help_text='dette felt sættes automatisk når en takst ændres', verbose_name='skal genberegnes'),
        ),
    ]
