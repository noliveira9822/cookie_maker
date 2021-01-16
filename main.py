import sys
import threading
import time

import cv2
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon, QPixmap

import Utils

'''
Thread to record video
'''


class VideoThread(threading.Thread):

    def __init__(self, camera) -> None:
        super().__init__()
        self.camera = cv2.VideoCapture(camera)
        self.stopped = False

    def stop(self):
        self.stopped = True
        if self.camera.isOpened():
            self.camera.release()

    def run(self) -> None:
        while True:
            if self.stopped:
                self.stopped = False
                return
            grabFrame(self.camera)
            time.sleep(0.1)

    def isRunning(self) -> bool:
        return not self.stopped


def grabFrame(camera):
    ret, image = camera.read()
    image = cv2.flip(image, 1)
    window.lbl_image.setPixmap(Utils.img2map(image))


def startVideo():
    global videoThread
    videoThread = VideoThread(int(window.combo_indice_camera.currentText()))
    videoThread.start()
    window.btn_start.setEnabled(False)
    window.btn_stop.setEnabled(True)


def stopVideo():
    global videoThread
    if videoThread.isRunning():
        videoThread.stop()
    window.btn_start.setEnabled(True)
    window.btn_stop.setEnabled(False)
    window.lbl_image.setPixmap(QPixmap("ui_files/black.png"))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("ui_files/MainWindow.ui", self)
        self.setWindowTitle("Manual Remote Control")
        self.setWindowIcon(QIcon("ui_files/ipca.png"))
        self.lbl_image.setPixmap(QPixmap("ui_files/black.png"))
        self.lbl_image.setScaledContents(True)

        # signals & slots
        self.btn_start.clicked.connect(startVideo)
        self.btn_stop.clicked.connect(stopVideo)
        self.combo_indice_camera.addItems(Utils.list_ports())

        # show interface
        self.show()


if __name__ == "__main__":
    print('Loading user interface...')
    QApp = QtWidgets.QApplication(sys.argv)
    QApp.setStyle("Fusion")
    window = MainWindow()
    window.show()

    # creates global threads variables to be used through whole file
    videoThread = None
    print("All initialized")

    sys.exit(QApp.exec())
