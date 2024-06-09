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

from .link_label import LinkLabel
from . import github
from .web_package import WebPackage
from .houdini_license import fullHoudiniLicenseName
from .package_status import fullPackageStatusName


class WebPackageInfoView(QWidget):
    # Signals
    installed = Signal(WebPackage)

    def __init__(self) -> None:
        super(WebPackageInfoView, self).__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        info_block_layout = QFormLayout()
        info_block_layout.setContentsMargins(4, 0, 0, 0)
        info_block_layout.setSpacing(4)
        info_block_layout.setHorizontalSpacing(10)
        info_block_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignTop)
        main_layout.addLayout(info_block_layout)

        name_label = QLabel('Name')
        name_label.setAlignment(Qt.AlignTop)
        self.name_info = QLabel()
        self.name_info.setWordWrap(True)
        info_block_layout.addRow(name_label, self.name_info)

        desc_label = QLabel('Description')
        desc_label.setAlignment(Qt.AlignTop)
        self.desc_info = QLabel()
        self.desc_info.setWordWrap(True)
        info_block_layout.addRow(desc_label, self.desc_info)

        author_label = QLabel('Author')
        author_label.setAlignment(Qt.AlignTop)
        self.author_info = QLabel()
        self.author_info.setWordWrap(True)
        info_block_layout.addRow(author_label, self.author_info)

        hversion_label = QLabel('Houdini')
        hversion_label.setAlignment(Qt.AlignTop)
        self.hversion_info = QLabel()
        self.hversion_info.setWordWrap(True)
        info_block_layout.addRow(hversion_label, self.hversion_info)

        hlicense_label = QLabel('License')
        hlicense_label.setAlignment(Qt.AlignTop)
        self.hlicense_info = QLabel()
        self.hlicense_info.setWordWrap(True)
        info_block_layout.addRow(hlicense_label, self.hlicense_info)

        status_label = QLabel('Status')
        status_label.setAlignment(Qt.AlignTop)
        self.status_info = QLabel()
        self.status_info.setWordWrap(True)
        info_block_layout.addRow(status_label, self.status_info)

        source_label = QLabel('Source')
        source_label.setAlignment(Qt.AlignTop)
        self.source_info = LinkLabel()
        self.source_info.setWordWrap(True)
        info_block_layout.addRow(source_label, self.source_info)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

        self.install_button = QPushButton('Download and Install')
        self.install_button.setDisabled(True)
        self.install_button.clicked.connect(self._onInstall)
        main_layout.addWidget(self.install_button)

        # Data
        self.web_package = None

    def clear(self) -> None:
        self.name_info.setText('')
        self.desc_info.setText('')
        self.author_info.setText('')
        self.hversion_info.setText('')
        self.hlicense_info.setText('')
        self.status_info.setText('')
        self.source_info.setText('')
        self.install_button.setDisabled(True)

    def updateFromCurrentPackage(self) -> None:
        if self.web_package is None:
            self.clear()
            return

        try:
            self.name_info.setText(self.web_package.name)
            self.desc_info.setText(self.web_package.description or github.repoDescription(self.web_package) or '-')
            self.author_info.setText(self.web_package.author or '-')
            self.hversion_info.setText(self.web_package.hversion or '*')
            self.hlicense_info.setText(fullHoudiniLicenseName(self.web_package.hlicense) or 'Commercial')
            self.status_info.setText(fullPackageStatusName(self.web_package.status) or 'Stable')
            if self.web_package.source != '-':
                self.source_info.setText('GitHub: ' + self.web_package.source)
                self.source_info.setLink(github.repoURL(*github.ownerAndRepoName(self.web_package.source)))
            else:
                self.source_info.setText(self.web_package.source)
                self.source_info.setLink(None)
            self.install_button.setEnabled(True)
        except Exception:  # Todo
            self.clear()

    def setWebPackage(self, web_package_item: WebPackage) -> None:
        self.web_package = web_package_item
        self.updateFromCurrentPackage()

    def _onInstall(self) -> None:
        if self.web_package.source_type == 'github':
            if not github.installFromRepo(self.web_package):
                return  # Cancelled
        self.web_package = None
        self.updateFromCurrentPackage()
        hou.ui.setStatusMessage('Successfully installed',
                                hou.severityType.ImportantMessage)
        self.installed.emit(self.web_package)
