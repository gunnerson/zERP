# Generated by Django 3.0.6 on 2020-05-28 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0012_auto_20200528_0636'),
    ]

    operations = [
        migrations.AddField(
            model_name='downtime',
            name='dt_status',
            field=models.CharField(choices=[('PE', 'Pending'), ('RE', 'Work in progress'), ('AP', 'Awaiting parts')], default='SB', max_length=2),
        ),
    ]