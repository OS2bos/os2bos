# Generated by Django 2.2.1 on 2019-11-12 09:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_transfer_steps_for_sections'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='allowed_for_steps',
        ),
    ]
