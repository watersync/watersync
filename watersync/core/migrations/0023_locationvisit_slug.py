# Generated by Django 5.0.8 on 2025-04-02 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_rename_comment_fieldwork_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationvisit',
            name='slug',
            field=models.SlugField(default='test-slug', editable=False, max_length=100, unique=False),
            preserve_default=False,
        ),
    ]
