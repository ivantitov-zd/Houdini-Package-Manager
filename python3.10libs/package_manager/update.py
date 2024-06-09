from time import time

from . import github
from .local_package import find_installed_packages
from .package import Package
from .update_dialog import UpdateDialog
from .update_options import UpdateOptions


def has_update(package: Package, only_stable: bool | None = None) -> bool:
    only_stable = only_stable or UpdateOptions().only_stable_for_package(package)
    if package.source_type == 'github':
        return github.repo_has_update(package.source, package.version, package.version_type, only_stable)
    return False


def update_package(package: Package) -> None:
    only_stable = UpdateOptions().only_stable_for_package(package)
    if package.source_type == 'github':
        github.install_from_repo(package, update=True, only_stable=only_stable)


def check_for_updates(ignore_options: bool = False) -> None:
    packages = []
    for package in find_installed_packages():
        if not package.source or not package.source_type or not package.version:
            continue

        if not package.author or not package.name:
            continue

        if not ignore_options and not UpdateOptions().check_on_startup_for_package(package):
            continue

        if has_update(package):
            packages.append(package)

    if packages:
        dialog = UpdateDialog()
        update, checked = dialog.get_update_flags(packages)
        if update:
            for package in packages:
                if package in checked:
                    update_package(package)

    UpdateOptions().set_last_check_time(time())
