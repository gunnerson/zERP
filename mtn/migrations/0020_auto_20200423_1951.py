# Generated by Django 3.0.5 on 2020-04-23 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0019_auto_20200422_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='timerep',
            field=models.FloatField(null=True),
        ),
    ]