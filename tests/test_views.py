from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from ..models import Scene, SceneRequest

client = Client()


class TestIndexView(TestCase):

    def test_index_response(self):
        response = client.get(reverse('imagery:index'))
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


class TestLoginLogoutView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'i@t.com', 'password')

    def test_loggin_response(self):
        response = client.get(reverse('imagery:login'))
        self.assertEqual(response.status_code, 200)

    def test_loggout_response(self):
        response = client.get(reverse('imagery:logout'))
        self.assertRedirects(response, reverse('imagery:index'))


class TestSceneRequestView(TestCase):

    def setUp(self):
        Scene.objects.create(
            path='227',
            row='059',
            sat='L7',
            date=date(2015, 6, 3),
            name='LE72270592015154CUB00',
            cloud_rate=20.3,
            status='downloading'
        )
        self.user = User.objects.create_user('user', 'i@t.com', 'password')

    def test_unlogged_response(self):
        response = self.client.get(reverse('imagery:scene-request'))
        self.assertRedirects(response, '/login/?next=/scene-request/')

    def test_logged_response(self):
        response = self.client.post(
            reverse('imagery:scene-request'),
            {'scene_name': 'LC80010012015001LGN00'}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse('imagery:login'),
            {'username': self.user.username, 'password': 'password'}
        )
        self.assertIn('_auth_user_id', self.client.session)

        response = self.client.post(
            reverse('imagery:scene-request'),
            {'scene_name': 'LC80010012015001LGN00'}
        )
        self.assertEqual(response.status_code, 200)

        # test uniqueness validation
        response = self.client.post(
            reverse('imagery:scene-request'),
            {'scene_name': 'LC80010012015001LGN00'}
        )
        # test validation of scene_name field
        response = self.client.post(
            reverse('imagery:scene-request'),
            {'scene_name': 'LE72270592015154CUB00'}
        )
        self.assertEqual(SceneRequest.objects.count(), 1)
