#!/usr/bin/env python
from datetime import date

from django.test import TestCase
from imagery.tasks import find_last_scene



class TestFindLastScene(TestCase):

    def test_find_last_scene(self):
        last_scene = 'LC82320582016072LGN00'
        path = 232
        row = 58
        min_date = date(year=2016, month=3, day=12)
        max_date = date(year=2016, month=3, day=14)
        scene_name = find_last_scene(path, row, min_date, max_date, 'LC8', 'LGN00')
        self.assertEqual(scene_name, last_scene)
