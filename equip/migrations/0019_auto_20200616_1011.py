# Generated by Django 3.0.7 on 2020-06-16 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invent', '0009_auto_20200616_0912'),
        ('equip', '0018_auto_20200616_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='upload',
            name='uhash',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='upload',
            name='part',
            field=models.ManyToManyField(blank=True, to='invent.Part'),
        ),
        migrations.AlterField(
            model_name='upload',
            name='press',
            field=models.ManyToManyField(blank=True, to='equip.Press'),
        ),
    ]