# -*- coding: utf-8 -*-
from os import listdir
from os.path import join

from django.core.management.base import BaseCommand

from ...tasks import inspect_dir


class Command(BaseCommand):
    args = 'folder'
    help = """Inspect a directory for its subdirs and import every subdir as a
    Scene object and every GeoTiff file as an Image object"""

    def handle(self, *args, **options):
        for dir in args:
            for subdir in listdir(dir):
                inspect_dir(join(dir, subdir))