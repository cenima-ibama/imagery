# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0019_auto_20151103_1028'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scenerequest',
            options={'ordering': ['-creation_date', 'scene_name'], 'verbose_name': 'Scene Request', 'verbose_name_plural': 'Scene Requests'},
        ),
        migrations.AlterField(
            model_name='scenerequest',
            name='creation_date',
            field=models.DateTimeField(verbose_name='Creation date', auto_now_add=True),
        ),
    ]
