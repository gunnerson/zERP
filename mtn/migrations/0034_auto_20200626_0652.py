# Generated by Django 3.0.7 on 2020-06-26 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0033_merge_20200626_0652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downtime',
            name='dttype',
            field=models.CharField(choices=[('RE', 'Maintenance'), ('AP', 'Awaiting Parts'), ('DN', 'Out of Order')], max_length=2, null=True),
        ),
    ]
