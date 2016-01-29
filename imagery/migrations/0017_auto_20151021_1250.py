# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import imagery.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('imagery', '0016_auto_20151019_1042'),
    ]

    operations = [
        migrations.CreateModel(
            name='SceneRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scene_name', models.CharField(validators=[imagery.models.validate_scene_name], max_length=28, unique=True)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(max_length=32, choices=[('created', 'Created'), ('downloading', 'Downloading'), ('downloaded', 'Downloaded'), ('not_found', 'Not found')], default='created')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='pastscenedownload',
            name='user',
        ),
        migrations.DeleteModel(
            name='PastSceneDownload',
        ),
    ]
