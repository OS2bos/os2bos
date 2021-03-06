# Generated by Django 2.2.13 on 2020-06-08 09:57

from django.db import migrations
import django.db.models.expressions

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_auto_20200605_1432'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rate',
            options={'verbose_name': 'takst', 'verbose_name_plural': 'takster'},
        ),
        migrations.AlterModelOptions(
            name='rateperdate',
            options={'ordering': [django.db.models.expressions.OrderBy(django.db.models.expressions.F('start_date'), nulls_first=True)], 'verbose_name': 'takst for datoer', 'verbose_name_plural': 'takster for datoer'},
        ),
    ]
