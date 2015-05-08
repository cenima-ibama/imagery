# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0010_auto_20150508_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scene',
            name='geom',
            field=django.contrib.gis.db.models.fields.PolygonField(srid=4674, null=True, blank=True),
        ),
    ]
