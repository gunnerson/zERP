# Generated by Django 3.0.5 on 2020-04-04 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0004_auto_20200404_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='press',
            name='descr',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='press',
            name='pname',
            field=models.CharField(max_length=12),
        ),
    ]
