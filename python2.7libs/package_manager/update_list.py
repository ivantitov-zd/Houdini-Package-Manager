import json
from operator import itemgetter

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou
import requests

from .web_package import WebPackage
from .version import Version, VersionRange


class UpdateListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(UpdateListModel, self).__init__(parent)

        self.__packages = ()
        self.__checked = set()

    def updateData(self, packages):
        self.beginResetModel()
        self.__packages = tuple(packages)
        self.__checked = set(packages)
        self.endResetModel()

    @property
    def checked(self):
        return self.__checked

    def rowCount(self, parent):
        return len(self.__packages)

    def flags(self, index):
        default_flags = super(UpdateListModel, self).flags(index)
        return default_flags | Qt.ItemIsUserCheckable

    def setData(self, index, value, role):
        if not index.isValid() or role != Qt.CheckStateRole:
            return False

        package = index.data(Qt.UserRole)
        if value == Qt.Checked:
            self.__checked.add(package)
        else:
            self.__checked.remove(package)

        self.dataChanged.emit(index, index)
        return True

    def data(self, index, role):
        package = self.__packages[index.row()]
        if role == Qt.DisplayRole:
            return package.name
        if role == Qt.UserRole:
            return package
        if role == Qt.CheckStateRole:
            return Qt.Checked if package in self.__checked else Qt.Unchecked


class UpdateListView(QListView):
    def __init__(self):
        super(UpdateListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
