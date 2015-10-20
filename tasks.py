# -*- coding: utf-8 -*-
from celery import group, shared_task
from lc8_download.lc8 import DownloaderErrors

from os import listdir
from os.path import join, getsize, isfile
from datetime import date, timedelta

from django.contrib.gis.geos import Polygon
from django.conf import settings

from .models import Scene, Image, ScheduledDownload, PastSceneDownload
from .utils import calendar_date, get_bounds, get_cloud_rate, download
from .utils import get_sat_code


@shared_task(bind=True)
def download_all(self):
    """Download all new Scenes of ScheduledDownloads."""
    try:
        for sd in ScheduledDownload.objects.all():
            sd.download_new_scene()
            sd.check_last_scene()
    except:
        raise self.retry(countdown=10)


@shared_task
def download_all_past_scenes(self):
    """Download all pending PastScenes."""
    for past_scene in PastSceneDownload.objects.filter(status='created'):
        download(past_scene)


def download_past_scene(past_scene):
    sat = get_sat_code(past_scene.scene_name)
    if sat == 'L8':
        bands = [6, 5, 4, 'BQA']
    else:
        bands = [5, 4, 3]

    try:
        past_scene.status = 'downloading'
        past_scene.save()
        complete = False
        while complete is False:
            downloaded = download(past_scene.scene_name, bands)
            complete = True
            for path, size in downloaded:
                if isfile(path) and getsize(path) != size:
                    complete = False
                    break

        inspect_dir(join(settings.MEDIA_ROOT, sat, past_scene.scene_name),
            'downloaded')
        past_scene.status = 'downloaded'
        past_scene.save()
    except DownloaderErrors:
        past_scene.status = 'Not found'
        past_scene.save()


@shared_task
def process_scene(scene):
    return scene.process()


@shared_task
def process_all():
    """Process all scenes that have status 'downloaded'."""
    scenes = Scene.objects.filter(status='downloaded')
    group(process_scene.s(scene) for scene in scenes)()


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

    images = Image.objects.filter(type__in=bands,
        scene__date__lt=date.today() - timedelta(days=32))
    num = images.count()
    images.delete()
    print('%s images deleted.' % num)
