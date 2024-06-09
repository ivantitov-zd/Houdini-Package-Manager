import json
from typing import Any

import hou
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from package_manager.package import Package


class UpdateOptions:
    _instance = None

    def __new__(cls, *args, **kwargs) -> 'UpdateOptions':
        if not cls._instance:
            cls._instance = super(UpdateOptions, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self.__class__._instance is not self:
            return

        self._options_file_path = hou.expandString('$HOUDINI_USER_PREF_DIR/package_manager.update_options')

    def set_field(self, field_name: str, value: Any) -> None:
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
        except (OSError, ValueError):
            options_data = {}

        with open(self._options_file_path, 'w') as file:
            options_data[field_name] = value
            json.dump(options_data, file, indent=4)

    def get_field(self, field_name: str) -> Any:
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
                return options_data.get(field_name)
        except (OSError, ValueError):
            return None

    def set_field_for_package(self, package: Package, field_name: str, value: Any) -> None:
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
            if 'packages' not in options_data:
                options_data['packages'] = {}
        except (OSError, ValueError):
            options_data = {
                'check_on_startup': True,
                'packages': {},
            }

        package_full_name = package.source.replace('/', '_').lower()
        if package_full_name not in options_data['packages']:
            options_data['packages'][package_full_name] = {}
        options_data['packages'][package_full_name][field_name] = value

        with open(self._options_file_path, 'w') as file:
            json.dump(options_data, file, indent=4)

    def get_field_for_package(self, package: Package, field_name: str) -> Any | None:
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
                package_full_name = package.source.replace('/', '_').lower()
                package_options_data = options_data['packages'][package_full_name]
                return package_options_data.get(field_name)
        except (OSError, ValueError, KeyError):
            return None

    def set_check_on_startup(self, enable: bool) -> None:
        self.set_field('check_on_startup', enable)

    def check_on_startup(self) -> bool:
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
            return options_data.get('check_on_startup', False)
        except (OSError, ValueError):
            # noinspection PyTypeChecker
            reply = QMessageBox.question(None, 'Package Manager: Update',
                                         'Check for updates on startup?',
                                         QMessageBox.Yes | QMessageBox.No)
            check = reply == QMessageBox.Yes
            self.set_check_on_startup(check)
            return check

    def set_last_check_time(self, time: int | float) -> None:
        self.set_field('last_update_check', time)

    def last_check_time(self) -> int | float:
        return self.get_field('last_update_check') or 0

    def set_check_on_startup_for_package(self, package: Package, enable: bool) -> None:
        self.set_field_for_package(package, 'check_on_startup', enable)

    def check_on_startup_for_package(self, package: Package) -> bool:
        check = self.get_field_for_package(package, 'check_on_startup')
        return check if check is not None else True

    def set_only_stable_for_package(self, package: Package, enable: bool) -> None:
        self.set_field_for_package(package, 'only_stable', enable)

    def only_stable_for_package(self, package: Package) -> bool:
        only_stable = self.get_field_for_package(package, 'only_stable')
        return only_stable if only_stable is not None else True
