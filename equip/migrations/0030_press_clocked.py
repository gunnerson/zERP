# Generated by Django 3.1.2 on 2020-10-30 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0029_press_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='press',
            name='clocked',
            field=models.BooleanField(default=False),
        ),
    ]
