from __future__ import print_function

DEVELOPMENT = 0
PROTOTYPE = 1
ALPHA = 2
BETA = 3
STABLE = 4


def packageStatusFromName(name):
    name = name.lower()

    if name.startswith('dev'):
        return DEVELOPMENT

    if name.startswith('prot'):
        return PROTOTYPE

    if name.startswith('a'):
        return ALPHA

    if name.startswith('b'):
        return BETA

    if name.startswith('stab'):
        return STABLE

    raise ValueError('Invalid status name')


def fullPackageStatusName(name_or_status):
    if isinstance(name_or_status, basestring):
        status = packageStatusFromName(name_or_status)
    else:  # isinstance(name_or_lic, int):
        status = name_or_status
    return {
        DEVELOPMENT: u'Development',
        PROTOTYPE: u'Prototype',
        ALPHA: u'Alpha',
        BETA: u'Beta',
        STABLE: u'Stable'
    }.get(status)
