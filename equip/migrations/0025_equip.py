# Generated by Django 3.1.2 on 2020-10-27 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0024_pmsched_procs'),
    ]

    operations = [
        migrations.AddField(
            model_name='press',
            name='pmed',
            field=models.BooleanField(default=False),
        ),
    ]
