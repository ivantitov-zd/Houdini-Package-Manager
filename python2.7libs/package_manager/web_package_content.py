try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from .link_label import LinkLabel
from .github import ownerAndRepoName, repoURL, installFromGitHubRepo
from .web_package import WebPackage
from .houdini_license import fullHoudiniLicenseName
from .package_status import fullPackageStatusName


class WebPackageInfoView(QWidget):
    # Signals
    installed = Signal(WebPackage)

    def __init__(self):
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

        self.name_label = QLabel()
        self.name_label.setWordWrap(True)
        info_block_layout.addRow('Name', self.name_label)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        info_block_layout.addRow('Description', self.desc_label)

        self.author_label = QLabel()
        self.author_label.setWordWrap(True)
        info_block_layout.addRow('Author', self.author_label)

        self.hversion_label = QLabel()
        self.hversion_label.setWordWrap(True)
        info_block_layout.addRow('Houdini', self.hversion_label)

        self.hlicense_label = QLabel()
        self.hlicense_label.setWordWrap(True)
        info_block_layout.addRow('License', self.hlicense_label)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        info_block_layout.addRow('Status', self.status_label)

        self.source_label = LinkLabel()
        self.source_label.setWordWrap(True)
        info_block_layout.addRow('Source', self.source_label)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

        self.install_button = QPushButton('Download and Install')
        self.install_button.setDisabled(True)
        self.install_button.clicked.connect(self._onInstall)
        main_layout.addWidget(self.install_button)

        # Data
        self.web_package = None

    def updateFromCurrentPackage(self):
        if self.web_package is None:
            self.self.name_label.setText('')
            self.desc_label.setText('')
            self.author_label.setText('')
            self.hversion_label.setText('')
            self.hlicense_label.setText('')
            self.status_label.setText('')
            self.source_label.setText('')
            self.install_button.setDisabled(True)
            return
        self.name_label.setText(self.web_package.name)
        self.desc_label.setText(self.web_package.description)
        self.author_label.setText(self.web_package.author)
        self.hversion_label.setText(self.web_package.hversion or '*')
        self.hlicense_label.setText(fullHoudiniLicenseName(self.web_package.hlicense) or 'Commercial')
        self.status_label.setText(fullPackageStatusName(self.web_package.status) or 'Stable')
        if self.web_package.source != 'Unknown':
            self.source_label.setText('GitHub: ' + self.web_package.source)
            self.source_label.setLink(repoURL(*ownerAndRepoName(self.web_package.source)))
        else:
            self.source_label.setText(self.web_package.source)
            self.source_label.setLink(None)
        self.install_button.setEnabled(True)

    def setWebPackage(self, web_package_item):
        self.web_package = web_package_item
        self.updateFromCurrentPackage()

    def _onInstall(self):
        if self.web_package.source_type == 'github':
            installFromGitHubRepo(self.web_package)
        self.web_package = None
        self.updateFromCurrentPackage()
        self.installed.emit()
