from datetime import date

from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from ..models import Scene

client = Client()


class TestIndexView(TestCase):

    def test_index_response(self):
        response = client.get(reverse('imagery:index'))
        self.assertEqual(response.status_code, 200)


class TestSearchView(TestCase):

    def test_search_response(self):
        response = client.get(reverse('imagery:search'))
        self.assertEqual(response.status_code, 200)


class TestSceneDetailView(TestCase):

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

    def test_scene_detail_response(self):
        response = client.get(reverse('imagery:scene', args=[self.scene.name]))
        self.assertEqual(response.status_code, 200)


class TestCloudRateView(TestCase):

    def test_cloud_rate_view(self):
        response = client.get(reverse('imagery:cloud-rate'))
        self.assertEqual(response.status_code, 200)