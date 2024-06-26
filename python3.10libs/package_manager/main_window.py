import hou
from PySide2.QtCore import QModelIndex
from PySide2.QtCore import QSize
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QButtonGroup
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtWidgets import QSpacerItem
from PySide2.QtWidgets import QSplitter
from PySide2.QtWidgets import QStackedLayout
from PySide2.QtWidgets import QTabWidget
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from package_manager.local_package import find_installed_packages
from package_manager.local_package_content import OperatorListModel
from package_manager.local_package_content import OperatorListView
from package_manager.local_package_content import PackageInfoView
from package_manager.local_package_content import PyPanelListModel
from package_manager.local_package_content import PyPanelListView
from package_manager.local_package_content import ShelfListModel
from package_manager.local_package_content import ShelfListView
from package_manager.local_package_content import ShelfToolListModel
from package_manager.local_package_content import ShelfToolListView
from package_manager.package_list import PackageListModel
from package_manager.package_list import PackageListView
from package_manager.settings import SettingsWidget
from package_manager.web_package_content import WebPackageInfoView
from package_manager.web_package_list import WebPackageListModel
from package_manager.web_package_list import WebPackageListView


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
        view_mode_button_group.buttonClicked['int'].connect(self._switch_panel)

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
        self.update_local_package_list()

        package_list_view = PackageListView()
        package_list_view.setModel(self.package_list_model)
        selection_model = package_list_view.selectionModel()
        selection_model.currentChanged.connect(self._set_current_package)
        splitter.addWidget(package_list_view)

        self.package_content_tabs = QTabWidget()
        self.package_content_tabs.setStyleSheet('QTabWidget::pane { border: 0; }')
        splitter.addWidget(self.package_content_tabs)

        splitter.setSizes((200, 400))
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        general_view = PackageInfoView()
        general_view.enabled.connect(self.update_local_package_list)
        general_view.disabled.connect(self.update_local_package_list)
        general_view.uninstalled.connect(self.update_local_package_list)
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
        selection_model.currentChanged.connect(self._set_current_web_package)
        splitter.addWidget(self.web_list_view)

        self.web_info_view = WebPackageInfoView()
        self.web_info_view.installed.connect(self.update_web_package_list)
        self.web_info_view.installed.connect(self.update_local_package_list)

        splitter.addWidget(self.web_info_view)
        splitter.setSizes((200, 400))
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # Settings
        self.settins = SettingsWidget()
        self.stack_layout.addWidget(self.settins)

        # Data
        self.current_package = None
        self.package_content_tabs.currentChanged.connect(self.update_content_source)

        self.current_web_package = None

    def update_local_package_list(self) -> None:
        self.package_list_model.set_package_list(find_installed_packages())
        self.current_package = None

    def update_web_package_list(self) -> None:
        self.web_list_model.update_data()

    def update_content_source(self) -> None:
        content_widget = self.package_content_tabs.currentWidget()
        content_widget.set_package(self.current_package)

    def update_web_content_source(self) -> None:
        self.web_info_view.set_web_package(self.current_web_package)

    def _set_current_package(self, index: QModelIndex) -> None:
        package = index.data(Qt.UserRole)
        self.current_package = package
        self.update_content_source()

    def _set_current_web_package(self, index: QModelIndex) -> None:
        web_package = index.data(Qt.UserRole)
        self.current_web_package = web_package
        self.update_web_content_source()

    def _switch_panel(self, panel_id: int) -> None:
        self.stack_layout.setCurrentIndex(panel_id)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        modifiers = event.modifiers()
        if modifiers == Qt.NoModifier and key == Qt.Key_F5:
            current_panel_index = self.stack_layout.currentIndex()
            if current_panel_index == 0:
                self.update_local_package_list()
            elif current_panel_index == 1:
                self.update_web_package_list()
        elif modifiers == Qt.NoModifier and key == Qt.Key_F1:
            desktop = hou.ui.curDesktop()
            desktop.displayHelpPath('/ref/windows/package_manager')
        elif modifiers == Qt.ControlModifier and key == Qt.Key_1:
            self.local_mode_button.setChecked(True)
            self._switch_panel(0)
        elif modifiers == Qt.ControlModifier and key == Qt.Key_2:
            self.web_mode_button.setChecked(True)
            self._switch_panel(1)
        elif modifiers == Qt.ControlModifier and key == Qt.Key_3:
            self.settings_mode_button.setChecked(True)
            self._switch_panel(2)
        else:
            super(MainWindow, self).keyPressEvent(event)
