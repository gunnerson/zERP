# Generated by Django 3.0.5 on 2020-04-07 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invent', '0013_remove_part_mwos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='parts',
        ),
    ]
