DEVELOPMENT = 0
PROTOTYPE = 1
ALPHA = 2
BETA = 3
STABLE = 4


def packageStatusFromName(name: str) -> int:
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


def fullPackageStatusName(name_or_status: str | int) -> str | None:
    if isinstance(name_or_status, str):
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
