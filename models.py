from django.db import models

from .utils import three_digit


class Scene(models.Model):

    sat_options = (
        ('LC8', 'Landsat 8'),
        ('LE7', 'Landsat 7'),
        ('LT5', 'Landsat 5'),
        )

    status_options = (
        ('downloading', 'Downloading'),
        ('dl_failed', 'Download Failed'),
        ('processing', 'Processing'),
        ('p_failed', 'Processing Failed'),
        ('processed', 'Processed')
        )

    path = models.CharField(max_length=3)
    row = models.CharField(max_length=3)
    sat = models.CharField('Satellite', choices=sat_options, max_length=50)
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
