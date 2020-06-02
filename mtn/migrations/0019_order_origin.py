# Generated by Django 3.0.6 on 2020-06-01 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_employee_user'),
        ('mtn', '0018_auto_20200601_1045'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='origin',
            field=models.ForeignKey(limit_choices_to=models.Q(('role', 'SV'), ('role', 'MT'), _connector='OR'), null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='staff.Employee'),
        ),
    ]