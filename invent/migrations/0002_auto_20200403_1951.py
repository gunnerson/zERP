# Generated by Django 3.0.5 on 2020-04-03 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0003_auto_20200403_1858'),
        ('invent', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='addr',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='part',
            name='amount',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='part',
            name='price',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='part',
            name='quant',
            field=models.CharField(default=1, max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='part',
            name='venci',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
        migrations.AddField(
            model_name='part',
            name='vendor',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.RemoveField(
            model_name='part',
            name='cat',
        ),
        migrations.AddField(
            model_name='part',
            name='cat',
            field=models.ManyToManyField(to='equip.Press'),
        ),
        migrations.AlterField(
            model_name='part',
            name='descr',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='partnum',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]