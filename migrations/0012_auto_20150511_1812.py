# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0011_auto_20150508_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='name',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
