# Generated by Django 2.2.16 on 2021-07-29 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0095_auto_20210622_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentschedule',
            name='recipient_name',
            field=models.CharField(blank=True, max_length=128, verbose_name='navn'),
        ),
    ]
