# Generated by Django 3.0.6 on 2020-05-28 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employee',
            options={'ordering': ['first_name']},
        ),
    ]
