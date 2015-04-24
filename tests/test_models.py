# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import Scene, Image, ScheduledDownload
from ..utils import three_digit


class TestScene(TestCase):

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
        self.assertEqual(self.scene.__str__(), 'LC8 001-001 01/01/15')
        self.assertEqual(self.scene.day(), '001')

        Scene.objects.create(
            path='001',
            row='001',
            sat='LC8',
            date=date(2015, 1, 17),
            name='LC80010012015017LGN00',
            status='downloading'
            )

        self.assertEqual(Scene.objects.all().count(), 2)

    def test_validation(self):
        with self.assertRaises(ValidationError):
            Scene.objects.create(
                path='001',
                row='001',
                sat='LC8',
                date=date(2015, 1, 1),
                name='LC80010012015001LGN00',
                status='downloading'
                )


class TestImage(TestCase):

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

        self.image = Image.objects.create(
            name='LC80010012015001LGN00_B4.TIF',
            type='B4',
            scene=self.scene
            )

    def test_creation(self):
        self.assertEqual(self.image.__str__(), 'LC80010012015001LGN00_B4.TIF')
        self.assertEqual(self.image.path(),
            'LC80010012015001LGN00/LC80010012015001LGN00_B4.TIF')

        Image.objects.create(
            name='LC80010012015001LGN00_B5.TIF',
            type='B5',
            scene=self.scene
            )

        self.assertEqual(Image.objects.all().count(), 2)
        self.assertEqual(self.scene.images().count(), 2)

    def test_validation(self):
        with self.assertRaises(ValidationError):
            Image.objects.create(
                name='LC80010012015001LGN00_B4.TIF',
                type='B4',
                scene=self.scene
                )


class TestScheduledDownload(TestCase):

    def setUp(self):
        self.sd = ScheduledDownload.objects.create(path='001', row='001')
        self.sd2 = ScheduledDownload.objects.create(path='001', row='002')

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
        self.assertEqual(self.sd.__str__(), 'LC8 001-001')
        self.assertEqual(ScheduledDownload.objects.all().count(), 2)

    def test_validation(self):
        with self.assertRaises(ValidationError):
            ScheduledDownload.objects.create(path='001', row='001')

    def test_last_scene(self):
        self.assertEqual(self.sd.last_scene(), self.scene)
        self.assertIsNone(self.sd2.last_scene())

    def test_has_new_scene(self):
        self.assertEqual(self.sd.has_new_scene(), True)

        day_number = three_digit(date.today().timetuple().tm_yday)
        Scene.objects.create(
            path='001',
            row='001',
            sat='LC8',
            date=date.today(),
            name='LC80010012015%sLGN00' % day_number,
            cloud_rate=20.3,
            status='downloading'
            )

        self.assertEqual(self.sd.has_new_scene(), False)

        self.assertEqual(self.sd2.has_new_scene(), True)

    def test_next_scene_name(self):
        self.assertEqual(self.sd.next_scene_name(), 'LC80010012015017LGN00')
        self.assertIsNone(self.sd2.next_scene_name())