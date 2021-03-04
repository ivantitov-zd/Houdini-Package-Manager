# coding: utf-8

from __future__ import print_function

import hou

HOUDINI_COMMERCIAL_LICENSE = hou.licenseCategoryType.Commercial
HOUDINI_INDIE_LICENSE = hou.licenseCategoryType.Indie
HOUDINI_EDUCATION_LICENSE = hou.licenseCategoryType.Education
HOUDINI_APPRENTICE_LICENSE = hou.licenseCategoryType.Apprentice


def houdiniLicenseFromName(name):
    name = name.lower()

    if name.startswith(('com', 'full', 'fx', 'core')):
        return HOUDINI_COMMERCIAL_LICENSE

    if name.startswith(('indie', 'lim')):
        return HOUDINI_INDIE_LICENSE

    if name.startswith('edu'):
        return HOUDINI_EDUCATION_LICENSE

    if name.startswith(('app', 'non')):
        return HOUDINI_APPRENTICE_LICENSE

    raise ValueError('Invalid license name')


def fullHoudiniLicenseName(name_or_lic):
    if isinstance(name_or_lic, basestring):
        lic = houdiniLicenseFromName(name_or_lic)
    elif isinstance(name_or_lic, hou.licenseCategoryType):
        lic = name_or_lic
    else:
        return None
    return {
        HOUDINI_COMMERCIAL_LICENSE: u'Commercial',
        HOUDINI_INDIE_LICENSE: u'Indie',
        HOUDINI_EDUCATION_LICENSE: u'Education',
        HOUDINI_APPRENTICE_LICENSE: u'Apprentice'
    }.get(lic)
