import math
import os


def truncate_mid(value: str, length: int) -> str:
    if len(value) <= length:
        return value

    if length <= 0:
        return ''

    if length == 1:
        return '…'

    mid = (length - 1) / 2
    pre = value[:int(mid)]
    post = value[int(len(value) - math.ceil(mid)):]

    return f'{pre}…{post}'


def truncate_path(path: str, length: int) -> str:
    if len(path) <= length:
        return path

    if length <= 0:
        return ''

    if length == 1:
        return '…'

    last_separator = path.rfind('/')

    if last_separator == -1:
        return truncate_mid(path, length)

    filename_length = len(path) - last_separator - 1

    if filename_length + 2 > length:
        return truncate_mid(path, length)

    pre = path[:length - filename_length - 2]
    post = path[last_separator:]

    return f'{pre}…{post}'


def prepare_path(path: str, length: int) -> str:
    return truncate_path(os.path.normpath(path).replace('\\', '/'), length)
