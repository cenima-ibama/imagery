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
COUNTDOWN_RETRY = 10

@shared_task(bind=True)
def download_all(self):
    """Download all new Scenes of ScheduledDownloads."""
    bands = settings.DOWNLOAD_BANDS
    logger.info('Starting download for bands: %s' % bands.__str__())

    for sd in ScheduledDownload.objects.all():
        logger.debug('Starting download processo to %s' % sd)
        try:
            logger.debug('Download new scene to path %s and row %s' %
                (sd.path, sd.row))
            sd.download_new_scene(bands)
            logger.debug('Checking last scenes of path %s and row %s' %
                (sd.path, sd.row))
            sd.check_last_scene(bands)
            logger.debug('Download process to path %s and row %s completed' %
                (sd.path, sd.row))

        except Exception as exc:
            logger.error('Unexpected error: %s' % exc)
            logger.debug('Retry in %s seconds' % COUNTDOWN_RETRY)
            raise self.retry(countdown=COUNTDOWN_RETRY, exc=exc)

@shared_task(bind=True)
def download_all_scene_requests(self):
    """Download all pending SceneRequests."""
    logger.debug('Searching pending SceneRequests')
    for scene in SceneRequest.objects.filter(status='pending'):
        logger.debug('Downloading scene: %s' % scene.scene_name)
        download_scene_request(scene)

