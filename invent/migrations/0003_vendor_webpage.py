# Generated by Django 3.0.5 on 2020-04-30 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invent', '0002_auto_20200428_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='webpage',
            field=models.URLField(blank=True, null=True),
        ),
    ]