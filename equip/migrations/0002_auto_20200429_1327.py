# Generated by Django 3.0.5 on 2020-04-29 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='press',
            name='pname',
            field=models.CharField(max_length=40),
        ),
    ]
