from typing import Any

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from package_manager.package import Package


class UpdateListModel(QAbstractListModel):
    def __init__(self, parent: QObject | None = None) -> None:
        super(UpdateListModel, self).__init__(parent)

        self.__packages = ()
        self.__checked = set()

    def update_data(self, packages: list[Package]) -> None:
        self.beginResetModel()
        self.__packages = tuple(packages)
        self.__checked = set(packages)
        self.endResetModel()

    @property
    def checked(self) -> set[Package]:
        return self.__checked

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__packages)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        default_flags = super(UpdateListModel, self).flags(index)
        return default_flags | Qt.ItemIsUserCheckable

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if not index.isValid() or role != Qt.CheckStateRole:
            return False

        package = index.data(Qt.UserRole)
        if value == Qt.Checked:
            self.__checked.add(package)
        else:
            self.__checked.remove(package)

        self.dataChanged.emit(index, index)
        return True

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        package = self.__packages[index.row()]
        if role == Qt.DisplayRole:
            return package.name
        if role == Qt.UserRole:
            return package
        if role == Qt.CheckStateRole:
            return Qt.Checked if package in self.__checked else Qt.Unchecked


class UpdateListView(QListView):
    def __init__(self) -> None:
        super(UpdateListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
