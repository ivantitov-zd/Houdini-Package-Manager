from typing import Any
from typing import Collection


try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou


class PackageListModel(QAbstractListModel):
    # Icons
    ACTIVE_ON_ICON = hou.qt.Icon('SCENEGRAPH_active_on', 16, 16)
    ACTIVE_OFF_ICON = hou.qt.Icon('SCENEGRAPH_active_off', 16, 16)

    def __init__(self, parent: QWidget | None = None) -> None:
        super(PackageListModel, self).__init__(parent)

        self.__data = ()

    def set_package_list(self, packages: Collection[dict]) -> None:
        self.beginResetModel()
        self.__data = tuple(packages)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__data)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.name
        if role == Qt.UserRole:
            return item
        if role == Qt.DecorationRole:
            if item.is_enabled():
                return PackageListModel.ACTIVE_ON_ICON
            else:
                return PackageListModel.ACTIVE_OFF_ICON


class PackageListView(QListView):
    def __init__(self) -> None:
        super(PackageListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
