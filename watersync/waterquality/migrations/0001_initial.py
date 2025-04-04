# Generated by Django 5.0.8 on 2025-04-02 15:34

import django.db.models.deletion
import django_extensions.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0024_alter_locationvisit_slug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(editable=False, max_length=100, unique=True)),
                ('method_name', models.CharField(max_length=100)),
                ('sample_collection', models.TextField(blank=True, null=True)),
                ('sample_preservation', models.TextField(blank=True, null=True)),
                ('sample_storage', models.TextField(blank=True, null=True)),
                ('analytical_method', models.TextField(blank=True, null=True)),
                ('data_postprocessing', models.TextField(blank=True, null=True)),
                ('standard_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, max_length=256, null=True)),
                ('user', models.ManyToManyField(related_name='protocols', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('target_parameters', models.CharField(max_length=50)),
                ('container_type', models.CharField(blank=True, max_length=50, null=True)),
                ('volume_collected', models.FloatField(blank=True, null=True)),
                ('replica_number', models.IntegerField(default=0)),
                ('detail', models.JSONField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('location_visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='samples', to='core.locationvisit')),
                ('protocol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='waterquality.protocol')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('parameter', models.CharField(max_length=100)),
                ('value', models.FloatField()),
                ('unit', models.CharField(max_length=50)),
                ('measured_on', models.DateField(blank=True, null=True)),
                ('details', models.TextField(blank=True, null=True)),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='measurements', to='waterquality.sample')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
