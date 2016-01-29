# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0014_pastscenedownload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pastscenedownload',
            name='scene',
            field=models.CharField(unique=True, max_length=28),
        ),
        migrations.AlterField(
            model_name='pastscenedownload',
            name='status',
            field=models.CharField(choices=[('created', 'Created'), ('downloading', 'Downloading'), ('downloaded', 'Downloaded'), ('not_found', 'Not found')], max_length=32, default='created'),
        ),
    ]