@shared_task
def process_all():
    """Process all scenes that have status 'downloaded'."""
    scenes = Scene.objects.filter(status='downloaded')
    group(process_scene.s(scene) for scene in scenes)()

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
                settings.""")

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

        logger.debug('Using bands %s to satellite %s' % (bands, sat))
        logger.debug('Changing scene status to downloading')
        scene_request.status = 'downloading'
        scene_request.save()
        logger.debug('Changing scene status complete')

        try:
            logger.debug('Starting download of bands %s for  scene %s' %
                (bands, scene_request.scene_name))
            downloaded = download(scene_request.scene_name, bands)
            logger.debug('Download of bands %s for scene %s completed' %
                (bands, scene_request.scene_name))
            path = join(settings.MEDIA_ROOT, sat, scene_request.scene_name)
            logger.debug('Starting registry of bands %s from path %s' % (bands, path))
            inspect_dir(path, 'downloaded')
            logger.debug('Changing scene status to downloaded')
            scene_request.status = 'downloaded'
            scene_request.save()
            logger.debug('Changing scene status complete')

        except DownloaderErrors as errors:
            logger.error('Scene %s not found.' % scene_request.scene_name)
            logger.debug('Changing scene status to not found')
            scene_request.status = 'not_found'
            scene_request.save()
            logger.debug('Changing scene status complete')

        except Exception as exc:
            logger.error('Unexpected error to scene %s (Error: %s)' %
                (scene_request.scene_name, exc))
            logger.debug('Changing scene status to dl_failed')
            scene_request.status = 'dl_failed'
            scene_request.save()
            logger.debug('Changing scene status complete')
    else:
        logger.info('The Scene Request %s was already downloaded.' % scene_request.scene_name)

@shared_task
def process_scene(scene):
    """Process a Scene. It needs to receive a Scene object."""
    return scene.process()

def inspect_dir(dir, status='processed'):
    """Create a Scene using the name of the dir and list all TIF files present
    in that dir to create the Image objects in the database. If the Scene already
    exists, only create the missing Image objects.
    """
    scene_name = dir.split('/')[-1]
    logger.info('Inspecting scene %s in path %s' % (scene_name, dir))

    #get cloud_rate of the scene
    try:
        logger.debug('Loading cloud rate of scene %s' % scene_name)
        cloud_rate = get_cloud_rate(scene_name)
    except FileNotFoundError as not_found_err:
        logger.error('Loadin error: %s' % not_found_err)
        cloud_rate = None
    logger.debug('Cloud rate of scene %s: %s' % (scene_name, cloud_rate))

    try:
        logger.debug('Verifying if scene %s exists' % scene_name)
        scene = Scene.objects.get(name=scene_name)
        if scene.cloud_rate is None:
            scene.cloud_rate = cloud_rate
            scene.save()

        logger.info('Scene %s already exists.' % scene_name)

    except Scene.DoesNotExist:
        logger.debug('Scene %s not found' % scene_name)

        try:
            logger.debug('Loading geometry of scene %s' % scene_name)
            geom = Polygon(get_bounds(scene_name))

        except IndexError as err:
            logger.error('Loading Error: %s' % err)
            geom = None

        logger.debug('Geometry of scene %s: %s' % (scene_name, geom))

        scene = Scene.objects.create(
            sat='L' + scene_name[2],
            path=scene_name[3:6],
            row=scene_name[6:9],
            date=calendar_date(scene_name[9:13], scene_name[13:16]),
            geom=geom,
            cloud_rate=cloud_rate,
            name=scene_name,
            status=status)

    logger.info('Loading Images in path %s' % dir)
    for image in listdir(dir):
        if image.endswith('.TIF') or image.endswith('.tif'):
            logger.debug('Creating image %s' % image)
            Image.objects.get_or_create(
                name=image,
                type=image.split('_')[1].split('.')[0],
                scene=scene)
            logger.debug('Image %s created' % image)

def delete_unneeded_bands(bands=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8',
    'B9', 'B10', 'B11', 'ndvi']):
    """Delete images of bands B1 to B11 and NDVI of scenes older than 32 days.
    """
    days_ago = 32
    logger.info('Deleting images about bands %s' % bands)
    min_date = date.today() - timedelta(days=days_ago)
    logger.debug('Deleting images of 32 %d days ago (date < %s)' % (days_ago, min_date))
    images = Image.objects.filter(type__in=bands, scene__date__lt=days_ago)
    num = images.count()
    resume = images.delete()
    logger.debug('Deleting success(%s)' % resume)
    logger.info('%s images deleted.' % num)

def find_last_scene(path, row, min_date=None, max_date=None, prefix='LC8', sufix='LGN00'):
    '''Search to the earliest scene in the period (min_date, max_date). The
    default value to max_date is current date, and the min_date is 30 days later
    to max_date'''

    found = False
    downloader = None
    max_date = max_date or date.today()
    min_date = min_date or max_date - timedelta(days=32)
    current_date = date(max_date.year, max_date.month, max_date.day)

    logger.info('Starting requests')

    while not downloader and current_date >= min_date:

        logger.debug('Trying with params: prefix %s, path %s, row %s, date %s, sufix %s' %
            (prefix, path, row, current_date, sufix))
        scene_name = create_scene_name(prefix, path, row, current_date, sufix)

        try :
            logger.debug('Searching Scene: %s' % scene_name)
            downloader = Downloader(scene_name)
            logger.info('Scene %s found' % scene_name)
            found = True
        except DownloaderErrors as error:
            logger.error('Downloader error: %s' % error)
            logger.info('Scene %s not found.' % scene_name)

        current_date -= timedelta(days=1)

    return scene_name if found else None


def create_scene_name(prefix, path, row, date, sufix):
    '''Return the scene name'''
    year_day = date.timetuple().tm_yday
    days = ('%s' % year_day).zfill(3)
    row = ('%s' % row).zfill(3)
    path = ('%s' % path).zfill(3)
    year = date.timetuple().tm_year
    return '%s%s%s%s%s%s' % (prefix, path, row, year, days, sufix)


@shared_task
def validate_geometry_not_null(self):
    """Validate geometry on each scene if geometry is None
    and update geom with a geometry from another scene with the same
    path and row
    """

    scenes = Scene.objects.filter(geom__isnull=True)

    for scene in scenes:
        if Scene.objects.filter(path=scene.path, row=scene.row, geom__isnull=False).count() > 0:
            last_geom = Scene.objects.filter(path=scene.path, row=scene.row, geom__isnull=False)[0]
            if last_geom:
                scene.geom = last_geom.geom
                scene.save()
                logger.info('Geometry from %s was updated' % scene.name)
            else:
                logger.info("There's no scenes without geometry")
