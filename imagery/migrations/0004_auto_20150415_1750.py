# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0003_auto_20150415_1637'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scene',
            name='files',
        ),
        migrations.AddField(
            model_name='file',
            name='scene',
            field=models.ForeignKey(default=1, to='imagery.Scene'),
            preserve_default=False,
        ),
    ]
