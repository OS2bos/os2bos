# Generated by Django 2.2.1 on 2019-11-18 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20191112_1048'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ('date',), 'verbose_name': 'betaling', 'verbose_name_plural': 'betalinger'},
        ),
    ]
