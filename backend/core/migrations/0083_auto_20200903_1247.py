# Generated by Django 2.2.13 on 2020-09-03 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0082_target_groups_to_csv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetgroup',
            name='required_fields_for_case',
            field=models.CharField(blank=True, max_length=1024, verbose_name='påkrævede felter på sag'),
        ),
    ]
