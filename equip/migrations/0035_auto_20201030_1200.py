# Generated by Django 3.1.2 on 2020-10-30 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0034_auto_20201030_1138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='press',
            name='clocked1',
        ),
        migrations.RemoveField(
            model_name='press',
            name='clocked2',
        ),
    ]
