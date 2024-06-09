from typing import Any

import hou
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QComboBox
from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QFormLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtWidgets import QSpacerItem
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from package_manager import github


class InstallFromWebLinkDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super(InstallFromWebLinkDialog, self).__init__(parent)

        self.setWindowTitle('Package Manager: Install from Web Link')
        self.resize(500, 50)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        supported_links = QLabel('Currently, only GitHub repositories are supported')
        supported_links.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(supported_links)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(4, 0, 0, 2)
        form_layout.setSpacing(4)
        main_layout.addLayout(form_layout)

        self.web_link_field = QLineEdit()
        self.web_link_field.setPlaceholderText('https://github.com/Houdini-Packages/Houdini-Package-Manager')
        form_layout.addRow('Web Link', self.web_link_field)

        self.setup_schema_combo = QComboBox()
        self.setup_schema_combo.setDisabled(True)
        form_layout.addRow('Setup Schema', self.setup_schema_combo)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)
        self.web_link_field.textChanged.connect(self.update_button_state)
        self.update_button_state()

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

    def update_button_state(self) -> None:
        path = self.web_link_field.text()
        self.ok_button.setEnabled(bool(path))

    @classmethod
    def get_installation_data(cls, parent: QWidget | None = None) -> tuple[int, str, Any]:
        dialog = cls(parent)
        return (dialog.exec_(),
                dialog.web_link_field.text(),
                dialog.setup_schema_combo.currentData(Qt.UserRole))


def install_package_from_web_link(parent: QWidget | None = None) -> bool:
    ok, link, schema = InstallFromWebLinkDialog.get_installation_data(parent)
    if ok and link:
        if github.install_from_repo(link, setup_schema=schema):
            hou.ui.setStatusMessage('Successfully installed',
                                    hou.severityType.ImportantMessage)
        return True
    return False
