# Generated by Django 5.0.8 on 2024-08-28 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0004_remove_sensor_owner_sensor_user_alter_sensor_detail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensorrecord',
            name='deployment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sensor.deployment'),
        ),
    ]