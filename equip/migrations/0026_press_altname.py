# Generated by Django 3.1.2 on 2020-10-27 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0025_equip'),
    ]

    operations = [
        migrations.AddField(
            model_name='press',
            name='altname',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]