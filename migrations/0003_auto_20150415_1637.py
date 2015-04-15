# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0002_auto_20150415_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scene',
            name='sat',
            field=models.CharField(verbose_name='Satellite', max_length=50, choices=[('LC8', 'Landsat 8'), ('LE7', 'Landsat 7'), ('LT5', 'Landsat 5')]),
        ),
        migrations.AlterField(
            model_name='scene',
            name='status',
            field=models.CharField(max_length=50, choices=[('downloading', 'Downloading'), ('dl_failed', 'Download Failed'), ('processing', 'Processing'), ('p_failed', 'Processing Failed'), ('processed', 'Processed')]),
        ),
    ]
