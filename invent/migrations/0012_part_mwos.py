# Generated by Django 3.0.5 on 2020-04-07 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0008_order_parts'),
        ('invent', '0011_auto_20200404_2010'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='mwos',
            field=models.ManyToManyField(blank=True, to='mtn.Order'),
        ),
    ]
