# Generated by Django 3.0.6 on 2020-05-14 19:37

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtn', '0008_auto_20200514_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='textsearchable_index_col',
            field=django.contrib.postgres.search.SearchVectorField(editable=False, null=True),
        ),
    ]
