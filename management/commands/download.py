# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from ...models import Scene, ScheduledDownload


class Command(BaseCommand):
    help = """Download and process all the new Scenes."""

    def handle(self, *args, **options):
        for sd in ScheduledDownload.objects.all():
            sd.download_new_scene()
            sd.check_last_scene()

        for scene in Scene.objects.filter(status='downloaded'):
            scene.process()