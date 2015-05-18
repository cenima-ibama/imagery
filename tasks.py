# -*- coding: utf-8 -*-
from .models import Scene, ScheduledDownload


def download_all():
    for sd in ScheduledDownload.objects.all():
        sd.download_new_scene()
        sd.check_last_scene()


def process_all():
    for scene in Scene.objects.filter(status='downloaded'):
        scene.process()