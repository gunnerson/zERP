# Generated by Django 3.0.6 on 2020-05-29 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0015_auto_20200529_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downtime',
            name='dt_status',
            field=models.CharField(choices=[('PE', 'Idle'), ('RE', 'Work in progress'), ('AP', 'Awaiting parts')], max_length=2),
        ),
    ]
