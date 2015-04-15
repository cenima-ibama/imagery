# -*- coding: utf-8 -*-
from datetime import date

from django.test import TestCase

from ..models import Scene


class TestScene(TestCase):

    def test_creation(self):
        scene = Scene.objects.create(
            path='001',
            row='001',
            sat='LC8',
            date=date(2015, 1, 1),
            cloud_rate=20.3,
            status='downloading'
            )

        self.assertEqual(scene.__str__(), 'LC8 001-001 01/01/15')

        Scene.objects.create(
            path='001',
            row='002',
            sat='LC8',
            date=date(2015, 1, 1),
            status='downloading'
            )

        self.assertEqual(Scene.objects.all().count(), 2)
