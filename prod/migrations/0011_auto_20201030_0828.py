# Generated by Django 3.1.2 on 2020-10-30 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prod', '0010_remove_jobinst_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobinst',
            name='shift',
            field=models.IntegerField(blank=True, choices=[(1, '1st Shift'), (2, '2nd Shift')], null=True),
        ),
    ]
