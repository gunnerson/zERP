# Generated by Django 3.0.7 on 2020-06-16 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0019_auto_20200616_1011'),
        ('invent', '0009_auto_20200616_0912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='cat',
            field=models.ManyToManyField(blank=True, to='equip.Press'),
        ),
    ]