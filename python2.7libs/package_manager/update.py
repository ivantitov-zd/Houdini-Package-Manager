import json

from .local_package import findInstalledPackages, LocalPackage
from . import github
from .update_dialog import UpdateDialog
from .web_package import WebPackage
from .update_options import UpdateOptions


def hasUpdate(package):
    only_stable = UpdateOptions().onlyStableForPackage(package)
    if package.source_type == 'github':
        return github.repoHasUpdate(package.source, package.version, package.version_type, only_stable)


def updatePackage(package):
    only_stable = UpdateOptions().onlyStableForPackage(package)
    if package.source_type == 'github':
        github.installFromRepo(package, update=True, only_stable=only_stable)


def checkForUpdates(ignore_options=False):
    packages = []
    for package in findInstalledPackages():
        if not package.source or not package.source_type or not package.version:
            continue

        if not package.author or not package.name:
            continue

        if not ignore_options and not UpdateOptions().checkOnStartupForPackage(package):
            continue

        if hasUpdate(package):
            packages.append(package)

    if packages:
        dialog = UpdateDialog()
        update, checked = dialog.getUpdateFlags(packages)
        if update:
            for package in packages:
                if package in checked:
                    updatePackage(package)
