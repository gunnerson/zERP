# Generated by Django 3.0.5 on 2020-04-11 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0014_merge_20200410_0155'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cost_of_repair',
            field=models.FloatField(null=True),
        ),
    ]
