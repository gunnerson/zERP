# Generated by Django 3.0.6 on 2020-06-01 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_employee_user'),
        ('mtn', '0022_auto_20200601_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='descrrep',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='repby',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'MT'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.Employee'),
        ),
    ]