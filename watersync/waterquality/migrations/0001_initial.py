# Generated by Django 5.0.8 on 2024-08-22 09:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('detail', models.JSONField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.location')),
            ],
            options={
                'verbose_name': 'Water Sample',
                'verbose_name_plural': 'Water Samples',
                'ordering': ['-timestamp'],
                'unique_together': {('location', 'timestamp')},
            },
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('property', models.CharField(max_length=50)),
                ('value', models.FloatField()),
                ('unit', models.CharField(max_length=50)),
                ('detail', models.JSONField(blank=True, null=True)),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='waterquality.sample')),
            ],
            options={
                'verbose_name': 'Water Measurement',
                'verbose_name_plural': 'Water Measurements',
                'ordering': ['sample', 'property'],
            },
        ),
    ]
