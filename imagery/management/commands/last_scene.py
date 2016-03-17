# -*- coding: utf-8 -*-
import sys
import re
import logging

from datetime import date
from django.core.management.base import BaseCommand

from ...utils import calendar_date
from ...tasks import find_last_scene
from ...models import ScheduledDownload, Scene


logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)

PATH_ROW_SEPARATOR = '/'

class Command(BaseCommand):

    help = '''Find the last scene available for the path and row.
    The command will find recursively by scene name, if exist some scene
    in the defined period (min_date and max_date), and return the earliest scene
    '''

    def add_arguments(self, parser):
        '''Setting arguments of command '''
        parser.add_argument(
            'path_row',
            nargs='*',
            type=str,
            help='''path(s) and row(s) to search'''
        )

        parser.add_argument(
            '--min_date',
            '-s',
            dest='min_date',
            help='''Minimum date to search the scene.
                    Default value is 30 days later to current date'''
        )

        parser.add_argument(
            '--max_date',
            '-e',
            dest='max_date',
            help='''Maximum date to search the scene'''
        )

        parser.add_argument(
            '--prefix',
            '-p',
            dest='prefix',
            type=str,
            default='LC8',
            help='''Prefix in the scene name. E. g. LT5'''
        )

        parser.add_argument(
            '--sufix',
            '-x',
            dest='sufix',
            type=str,
            default='LGN00',
            help='''Sufix in the scene name. E. g. LGN00'''
        )

        parser.add_argument(
            '--schedule',
            '-d',
            dest='schedule',
            action='store_true',
            help='''Add the path(s) and row(s) on Scheduling to download from
            the date of earliest scene found'''
        )

        parser.add_argument(
            '--separator',
            '-t',
            dest='separator',
            type=str,
            default=PATH_ROW_SEPARATOR,
            help='''Character separator used between path and row'''
        )

        parser.add_argument(
            '--file',
            '-f',
            dest='file',
            metavar="FILE",
            help='''File with list of paths and rows'''
        )

        parser.add_argument(
            '--output',
            '-o',
            dest='output',
            metavar="FILE",
            help='''File to put scene names found'''
        )

    def handle(self, **options):
        '''Command execution '''

        scene_names = []

        paths_rows = options['path_row']
        min_date = options['min_date']
        max_date = options['max_date']
        prefix = options['prefix']
        sufix = options['sufix']
        sep = options['separator']
        schedule = options['schedule']
        output_file = options['output']
        ops_file = options['file']

        logger.info('Options:')

        if ops_file:
            paths_rows = self.get_from_file(ops_file, sep)

        if options['verbosity']:
            self.enable_verbose()

        #if not len(paths_rows):
        #    raise Exception('Paths and rows are invalid')

        logger.debug('Path and Rows: %s' % paths_rows)
        logger.info('Starting')

        if min_date:
            logger.debug('Parameter min_date: %s' % min_date)
            min_date = self.parse_date(min_date)

        if max_date:
            logger.debug('Param max_date: %s' % max_date)
            max_date = self.parse_date(max_date)

        for path_row in paths_rows:

            logger.debug('Searching path and row %s' % path_row)
            path_row = path_row.split(sep)
            scene_name = find_last_scene(
                path_row[0],
                path_row[1],
                min_date,
                max_date,
                prefix,
                sufix
            )

            if scene_name:
                logger.info('Scene found: %s' % scene_name)
                scene_names.append(scene_name)
            else:
                logger.info('Scene not found: %s' % scene_name)

        if schedule:
            self.schedule_downloads(scene_names)

        if output_file:
            self.output_file(output_file, scene_names)

    def parse_date(self, str_date):
        '''Parse the date argument and return a instance of 'date' '''
        result = None
        regex = re.compile('(\d{1,2})\/(\d{1,2})\/(\d{4})')
        matched = regex.match(str_date)
        if matched:
            result = date(
                int(matched.group(3)),
                int(matched.group(2)),
                int(matched.group(1))
            )
        else:
            raise Exception('Invalid date: %s. Must be in the format dd/mm/yyyy' % str_date)
        return result

    def enable_verbose(self):
        '''Enable to show logs on standard output'''
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    def schedule_downloads(self, scene_names):
        '''Schedule the downloads for scene names. Add (if not exists) a record
        of the ScheduledDownload model and of Scene model in database'''
        for scene_name in scene_names:
            logger.info('Scheduling scene: %s' % scene_name)
            path = scene_name[3:6]
            row = scene_name[6:9]
            logger.debug('Creating ScheduleDownload(path=%s, row=%s)' % (path, row))
            schedule = ScheduledDownload.objects.get_or_create(path=path, row=row)
            logger.debug('ScheduleDownload created')
            self.create_scene(path, row, scene_name)
            logger.info('Scheduling completed')

    def create_scene(self, path, row, name):
        """Get or Create a new Scene object for this path and row."""
        scene_date = calendar_date(name[9:13], name[13:16])
        logger.debug(
            'Creating Scene(path=%s, row=%s, sat=L8, name=%s, date=%s, status=created)'
            % (path, row, name, scene_date)
        )
        return Scene.objects.get_or_create(
            path=path,
            row=row,
            sat='L8',
            name=name,
            date=scene_date,
            status='created',
        )
        logger.debug('Scene created')

    def get_from_file(self, ops_file, sep):
        ''' '''
        path_rows = []
        regex = re.compile(r'(\d{1,3}%s\d{1,3})' % sep)
        logger.info('Loading from: %s' % ops_file)
        f = open(ops_file, 'r')
        lines = f.readlines()
        for line in lines:
            logger.debug('Loading Line: %s' % line)
            matched = regex.match(line)
            if not matched:
                continue
            path_row = matched.group(1)
            path_rows.append(path_row)
        return path_rows

    def output_file(self, output_file, scene_names):
        logger.info('Output in: %s' % output_file)
        f = open(output_file, 'w')
        for scene_name in scene_names:
            f.write(scene_name)
            f.write('\n')
        f.close()
