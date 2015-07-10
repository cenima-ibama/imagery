# -*- coding: utf-8 -*-
from tempfile import mkdtemp
from os import mkdir
from os.path import join
from datetime import date

from django.test import TestCase
from django.core.management import call_command

from ..models import Scene, Image


class TestInspectImageryDir(TestCase):

    def setUp(self):
        self.folder = mkdtemp()
        mkdir(join(self.folder, 'LC82200662015001LGN00'))
        f = open(join(self.folder, 'LC82200662015001LGN00',
            'LC82200662015001LGN00_B1.TIF'), 'w')
        f.close()

    def test_command(self):
        call_command('inspect_imagery_dir', self.folder)

        self.assertEqual(Scene.objects.all().count(), 1)
        self.assertEqual(Image.objects.all().count(), 1)

        scene = Scene.objects.all()[0]
        image = Image.objects.all()[0]
        self.assertEqual(scene.sat, 'L8')
        self.assertEqual(scene.path, '220')
        self.assertEqual(scene.row, '066')
        self.assertEqual(scene.date, date(2015, 1, 1))
        self.assertEqual(scene.status, 'processed')
        self.assertEqual(scene.name, 'LC82200662015001LGN00')

        self.assertEqual(image.name, 'LC82200662015001LGN00_B1.TIF')
        self.assertEqual(image.type, 'B1')
        self.assertEqual(image.scene, scene)


class TestCreateScene(TestCase):

    def setUp(self):
        self.folder = mkdtemp()
        mkdir(join(self.folder, 'LC82200662015001LGN00'))
        f = open(join(self.folder, 'LC82200662015001LGN00',
            'LC82200662015001LGN00_B1.TIF'), 'w')
        f.close()

    def test_command(self):
        call_command('create_scene', join(self.folder, 'LC82200662015001LGN00'))

        self.assertEqual(Scene.objects.all().count(), 1)
        self.assertEqual(Image.objects.all().count(), 1)

        scene = Scene.objects.all()[0]
        image = Image.objects.all()[0]
        self.assertEqual(scene.sat, 'L8')
        self.assertEqual(scene.path, '220')
        self.assertEqual(scene.row, '066')
        self.assertEqual(scene.date, date(2015, 1, 1))
        self.assertEqual(scene.status, 'processed')
        self.assertEqual(scene.name, 'LC82200662015001LGN00')

        self.assertEqual(image.name, 'LC82200662015001LGN00_B1.TIF')
        self.assertEqual(image.type, 'B1')
        self.assertEqual(image.scene, scene)

