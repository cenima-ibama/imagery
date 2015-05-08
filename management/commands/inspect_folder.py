# -*- coding: utf-8 -*-
from os import listdir
from os.path import join

from django.core.management.base import BaseCommand

from ...models import Scene, Image
from ...utils import calendar_date


class Command(BaseCommand):
    args = 'folder'
    help = """Inspect a directory for its subdirs and import every subdir as a
    Scene object and every GeoTiff file as an Image object"""

    def handle(self, *args, **options):
        for dir in args:
            for subdir in listdir(dir):
                scene = Scene.objects.create(
                    sat='L' + subdir[2],
                    path=subdir[3:6],
                    row=subdir[6:9],
                    date=calendar_date(subdir[9:13], subdir[13:16]),
                    name=subdir,
                    status='processed'
                    )

                for image in listdir(join(dir, subdir)):
                    if image.endswith('.TIF') or image.endswith('.tif'):
                        Image.objects.create(
                            name=image,
                            type=image.split('_')[1].split('.')[0],
                            scene=scene
                            )