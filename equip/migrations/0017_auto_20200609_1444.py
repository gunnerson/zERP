# Generated by Django 3.0.6 on 2020-06-09 19:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0016_auto_20200609_1433'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobinst',
            name='job',
        ),
        migrations.RemoveField(
            model_name='jobinst',
            name='press',
        ),
        migrations.DeleteModel(
            name='Job',
        ),
        migrations.DeleteModel(
            name='JobInst',
        ),
    ]
