# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=30)),
                ('creation_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Scene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('path', models.CharField(max_length=3)),
                ('row', models.CharField(max_length=3)),
                ('satellite', models.CharField(max_length=50, choices=[('lc8', 'Landsat 8'), ('le7', 'Landsat 7'), ('lt5', 'Landsat 5')])),
                ('date', models.DateField()),
                ('name', models.CharField(max_length=28)),
                ('cloud_rate', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(max_length=50, choices=[('downloading', 'Downloading'), ('dl_failed', 'Download Failed'), ('processing', 'Processing'), ('p_failed', 'Processing Failed')])),
                ('files', models.ManyToManyField(related_name='scene', to='imagery.File')),
            ],
        ),
    ]
