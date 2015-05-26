from django.test import TestCase, Client
from django.core.urlresolvers import reverse

client = Client()


class TestIndexView(TestCase):

    def test_scene_list_response(self):
        response = client.get(reverse('imagery:index'))
        self.assertEqual(response.status_code, 200)