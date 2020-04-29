from __future__ import print_function

import webbrowser

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *


def isLink(url):
    return url.startswith(('http:', 'https:', 'ftp:', 'www.', 'file:'))


class LinkLabel(QLabel):
    def __init__(self, text='', link=None):
        super(LinkLabel, self).__init__(text)

        self.setToolTip('Open Link')
        self.setStyleSheet('QLabel::hover { color: rgb(40, 123, 222); }')

        self.__link = None
        self.setLink(link)

        # Menu
        self.menu = QMenu(self)
        self.menu.addAction('Copy', lambda: QApplication.clipboard().setText(self.__link))

    def link(self):
        return self.__link

    def setLink(self, url):
        if not url:
            url = self.text()
        if isLink(url):
            self.__link = url
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.__link = None
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.__link:
            webbrowser.open(self.__link)
        elif event.button() == Qt.RightButton and self.__link:
            self.menu.exec_(event.globalPos())
        else:
            super(LinkLabel, self).mouseReleaseEvent(event)
