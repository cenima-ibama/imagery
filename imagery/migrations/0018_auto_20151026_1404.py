# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import imagery.models


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0017_auto_20151021_1250'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'verbose_name': 'Image', 'verbose_name_plural': 'Images'},
        ),
        migrations.AlterModelOptions(
            name='scene',
            options={'verbose_name': 'Scene', 'verbose_name_plural': 'Scenes', 'ordering': ['-date', 'path', 'row']},
        ),
        migrations.AlterModelOptions(
            name='scenerequest',
            options={'verbose_name': 'Scene Request', 'verbose_name_plural': 'Scene Requests'},
        ),
        migrations.AlterField(
            model_name='image',
            name='creation_date',
            field=models.DateField(verbose_name='Creation date', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='scenerequest',
            name='creation_date',
            field=models.DateField(verbose_name='Creation date', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='scenerequest',
            name='scene_name',
            field=models.CharField(unique=True, validators=[imagery.models.validate_scene_name], max_length=28, verbose_name='Scene name'),
        ),
        migrations.AlterField(
            model_name='scenerequest',
            name='status',
            field=models.CharField(max_length=32, choices=[('pending', 'Pending'), ('downloading', 'Downloading'), ('downloaded', 'Downloaded'), ('not_found', 'Not found')], default='pending'),
        ),
        migrations.AlterField(
            model_name='scheduleddownload',
            name='creation_date',
            field=models.DateField(verbose_name='Creation date', auto_now_add=True),
        ),
    ]
