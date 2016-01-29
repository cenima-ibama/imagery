# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from ...tasks import inspect_dir


class Command(BaseCommand):
    args = 'folder'
    help = """Create a Scene object and inspect its folder to add every GeoTiff
        file as an Image object"""

    def handle(self, *args, **options):
        for dir in args:
            inspect_dir(dir)