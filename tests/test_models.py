# -*- coding: utf-8 -*-
from datetime import date
from os.path import join, isfile
from os import makedirs
from shutil import rmtree

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Polygon
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.conf import settings
from ..models import Scene, Image, ScheduledDownload, SceneRequest
from ..utils import three_digit


class TestScene(TestCase):

    def setUp(self):
        self.scene = Scene.objects.create(
            path='001',
            row='001',
            sat='L8',
            date=date(2015, 1, 1),
            name='LC80010012015001LGN00',
            cloud_rate=20.3,
            status='downloading'
            )

        self.l7 = Scene.objects.create(
            path='227',
            row='059',
            sat='L7',
            date=date(2015, 6, 3),
            name='LE72270592015154CUB00',
            cloud_rate=20.3,
            status='downloading'
            )

        self.l5 = Scene.objects.create(
            path='227',
            row='059',
            sat='L5',
            date=date(2011, 10, 22),
            name='LT52270592011295CUB01',
            cloud_rate=20.3,
            status='downloading'
            )

    def test_creation(self):
        self.assertEqual(self.scene.__str__(), 'L8 001-001 01/01/15')
        self.assertEqual(self.scene.day(), '001')
        self.assertEqual(self.scene.dir(),
            join(settings.MEDIA_ROOT, 'L8/LC80010012015001LGN00'))
        self.scene.status = 'downloaded'
        self.scene.save()
        self.assertEqual(self.scene.status, 'downloaded')

        Scene.objects.create(
            path='001',
            row='001',
            sat='L8',
            date=date(2015, 1, 17),
            name='LC80010012015017LGN00',
            status='downloading'
            )

        self.assertEqual(Scene.objects.all().count(), 4)

    def test_quicklook(self):
        self.assertEqual(self.scene.quicklook(),
            'http://earthexplorer.usgs.gov/browse/landsat_8/2015/001/001/LC80010012015001LGN00.jpg'
        )
        self.assertEqual(self.l7.quicklook(),
            'http://earthexplorer.usgs.gov/browse/etm/227/59/2015/LE72270592015154CUB00_REFL.jpg'
        )
        self.assertEqual(self.l5.quicklook(),
            'http://earthexplorer.usgs.gov/browse/tm/227/59/2011/LT52270592011295CUB01_REFL.jpg'
        )

    def test_validation(self):
        with self.assertRaises(ValidationError):
            Scene.objects.create(
                path='001',
                row='001',
                sat='L8',
                date=date(2015, 1, 1),
                name='LC80010012015001LGN00',
                status='downloading'
                )

        with self.assertRaises(ValidationError):
            Scene.objects.create(
                path='001',
                row='001',
                sat='L8',
                date=date(2015, 1, 1),
                name='LC80010012015001LGN00_123',
                status='downloading'
                )


