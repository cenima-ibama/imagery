# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imagery', '0008_auto_20150420_1740'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheduleddownload',
            name='last_date',
        ),
    ]
