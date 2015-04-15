# -*- coding: utf-8 -*-
from datetime import date

from django.test import TestCase

from ..models import Scene, File


class TestScene(TestCase):

    def test_creation(self):
        scene = Scene.objects.create(
            path='001',
            row='001',
            sat='LC8',
            date=date(2015, 1, 1),
            name='LC80010012015001LGN00',
            cloud_rate=20.3,
            status='downloading'
            )

        self.assertEqual(scene.__str__(), 'LC8 001-001 01/01/15')

        Scene.objects.create(
            path='001',
            row='002',
            sat='LC8',
            date=date(2015, 1, 1),
            name='LC80010012015001LGN00',
            status='downloading'
            )

        self.assertEqual(Scene.objects.all().count(), 2)


class TestFile(TestCase):

    def setUp(self):
        self.scene = Scene.objects.create(
            path='001',
            row='001',
            sat='LC8',
            date=date(2015, 1, 1),
            name='LC80010012015001LGN00',
            cloud_rate=20.3,
            status='downloading'
            )

    def test_creation(self):
        f = File.objects.create(
            name='LC80010012015001LGN00_B4.TIF',
            type='B4',
            scene=self.scene
            )

        self.assertEqual(f.__str__(), 'LC80010012015001LGN00_B4.TIF')
        self.assertEqual(File.objects.all().count(), 1)
        self.assertEqual(self.scene.files().count(), 1)