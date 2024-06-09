import json
from operator import itemgetter
from time import sleep
from typing import Any


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


class WebPackageListModel(QAbstractListModel):
    def __init__(self, parent: QObject | None = None) -> None:
        super(WebPackageListModel, self).__init__(parent)

        self.__data = ()
        self.update_data()

    def update_data(self, packages: list[WebPackage] | None = None) -> None:
        self.beginResetModel()
        hversion = Version(hou.applicationVersionString())
        items = []
        if packages:
            items = packages
        else:
            attempts = 3
            while attempts != 0:
                try:
                    r = requests.get('https://raw.githubusercontent.com/anvdev/'
                                     'Houdini-Package-List/master/data.json')
                    data = json.loads(r.text)
                    if hou.getenv('username') == 'MarkWilson':  # Debug only
                        with open(r'C:\Users\MarkWilson\Documents\Houdini-Package-List\data.json') as file:
                            data = json.load(file)
                    break
                except IOError:
                    attempts -= 1
                    sleep(0.125)
            else:
                data = {}

            for name, package_data in sorted(data.items(), key=itemgetter(0)):
                if not package_data.get('visible', True):
                    continue

                if hversion not in VersionRange.from_pattern(package_data.get('hversion', '*')):
                    continue

                items.append(WebPackage(
                    name,
                    package_data.get('description'),
                    package_data.get('author'),
                    package_data['source'],
                    package_data['source_type'],
                    package_data.get('hversion'),
                    package_data.get('hlicense'),
                    package_data.get('status'),
                    package_data.get('setup_schema')
                ))

        self.__data = tuple(items)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__data)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.name
        if role == Qt.UserRole:
            return item


class WebPackageListView(QListView):
    def __init__(self) -> None:
        super(WebPackageListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
