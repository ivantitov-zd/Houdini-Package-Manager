try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou


class SettingsWidget(QWidget):
    def __init__(self):
        super(SettingsWidget, self).__init__()

        # Layout
        layout = QFormLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Installation
        self.path_field = QLineEdit('$HOUDINI_USER_PREF_DIR')
        layout.addRow('Installation path', self.path_field)
