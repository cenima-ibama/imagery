from django.db import models


class File(models.Model):

    name = models.CharField(max_length=30)
    type = models.CharField(max_length=30)
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.name, self.type)


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
    name = models.CharField(max_length=28)
    cloud_rate = models.FloatField(null=True, blank=True)
    status = models.CharField(choices=status_options, max_length=50, blank=True)
    files = models.ManyToManyField(File, related_name='scene')

    def __str__(self):
        return '%s %s-%s %s' % (self.sat, self.path, self.row, self.date.strftime('%x'))