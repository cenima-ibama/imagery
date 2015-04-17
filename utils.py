# -*- coding: utf-8 -*-
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
    return date(int(year), 1, 1) + timedelta(int(day) -1)