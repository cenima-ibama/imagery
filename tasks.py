# -*- coding: utf-8 -*-
from os import listdir

from django.contrib.gis.geos import Polygon

from .models import Scene, Image, ScheduledDownload
from .utils import calendar_date, get_bounds, get_cloud_rate


def download_all():
    for sd in ScheduledDownload.objects.all():
        sd.download_new_scene()
        sd.check_last_scene()


def process_all():
    for scene in Scene.objects.filter(status='downloaded'):
        scene.process()


def inspect_dir(dir):
    """Create a Scene using the name of the dir and list all TIF files present
    in that dir to create the Image objects in the database.
    """
    scene_name = dir.split('/')[-1]

    try:
        geom = Polygon(get_bounds(scene_name))
    except IndexError:
        geom = None

    try:
        cloud_rate = get_cloud_rate(scene_name)
    except FileNotFoundError:
        cloud_rate = None

    scene = Scene.objects.create(
        sat='L' + scene_name[2],
        path=scene_name[3:6],
        row=scene_name[6:9],
        date=calendar_date(scene_name[9:13], scene_name[13:16]),
        geom=geom,
        cloud_rate=cloud_rate,
        name=scene_name,
        status='processed'
        )

    for image in listdir(dir):
        if image.endswith('.TIF') or image.endswith('.tif'):
            Image.objects.create(
                name=image,
                type=image.split('_')[1].split('.')[0],
                scene=scene
                )
