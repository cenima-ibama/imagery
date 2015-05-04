# -*- coding: utf-8 -*-
from lc8_download import lc8

from datetime import date, timedelta


def three_digit(number):
    """ Add 0s to inputs that their length is less than 3.
    For example: 1 --> 001 | 02 --> 020 | st --> 0st
    """
    number = str(number)
    if len(number) == 1:
        return '00%s' % number
    elif len(number) == 2:
        return '0%s' % number
    else:
        return number


def calendar_date(year, day):
    """Receive a year and the number of the day in the year and return the
    calendar date.
    """
    return date(int(year), 1, 1) + timedelta(int(day) - 1)


def download(scene_name, bands, path=None):
    scene = lc8.Downloader(scene_name)
    if path is None:
        return scene.download(bands, metadata=True)
    else:
        return scene.download(bands, path, metadata=True)
