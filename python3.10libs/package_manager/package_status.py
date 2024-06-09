DEVELOPMENT = 0
PROTOTYPE = 1
ALPHA = 2
BETA = 3
STABLE = 4


def package_status_from_name(name: str) -> int:
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


def full_package_status_name(name_or_status: str | int) -> str | None:
    if isinstance(name_or_status, str):
        status = package_status_from_name(name_or_status)
    else:  # isinstance(name_or_lic, int):
        status = name_or_status
    return {
        DEVELOPMENT: 'Development',
        PROTOTYPE: 'Prototype',
        ALPHA: 'Alpha',
        BETA: 'Beta',
        STABLE: 'Stable',
    }.get(status)
