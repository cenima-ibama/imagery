# -*- coding: utf-8 -*-
from celery import group, shared_task
from lc8_download.lc8 import DownloaderErrors, Downloader

import logging

from os import listdir
from os.path import join, getsize, isfile
from datetime import date, timedelta

from django.contrib.gis.geos import Polygon
from django.conf import settings
from django.utils.translation import ugettext as _

from .models import Scene, Image, ScheduledDownload, SceneRequest
from .utils import calendar_date, get_bounds, get_cloud_rate, download
from .utils import get_sat_code, send_multipart_email

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def download_all(self):
    """Download all new Scenes of ScheduledDownloads."""
    try:
        for sd in ScheduledDownload.objects.all():
            sd.download_new_scene(settings.DOWNLOAD_BANDS)
            sd.check_last_scene(settings.DOWNLOAD_BANDS)
    except:
        raise self.retry(countdown=10)


@shared_task(bind=True)
def download_all_scene_requests(self):
    """Download all pending SceneRequests."""
    for scene in SceneRequest.objects.filter(status='pending'):
        download_scene_request(scene)


@shared_task
def download_scene_request(scene_request):
    """Download a SceneRequest. It needs to receive a SceneRequest object."""
    if scene_request.status != 'downloaded':
        sat = get_sat_code(scene_request.scene_name)
        if sat == 'L8':
            try:
                bands = settings.DOWNLOAD_BANDS
            except AttributeError:
                bands = [4, 5, 6, 'BQA']
        else:
            bands = [5, 4, 3]

        try:
            scene_request.status = 'downloading'
            scene_request.save()
            complete = False
            while complete is False:
                downloaded = download(scene_request.scene_name, bands)
                complete = True
                for path, size in downloaded:
                    if isfile(path) and getsize(path) != size:
                        complete = False
                        break

            inspect_dir(join(settings.MEDIA_ROOT, sat, scene_request.scene_name),
                'downloaded')
            scene_request.status = 'downloaded'
            scene_request.save()
        except DownloaderErrors:
            scene_request.status = 'Not found'
            scene_request.save()
    else:
        print('The Scene Request %s was already downloaded.' % scene_request.scene_name)


@shared_task
def process_scene(scene):
    """Process a Scene. It needs to receive a Scene object."""
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


@shared_task
def not_found_scenes_alert():
    """Send email if there are Scene Requests that were not found in AWS and
    Google Earth servers and need manual download.
    """
    yesterday = date.today() - timedelta(days=1)
    if SceneRequest.objects.filter(status='not_found',
        creation_date__gte=yesterday).count() > 0:
        try:
            send_multipart_email(
                subject='Not Found Scene Requests',
                html_template='imagery/email_not_found_scenerequests.html',
                from_email=settings.SERVER_EMAIL,
                to_email=settings.NOT_FOUND_SCENES_ADMIN_EMAILS
                )
        except AttributeError:

            logger.error(
                """There are scene requests that require manual download but we
                could not send email because the variables SERVER_EMAIL or
                NOT_FOUND_SCENES_ADMIN_EMAILS are not configured in your
                settings."""
            )


def find_last_scene(path, row, min_date=None, max_date=None, prefix='LC8', sufix='LGN00'):
    '''Search to the earliest scene in the period (min_date, max_date). The
    default value to max_date is current date, and the min_date is 30 days later
    to max_date'''

    found = False
    downloader = None
    max_date = max_date or date.today()
    min_date = min_date or max_date - timedelta(days=30)
    current_date = date(max_date.year, max_date.month, max_date.day)

    logger.info('Starting requests')

    while not downloader and current_date >= min_date:

        logger.info('Searching scene')
        logger.debug('Date: %s' % current_date)
        scene_name = create_scene_name(prefix, path, row, current_date, sufix)
        logger.debug('Scene name: %s' % scene_name)
        try :
            downloader = Downloader(scene_name)
            found = True
        except DownloaderErrors as error:
            logger.info('Scene %s not found.' % scene_name)

        current_date -= timedelta(days=1)

    return scene_name if found else None


def create_scene_name(prefix, path, row, date, sufix):

    year_day = date.timetuple().tm_yday
    days = ('%s' % year_day).zfill(3)
    row = ('%s' % row).zfill(3)
    path = ('%s' % path).zfill(3)
    year = date.timetuple().tm_year
    return '%s%s%s%s%s%s' % (prefix, path, row, year, days, sufix)
