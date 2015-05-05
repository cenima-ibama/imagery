# -*- coding: utf-8 -*-
from lc8_download.lc8 import RemoteFileDoesntExist

from datetime import date
from os.path import isfile
from shutil import rmtree

from django.test import TestCase

from ..utils import three_digit, calendar_date, download


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
        with self.assertRaises(RemoteFileDoesntExist):
            download('LC80010012015367LGN00', [11], 'imagery/tests/')

        download('LC80030172015001LGN00', [11], 'imagery/tests/')

        self.assertTrue(isfile('imagery/tests/LC80030172015001LGN00/' +
            'LC80030172015001LGN00_B11.TIF'))

    def tearDown(self):
        rmtree('imagery/tests/LC80030172015001LGN00/')