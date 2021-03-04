# coding: utf-8

from __future__ import print_function

import json

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou


class UpdateOptions(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UpdateOptions, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self.__class__._instance is not self:
            return

        self._options_file_path = hou.expandString('$HOUDINI_USER_PREF_DIR/package_manager.update_options')

    def setField(self, field_name, value):
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
        except (IOError, ValueError):
            options_data = {}

        with open(self._options_file_path, 'w') as file:
            options_data[field_name] = value
            json.dump(options_data, file, indent=4)

    def getField(self, field_name):
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
                return options_data.get(field_name)
        except (IOError, ValueError):
            return

    def setFieldForPackage(self, package, field_name, value):
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
            if 'packages' not in options_data:
                options_data['packages'] = {}
        except (IOError, ValueError):
            options_data = {
                'check_on_startup': True,
                'packages': {}
            }

        package_full_name = package.source.replace('/', '_').lower()
        if package_full_name not in options_data['packages']:
            options_data['packages'][package_full_name] = {}
        options_data['packages'][package_full_name][field_name] = value

        with open(self._options_file_path, 'w') as file:
            json.dump(options_data, file, indent=4)

    def getFieldForPackage(self, package, field_name):
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
                package_full_name = package.source.replace('/', '_').lower()
                package_options_data = options_data['packages'][package_full_name]
                return package_options_data.get(field_name)
        except (IOError, ValueError, KeyError):
            return

    def setCheckOnStartup(self, enable):
        self.setField('check_on_startup', enable)

    def checkOnStartup(self):
        try:
            with open(self._options_file_path) as file:
                options_data = json.load(file)
            return options_data.get('check_on_startup', False)
        except (IOError, ValueError):
            # noinspection PyTypeChecker
            reply = QMessageBox.question(None, 'Package Manager: Update',
                                         'Check for updates on startup?',
                                         QMessageBox.Yes | QMessageBox.No)
            check = reply == QMessageBox.Yes
            self.setCheckOnStartup(check)
            return check

    def setLastCheckTime(self, time):
        self.setField('last_update_check', time)

    def lastCheckTime(self):
        return self.getField('last_update_check') or 0

    def setCheckOnStartupForPackage(self, package, enable):
        self.setFieldForPackage(package, 'check_on_startup', enable)

    def checkOnStartupForPackage(self, package):
        check = self.getFieldForPackage(package, 'check_on_startup')
        return check if check is not None else True

    def setOnlyStableForPackage(self, package, enable):
        self.setFieldForPackage(package, 'only_stable', enable)

    def onlyStableForPackage(self, package):
        only_stable = self.getFieldForPackage(package, 'only_stable')
        return only_stable if only_stable is not None else True
