import webbrowser

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


def is_link(url: str) -> bool:
    return url.startswith(('http:', 'https:', 'ftp:', 'www.', 'file:'))


class LinkLabel(QLabel):
    def __init__(self, text: str = '', link: str | None = None) -> None:
        super(LinkLabel, self).__init__(text)

        self.setToolTip('Open Link')
        self.setStyleSheet('QLabel::hover { color: rgb(40, 123, 222); }')

        self.__link = None
        self.set_link(link)

        # Menu
        self.menu = QMenu(self)
        self.menu.addAction('Copy', lambda: QApplication.clipboard().setText(self.__link))

    def link(self) -> str | None:
        return self.__link

    def set_link(self, url: str) -> None:
        if not url:
            url = self.text()
        if is_link(url):
            self.__link = url
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.__link = None
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and self.__link:
            webbrowser.open(self.__link)
        elif event.button() == Qt.RightButton and self.__link:
            self.menu.exec_(event.globalPos())
        else:
            super(LinkLabel, self).mouseReleaseEvent(event)
