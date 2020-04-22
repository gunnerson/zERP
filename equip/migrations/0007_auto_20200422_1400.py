# Generated by Django 3.0.5 on 2020-04-22 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0006_press_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='press',
            name='descr',
        ),
        migrations.AlterField(
            model_name='press',
            name='status',
            field=models.CharField(choices=[('RE', 'Out of Order'), ('ST', 'Setup Due'), ('PM', 'PM Due'), ('OK', 'OK')], default='OK', max_length=2),
        ),
    ]
