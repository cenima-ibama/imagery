# -*- coding: utf-8 -*-
from pyquery import PyQuery
from lc8_download import lc8

from os.path import join, expanduser
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


def get_cloud_rate(scene_name):
    """Read the MTL file of the scene and return the cloud_rate of the scene
    """

    mtl_path = join(expanduser('~'), 'landsat', scene_name, scene_name + '_MTL.txt')
    with open(mtl_path, 'r') as f:
        lines = f.readlines()
        cloud_rate = [float(line.split(' = ')[-1]) for line in lines if 'CLOUD_COVER' in line][0]
        return cloud_rate


def get_bounds(scene_name):
    """Use the Earth Explorer metadata to get bounds of the Scene"""
    metadata = PyQuery('http://earthexplorer.usgs.gov/fgdc/4923/%s/' % scene_name)
    metadata = metadata.text()[
        metadata.text().find('G-Ring_Latitude:'):
        metadata.text().find('\n  Keywords:')]
    coords = metadata.replace(' ', '') \
                .replace('G-Ring_Latitude:', '') \
                .replace('G-Ring_Longitude:', '')\
                .split('\n')
    coords = [float(coord) for coord in coords if coord != '']
    coords = [coords[i:i + 2] for i in range(0, len(coords), 2)]
    [coord.reverse() for coord in coords]
    coords.append(coords[0])
    return coords