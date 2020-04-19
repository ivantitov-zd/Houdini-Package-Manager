from .local_package import findInstalledPackages, LocalPackage
from . import github
from .update_dialog import UpdateDialog
from .web_package import WebPackage


def hasUpdate(package):
    if package.source_type == 'github':
        return github.repoHasUpdate(package.source, package.version, package.version_type)


def updatePackage(package):
    if package.source_type == 'github':
        github.installFromRepo(package, update=True)


def checkForUpdates():
    dialog = UpdateDialog()
    packages = []
    for package in findInstalledPackages():
        if package.source and package.source_type and package.version:
            if hasUpdate(package):
                packages.append(package)
    if packages:
        update, flags = dialog.getUpdateFlags(packages)
        if update:
            for package in packages:
                if not flags.get(package):
                    updatePackage(package)
