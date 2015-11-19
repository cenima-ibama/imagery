from __future__ import unicode_literals

from lc8_download.lc8 import DownloaderErrors
from indicar.process import Process

from os.path import getsize, join, isfile
from os import remove
from datetime import date, timedelta

from django.utils.encoding import python_2_unicode_compatible
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, ugettext_lazy as _
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.conf import settings
from .utils import three_digit, calendar_date, download
from .utils import get_bounds, get_cloud_rate


@python_2_unicode_compatible
class Scene(models.Model):
    """Class to register the Scenes of Landsat imagery"""

    sat_options = (
        ('L8', 'Landsat 8'),
        ('L7', 'Landsat 7'),
        ('L5', 'Landsat 5'),
        )

    status_options = (
        ('downloading', _('Downloading')),
        ('dl_failed', _('Download Failed')),
        ('downloaded', _('Downloaded')),
        ('processing', _('Processing')),
        ('p_failed', _('Processing Failed')),
        ('processed', _('Processed'))
        )

    path = models.CharField(max_length=3)
    row = models.CharField(max_length=3)
    sat = models.CharField('Satellite', choices=sat_options, max_length=50)
    date = models.DateField()
    name = models.CharField(max_length=21, unique=True)
    cloud_rate = models.FloatField(null=True, blank=True)
    geom = models.PolygonField(srid=4674, null=True, blank=True)
    status = models.CharField(choices=status_options, max_length=50)

    objects = models.GeoManager()

    def __str__(self):
        return '%s %s-%s %s' % (self.sat, self.path, self.row, self.date.strftime('%x'))

    def day(self):
        """Return the julian day of the scene's date as a 3 character string"""
        return three_digit(self.date.timetuple().tm_yday)

    def process(self):
        """Process the Scene using indicar-tools library. It will create a 654
        image composition, a NDVI and a change detection to Landsat 8 Scenes.
        To Landsat 5 and 7, it will create only a 543 composition.
        """
        if self.sat == 'L8':
            if self.images.filter(type__in=['B4', 'B5', 'B6', 'BQA']).count() == 4:
                self.status = 'processing'
                self.save()
                process = Process(self.dir())

                rgb = process.make_img([6, 5, 4])
                if rgb is not False:
                    Image.objects.get_or_create(
                        name=rgb.split('/')[-1],
                        type='r6g5b4',
                        scene=self
                    )

                ndvi = process.make_ndvi()
                if ndvi is not False:
                    Image.objects.get_or_create(name=ndvi.split('/')[-1],
                        type='ndvi',
                        scene=self)

                detection = process.change_detection()
                if detection is not False:
                    Image.objects.get_or_create(name=detection.split('/')[-1],
                        type='detection',
                        scene=self)

                if rgb and ndvi:
                    self.status = 'processed'
                    self.save()
                    return True
                else:
                    self.status = 'p_failed'
                    self.save()
                    return False
            else:
                print('Check if you have B4, B5, B6 and BQA files of this scene.')
                return False

        elif self.sat in ['L5', 'L7']:
            if self.images.filter(type__in=['B3', 'B4', 'B5']).count() == 3:
                self.status = 'processing'
                self.save()
                process = Process(self.dir())
                rgb = process.make_img([5, 4, 3])

                if rgb is not False:
                    Image.objects.get_or_create(name=rgb.split('/')[-1],
                        type='r5g4b3',
                        scene=self)
                    self.status = 'processed'
                    self.save()
                else:
                    self.status = 'p_failed'
                    self.save()
                    return False
            else:
                print('Check if you have B3, B4 and B5 files of this scene.')
                return False

    def quicklook(self):
        """Return the URL of the Natural View quicklook image."""
        base_url = 'http://earthexplorer.usgs.gov/browse'
        if self.sat == 'L8':
            return '%s/landsat_8/%s/%s/%s/%s.jpg' % (base_url, self.date.year,
                self.path, self.row, self.name)
        if self.sat == 'L7':
            return '%s/etm/%s/%s/%s/%s_REFL.jpg' % (base_url, int(self.path),
                int(self.row), self.date.year, self.name)
        if self.sat == 'L5':
            return '%s/tm/%s/%s/%s/%s_REFL.jpg' % (base_url, int(self.path),
                int(self.row), self.date.year, self.name)

    def dir(self):
        """Return the folder where the files of the scenes are saved."""
        return join(settings.MEDIA_ROOT, self.sat, self.name)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Scene, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-date', 'path', 'row']
        verbose_name = _('Scene')
        verbose_name_plural = _('Scenes')


@python_2_unicode_compatible
class Image(models.Model):
    """Class to register the image files. All Images are associated with
    one Scene object.False
    """

    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=30)
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    scene = models.ForeignKey(Scene, related_name='images')

    def __str__(self):
        return '%s' % self.name

    def url(self):
        """URL string to be used concatenated with MEDIA_URL"""
        return join(settings.MEDIA_URL, self.scene.sat, self.scene.name, self.name)

    def file_path(self):
        """File path of the Image in the filesystem."""
        return '%s' % join(self.scene.dir(), self.name)

    def file_exists(self):
        """Test if the file exists on filesystem."""
        return isfile(self.file_path())

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Image, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')


@receiver(post_delete, sender=Image)
def post_delete_image(sender, instance, *args, **kwargs):
    """Overwrites post_delete method of Image Model to delete also the file
    fisically in the disk.
    """
    if instance.file_exists():
        remove(instance.file_path())


