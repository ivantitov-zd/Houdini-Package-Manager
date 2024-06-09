from typing import Any

import hou
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from package_manager import github
from package_manager import pypanel
from package_manager.link_label import LinkLabel
from package_manager.local_package import LocalPackage
from package_manager.package import Package
from package_manager.path_text import prepare_path
from package_manager.shelves import shelves_in_file
from package_manager.shelves import tools_in_file
from package_manager.update_options import UpdateOptions


class IconCache:
    img = QImage(32, 32, QImage.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))
    DEFAULT_ICON = QIcon(QPixmap(img))

    cache_data = {}

    @staticmethod
    def icon(name: str) -> hou.qt.Icon:
        if name not in IconCache.cache_data:
            try:
                IconCache.cache_data[name] = hou.qt.Icon(name, 32, 32)
            except hou.OperationFailed:
                IconCache.cache_data[name] = IconCache.DEFAULT_ICON
        return IconCache.cache_data[name]


class PackageInfoView(QWidget):
    # Signals
    enabled = Signal()
    disabled = Signal()
    uninstalled = Signal()

    def __init__(self) -> None:
        super(PackageInfoView, self).__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        info_block_layout = QFormLayout()
        info_block_layout.setContentsMargins(4, 0, 0, 0)
        info_block_layout.setSpacing(4)
        info_block_layout.setHorizontalSpacing(10)
        main_layout.addLayout(info_block_layout)

        name_label = QLabel('Name')
        name_label.setAlignment(Qt.AlignTop)
        self.name_info = QLabel()
        self.name_info.setWordWrap(True)
        info_block_layout.addRow(name_label, self.name_info)

        desc_label = QLabel('Description')
        desc_label.setAlignment(Qt.AlignTop)
        self.desc_info = QLabel()
        self.desc_info.setWordWrap(True)
        info_block_layout.addRow(desc_label, self.desc_info)

        author_label = QLabel('Author')
        author_label.setAlignment(Qt.AlignTop)
        self.author_info = QLabel()
        self.author_info.setWordWrap(True)
        info_block_layout.addRow(author_label, self.author_info)

        version_label = QLabel('Version')
        version_label.setAlignment(Qt.AlignTop)
        self.version_info = QLabel()
        self.version_info.setWordWrap(True)
        info_block_layout.addRow(version_label, self.version_info)

        hversion_label = QLabel('Houdini')
        hversion_label.setAlignment(Qt.AlignTop)
        self.hversion_info = QLabel()
        self.hversion_info.setWordWrap(True)
        info_block_layout.addRow(hversion_label, self.hversion_info)

        hlicense_label = QLabel('License')
        hlicense_label.setAlignment(Qt.AlignTop)
        self.hlicense_info = QLabel()
        self.hlicense_info.setWordWrap(True)
        info_block_layout.addRow(hlicense_label, self.hlicense_info)

        status_label = QLabel('Status')
        status_label.setAlignment(Qt.AlignTop)
        self.status_info = QLabel()
        self.status_info.setWordWrap(True)
        info_block_layout.addRow(status_label, self.status_info)

        location_label = QLabel('Location')
        location_label.setAlignment(Qt.AlignTop)
        self.location = ''
        self.location_info = LinkLabel()
        self.location_info.setWordWrap(True)
        self.location_info.setToolTip('Open Location')
        info_block_layout.addRow(location_label, self.location_info)

        source_label = QLabel('Source')
        source_label.setAlignment(Qt.AlignTop)
        self.source_info = LinkLabel()
        self.source_info.setWordWrap(True)
        info_block_layout.addRow(source_label, self.source_info)

        state_label = QLabel('State')
        state_label.setAlignment(Qt.AlignTop)
        self.state_info = QLabel()
        self.state_info.setWordWrap(True)
        info_block_layout.addRow(state_label, self.state_info)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

        # Update
        self.update_group = QGroupBox('Update')
        self.update_group.hide()
        self.update_group.setDisabled(True)
        main_layout.addWidget(self.update_group)

        update_layout = QVBoxLayout()
        update_layout.setContentsMargins(6, 8, 6, 8)
        update_layout.setSpacing(4)
        self.update_group.setLayout(update_layout)

        self.check_updates_on_startup_toggle = QCheckBox('Check on Startup')
        self.check_updates_on_startup_toggle.toggled.connect(self._on_toggle_check_update)
        update_layout.addWidget(self.check_updates_on_startup_toggle)

        self.check_only_stable_toggle = QCheckBox('Only Stable Releases')
        self.check_only_stable_toggle.toggled.connect(self._on_toggle_check_only_stable)
        update_layout.addWidget(self.check_only_stable_toggle)

        # TODO: update button

        # Enable/Disable
        self.enable_button = QPushButton('Enable')
        self.enable_button.setDisabled(True)
        self.enable_button.clicked.connect(self._on_enable)
        main_layout.addWidget(self.enable_button)

        self.disable_button = QPushButton('Disable')
        self.disable_button.hide()
        self.disable_button.clicked.connect(self._on_disable)
        main_layout.addWidget(self.disable_button)

        # Uninstall
        self.uninstall_button = QPushButton('Uninstall')
        self.uninstall_button.setDisabled(True)
        self.uninstall_button.clicked.connect(self._on_uninstall)
        main_layout.addWidget(self.uninstall_button)

        # Data
        self.__package = None

    def update_path(self) -> None:
        if self.__package is None:
            self.location_info.setText('')
            return
        matrics = self.location_info.fontMetrics()
        char_width = matrics.horizontalAdvance('Mo') * 0.6
        available_length = char_width * len(self.__package.content_path)
        if available_length > self.width() - char_width * 18:
            available_length = int(self.width() / char_width)
        self.location_info.setText(prepare_path(self.__package.content_path, available_length))

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.update_path()
        super(PackageInfoView, self).resizeEvent(event)

    def update_from_current_package(self) -> None:
        if self.__package is None:
            self.name_info.setText('')
            self.desc_info.setText('')
            self.author_info.setText('')
            self.version_info.setText('')
            self.hversion_info.setText('')
            self.hlicense_info.setText('')
            self.status_info.setText('')
            self.location_info.setText('')
            self.location_info.set_link(None)
            self.source_info.setText('')
            self.source_info.set_link(None)
            self.state_info.setText('')
            self.update_group.hide()
            self.enable_button.setDisabled(True)
            self.disable_button.hide()
            self.uninstall_button.setDisabled(True)
            return

        self.uninstall_button.setEnabled(True)
        self.name_info.setText(self.__package.name)
        self.desc_info.setText(self.__package.description or '-')
        self.author_info.setText(self.__package.author or '-')
        self.version_info.setText(self.__package.version or '-')
        self.hversion_info.setText(self.__package.hversion or '-')
        self.hlicense_info.setText(self.__package.hlicense or '-')
        self.status_info.setText(self.__package.status or '-')
        self.location_info.set_link('file:///' + self.__package.content_path)
        self.update_path()
        self.update_group.setEnabled(True)
        if self.__package.source is not None:
            self.source_info.setText('GitHub: ' + self.__package.source)
            self.source_info.set_link(github.repo_url(*github.owner_and_repo_name(self.__package.source)))
        else:
            self.source_info.setText('-')
            self.source_info.set_link(None)
        if self.__package.source and self.__package.source_type and self.__package.version:
            check = UpdateOptions().check_on_startup_for_package(self.__package)
            self.check_updates_on_startup_toggle.blockSignals(True)
            self.check_updates_on_startup_toggle.setChecked(check)
            self.check_updates_on_startup_toggle.blockSignals(False)

            only_stable = UpdateOptions().only_stable_for_package(self.__package)
            self.check_only_stable_toggle.blockSignals(True)
            self.check_only_stable_toggle.setChecked(only_stable)
            self.check_only_stable_toggle.blockSignals(False)

            self.update_group.show()
        else:
            self.update_group.hide()
        if self.__package.is_enabled():
            self.state_info.setText('Enabled')
            self.enable_button.hide()
            self.disable_button.setEnabled(True)
            self.disable_button.show()
        else:
            self.state_info.setText('Disabled')
            self.enable_button.setEnabled(True)
            self.enable_button.show()
            self.disable_button.hide()

    def package(self):
        return self.__package

    def set_package(self, package: Package) -> None:
        self.__package = package
        self.update_from_current_package()

    def _on_toggle_check_update(self, state: bool) -> None:
        UpdateOptions().set_check_on_startup_for_package(self.__package, state)

    def _on_toggle_check_only_stable(self, state: bool) -> None:
        UpdateOptions().set_only_stable_for_package(self.__package, state)

    def _on_enable(self) -> None:
        self.__package.enable(True)
        self.update_from_current_package()
        self.enabled.emit()

    def _on_disable(self) -> None:
        self.__package.enable(False)
        self.update_from_current_package()
        self.disabled.emit()

    def _on_uninstall(self) -> None:
        self.__package.uninstall()
        self.uninstalled.emit()
        self.__package = None
        self.update_from_current_package()


