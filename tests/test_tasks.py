#!/usr/bin/env python
from datetime import date

from django.contrib.gis.geos import Polygon
from django.test import TestCase

from imagery.tasks import find_last_scene, validate_geometry_not_null
from imagery.models import Scene



class TestFindLastScene(TestCase):

    def test_find_last_scene(self):
        last_scene = 'LC82320582016072LGN00'
        path = 232
        row = 58
        min_date = date(year=2016, month=3, day=12)
        max_date = date(year=2016, month=3, day=14)
        scene_name = find_last_scene(path, row, min_date, max_date, 'LC8', 'LGN00')
        self.assertEqual(scene_name, last_scene)


class TestGeometryCreation(TestCase):

    def setUp(self):
        self.scene = Scene.objects.create(
            path='001',
            row='001',
            sat='L8',
            date=date(2015, 1, 2),
            name='LC80010012015002LGN00',
            cloud_rate=20.3,
            status='downloading',
            geom = Polygon(
                (
                    (-45.4508, -7.62855), (-43.75824, -7.98923),
                    (-44.12919, -9.73044), (-45.82968, -9.36601), 
                    (-45.4508, -7.62855)
                )
            )
        )

        self.scene2 = Scene.objects.create(
         path='001',
            row='001',
            sat='L8',
            date=date(2015, 1, 18),
            name='LC80010012015018LGN00',
            cloud_rate=20.3,
            status='downloading'
        )

        self.scene3 = Scene.objects.create(
            path='227',
            row='059',
            sat='L8',
            date=date(2015, 1, 1),
            name='LC82270592015001LGN00',
            cloud_rate=20.3,
            status='downloading'
        )

        self.scene4 = Scene.objects.create(
            path='227',
            row='059',
            sat='L8',
            date=date(2015, 1, 17),
            name='LC82270592015017LGN00',
            cloud_rate=20.3,
            status='downloading',
            geom = Polygon(
                (
                    (-41.4508, -8.62855), (-44.75824, -8.98923),
                    (-45.12919, -10.73044), (-46.82968, -10.36601), 
                    (-41.4508, -8.62855)
                )
            )

        )

        self.new_scene = Scene.objects.create(
            path='002',
            row='060',
            sat='L8',
            date=date(2015, 2, 21),
            name='LC80020602015052LGN00',
            cloud_rate=20.3,
            status='downloading',
        )


    def test_create_geometry(self):

        self.assertEqual(Scene.objects.filter(geom__isnull=False).count(), 2) # Not null Geom
        self.assertEqual(Scene.objects.filter(geom__isnull=True).count(), 3) # Null Geom

        validate_geometry_not_null(self)
        self.assertEqual(Scene.objects.filter(geom__isnull=True).count(), 1) # Null Geom

        self.new_scene = Scene.objects.create(
            path='002',
            row='060',
            sat='L8',
            date=date(2015, 2, 21),
            name='LC80020602015036LGN00',
            cloud_rate=20.3,
            status='downloading',
            geom = Polygon(
                (
                    (-41.4508, -8.62855), (-44.75824, -8.98923),
                    (-45.12919, -10.73044), (-46.82968, -10.36601), 
                    (-41.4508, -8.62855)
                )
            )
        )

        validate_geometry_not_null(self)
        self.assertEqual(Scene.objects.filter(geom__isnull=True).count(), 0) # Null Geom
        self.assertEqual(Scene.objects.filter(geom__isnull=False).count(), 6) # Not null Geom