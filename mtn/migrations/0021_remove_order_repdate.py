# Generated by Django 3.0.6 on 2020-06-01 17:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0020_order_timerepidle'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='repdate',
        ),
    ]
