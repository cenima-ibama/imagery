# -*- coding: utf-8 -*-
from datetime import date

from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import Scene, Image


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