# Generated by Django 3.0.6 on 2020-05-29 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0014_auto_20200528_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downtime',
            name='dt_status',
            field=models.CharField(choices=[('PE', 'Idle'), ('RE', 'Work in progress'), ('AP', 'Awaiting parts')], default='PE', max_length=2),
        ),
    ]
