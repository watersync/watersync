# Generated by Django 5.0.8 on 2024-12-17 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waterquality', '0003_alter_samplingevent_executed_by_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='measurement',
            old_name='parameter_name',
            new_name='parameter',
        ),
    ]
