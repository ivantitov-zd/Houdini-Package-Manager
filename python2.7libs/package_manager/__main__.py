import sys

try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    from PySide2.QtWidgets import QApplication

from .window import MainWindow

try:
    import hou
except ModuleNotFoundError:
    input('This application works with Hython only. Press Enter to exit...')
    hou.exit(1)

app = QApplication(sys.argv)
window = MainWindow()
exit_code = app.exec_()
sys.exit(exit_code)
