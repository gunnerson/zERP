# Generated by Django 3.0.5 on 2020-04-30 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0004_auto_20200430_1224'),
        ('invent', '0004_auto_20200430_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='cat',
            field=models.ManyToManyField(blank=True, to='equip.Press'),
        ),
    ]
