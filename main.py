import os
import sys
import platform
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2 import QtCore
from main_window import Ui_MainWindow
from youtube import MyYouTuBe, MyPlayList


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.button_get.clicked.connect(self.button_click)
        self.thread = {}

    def button_click(self):
        self.ui.text_browser.clear()
        self.thread[1] = ThreadClass(self, index=1)
        self.ui.progress_bar.setValue(0)
        self.thread[1].start()
        self.thread[1].progress_bar_signal.connect(self.progress_bar_update)

    def progress_bar_update(self, value):
        self.ui.progress_bar.setValue(value)

    def append_text_browser_message(self, msg):
        self.ui.text_browser.append(msg)
        self.ui.text_browser.verticalScrollBar().setValue(self.ui.text_browser.verticalScrollBar().maximum())


class ThreadClass(QtCore.QThread, MyYouTuBe):
    progress_bar_signal = QtCore.Signal(int)

    def __init__(self, parent=None, index=0):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        self.parent = parent
        self.file_size = 0
        self.progress_bar_value = 0
        self.download_is_done = False

    def run(self) -> None:
        self.parent.ui.button_get.setEnabled(False)
        self.download_is_done = False

        url = window.ui.line_edit_url.text()

        # trying to download a playlist
        try:
            play_list = MyPlayList(url)
            folder = play_list.title        # rise KeyError if the url does not contain a playlist
            try:
                os.mkdir('video/' + folder)
            except Exception as ex:
                print(ex)

            count = 1
            max_count = len(play_list)

            for url in play_list.video_urls:
                i = 0
                while i < 3:        # three attempts to download content
                    i += 1
                    try:
                        self.parent.append_text_browser_message(f'[{count}|{max_count}]')
                        super(MyYouTuBe, self).__init__(url=url)
                        self.register_on_complete_callback(self.on_complete)
                        self.register_on_progress_callback(self.on_progress)
                        self.parent.append_text_browser_message(f'Title:\t"{self.title}"\n'
                                                                f'Author:\t"{self.author}"')
                        self.parent.append_text_browser_message(f'Size:\t{self.best_video_size: ,} bytes')
                        self.file_size = self.best_video_size
                        self.download_best_video(path='video/' + folder)
                        count += 1
                        break
                    except Exception as ex:
                        self.parent.append_text_browser_message(f'{ex}. Try again...')

        # else download one best video
        except KeyError:
            try:
                super(MyYouTuBe, self).__init__(url=url)
                self.register_on_complete_callback(self.on_complete)
                self.register_on_progress_callback(self.on_progress)
                self.parent.append_text_browser_message(f'Title:\t"{self.title}"\n'
                                                        f'Author:\t"{self.author}"')
                self.parent.append_text_browser_message(f'Size:\t{self.best_video_size: ,} bytes')
                self.file_size = self.best_video_size
                self.download_best_video()
            except Exception as ex:              # PytubeError
                self.parent.append_text_browser_message(f'ERROR:\t{ex}"')

        finally:
            self.parent.ui.button_get.setEnabled(True)

    def stop(self):
        self.is_running = False
        self.terminate()
        self.parent.ui.button_get.setEnabled(True)

    def on_progress(self, stream, chunk, bytes_remaining):
        percent = (self.file_size - bytes_remaining) / self.file_size
        self.parent.append_text_browser_message(f'Downloaded:\t{int(percent * 100)} %')
        self.progress_bar_signal.emit(int(percent * 100))

    def on_complete(self, stream, path: str):
        self.parent.append_text_browser_message("File saved as:\n" + path)

        # CheckBox "Open folder after download"
        if self.parent.ui.check_box_open_folder.isChecked():
            current_system = platform.system().lower()
            if current_system in ('linux', 'darwin'):
                os.system(f'open {os.path.curdir}/video')  # macos/linux
            elif current_system == 'windows':
                os.system(f'start {os.path.curdir}/video')  # windows


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle('YouTube downloader')
    window.show()
    sys.exit(app.exec_())
