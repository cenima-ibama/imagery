from lc8_download.lc8 import RemoteFileDoesntExist

from os.path import getsize
from os import remove
from datetime import date, timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, ugettext_lazy as _

from .utils import three_digit, calendar_date, download


class Scene(models.Model):

    sat_options = (
        ('LC8', 'Landsat 8'),
        ('LE7', 'Landsat 7'),
        ('LT5', 'Landsat 5'),
        )

    status_options = (
        ('downloading', 'Downloading'),
        ('downloaded', 'Downloaded'),
        ('processing', 'Processing'),
        ('p_failed', 'Processing Failed'),
        ('processed', 'Processed')
        )

    path = models.CharField(max_length=3)
    row = models.CharField(max_length=3)
    sat = models.CharField('Satellite', choices=sat_options, max_length=50, default='LC8')
    date = models.DateField()
    name = models.CharField(max_length=28, unique=True)
    cloud_rate = models.FloatField(null=True, blank=True)
    status = models.CharField(choices=status_options, max_length=50)

    def __str__(self):
        return '%s %s-%s %s' % (self.sat, self.path, self.row, self.date.strftime('%x'))

    def day(self):
        return three_digit(self.date.timetuple().tm_yday)

    def images(self):
        return self.image_set.all()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Scene, self).save(*args, **kwargs)


class Image(models.Model):

    name = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=30)
    creation_date = models.DateField(auto_now_add=True)
    scene = models.ForeignKey(Scene)

    def __str__(self):
        return '%s' % self.name

    def path(self):
        return '%s/%s' % (self.scene.name, self.name)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Image, self).save(*args, **kwargs)


class ScheduledDownload(models.Model):

    path = models.CharField(max_length=3)
    row = models.CharField(max_length=3)
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return 'LC8 %s-%s' % (self.path, self.row)

    def last_scene(self):
        """Return the last Scene of this path and row or None if there isn't
        any Scene yet.
        """
        if Scene.objects.filter(path=self.path, row=self.row):
            return Scene.objects.filter(path=self.path, row=self.row) \
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
        isn't any registered Scene, it will return the name with the date of
        today.
        """
        if self.last_scene() is not None:
            first_part = self.last_scene().name[:13]
            end = self.last_scene().name[16:]
            day = three_digit(int(self.last_scene().day()) + 16)
            return '%s%s%s' % (first_part, day, end)
        else:
            year = date.today().year
            day = three_digit(date.today().timetuple().tm_yday)
            return 'LC8%s%s%s%sLGN00' % (self.path, self.row, year, day)

    def create_scene(self):
        scene_date = calendar_date(
            self.next_scene_name()[9:13],
            self.next_scene_name()[13:16]
            )
        return Scene.objects.get_or_create(
            path=self.path,
            row=self.row,
            name=self.next_scene_name(),
            date=scene_date,
            status='downloading'
            )

    def create_image(self, image_name):
        return Image.objects.get_or_create(
            name=image_name,
            type=image_name.split('_')[1].split('.')[0],
            scene=Scene.objects.get(name=image_name.split('_')[0])
            )

    def download_new_scene(self, bands=[4, 5, 6, 'BQA']):
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
            except RemoteFileDoesntExist:
                return []

    def clean(self):
        self.clean_fields()
        try:
            ScheduledDownload.objects.get(path=self.path, row=self.row)
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