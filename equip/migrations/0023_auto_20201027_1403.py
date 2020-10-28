# Generated by Django 3.1.2 on 2020-10-27 19:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0022_auto_20201027_1200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pmsched',
            name='local',
        ),
        migrations.AddField(
            model_name='pmsched',
            name='local',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='equip.press'),
        ),
    ]
