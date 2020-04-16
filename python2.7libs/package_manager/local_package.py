import json
import os

import hou

from .houdini_license import fullHoudiniLicenseName
from .package_status import fullPackageStatusName


class NotPackageError(IOError):
    pass


class NotInstalledError(IOError):
    pass


class AlreadyInstalledError(IOError):
    pass


def isPackage(items, level=2):
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
    return scores >= level


def isPackageFolder(path):
    if not os.path.isdir(path):
        return None
    return isPackage(os.listdir(path))


def packageNameFromContent(content_path):
    setup_file_path = os.path.join(content_path, 'package.setup')
    name = None
    if os.path.isfile(setup_file_path):
        with open(setup_file_path) as file:
            data = json.load(file)
        name = data.get('name')
    if name is None:
        name = os.path.basename(content_path)
    return name


def findFiles(path, ignore_folders=True, recursive=False):
    for root, folders, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)
        if not ignore_folders:
            for folder in folders:
                yield os.path.join(root, folder)
        if not recursive:
            break


class LocalPackage:
    def __init__(self, package_file):
        self.package_file = os.path.normpath(package_file).replace('\\', '/')

        if not os.path.isfile(package_file):
            raise IOError('File "{0}" not found'.format(package_file))

        with open(package_file) as file:
            data = json.load(file)

        self.content_path = os.path.normpath(data['path']).replace('\\', '/')
        if not os.path.isdir(self.content_path):
            raise IOError(self.content_path)
        if not isPackageFolder(self.content_path):
            raise NotPackageError('Folder "{0}" is not a package'.format(self.content_path))

        setup_file = os.path.join(self.content_path, 'package.setup')
        if os.path.isfile(setup_file):
            with open(setup_file) as file:
                data = json.load(file)
        else:
            data = {}
        self.name = data.get(u'name') or os.path.basename(self.content_path)
        self.description = data.get(u'description')
        self.source = data.get(u'source')
        self.source_type = data.get(u'source_type')
        self.author = data.get(u'author')
        self.version = data.get(u'version')
        self.version_type = data.get(u'version_type')
        self.hversion = data.get(u'hversion')
        self.hlicense = fullHoudiniLicenseName(data.get(u'hlicense'))
        self.status = fullPackageStatusName(data.get(u'status'))

    def files(self, extensions, root='', ignore_folders=True, recursive=False):
        if not os.path.isdir(self.content_path):
            raise hou.ObjectWasDeleted

        path = os.path.join(self.content_path, root)
        if not os.path.isdir(path):
            return ()

        file_list = []
        for file in findFiles(path, ignore_folders, recursive):
            if file.endswith(extensions):
                file_path = os.path.join(path, file)
                file_list.append(file_path)
        return tuple(file_list)

    def libraries(self):
        return self.files(('.otl', '.otlnc', '.otllc',
                           '.hda', '.hdanc', '.hdalc'),
                          root='otls',
                          ignore_folders=False)

    def shelves(self):
        return self.files('.shelf', 'toolbar')

    def panels(self):
        return self.files('.pypanel', 'python_panels')

    def isInstalled(self):
        return os.path.isfile(self.package_file)

    def isEnabled(self):
        try:
            with open(self.package_file, 'r') as file:
                data = json.load(file, encoding='utf-8')
                return data.get(u'enable', True)
        except IOError:
            return False  # Todo: raise NotInstalledError?

    def enable(self, enable=True):
        # Todo: check if not installed
        with open(self.package_file, 'r') as file:
            data = json.load(file)
        with open(self.package_file, 'w') as file:
            data[u'enable'] = enable
            json.dump(data, file, indent=4, encoding='utf-8')

    @staticmethod
    def install(content_path, enable=True, force_overwrite=False):
        content_path = os.path.normpath(content_path).replace('\\', '/')
        if not os.path.isdir(content_path) or not isPackageFolder(content_path):
            raise NotPackageError('Folder is not a package')
        name = packageNameFromContent(content_path).replace(' ', '_')
        package_file = os.path.join(hou.expandString('$HOUDINI_USER_PREF_DIR/packages'),
                                    name + '.json')
        if not force_overwrite and os.path.isfile(package_file):
            raise AlreadyInstalledError('Package already installed')
        data = {
            u'enable': enable,
            u'path': content_path
        }
        with open(package_file, 'w') as file:
            json.dump(data, file, indent=4, encoding='utf-8')

    def uninstall(self):
        # Todo: optional remove package content folder
        os.remove(self.package_file)

    def __repr__(self):
        return 'Package(r"{0}")'.format(self.package_file)

    def __str__(self):
        return self.content_path


def findInstalledPackages():
    def jsonsFromFolderAlphabetical(path):
        if not os.path.isdir(path):
            return ()
        file_paths = []
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if file.endswith('.json') and os.path.isfile(file_path):
                file_paths.append(file_path)
        return sorted(file_paths)

    json_paths = []

    packages_path = hou.expandString('$HOUDINI_USER_PREF_DIR/packages')
    json_paths.extend(jsonsFromFolderAlphabetical(packages_path))

    packages_path = hou.expandString('$HFS/packages')
    json_paths.extend(jsonsFromFolderAlphabetical(packages_path))

    if hou.getenv('HSITE') is not None:
        major, minor, build = hou.applicationVersion()
        packages_path = hou.expandString('$HSITE/houdini{0}.{1}/packages'.format(major, minor))
        json_paths.extend(jsonsFromFolderAlphabetical(packages_path))

    if hou.getenv('HOUDINI_PACKAGE_DIR') is not None:
        packages_path = hou.expandString('$HOUDINI_PACKAGE_DIR')
        json_paths.extend(jsonsFromFolderAlphabetical(packages_path))

    # Todo: support dynamic setting of the package dir if possible

    return tuple(LocalPackage(path) for path in json_paths)
