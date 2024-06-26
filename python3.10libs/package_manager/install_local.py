import os
from typing import Any

import hou
from PySide2.QtCore import Qt
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QComboBox
from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QFormLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtWidgets import QSpacerItem
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from package_manager.local_package import LocalPackage


class FolderField(QWidget):
    # Signals
    textChanged = Signal(str)

    def __init__(self, content: str = '') -> None:
        super(FolderField, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.edit = QLineEdit(content)
        self.edit.textChanged.connect(self.textChanged.emit)
        layout.addWidget(self.edit)

        self.pick_folder_button = QPushButton()
        self.pick_folder_button.setToolTip('Pick location')
        self.pick_folder_button.setFixedSize(24, 24)
        self.pick_folder_button.setIcon(hou.qt.Icon('BUTTONS_chooser_folder', 16, 16))
        self.pick_folder_button.clicked.connect(self._pick_location)
        layout.addWidget(self.pick_folder_button)

    def text(self) -> str:
        return self.edit.text()

    def path(self) -> str:
        return hou.expandString(self.edit.text())

    def _pick_location(self) -> None:
        path = QFileDialog.getExistingDirectory(self, 'Package Folder', self.path())
        if path:
            path = path.replace('\\', '/')
            self.edit.setText(path)


class InstallFromFolderPathDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super(InstallFromFolderPathDialog, self).__init__(parent)

        self.setWindowTitle('Package Manager: Install from Local Folder')
        self.resize(500, 50)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(4, 0, 0, 2)
        form_layout.setSpacing(4)
        main_layout.addLayout(form_layout)

        self.folder_path_field = FolderField()
        form_layout.addRow('Folder Path', self.folder_path_field)

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
        self.folder_path_field.textChanged.connect(self.update_button_state)
        self.update_button_state()

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

    def update_button_state(self) -> None:
        path = self.folder_path_field.path()
        self.ok_button.setEnabled(bool(path and os.path.exists(path) and os.path.isdir(path)))

    @classmethod
    def get_installation_data(cls, parent: QWidget | None = None) -> tuple[int, str, Any]:
        dialog = cls(parent)
        return (dialog.exec_(),
                dialog.folder_path_field.text(),
                dialog.setup_schema_combo.currentData(Qt.UserRole))


def pick_and_install_package_from_folder(parent=None) -> bool:
    ok, path, schema = InstallFromFolderPathDialog.get_installation_data(parent)
    if ok and path:
        if LocalPackage.install(path, setup_schema=schema):
            hou.ui.setStatusMessage('Successfully installed',
                                    hou.severityType.ImportantMessage)
        return True
    return False
