# -*- coding: utf-8 -*-
from pyquery import PyQuery
from lc8_download import lc8

from os.path import join, isfile
from datetime import date, timedelta

from django.conf import settings


def get_metadata_code(scene_name):
    if scene_name[2] == '5':
        return '3119'
    elif scene_name[2] == '7':
        if int(scene_name[9:13]) < 2004:
            return '3372'
        else:
            return '3373'
    elif scene_name[2] == '8':
        return '4923'


def three_digit(number):
    """ Add left zeros to numbers with less than 3 digits.
    For example: 1 --> '001' | 02 --> '020' | st --> '0st'
    """
    number = str(number)
    if len(number) == 1:
        return '00%s' % number
    elif len(number) == 2:
        return '0%s' % number
    else:
        return number


def calendar_date(year, day):
    """Receive a year and a julian day number and return the calendar date."""
    return date(int(year), 1, 1) + timedelta(int(day) - 1)


def download(scene_name, bands, path=None):
    """Call the lc8_download library to download Landsat 8 imagery."""
    if path is None:
        path = join(settings.MEDIA_ROOT, get_sat_code(scene_name))
    scene = lc8.Downloader(scene_name)
    return scene.download(bands, path, metadata=True)


def get_cloud_rate(scene_name):
    """Read the MTL file and return the cloud_rate of the scene."""
    sat = 'L%s' % scene_name[2]
    mtl_path = join(settings.MEDIA_ROOT, sat, scene_name, scene_name + '_MTL.txt')

    if isfile(mtl_path):
        with open(mtl_path, 'r') as f:
            lines = f.readlines()
            cloud_rate = [float(line.split(' = ')[-1]) for line in lines if 'CLOUD_COVER' in line][0]
            return cloud_rate
    else:
        url_code = get_metadata_code(scene_name)
        metadata = PyQuery(
            'http://earthexplorer.usgs.gov/metadata/%s/%s/' % (url_code, scene_name)
        )
        metadata = metadata.text()[metadata.text().find('Cloud Cover '):]
        return float(metadata.split(' ')[2])


def get_bounds(scene_name):
    """Use Earth Explorer metadata to get bounds of a Scene"""
    url_code = get_metadata_code(scene_name)

    metadata = PyQuery(
        'http://earthexplorer.usgs.gov/fgdc/%s/%s/' % (url_code, scene_name)
        )
    metadata = metadata.text()[
        metadata.text().find('G-Ring_Latitude:'):
        metadata.text().find('\n  Keywords:')]
    coords = metadata.replace(' ', '') \
                .replace('G-Ring_Latitude:', '') \
                .replace('G-Ring_Longitude:', '')\
                .split('\n')
    coords = [float(coord) for coord in coords if coord != '']
    # create a list of lists with the coordinates
    coords = [coords[i:i + 2] for i in range(0, len(coords), 2)]
    # use reverse() to change [lat, lon] to [lon, lat]
    [coord.reverse() for coord in coords]
    # repeat the first coordinate on the end of the list
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords


def get_sat_code(scene_name):
    """Return the code of the satellite of the scene."""
    return 'L%s' % (scene_name[2])