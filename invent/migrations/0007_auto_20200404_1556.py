# Generated by Django 3.0.5 on 2020-04-04 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0005_auto_20200404_1542'),
        ('invent', '0006_auto_20200404_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='cat',
            field=models.ManyToManyField(blank=True, null=True, to='equip.Press'),
        ),
    ]
