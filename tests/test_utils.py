# -*- coding: utf-8 -*-
from django.test import TestCase

from ..utils import three_digit


class TestThreeDigit(TestCase):

    def test_conversion(self):
        self.assertEqual(three_digit(1), '001')
        self.assertEqual(three_digit(10), '010')
