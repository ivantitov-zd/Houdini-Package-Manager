from .package import Package


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
    def __init__(self, parent: QWidget | None = None) -> None:
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

        self.update_changes_label = QTextEdit()
        size_policy = self.update_changes_label.sizePolicy()
        size_policy.setVerticalStretch(1)
        self.update_changes_label.setSizePolicy(size_policy)
        self.update_changes_label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.update_changes_label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.update_changes_label.setReadOnly(True)
        form_layout.addRow('Changes', self.update_changes_label)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        update_button = QPushButton('Update Selected')
        update_button.clicked.connect(self.accept)
        buttons_layout.addWidget(update_button)

        skip_button = QPushButton('Skip Updating')
        skip_button.clicked.connect(self.reject)
        buttons_layout.addWidget(skip_button)

        self.package = None

    def _setCurrentPackage(self, index: QModelIndex) -> None:
        package = index.data(Qt.UserRole)
        self.package = package
        self.current_version_label.setText(package.version)
        if package.source_type == 'github':
            releases_api_url = 'https://api.github.com/repos/{0}/{1}/releases'.format(
                *github.ownerAndRepoName(package.source)
            )
            releases_data = github.API.get(releases_api_url)
            if releases_data:
                last_version_data = releases_data[0]
                new_version = last_version_data['tag_name']
                changes = last_version_data['body']
            else:
                repo_api_url = 'https://api.github.com/repos/{0}/{1}'.format(*github.ownerAndRepoName(package.source))
                repo_data = github.API.get(repo_api_url)
                new_version = repo_data['pushed_at']
                changes = 'No information'
            self.new_version_label.setText(new_version)
            self.update_changes_label.setText(changes)

    def setPackageList(self, packages: list[Package]) -> None:
        self.web_list_model.updateData(packages)

    @classmethod
    def getUpdateFlags(cls, packages: list[Package]) -> tuple[int, set]:
        window = cls(hou.qt.mainWindow())
        window.setPackageList(packages)
        return window.exec_(), window.web_list_model.checked
