# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0009_remove_scheduleddownload_last_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='scene',
            name='geom',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='scene',
            name='sat',
            field=models.CharField(max_length=50, verbose_name='Satellite', choices=[('L8', 'Landsat 8'), ('L7', 'Landsat 7'), ('L5', 'Landsat 5')]),
        ),
        migrations.AlterField(
            model_name='scene',
            name='status',
            field=models.CharField(max_length=50, choices=[('downloading', 'Downloading'), ('dl_failed', 'Download Failed'), ('downloaded', 'Downloaded'), ('processing', 'Processing'), ('p_failed', 'Processing Failed'), ('processed', 'Processed')]),
        ),
    ]
