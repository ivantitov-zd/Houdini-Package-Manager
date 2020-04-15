try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


class NewVersionDialog(QDialog):
    def __init__(self, parent=None):
        super(NewVersionDialog, self).__init__(parent)

        self.setWindowTitle('New version')

        layout = QFormLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.current_version_label = QLabel()
        layout.addRow('Current version', self.current_version_label)

        self.next_version_label = QLabel()
        layout.addRow('Next version', self.next_version_label)

        self.update_info_label = QLabel()
        layout.addRow('Info', self.update_info_label)

        # Data
        self.__package = None

    def updateFromCurrentPackage(self):
        pass

    @classmethod
    def getUserChoice(cls):
        pass
