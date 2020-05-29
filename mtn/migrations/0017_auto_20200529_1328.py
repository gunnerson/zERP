# Generated by Django 3.0.6 on 2020-05-29 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0016_auto_20200529_1115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='downtime',
            name='dt_status',
        ),
        migrations.AddField(
            model_name='downtime',
            name='dt_type',
            field=models.CharField(choices=[('ID', 'Awaiting repair'), ('RE', 'Work in progress'), ('AP', 'Awaiting parts')], default='ID', max_length=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('SB', 'Ready'), ('PR', 'Production'), ('DN', 'Out of order'), ('RE', 'Maintenance'), ('AP', 'Awaiting parts'), ('ID', 'Awaiting repairs')], default='SB', max_length=2),
        ),
    ]