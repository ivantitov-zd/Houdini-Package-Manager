from typing import Collection


class Package:
    source: str
    content_path: str | None


def packageScore(items: Collection[str]) -> int:
    XML_NAMES = ('AnimationEditorDopesheetContextMenu',
                 'AnimationEditorDopesheetMenu',
                 'AnimationEditorGraphContextMenu',
                 'AnimationEditorGraphMenu',
                 'AnimationEditorMenu',
                 'AnimationEditorTableContextMenu',
                 'AnimationEditorTableMenu',
                 'ChannelListMenu',
                 'CHGmenu',
                 'DesktopsMenu',
                 'ExampleMenu',
                 'GEOclassicXlate',
                 'KeyframesMenu',
                 'MainMenuARecord',
                 'MainMenuCommon',
                 'MainMenuEscape',
                 'MainMenuGPlay',
                 'MainMenuHKey',
                 'MainMenuHOTLView',
                 'MainMenuMaster',
                 'MainMenuMPlay',
                 'MainMenuPDG',
                 'MotionEffectsMenu',
                 'NetworkViewMenu',
                 'NetworkViewMenuPDG',
                 'NetworkViewMenuTOP',
                 'OPmenu',
                 'PaneTabTypeMenu',
                 'PaneTabTypeMenuPDG',
                 'ParmGearMenu',
                 'PARMmenu',
                 'PlaybarMenu',
                 'ShelfMenu',
                 'ShelfSetMenu',
                 'ShelfSetPlusMenu',
                 'ShelfToolMenu',
                 'TakeListMenu',
                 'UsdStagePrimMenu',
                 'VOPFXmenu')
    scores = 0
    if 'bin' in items:
        scores += 1
    if 'config' in items:
        scores += 1
    if 'presets' in items:
        scores += 1
    if 'desktop' in items:
        scores += 1
    if 'packages' in items:
        scores += 1
    if 'radialmenu' in items:
        scores += 2
    if 'dso' in items:
        scores += 1
    if 'inlinecpp' in items:
        scores += 1
    if 'otls' in items:
        scores += 2
    if 'help' in items:
        scores += 1
    if 'python_panels' in items:
        scores += 2
    if 'scripts' in items:
        scores += 1
    if 'toolbar' in items:
        scores += 1
    if 'ocl' in items:
        scores += 1
    if 'vex' in items:
        scores += 2
    if 'vop' in items:
        scores += 2
    if 'python2.7libs' in items:
        scores += 1
    if 'python3.7libs' in items:
        scores += 1
    if 'viewer_states' in items:
        scores += 2
    for item in items:
        if item.endswith('.xml') and item.split('.')[0] in XML_NAMES:
            scores += 2
    if 'OPcustomize' in items:
        scores += 2
    if 'Expressions.txt' in items:
        scores += 1
    if 'VEXpressions.txt' in items:
        scores += 2
    if 'PythonScripts.txt' in items:
        scores += 1
    return scores


def isPackage(items: Collection[str], threshold: int = 2) -> bool:
    return packageScore(items) >= threshold
