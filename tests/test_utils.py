# -*- coding: utf-8 -*-
from datetime import date

from django.test import TestCase

from ..utils import three_digit, calendar_date


class TestThreeDigit(TestCase):

    def test_conversion(self):
        self.assertEqual(three_digit(1), '001')
        self.assertEqual(three_digit(10), '010')


class TestCalendarDate(TestCase):

    def test_conversion(self):
        self.assertEqual(calendar_date('2015', '001'), date(2015, 1, 1))
        self.assertEqual(calendar_date('2015', '032'), date(2015, 2, 1))
