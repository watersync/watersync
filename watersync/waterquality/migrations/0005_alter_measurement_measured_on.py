# Generated by Django 5.0.8 on 2024-12-17 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waterquality', '0004_rename_parameter_name_measurement_parameter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurement',
            name='measured_on',
            field=models.DateField(blank=True, null=True),
        ),
    ]
