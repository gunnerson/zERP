# Generated by Django 3.0.5 on 2020-04-04 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invent', '0005_auto_20200404_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='parts',
            field=models.ManyToManyField(to='invent.Part'),
        ),
        migrations.AddField(
            model_name='vendor',
            name='vcomm',
            field=models.TextField(blank=True, null=True),
        ),
    ]