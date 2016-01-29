# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0006_auto_20150416_0953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='file',
        ),
        migrations.AddField(
            model_name='image',
            name='name',
            field=models.CharField(default='LC8', max_length=30, unique=True),
            preserve_default=False,
        ),
    ]
