# Generated by Django 2.2.9 on 2020-04-27 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20200422_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='allowed_for_target_groups',
            field=models.ManyToManyField(blank=True, related_name='sections', to='core.TargetGroup', verbose_name='tilladt for målgrupper'),
        ),
    ]