@python_2_unicode_compatible
class ScheduledDownload(models.Model):
    """Class to schedule the download of Landsat 8 imagery."""

    path = models.CharField(max_length=3)
    row = models.CharField(max_length=3)
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)

    def __str__(self):
        return 'L8 %s-%s' % (self.path, self.row)

    def last_scene(self):
        """Return the last Scene of this path and row or None if there isn't
        any Scene yet.
        """
        if Scene.objects.filter(path=self.path, row=self.row, sat='L8'):
            return Scene.objects.filter(path=self.path, row=self.row, sat='L8') \
                .latest('date')
        else:
            return None

    def has_new_scene(self):
        """Return True if it has more than 16 days since the last Scene of this
        path and row or if there isn't any Scene registered for this path and
        row.
        """
        if self.last_scene() is None:
            return True
        elif date.today() - self.last_scene().date >= timedelta(16):
            return True
        else:
            return False

    def next_scene_name(self):
        """Return the name of the next Scene for this path and row. If there
        isn't any registered Scene or the last registered Scene is older than 32
        days, it will return the scene name with the date of today.
        """
        if self.last_scene() is not None and \
            (self.creation_date - self.last_scene().date <= timedelta(32)):
            first_part = self.last_scene().name[:13]
            end = self.last_scene().name[16:]
            day = three_digit(int(self.last_scene().day()) + 16)
            return '%s%s%s' % (first_part, day, end)
        else:
            year = date.today().year
            day = three_digit(date.today().timetuple().tm_yday)
            return 'LC8%s%s%s%sLGN00' % (self.path, self.row, year, day)

    def create_scene(self):
        """Get or Create a new Scene object for this path and row."""
        scene_date = calendar_date(
            self.next_scene_name()[9:13],
            self.next_scene_name()[13:16]
            )

        try:
            geom = Polygon(get_bounds(self.next_scene_name()))
        except IndexError:
            geom = None

        try:
            cloud_rate = get_cloud_rate(self.next_scene_name())
        except FileNotFoundError:
            cloud_rate = None

        return Scene.objects.get_or_create(
            path=self.path,
            row=self.row,
            sat='L8',
            name=self.next_scene_name(),
            date=scene_date,
            status='downloading',
            geom=geom,
            cloud_rate=cloud_rate
            )

    def create_image(self, image_name):
        """Create a new Image object."""
        return Image.objects.get_or_create(
            name=image_name,
            type=image_name.split('_')[1].split('.')[0],
            scene=Scene.objects.get(name=image_name.split('_')[0])
            )

    def download_new_scene(self, bands=[4, 5, 6, 'BQA']):
        """Download the bands B4, B5, B6 and BQA of the next scene."""
        if self.has_new_scene():
            try:
                downloaded = download(self.next_scene_name(), bands)
                self.create_scene()
                for path, size in downloaded:
                    if getsize(path) == size:
                        self.create_image(path.split('/')[-1])
                    else:
                        remove(path)
                return downloaded
            except DownloaderErrors:
                return []

    def check_last_scene(self, bands=[4, 5, 6, 'BQA']):
        """Check if the last scene already has all image bands. If not, try to
        download.
        """
        last_scene = self.last_scene()
        if last_scene is not None:
            if last_scene.images.count() < len(bands) or last_scene.status == 'dl_failed':
                try:
                    downloaded = download(last_scene.name, bands)
                    for path, size in downloaded:
                        if getsize(path) == size:
                            self.create_image(path.split('/')[-1])
                        else:
                            remove(path)
                    return downloaded
                except RemoteFileDoesntExist:
                    if last_scene.status != 'dl_failed':
                        last_scene.status = 'dl_failed'
                        last_scene.save()
                    return []
            else:
                if last_scene.status == 'downloading':
                    last_scene.status = 'downloaded'
                    last_scene.save()
                return []
        else:
            print('There is not any Scenes registered for this path and row')

    def clean(self):
        self.clean_fields()
        try:
            if self != ScheduledDownload.objects.get(path=self.path, row=self.row):
                raise ValidationError(
                    _('There is already a scheduled scene with this path and row.')
                    )
        except self.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ScheduledDownload, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Scheduled Download')
        verbose_name_plural = _('Scheduled Downloads')


def validate_scene_name(value):
    """Validator for the scene_name field of PastSceneDownload Model."""
    try:
        Scene.objects.get(name=value)
        raise ValidationError(
            _('The scene you want is already on our database.')
            )
    except Scene.DoesNotExist:
        if len(value) != 21:
            raise ValidationError(
            _('The scene name needs to have 21 characters.')
            )
        elif not value.startswith('L') or value[2] not in ['5', '7', '8']:
            raise ValidationError(
            _('Wrong scene name. Please check it.')
            )


class SceneRequest(models.Model):
    """Model to receive requests of download of past Scenes. It can download
    Landsat 5, 7 and 8 from AWS or Google Earth Engine.
    """
    status_options = (
        ('pending', _('Pending')),
        ('downloading', _('Downloading')),
        ('downloaded', _('Downloaded')),
        ('not_found', _('Not found'))
    )

    scene_name = models.CharField(_('Scene name'), max_length=21, unique=True,
        validators=[validate_scene_name])
    user = models.ForeignKey(User)
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    status = models.CharField(max_length=32, choices=status_options,
        default='pending')

    def __str__(self):
        return self.scene_name

    def scene_url(self):
        """Return the URL of the Scene if it was already downloaded."""
        if self.status == 'downloaded':
            return reverse('imagery:scene', args=[self.scene_name])
        else:
            return None

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(SceneRequest, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-creation_date', 'scene_name']
        verbose_name = _('Scene Request')
        verbose_name_plural = _('Scene Requests')


