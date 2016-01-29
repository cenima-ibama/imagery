# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scene',
            name='satellite',
        ),
        migrations.AddField(
            model_name='scene',
            name='sat',
            field=models.CharField(max_length=50, default='lc8', verbose_name='Satellite', choices=[('lc8', 'Landsat 8'), ('le7', 'Landsat 7'), ('lt5', 'Landsat 5')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='scene',
            name='status',
            field=models.CharField(max_length=50, blank=True, choices=[('downloading', 'Downloading'), ('dl_failed', 'Download Failed'), ('processing', 'Processing'), ('p_failed', 'Processing Failed'), ('processed', 'Processed')]),
        ),
    ]
