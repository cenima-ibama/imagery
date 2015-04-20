# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0007_auto_20150416_1023'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledDownload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('path', models.CharField(max_length=3)),
                ('row', models.CharField(max_length=3)),
                ('creation_date', models.DateField(auto_now_add=True)),
                ('last_date', models.DateField(blank=True, verbose_name='Last Download Date', null=True)),
            ],
            options={
                'verbose_name': 'Scheduled Download',
                'verbose_name_plural': 'Scheduled Downloads',
            },
        ),
        migrations.AlterField(
            model_name='scene',
            name='name',
            field=models.CharField(max_length=28, unique=True),
        ),
    ]
