# encoding: utf-8

from __future__ import print_function

import math
import os


def truncateMid(value, length):
    if len(value) <= length:
        return value

    if length <= 0:
        return ''

    if length == 1:
        return '…'

    mid = (length - 1) / 2
    pre = value[:int(mid)]
    post = value[int(len(value) - math.ceil(mid)):]

    return '{0}…{1}'.format(pre, post)


def truncatePath(path, length):
    if len(path) <= length:
        return path

    if length <= 0:
        return ''

    if length == 1:
        return '…'

    last_separator = path.rfind('/')

    if last_separator == -1:
        return truncateMid(path, length)

    filename_length = len(path) - last_separator - 1

    if filename_length + 2 > length:
        return truncateMid(path, length)

    pre = path[:length - filename_length - 2]
    post = path[last_separator:]

    return '{0}…{1}'.format(pre, post)


def preparePath(path, length):
    return truncatePath(os.path.normpath(path).replace('\\', '/'), length)