class OperatorListModel(QAbstractListModel):
    def __init__(self, parent: QObject | None = None) -> None:
        super(OperatorListModel, self).__init__(parent)

        self.__data = ()

    def set_package(self, package: LocalPackage) -> None:
        self.beginResetModel()
        try:
            hdas = []
            for lib_path in package.libraries():
                hdas.extend(hou.hda.definitionsInFile(lib_path))
            self.__data = tuple(hdas)
        except (OSError, AttributeError):
            self.__data = ()
        self.endResetModel()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__data)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.description()
        if role == Qt.ToolTipRole:
            if item.isInstalled():
                return item.nodeType().nameWithCategory()
        if role == Qt.DecorationRole:
            return IconCache.icon(item.icon())


class OperatorListView(QListView):
    def __init__(self) -> None:
        super(OperatorListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def set_package(self, package: LocalPackage) -> None:
        self.model().set_package(package)


class ShelfListModel(QAbstractListModel):
    def __init__(self, parent: QObject | None = None) -> None:
        super(ShelfListModel, self).__init__(parent)

        self.__data = ()

    def set_package(self, package: LocalPackage) -> None:
        self.beginResetModel()
        try:
            shelves = []
            for shelf_path in package.shelves():
                shelves.extend(shelves_in_file(shelf_path))
            self.__data = tuple(shelves)
        except (OSError, AttributeError):
            self.__data = ()
        self.endResetModel()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__data)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.label()
        if role == Qt.ToolTipRole:
            return item.name()


