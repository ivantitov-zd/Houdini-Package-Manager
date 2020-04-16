from .local_package import findInstalledPackages, LocalPackage
from . import github
from .new_version_dialog import NewVersionDialog


def checkForUpdates():
    dialog = NewVersionDialog()
    packages = []
    for package in findInstalledPackages():
        if package.source and package.source_type and package.version:
            if package.source_type == 'github':
                if github.repoHasUpdate(package.source, package.version, package.version_type):
                    print(package.name + ' package has update')
    if packages:
        dialog.setPackageList(packages)
        dialog.exec_()
