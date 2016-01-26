# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import sys

DEBUG = False


class CMDLineExit(Exception):
    pass


def info(message):
    print(message)


def error(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def debug(message):
    if DEBUG:
        print(message)
