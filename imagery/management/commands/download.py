# -*- coding: utf-8 -*-
import sys

from django.core.management.base import BaseCommand

from ...tasks import download_all, process_all


class Command(BaseCommand):
    help = """Download and process all the new Scenes."""

    def handle(self, *args, **options):
        download_all()
        process_all()

        sys.exit(0)