class TestImage(TestCase):

    def setUp(self):
        self.scene = Scene.objects.create(
            path='001',
            row='001',
            sat='L8',
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

        self.image_folder = join(settings.MEDIA_ROOT, 'L8/LC80010012015001LGN00')
        makedirs(self.image_folder)
        f = open(join(self.image_folder, 'LC80010012015001LGN00_B4.TIF'), 'w')
        f.close()

    def test_creation(self):
        self.assertEqual(self.image.__str__(), 'LC80010012015001LGN00_B4.TIF')
        self.assertEqual(self.image.file_path(),
            join(settings.MEDIA_ROOT, 'L8/LC80010012015001LGN00/LC80010012015001LGN00_B4.TIF')
            )
        self.assertTrue(self.image.file_exists())
        self.assertEqual(self.image.url(),
            join(settings.MEDIA_URL, 'L8/LC80010012015001LGN00/LC80010012015001LGN00_B4.TIF')
            )

        Image.objects.create(
            name='LC80010012015001LGN00_B5.TIF',
            type='B5',
            scene=self.scene
            )

        self.assertEqual(Image.objects.all().count(), 2)
        self.assertEqual(self.scene.images.count(), 2)

    def test_validation(self):
        with self.assertRaises(ValidationError):
            Image.objects.create(
                name='LC80010012015001LGN00_B4.TIF',
                type='B4',
                scene=self.scene
                )

    def test_delete_with_post_delete(self):
        self.image.delete()
        self.assertEqual(Image.objects.all().count(), 0)
        self.assertFalse(isfile(self.image.file_path()))

    def tearDown(self):
        rmtree(self.image_folder)


class TestScheduledDownload(TestCase):

    def setUp(self):
        self.sd = ScheduledDownload.objects.create(path='220', row='066')
        self.sd2 = ScheduledDownload.objects.create(path='999', row='002')

        self.scene = Scene.objects.create(
            path='220',
            row='066',
            sat='L8',
            date=date(2015, 1, 1),
            name='LC82200662015001LGN00',
            cloud_rate=20.3,
            status='downloading'
            )

    def test_creation(self):
        self.assertEqual(self.sd.__str__(), 'L8 220-066')
        self.assertEqual(ScheduledDownload.objects.all().count(), 2)

    def test_validation(self):
        with self.assertRaises(ValidationError):
            ScheduledDownload.objects.create(path='220', row='066')

    def test_last_scene(self):
        self.assertEqual(self.sd.last_scene(), self.scene)
        self.assertIsNone(self.sd2.last_scene())

    def test_has_new_scene(self):
        self.assertEqual(self.sd.has_new_scene(), True)

        day_number = three_digit(date.today().timetuple().tm_yday)
        Scene.objects.create(
            path='220',
            row='066',
            sat='L8',
            date=date.today(),
            name='LC82200662015%sLGN00' % day_number,
            cloud_rate=20.3,
            status='downloading'
        )

        self.assertEqual(self.sd.has_new_scene(), False)
        self.assertEqual(self.sd.last_scene().name,
            'LC82200662015%sLGN00' % day_number)

        self.assertEqual(self.sd2.has_new_scene(), True)

    def test_next_scene_name(self):
        self.assertEqual(self.sd.next_scene_name(), 'LC82200662015017LGN00')
        year = date.today().year
        day = three_digit(date.today().timetuple().tm_yday)
        self.assertEqual(
            self.sd2.next_scene_name(),
            'LC8999002%s%sLGN00' % (year, day)
        )

    def test_create_scene(self):
        scene = self.sd.create_scene()[0]
        self.assertIsInstance(scene, Scene)
        self.assertEqual(scene.path, '220')
        self.assertEqual(scene.row, '066')
        self.assertEqual(scene.date, date(2015, 1, 17))
        self.assertEqual(scene.sat, 'L8')

    def test_create_image(self):
        self.sd.create_scene()
        image = self.sd.create_image('LC82200662015017LGN00_BQA.TIF')[0]
        self.assertIsInstance(image, Image)
        self.assertEqual(image.type, 'BQA')
        self.assertEqual(image.scene.name, 'LC82200662015017LGN00')

    def test_download(self):
        downloaded = self.sd.download_new_scene([10, 11])
        self.assertEqual(len(downloaded), 2)

        scene = Scene.objects.get(name='LC82200662015017LGN00')
        self.assertIsInstance(scene, Scene)
        bounds = Polygon(((-45.4508, -7.62855), (-43.75824, -7.98923),
            (-44.12919, -9.73044), (-45.82968, -9.36601), (-45.4508, -7.62855)))
        self.assertEqual(scene.cloud_rate, 65.28)
        self.assertEqual(scene.geom, bounds)
        self.assertEqual(scene.status, 'downloading')

        self.assertIsInstance(Image.objects.get(name='LC82200662015017LGN00_B10.TIF'),
        Image)
        self.assertIsInstance(Image.objects.get(name='LC82200662015017LGN00_B11.TIF'),
        Image)

        self.assertEqual(self.sd.check_last_scene([10, 11]), [])
        self.assertEqual(self.sd.last_scene().status, 'downloaded')

        downloaded = self.sd.check_last_scene([10, 11, 'BQA'])
        self.assertEqual(len(downloaded), 3)
        self.assertIsInstance(Image.objects.get(name='LC82200662015017LGN00_BQA.TIF'),
        Image)
        rmtree(downloaded[2][0].replace('/LC82200662015017LGN00_BQA.TIF', ''))

        self.assertEqual(self.sd2.download_new_scene(['BQA']), [])


class TestSceneRequest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'i@t.com', 'password')
        self.scene_request = SceneRequest.objects.create(
                scene_name='LC82270592015001CUB00',
                user=self.user
            )

    def test_past_scene_creation(self):

        self.assertEqual(SceneRequest.objects.count(), 1)
        self.assertEqual(self.scene_request.status, 'pending')

        with self.assertRaises(ValidationError):
            SceneRequest.objects.create(
                scene_name='LC82270592015001CUB00',
                user=self.user
            )
        self.assertEqual(SceneRequest.objects.count(), 1)

    def test_scene_url_method(self):
        self.assertEqual(self.scene_request.scene_url(), None)

        # mock scene_request download
        scene = Scene.objects.create(
            path='227',
            row='059',
            sat='L8',
            date=date(2015, 1, 1),
            name='LC82270592015001CUB00',
            cloud_rate=20.3,
            status='downloading'
        )
        self.scene_request.status = 'downloaded'
        self.scene_request.save()
        #test scene_url method
        self.assertEqual(
            self.scene_request.scene_url(),
            reverse('imagery:scene', args=[scene.name])
        )