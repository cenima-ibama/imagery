# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0012_auto_20150511_1812'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scene',
            options={'ordering': ['-date', 'path', 'row']},
        ),
        migrations.AlterField(
            model_name='image',
            name='scene',
            field=models.ForeignKey(related_name='images', to='imagery.Scene'),
        ),
    ]
