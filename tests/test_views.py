from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from ..models import Scene, PastSceneDownload

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

    def setUp (self):
        self.user = User.objects.create_user('user', 'i@t.com', 'password')

    def test_loggin_response(self):
        response = client.get(reverse('imagery:login'))
        self.assertEqual(response.status_code, 200)

    def test_loggout_response(self):
        response = client.get(reverse('imagery:logout'))
        self.assertRedirects(response, reverse('imagery:index'))

class TestSchedulingView(TestCase):

    def setUp (self):
        self.scene = 'LC80010012015001LGN00'
        self.user = User.objects.create_user('user', 'i@t.com', 'password')

    def test_unlogged_response(self):
        response = self.client.get(reverse('imagery:scheduling'))
        self.assertRedirects(response, '/login/?next=/scheduling/')

    def test_logged_response(self):
        response = self.client.post(reverse('imagery:scheduling'), {'scene' : self.scene})
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('imagery:login'), {'username' : self.user.username, 'password' : 'password'})
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.post(reverse('imagery:scheduling'), {'scene' : self.scene})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PastSceneDownload.objects.count(), 1)
