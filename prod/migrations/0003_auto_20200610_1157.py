# Generated by Django 3.0.6 on 2020-06-10 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prod', '0002_auto_20200610_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobinst',
            name='shift',
            field=models.IntegerField(choices=[(1, '1st Shift'), (0, '2nd Shift'), (2, '3rd Shift'), (3, 'SAT')], max_length=1, null=True),
        ),
    ]
