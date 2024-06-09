import hou


HOUDINI_COMMERCIAL_LICENSE = hou.licenseCategoryType.Commercial
HOUDINI_INDIE_LICENSE = hou.licenseCategoryType.Indie
HOUDINI_EDUCATION_LICENSE = hou.licenseCategoryType.Education
HOUDINI_APPRENTICE_LICENSE = hou.licenseCategoryType.Apprentice


def houdini_license_from_name(name: str) -> hou.licenseCategoryType:
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


def full_houdini_license_name(name_or_lic: str | hou.licenseCategoryType) -> str | None:
    if isinstance(name_or_lic, str):
        lic = houdini_license_from_name(name_or_lic)
    elif isinstance(name_or_lic, hou.licenseCategoryType):
        lic = name_or_lic
    else:
        return None
    return {
        HOUDINI_COMMERCIAL_LICENSE: 'Commercial',
        HOUDINI_INDIE_LICENSE: 'Indie',
        HOUDINI_EDUCATION_LICENSE: 'Education',
        HOUDINI_APPRENTICE_LICENSE: 'Apprentice',
    }.get(lic)
