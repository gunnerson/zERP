# Generated by Django 3.0.5 on 2020-04-10 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invent', '0019_usedpart_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usedpart',
            name='amount_used',
            field=models.PositiveIntegerField(null=True),
        ),
    ]