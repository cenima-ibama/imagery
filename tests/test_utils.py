# -*- coding: utf-8 -*-
from lc8_download.lc8 import DownloaderErrors

from datetime import date
from os.path import isfile
from shutil import rmtree

from django.test import TestCase
from django.core import mail

from ..utils import (three_digit, calendar_date, download, get_bounds,
    get_cloud_rate, get_sat_code, send_multipart_email)


class TestThreeDigit(TestCase):

    def test_conversion(self):
        self.assertEqual(three_digit(1), '001')
        self.assertEqual(three_digit(10), '010')


class TestCalendarDate(TestCase):

    def test_conversion(self):
        self.assertEqual(calendar_date('2015', '001'), date(2015, 1, 1))
        self.assertEqual(calendar_date('2015', '032'), date(2015, 2, 1))


class TestDownload(TestCase):

    def test_download(self):
        with self.assertRaises(DownloaderErrors):
            download('LC80010012015367LGN00', [11], 'imagery/tests/')

        download('LC80030172015001LGN00', [11], 'imagery/tests/')

        self.assertTrue(isfile('imagery/tests/LC80030172015001LGN00/' +
            'LC80030172015001LGN00_B11.TIF'))

    def tearDown(self):
        rmtree('imagery/tests/LC80030172015001LGN00/')


class TestGetCloudRate(TestCase):

    def test_get_cloud_rate(self):
        self.assertEqual(get_cloud_rate('LC80020662015186LGN00'), 87.58)
        self.assertEqual(get_cloud_rate('LE72270592015154CUB00'), 42.04)
        self.assertEqual(get_cloud_rate('LE72300692003142EDC00'), 7.84)
        self.assertEqual(get_cloud_rate('LT52270592011295CUB01'), 92.02)


class TestGetBounds(TestCase):

    def test_L5_bounds(self):
        coords = [
            [-54.10077, 2.36342],
            [-52.45473, 2.12404],
            [-52.79384, 0.53251],
            [-54.43875, 0.77173],
            [-54.10077, 2.36342]
            ]
        self.assertEqual(get_bounds('LT52270592011295CUB01'), coords)

    def test_L7_bounds_2004_present(self):
        coords = [
            [-54.1274, 2.37448],
            [-52.43042, 2.12839],
            [-52.77428, 0.51088],
            [-54.47061, 0.75688],
            [-54.1274, 2.37448]
            ]
        self.assertEqual(get_bounds('LE72270592015154CUB00'), coords)

    def test_L7_bounds_until_2003(self):
        coords = [
            [-61.9403, -12.0854],
            [-60.1977, -12.3374],
            [-60.551, -13.9749],
            [-62.3059, -13.721],
            [-61.9403, -12.0854],
            ]
        self.assertEqual(get_bounds('LE72300692003142EDC00'), coords)


class TestGetSatCode(TestCase):

    def test_get_sat_code(self):
        self.assertEqual(get_sat_code('LC80020662015186LGN00'), 'L8')
        self.assertEqual(get_sat_code('LO80020662015186LGN00'), 'L8')
        self.assertEqual(get_sat_code('LE72300692003142EDC00'), 'L7')
        self.assertEqual(get_sat_code('LT52300692003142CUB00'), 'L5')


class TestSendEmail(TestCase):

    def test_send_email(self):
        send_multipart_email('test', '404.html', 'sender@m.com', 'dest@m.com')
        self.assertEqual(len(mail.outbox), 1)