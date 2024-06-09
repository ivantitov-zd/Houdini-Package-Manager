try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou

from .local_package import findInstalledPackages
from .package_list import *
from .local_package_content import *
from .web_package_list import *
from .web_package_content import WebPackageInfoView
from .settings import SettingsWidget


class MainWindow(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super(MainWindow, self).__init__(parent, Qt.Window)

        self.setWindowTitle('Package Manager')
        self.setWindowIcon(hou.qt.Icon('MISC_conductor', 32, 32))
        self.resize(600, 450)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Top
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)
        main_layout.addLayout(top_layout)

        view_mode_button_group = QButtonGroup(self)
        view_mode_button_group.setExclusive(True)
        view_mode_button_group.buttonClicked['int'].connect(self._switchPanel)

        self.local_mode_button = QPushButton()
        self.local_mode_button.setFixedSize(24, 24)
        self.local_mode_button.setToolTip('Installed\tCtrl+1')
        self.local_mode_button.setIcon(hou.qt.Icon('DOP_fetchdata', 16, 16))
        self.local_mode_button.setIconSize(QSize(16, 16))
        self.local_mode_button.setCheckable(True)
        self.local_mode_button.toggle()
        view_mode_button_group.addButton(self.local_mode_button)
        view_mode_button_group.setId(self.local_mode_button, 0)
        top_layout.addWidget(self.local_mode_button)

        self.web_mode_button = QPushButton()
        self.web_mode_button.setFixedSize(24, 24)
        self.web_mode_button.setToolTip('Install from Web\tCtrl+2')
        self.web_mode_button.setIcon(hou.qt.Icon('MISC_database', 16, 16))  # IMAGE_auto_update
        self.web_mode_button.setIconSize(QSize(16, 16))
        self.web_mode_button.setCheckable(True)
        view_mode_button_group.addButton(self.web_mode_button)
        view_mode_button_group.setId(self.web_mode_button, 1)
        top_layout.addWidget(self.web_mode_button)

        self.settings_mode_button = QPushButton()
        self.settings_mode_button.setFixedSize(24, 24)
        self.settings_mode_button.setToolTip('Settings\tCtrl+3')
        self.settings_mode_button.setIcon(hou.qt.Icon('LOP_rendersettings', 16, 16))
        self.settings_mode_button.setIconSize(QSize(16, 16))
        self.settings_mode_button.setCheckable(True)
        view_mode_button_group.addButton(self.settings_mode_button)
        view_mode_button_group.setId(self.settings_mode_button, 2)
        top_layout.addWidget(self.settings_mode_button)

        top_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        top_layout.addSpacerItem(top_spacer)

        help_button = hou.qt.HelpButton('/ref/windows/package_manager', 'Show help for this window\tF1')
        top_layout.addWidget(help_button)

        self.stack_layout = QStackedLayout()
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        self.stack_layout.setSpacing(0)
        main_layout.addLayout(self.stack_layout)

        # Local
        local_widget = QWidget()
        self.stack_layout.addWidget(local_widget)

        local_layout = QVBoxLayout(local_widget)
        local_layout.setContentsMargins(0, 0, 0, 0)
        local_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        local_layout.addWidget(splitter)

        self.package_list_model = PackageListModel(self)
        self.updateLocalPackageList()

        package_list_view = PackageListView()
        package_list_view.setModel(self.package_list_model)
        selection_model = package_list_view.selectionModel()
        selection_model.currentChanged.connect(self._setCurrentPackage)
        splitter.addWidget(package_list_view)

        self.package_content_tabs = QTabWidget()
        self.package_content_tabs.setStyleSheet('QTabWidget::pane { border: 0; }')
        splitter.addWidget(self.package_content_tabs)

        splitter.setSizes((200, 400))
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        general_view = PackageInfoView()
        general_view.enabled.connect(self.updateLocalPackageList)
        general_view.disabled.connect(self.updateLocalPackageList)
        general_view.uninstalled.connect(self.updateLocalPackageList)
        self.package_content_tabs.addTab(general_view, 'General')

        operator_list_view = OperatorListView()
        operator_list_view.setModel(OperatorListModel(self))
        self.package_content_tabs.addTab(operator_list_view, 'Digital Assets')

        shelf_list_view = ShelfListView()
        shelf_list_view.setModel(ShelfListModel(self))
        self.package_content_tabs.addTab(shelf_list_view, 'Shelves')

        shelf_tool_list_view = ShelfToolListView()
        shelf_tool_list_view.setModel(ShelfToolListModel(self))
        self.package_content_tabs.addTab(shelf_tool_list_view, 'Shelf Tools')

        panel_list_view = PyPanelListView()
        panel_list_view.setModel(PyPanelListModel(self))
        self.package_content_tabs.addTab(panel_list_view, 'Python Panels')

        # Web
        web_widget = QWidget()
        self.stack_layout.addWidget(web_widget)

        web_layout = QVBoxLayout(web_widget)
        web_layout.setContentsMargins(0, 0, 0, 0)
        web_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        web_layout.addWidget(splitter)

        self.web_list_model = WebPackageListModel(self)

        self.web_list_view = WebPackageListView()
        self.web_list_view.setModel(self.web_list_model)
        selection_model = self.web_list_view.selectionModel()
        selection_model.currentChanged.connect(self._setCurrentWebPackage)
        splitter.addWidget(self.web_list_view)

        self.web_info_view = WebPackageInfoView()
        self.web_info_view.installed.connect(self.updateWebPackageList)
        self.web_info_view.installed.connect(self.updateLocalPackageList)

        splitter.addWidget(self.web_info_view)
        splitter.setSizes((200, 400))
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # Settings
        self.settins = SettingsWidget()
        self.stack_layout.addWidget(self.settins)

        # Data
        self.current_package = None
        self.package_content_tabs.currentChanged.connect(self.updateContentSource)

        self.current_web_package = None

    def updateLocalPackageList(self) -> None:
        self.package_list_model.setPackageList(findInstalledPackages())
        self.current_package = None

    def updateWebPackageList(self) -> None:
        self.web_list_model.updateData()

    def updateContentSource(self) -> None:
        content_widget = self.package_content_tabs.currentWidget()
        content_widget.setPackage(self.current_package)

    def updateWebContentSource(self) -> None:
        self.web_info_view.setWebPackage(self.current_web_package)

    def _setCurrentPackage(self, index: QModelIndex) -> None:
        package = index.data(Qt.UserRole)
        self.current_package = package
        self.updateContentSource()

    def _setCurrentWebPackage(self, index: QModelIndex) -> None:
        web_package = index.data(Qt.UserRole)
        self.current_web_package = web_package
        self.updateWebContentSource()

    def _switchPanel(self, panel_id: int) -> None:
        self.stack_layout.setCurrentIndex(panel_id)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        modifiers = event.modifiers()
        if modifiers == Qt.NoModifier and key == Qt.Key_F5:
            current_panel_index = self.stack_layout.currentIndex()
            if current_panel_index == 0:
                self.updateLocalPackageList()
            elif current_panel_index == 1:
                self.updateWebPackageList()
        elif modifiers == Qt.NoModifier and key == Qt.Key_F1:
            desktop = hou.ui.curDesktop()
            desktop.displayHelpPath('/ref/windows/package_manager')
        elif modifiers == Qt.ControlModifier and key == Qt.Key_1:
            self.local_mode_button.setChecked(True)
            self._switchPanel(0)
        elif modifiers == Qt.ControlModifier and key == Qt.Key_2:
            self.web_mode_button.setChecked(True)
            self._switchPanel(1)
        elif modifiers == Qt.ControlModifier and key == Qt.Key_3:
            self.settings_mode_button.setChecked(True)
            self._switchPanel(2)
        else:
            super(MainWindow, self).keyPressEvent(event)
