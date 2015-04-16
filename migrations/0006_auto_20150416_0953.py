# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0005_auto_20150416_0946'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='File',
            new_name='Image',
        ),
        migrations.RenameField(
            model_name='image',
            old_name='name',
            new_name='file',
        ),
    ]
