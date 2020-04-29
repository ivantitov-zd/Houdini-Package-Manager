from __future__ import print_function

import os

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

from .local_package import LocalPackage


class FolderField(QWidget):
    # Signals
    textChanged = Signal(str)

    def __init__(self, content=''):
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
        self.pick_folder_button.clicked.connect(self._pickLocation)
        layout.addWidget(self.pick_folder_button)

    def text(self):
        return self.edit.text()

    def path(self):
        return hou.expandString(self.edit.text())

    def _pickLocation(self):
        path = QFileDialog.getExistingDirectory(self, 'Package Folder', self.path())
        if path:
            path = path.replace('\\', '/')
            self.edit.setText(path)


class InstallFromFolderPathDialog(QDialog):
    def __init__(self, parent=None):
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
        self.folder_path_field.textChanged.connect(self.updateButtonState)
        self.updateButtonState()

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

    def updateButtonState(self):
        path = self.folder_path_field.path()
        self.ok_button.setEnabled(bool(path and os.path.exists(path) and os.path.isdir(path)))

    @classmethod
    def getInstallationData(cls, parent=None):
        dialog = cls(parent)
        return dialog.exec_(), dialog.folder_path_field.text()


def pickAndInstallPackageFromFolder(parent=None):
    ok, path = InstallFromFolderPathDialog.getInstallationData(parent)
    if ok and path:
        LocalPackage.install(path)
        hou.ui.setStatusMessage('Successfully installed',
                                hou.severityType.ImportantMessage)
        return True
