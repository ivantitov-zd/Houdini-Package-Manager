# coding: utf-8

from __future__ import print_function

import os
from operator import itemgetter

from .package import packageScore


def dirPackageScore(path):
    return packageScore(os.listdir(path))


def findPackageRootPath(path):
    paths = []
    scores = []
    for root, folders, files in os.walk(path):
        score = dirPackageScore(root)
        if score > 0:
            paths.append(root)
            scores.append(score)
    if not paths:
        raise FileNotFoundError('No package found')
    return sorted(zip(paths, scores), key=itemgetter(1))[-1][0]


def findDigitalAssetsRoots(package_root_path):
    paths = []
    for root, folders, files in os.walk(package_root_path):
        if root.lower() == os.path.join(package_root_path, 'otls').lower():
            continue

        if os.path.basename(root) == 'backup':
            continue

        for file in files:
            if file.endswith(('.otl', '.otlnc', '.otllc',
                              '.hda', '.hdanc', '.hdalc')):
                paths.append(root)
                break
    return tuple(paths)


def makeSetupSchema(path):
    try:
        package_root_path = findPackageRootPath(path)
    except FileNotFoundError:
        return
    package_root = package_root_path.replace(path, '').strip('\\/').replace('\\', '/')
    hda_roots = map(lambda p: p.replace(package_root_path, '').strip('\\/').replace('\\', '/'),
                    findDigitalAssetsRoots(package_root_path))
    schema = {'root': package_root,
              'hda_roots': tuple(hda_roots)}
    return schema
