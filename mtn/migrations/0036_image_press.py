# Generated by Django 3.1.2 on 2020-10-23 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0020_auto_20200618_0641'),
        ('mtn', '0035_auto_20200723_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='press',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='equip.press'),
        ),
    ]