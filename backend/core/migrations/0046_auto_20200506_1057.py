# Generated by Django 2.2.9 on 2020-05-06 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_auto_20200505_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktiv'),
        ),
        migrations.AlterField(
            model_name='activitydetails',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktiv'),
        ),
        migrations.AlterField(
            model_name='approvallevel',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktiv'),
        ),
        migrations.AlterField(
            model_name='effortstep',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktiv'),
        ),
        migrations.AlterField(
            model_name='municipality',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktiv'),
        ),
        migrations.AlterField(
            model_name='schooldistrict',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktiv'),
        ),
        migrations.AlterField(
            model_name='section',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktiv'),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktiv'),
        ),
        migrations.AlterField(
            model_name='targetgroup',
            name='active',
            field=models.BooleanField(default=True, verbose_name='aktiv'),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile',
            field=models.CharField(blank=True, choices=[('readonly', 'Kun læse'), ('edit', 'Læse og skrive'), ('grant', 'Bevilge'), ('workflow_engine', 'Redigere klassifikationer'), ('admin', 'Admin')], max_length=128, verbose_name='brugerprofil'),
        ),
    ]
