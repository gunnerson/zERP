# Generated by Django 3.1.2 on 2021-02-03 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('equip', '0036_auto_20201109_1647'),
        ('mtn', '0041_remove_order_timerepidle'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='local2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='local2_id', to='equip.press'),
        ),
    ]