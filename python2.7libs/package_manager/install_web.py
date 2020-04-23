try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou

from . import github


class InstallFromWebLinkDialog(QDialog):
    def __init__(self, parent=None):
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

        self.setup_scheme_combo = QComboBox()
        self.setup_scheme_combo.setDisabled(True)
        form_layout.addRow('Setup Scheme', self.setup_scheme_combo)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)
        self.web_link_field.textChanged.connect(self.updateButtonState)
        self.updateButtonState()

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

    def updateButtonState(self):
        path = self.web_link_field.text()
        self.ok_button.setEnabled(bool(path))

    @classmethod
    def getInstallationData(cls, parent=None):
        dialog = cls(parent)
        return dialog.exec_(), dialog.web_link_field.text()


def installPackageFromWebLink(parent=None):
    ok, link = InstallFromWebLinkDialog.getInstallationData(parent)
    if ok and link:
        github.installFromRepo(link)
        hou.ui.setStatusMessage('Successfully installed',
                                hou.severityType.ImportantMessage)
        return True
