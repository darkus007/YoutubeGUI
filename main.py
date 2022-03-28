import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from main_window import Ui_MainWindow


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle('YouTube downloader')
    window.show()
    sys.exit(app.exec_())

