# Generated by Django 3.0.5 on 2020-04-28 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mtn', '0001_initial'),
        ('equip', '0001_initial'),
        ('invent', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usedpart',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mtn.Order'),
        ),
        migrations.AddField(
            model_name='usedpart',
            name='part',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='invent.Part'),
        ),
        migrations.AddField(
            model_name='part',
            name='cat',
            field=models.ManyToManyField(to='equip.Press'),
        ),
        migrations.AddField(
            model_name='part',
            name='vendr',
            field=models.ManyToManyField(blank=True, to='invent.Vendor'),
        ),
    ]
