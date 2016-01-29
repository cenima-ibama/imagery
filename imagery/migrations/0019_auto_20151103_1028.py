# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import imagery.models


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0018_auto_20151026_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scene',
            name='name',
            field=models.CharField(unique=True, max_length=21),
        ),
        migrations.AlterField(
            model_name='scenerequest',
            name='scene_name',
            field=models.CharField(validators=[imagery.models.validate_scene_name], unique=True, max_length=21, verbose_name='Scene name'),
        ),
    ]
