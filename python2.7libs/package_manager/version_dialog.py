try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


class VersionDialog(QDialog):
    def __init__(self, parent=None):
        super(VersionDialog, self).__init__(parent)

        self.setWindowTitle('Choose version')

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)
        # form_layout.setContentsMargins(4, 4, 4, 4)
        # form_layout.setSpacing(4)

        self.version_combo = QComboBox()
        form_layout.addRow('Version', self.version_combo)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self._onOk)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        self.current_version = None

    def _onOk(self):
        self.current_version = self.version_combo.currentData(Qt.UserRole)
        self.accept()

    def _setVersionList(self, versions):
        self.version_combo.clear()
        for version in versions:
            self.version_combo.addItem(version.raw, version)

    @classmethod
    def getVersion(cls, parent=None, versions=()):
        window = cls(parent)
        window._setVersionList(versions)
        window.exec_()
        return window.current_version
