# Generated by Django 2.2.9 on 2020-04-28 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_activitydetails_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Effort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='navn')),
                ('description', models.CharField(blank=True, max_length=128, verbose_name='beskrivelse')),
                ('allowed_for_target_groups', models.ManyToManyField(blank=True, related_name='efforts', to='core.TargetGroup', verbose_name='tilladt for målgrupper')),
            ],
            options={
                'verbose_name': 'indsats',
                'verbose_name_plural': 'indsatser',
            },
        ),
        migrations.AddField(
            model_name='case',
            name='efforts',
            field=models.ManyToManyField(blank=True, related_name='cases', to='core.Effort', verbose_name='indsatser'),
        ),
    ]
