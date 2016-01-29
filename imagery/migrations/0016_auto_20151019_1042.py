# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0015_auto_20151015_1715'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pastscenedownload',
            old_name='scene',
            new_name='scene_name',
        ),
    ]
