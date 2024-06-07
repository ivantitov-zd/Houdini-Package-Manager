# coding: utf-8

from __future__ import print_function

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

from .link_label import LinkLabel
from .path_text import preparePath
from .shelves import shelvesInFile, toolsInFile
from . import github
from .update_options import UpdateOptions
from . import pypanel


class IconCache:
    img = QImage(32, 32, QImage.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))
    DEFAULT_ICON = QIcon(QPixmap(img))

    cache_data = {}

    @staticmethod
    def icon(name):
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

    def __init__(self):
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
        self.check_updates_on_startup_toggle.toggled.connect(self._onToggleCheckUpdate)
        update_layout.addWidget(self.check_updates_on_startup_toggle)

        self.check_only_stable_toggle = QCheckBox('Only Stable Releases')
        self.check_only_stable_toggle.toggled.connect(self._onToggleCheckOnlyStable)
        update_layout.addWidget(self.check_only_stable_toggle)

        # Todo: update button

        # Enable/Disable
        self.enable_button = QPushButton('Enable')
        self.enable_button.setDisabled(True)
        self.enable_button.clicked.connect(self._onEnable)
        main_layout.addWidget(self.enable_button)

        self.disable_button = QPushButton('Disable')
        self.disable_button.hide()
        self.disable_button.clicked.connect(self._onDisable)
        main_layout.addWidget(self.disable_button)

        # Uninstall
        self.uninstall_button = QPushButton('Uninstall')
        self.uninstall_button.setDisabled(True)
        self.uninstall_button.clicked.connect(self._onUninstall)
        main_layout.addWidget(self.uninstall_button)

        # Data
        self.__package = None

    def updatePath(self):
        if self.__package is None:
            self.location_info.setText('')
            return
        matrics = self.location_info.fontMetrics()
        char_width = matrics.horizontalAdvance('Mo') * 0.6
        available_length = char_width * len(self.__package.content_path)
        if available_length > self.width() - char_width * 18:
            available_length = int(self.width() / char_width)
        self.location_info.setText(preparePath(self.__package.content_path, available_length))

    def resizeEvent(self, event):
        self.updatePath()
        super(PackageInfoView, self).resizeEvent(event)

    def updateFromCurrentPackage(self):
        if self.__package is None:
            self.name_info.setText('')
            self.desc_info.setText('')
            self.author_info.setText('')
            self.version_info.setText('')
            self.hversion_info.setText('')
            self.hlicense_info.setText('')
            self.status_info.setText('')
            self.location_info.setText('')
            self.location_info.setLink(None)
            self.source_info.setText('')
            self.source_info.setLink(None)
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
        self.location_info.setLink('file:///' + self.__package.content_path)
        self.updatePath()
        self.update_group.setEnabled(True)
        if self.__package.source is not None:
            self.source_info.setText('GitHub: ' + self.__package.source)
            self.source_info.setLink(github.repoURL(*github.ownerAndRepoName(self.__package.source)))
        else:
            self.source_info.setText('-')
            self.source_info.setLink(None)
        if self.__package.source and self.__package.source_type and self.__package.version:
            check = UpdateOptions().checkOnStartupForPackage(self.__package)
            self.check_updates_on_startup_toggle.blockSignals(True)
            self.check_updates_on_startup_toggle.setChecked(check)
            self.check_updates_on_startup_toggle.blockSignals(False)

            only_stable = UpdateOptions().onlyStableForPackage(self.__package)
            self.check_only_stable_toggle.blockSignals(True)
            self.check_only_stable_toggle.setChecked(only_stable)
            self.check_only_stable_toggle.blockSignals(False)

            self.update_group.show()
        else:
            self.update_group.hide()
        if self.__package.isEnabled():
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

    def setPackage(self, package):
        self.__package = package
        self.updateFromCurrentPackage()

    def _onToggleCheckUpdate(self, state):
        UpdateOptions().setCheckOnStartupForPackage(self.__package, state)

    def _onToggleCheckOnlyStable(self, state):
        UpdateOptions().setOnlyStableForPackage(self.__package, state)

    def _onEnable(self):
        self.__package.enable(True)
        self.updateFromCurrentPackage()
        self.enabled.emit()

    def _onDisable(self):
        self.__package.enable(False)
        self.updateFromCurrentPackage()
        self.disabled.emit()

    def _onUninstall(self):
        self.__package.uninstall()
        self.uninstalled.emit()
        self.__package = None
        self.updateFromCurrentPackage()


class OperatorListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(OperatorListModel, self).__init__(parent)

        self.__data = ()

    def setPackage(self, package):
        self.beginResetModel()
        try:
            hdas = []
            for lib_path in package.libraries():
                hdas.extend(hou.hda.definitionsInFile(lib_path))
            self.__data = tuple(hdas)
        except (IOError, AttributeError):
            self.__data = ()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.description()
        if role == Qt.ToolTipRole:
            if item.isInstalled():
                return item.nodeType().nameWithCategory()
        if role == Qt.DecorationRole:
            return IconCache.icon(item.icon())


class OperatorListView(QListView):
    def __init__(self):
        super(OperatorListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setPackage(self, package):
        self.model().setPackage(package)


class ShelfListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(ShelfListModel, self).__init__(parent)

        self.__data = ()

    def setPackage(self, package):
        self.beginResetModel()
        try:
            shelves = []
            for shelf_path in package.shelves():
                shelves.extend(shelvesInFile(shelf_path))
            self.__data = tuple(shelves)
        except (IOError, AttributeError):
            self.__data = ()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.label()
        if role == Qt.ToolTipRole:
            return item.name()


class ShelfListView(QListView):
    def __init__(self):
        super(ShelfListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setPackage(self, package):
        self.model().setPackage(package)


class ShelfToolListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(ShelfToolListModel, self).__init__(parent)

        self.__data = ()

    def setPackage(self, package):
        self.beginResetModel()
        try:
            tools = []
            for shelf_path in package.shelves():
                tools.extend(toolsInFile(shelf_path))
            self.__data = tuple(tools)
        except (IOError, AttributeError):
            self.__data = ()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.label()
        if role == Qt.ToolTipRole:
            return item.name()
        if role == Qt.DecorationRole:
            return IconCache.icon(item.icon())


class ShelfToolListView(QListView):
    def __init__(self):
        super(ShelfToolListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setPackage(self, package):
        self.model().setPackage(package)


class PyPanelListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(PyPanelListModel, self).__init__(parent)

        self.__data = ()

    def setPackage(self, package):
        self.beginResetModel()
        try:
            panels = []
            for panel_path in package.panels():
                panels.extend(pypanel.interfacesInFile(panel_path))
            self.__data = tuple(panels)
        except (IOError, AttributeError):
            self.__data = ()
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.label()
        if role == Qt.ToolTipRole:
            return item.name()
        if role == Qt.DecorationRole:
            return IconCache.icon(item.icon())


class PyPanelListView(QListView):
    def __init__(self):
        super(PyPanelListView, self).__init__()
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def setPackage(self, package):
        self.model().setPackage(package)
