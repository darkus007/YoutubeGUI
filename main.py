import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide2 import QtCore, QtWidgets
from main_window import Ui_MainWindow
from youtube import MyYouTuBe


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.button_get.clicked.connect(self.button_click)

        self.ui.line_edit_url.setText('https://www.youtube.com/watch?v=t5Bo1Je9EmE')

        self.thread = {}

    def button_click(self):
        self.thread[1] = ThreadClass(self, index=1)
        self.ui.progress_bar.setValue(0)
        self.thread[1].start()
        self.thread[1].progress_bar_signal.connect(self.progress_bar_update)

    def progress_bar_update(self, value):
        self.ui.progress_bar.setValue(value)


class ThreadClass(QtCore.QThread, MyYouTuBe):
    progress_bar_signal = QtCore.Signal(int)

    def __init__(self, parent=None, index=0):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        self.parent = parent
        self.file_size = 0
        self.progress_bar_value = 0

    def run(self) -> None:
        print(f'Start thread {self.index}')

        url = window.ui.line_edit_url.text()
        super(MyYouTuBe, self).__init__(url=url)
        self.register_on_complete_callback(self.on_complete)
        self.register_on_progress_callback(self.on_progress)
        self.parent.ui.text_browser.append(f'Title:\t"{self.title}"')
        self.parent.ui.text_browser.append(f'Author:\t"{self.author}"')
        self.parent.ui.text_browser.append('Size:\t{:= 3d} bytes'.format(self.best_video_size))
        self.file_size = self.best_video_size
        self.download_best_video()

    def stop(self):
        self.is_running = False
        print(f'Stop thread {self.index}')
        self.terminate()

    def on_progress(self, stream, chunk, bytes_remaining):
        percent = (self.file_size - bytes_remaining) / self.file_size
        self.parent.ui.text_browser.append(f'Downloaded:\t{int(percent * 100)} %')
        # self.parent.ui.progress_bar.setValue(int(percent * 100))
        # self.parent.update()
        self.progress_bar_signal.emit(int(percent * 100))
        # print(f'Downloaded: {percent:.0%}', end='\r')

    def on_complete(self, stream, path: str):
        self.parent.ui.text_browser.append("\nFile saved as:\n" + path)
        # print('Done')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle('YouTube downloader')
    window.show()
    sys.exit(app.exec_())
