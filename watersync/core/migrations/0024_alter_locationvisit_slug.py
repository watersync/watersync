# Generated by Django 5.0.8 on 2025-04-02 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_locationvisit_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationvisit',
            name='slug',
            field=models.SlugField(editable=False, max_length=100),
        ),
    ]
