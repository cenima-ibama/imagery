# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('imagery', '0013_auto_20150612_1624'),
    ]

    operations = [
        migrations.CreateModel(
            name='PastSceneDownload',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('scene', models.CharField(max_length=28)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[('created', 'Created'), ('downloading', 'Downloading'), ('downloaded', 'Downloaded'), ('not_found', 'Not found')], max_length=32)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
