# Generated by Django 5.0.8 on 2025-03-23 17:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_rename_users_fieldwork_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationvisit',
            name='fieldwork',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='visits', to='core.fieldwork'),
        ),
    ]
