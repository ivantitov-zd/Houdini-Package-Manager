try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou

from .update_list import UpdateListModel, UpdateListView
from . import github


class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        super(UpdateDialog, self).__init__(parent)

        self.setWindowTitle('Package Manager: Updates')
        self.setWindowIcon(hou.qt.Icon('IMAGE_auto_update', 32, 32))
        self.setStyleSheet(hou.qt.styleSheet())
        self.resize(600, 400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(4)
        main_layout.addLayout(middle_layout)

        self.web_list_model = UpdateListModel(self)

        self.web_list_view = UpdateListView()
        self.web_list_view.setModel(self.web_list_model)
        self.web_list_view.setFixedWidth(120)
        selection_model = self.web_list_view.selectionModel()
        selection_model.currentChanged.connect(self._setCurrentPackage)
        middle_layout.addWidget(self.web_list_view)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(4, 4, 4, 4)
        form_layout.setSpacing(4)
        form_layout.setHorizontalSpacing(8)
        middle_layout.addLayout(form_layout)

        self.current_version_label = QLabel()
        form_layout.addRow('Current version', self.current_version_label)

        self.new_version_label = QLabel()
        form_layout.addRow('New version', self.new_version_label)

        self.update_changes_label = QLabel()
        self.update_changes_label.setWordWrap(True)
        # Todo: scroll area
        self.update_changes_label.setMaximumHeight(800)
        form_layout.addRow('Changes', self.update_changes_label)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        update_button = QPushButton('Update Selected')
        update_button.clicked.connect(self.accept)
        buttons_layout.addWidget(update_button)

        skip_button = QPushButton('Skip Updating')
        skip_button.setToolTip('Skipidi-pa-pa')
        skip_button.clicked.connect(self.reject)
        buttons_layout.addWidget(skip_button)

        self.package = None

    def _setCurrentPackage(self, index):
        package = index.data(Qt.UserRole)
        self.package = package
        self.current_version_label.setText(package.version)
        if package.source_type == 'github':
            releases_api_url = 'https://api.github.com/repos/{0}/{1}/releases'.format(*github.ownerAndRepoName(package.source))
            last_version_data = github.GitHubAPICache.get(releases_api_url)[0]
            new_version = last_version_data['tag_name']
            self.new_version_label.setText(new_version)
            changes = last_version_data['body']
            self.update_changes_label.setText(changes)

    def setPackageList(self, packages):
        self.web_list_model.updateData(packages)

    @classmethod
    def getUpdateFlags(cls, packages):
        window = cls(hou.qt.mainWindow())
        window.setPackageList(packages)
        return window.exec_(), window.web_list_model.checked
