# -*- coding: utf-8 -*-
from os import listdir
from datetime import date, timedelta

from django.contrib.gis.geos import Polygon

from .models import Scene, Image, ScheduledDownload
from .utils import calendar_date, get_bounds, get_cloud_rate


def download_all():
    """Download all new Scenes of ScheduledDownloads."""
    for sd in ScheduledDownload.objects.all():
        sd.download_new_scene()
        sd.check_last_scene()


def process_all():
    """Process all scenes that have status 'downloaded'."""
    for scene in Scene.objects.filter(status='downloaded'):
        scene.process()


def inspect_dir(dir, status='processed'):
    """Create a Scene using the name of the dir and list all TIF files present
    in that dir to create the Image objects in the database. If the Scene already
    exists, only create the missing Image objects.
    """
    scene_name = dir.split('/')[-1]

    #get cloud_rate of the scene
    try:
        cloud_rate = get_cloud_rate(scene_name)
    except FileNotFoundError:
        cloud_rate = None

    try:
        scene = Scene.objects.get(name=scene_name)
        if scene.cloud_rate is None:
            scene.cloud_rate = cloud_rate
            scene.save()

        print('%s already exists.' % scene_name)

    except Scene.DoesNotExist:
        #get geom of the Scene
        try:
            geom = Polygon(get_bounds(scene_name))
        except IndexError:
            geom = None

        scene = Scene.objects.create(
            sat='L' + scene_name[2],
            path=scene_name[3:6],
            row=scene_name[6:9],
            date=calendar_date(scene_name[9:13], scene_name[13:16]),
            geom=geom,
            cloud_rate=cloud_rate,
            name=scene_name,
            status=status
            )

    for image in listdir(dir):
        if image.endswith('.TIF') or image.endswith('.tif'):
            Image.objects.get_or_create(
                name=image,
                type=image.split('_')[1].split('.')[0],
                scene=scene
                )


def delete_unneeded_bands(bands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8',
    'B9', 'B10', 'B11', 'ndvi']):
    """Delete images of bands B1 to B11 and NDVI of scenes older than 32 days.
    """

    images = Image.objects.filter(
        type__in=bands,
        scene__date__lt=date.today() - timedelta(days=32)
    )
    images.delete()
    print('%s images deleted.' % images.count())
