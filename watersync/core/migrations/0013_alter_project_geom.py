# Generated by Django 5.0.8 on 2025-03-21 14:51

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_project_geom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
