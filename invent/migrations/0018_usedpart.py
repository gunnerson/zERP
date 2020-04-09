# Generated by Django 3.0.5 on 2020-04-09 17:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invent', '0017_auto_20200409_1731'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsedPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_used', models.PositiveIntegerField()),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invent.Part')),
            ],
        ),
    ]
