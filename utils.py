# -*- coding: utf-8 -*-
from os.path import join, expanduser

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
    """Call the lc8_download library to download Landsat 8 imagery."""
    scene = lc8.Downloader(scene_name)
    if path is None:
        return scene.download(bands, metadata=True)
    else:
        return scene.download(bands, path, metadata=True)


def bounds_and_clouds(scene_name):
    """Read the MTL file of the scene and return a list with the bounds
    coordinates of the Scene and the cloud_rate
    """

    mtl_path = join(expanduser('~'), 'landsat', scene_name, scene_name + '_MTL.txt')
    with open(mtl_path, 'r') as f:
        lines = f.readlines()
        lons = [float(line.split(' = ')[-1]) for line in lines if 'LON_PRODUCT' in line]
        lats = [float(line.split(' = ')[-1]) for line in lines if 'LAT_PRODUCT' in line]
        coords = list(zip(lons, lats))
        # repeat the first coordinate on the end to close Polygon
        coords.append(coords[0])
        cloud_rate = [float(line.split(' = ')[-1]) for line in lines if 'CLOUD_COVER' in line][0]
        return [coords, cloud_rate]