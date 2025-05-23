# Generated by Django 5.0.8 on 2025-04-09 15:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_remove_locationvisit_slug_locationvisit_date'),
        ('waterquality', '0004_rename_details_measurement_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='date',
            field=models.DateField(default='2022-01-01'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sample',
            name='location',
            field=models.ForeignKey(default=10, on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='core.location'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sample',
            name='location_visit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='core.locationvisit'),
        ),
    ]
