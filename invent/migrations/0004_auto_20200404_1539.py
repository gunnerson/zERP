# Generated by Django 3.0.5 on 2020-04-04 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invent', '0003_auto_20200404_1453'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('addr1', models.TextField(blank=True, null=True)),
                ('addr2', models.TextField(blank=True, null=True)),
                ('city', models.TextField(blank=True, null=True)),
                ('state', models.TextField(blank=True, null=True)),
                ('zipcode', models.TextField(blank=True, null=True)),
                ('email', models.TextField(blank=True, null=True)),
                ('phone', models.TextField(blank=True, null=True)),
                ('vcomm', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='part',
            name='venci',
        ),
        migrations.RemoveField(
            model_name='part',
            name='vendor',
        ),
        migrations.AlterField(
            model_name='part',
            name='addr',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='part',
            name='partnum',
            field=models.TextField(default=345345345),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='part',
            name='price',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='part',
            name='unit',
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name='part',
            name='vendr',
            field=models.ManyToManyField(to='invent.Vendor'),
        ),
    ]