class ShelfListView(QListView):
    def __init__(self) -> None:
        super(ShelfListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def set_package(self, package: LocalPackage) -> None:
        self.model().set_package(package)


class ShelfToolListModel(QAbstractListModel):
    def __init__(self, parent: QObject | None = None) -> None:
        super(ShelfToolListModel, self).__init__(parent)

        self.__data = ()

    def set_package(self, package: LocalPackage) -> None:
        self.beginResetModel()
        try:
            tools = []
            for shelf_path in package.shelves():
                tools.extend(tools_in_file(shelf_path))
            self.__data = tuple(tools)
        except (OSError, AttributeError):
            self.__data = ()
        self.endResetModel()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__data)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.label()
        if role == Qt.ToolTipRole:
            return item.name()
        if role == Qt.DecorationRole:
            return IconCache.icon(item.icon())


class ShelfToolListView(QListView):
    def __init__(self) -> None:
        super(ShelfToolListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def set_package(self, package: LocalPackage) -> None:
        self.model().set_package(package)


class PyPanelListModel(QAbstractListModel):
    def __init__(self, parent: QObject | None = None) -> None:
        super(PyPanelListModel, self).__init__(parent)

        self.__data = ()

    def set_package(self, package: LocalPackage) -> None:
        self.beginResetModel()
        try:
            panels = []
            for panel_path in package.panels():
                panels.extend(pypanel.interfaces_in_file(panel_path))
            self.__data = tuple(panels)
        except (OSError, AttributeError):
            self.__data = ()
        self.endResetModel()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.__data)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.label()
        if role == Qt.ToolTipRole:
            return item.name()
        if role == Qt.DecorationRole:
            return IconCache.icon(item.icon())


class PyPanelListView(QListView):
    def __init__(self) -> None:
        super(PyPanelListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def set_package(self, package: LocalPackage) -> None:
        self.model().set_package(package)
