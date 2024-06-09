from PySide2.QtWidgets import QCheckBox
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtWidgets import QSpacerItem
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from package_manager.update_options import UpdateOptions


class SettingsWidget(QWidget):
    def __init__(self) -> None:
        super(SettingsWidget, self).__init__()

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Updating
        self.check_on_startup_toggle = QCheckBox('Check for updates on startup')
        self.check_on_startup_toggle.toggled.connect(UpdateOptions().set_check_on_startup)
        main_layout.addWidget(self.check_on_startup_toggle)

        self.update_settings()

        spacer = QSpacerItem(0, 10, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

        # form_layout = QFormLayout()
        # form_layout.setContentsMargins(0, 0, 0, 0)
        # form_layout.setSpacing(4)
        # form_layout.setHorizontalSpacing(8)
        # main_layout.addLayout(form_layout)

        # # Installation
        # self.path_field = QLineEdit('$HOUDINI_USER_PREF_DIR')
        # form_layout.addRow('Installation Path', self.path_field)
        #
        # buttons_layout = QHBoxLayout()
        # main_layout.addLayout(buttons_layout)
        #
        # spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        # buttons_layout.addSpacerItem(spacer)
        #
        # save_button = QPushButton('Save')
        # buttons_layout.addWidget(save_button)
        #
        # revert_button = QPushButton('Revert')
        # buttons_layout.addWidget(revert_button)

    def update_settings(self) -> None:
        self.check_on_startup_toggle.blockSignals(True)
        self.check_on_startup_toggle.setChecked(UpdateOptions().check_on_startup())
        self.check_on_startup_toggle.blockSignals(False)
