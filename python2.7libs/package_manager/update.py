from .local_package import findInstalledPackages
from .github import installFromGitHubRepo
from .new_version_dialog import NewVersionDialog


def checkForUpdates():
    dialog = NewVersionDialog()
    packages = []
    for package in findInstalledPackages():
        if package.source and package.version:
            if package.source_type == 'github':
                if package.hasUpdates():
                    packages.append(package)
    if packages:
        dialog.setPackageList(packages)
        dialog.exec_()
