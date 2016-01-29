# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0004_auto_20150415_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.FileField(max_length=30, upload_to=''),
        ),
    ]
