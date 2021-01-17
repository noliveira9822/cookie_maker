import sys
import threading
import time
import asyncio
import traceback

import cv2
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QComboBox, \
    QLabel, QPlainTextEdit, QErrorMessage

from qasync import QEventLoop
from functools import wraps

from serial_asyncio import create_serial_connection

import Utils
from ui_files import resources

'''
Coroutines taken from turbohostlink
'''


def display_error(err):
    app = QApplication.instance()
    window = app.activeWindow()
    dialog = QErrorMessage(window)
    dialog.setWindowModality(Qt.WindowModal)
    dialog.setWindowTitle("Error")
    dialog.showMessage(err)


def slot_coroutine(async_func):
    if not asyncio.iscoroutinefunction(async_func):
        raise RuntimeError('Must be a coroutine!')

    def log_error(future):
        try:
            future.result()
        except Exception as err:
            display_error(traceback.format_exc())

    @wraps(async_func)
    def wrapper(self, *args):
        loop = asyncio.get_event_loop()
        future = loop.create_task(async_func(self, *args[:-1]))
        future.add_done_callback(log_error)

    return wrapper


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
    videoThread.setDaemon(True)
    videoThread.start()
    window.btn_start.setEnabled(False)
    window.btn_stop.setEnabled(True)


def stopVideo():
    global videoThread
    if videoThread.isRunning():
        videoThread.stop()
    window.btn_start.setEnabled(True)
    window.btn_stop.setEnabled(False)
    window.lbl_image.setPixmap(QPixmap("ui_files/images/black.png"))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, loop):
        super(MainWindow, self).__init__()
        uic.loadUi("ui_files/MainWindow.ui", self)
        self.setWindowTitle("Manual Remote Control")
        self.setWindowIcon(QIcon(":/icon/images/ipca.png"))
        self.lbl_image.setPixmap(QPixmap(":/icon/images/black.png"))
        self.lbl_image.setScaledContents(True)

        self.lbl_estado_massa.setPixmap(QPixmap(":/state_lights/images/green.png"))
        self.lbl_estado_recheio.setPixmap(QPixmap(":/state_lights/images/green.png"))
        self.lbl_estado_temperatura.setPixmap(QPixmap(":/state_lights/images/green.png"))

        # setup hostlink
        self.loop = loop

        # signals & slots
        self.btn_start.clicked.connect(startVideo)
        self.btn_stop.clicked.connect(stopVideo)
        self.combo_indice_camera.addItems(Utils.list_ports())

        Utils.setup_serial(self)
        self.btn_connect.clicked.connect(self.open_port)
        self.btn_disconnect.clicked.connect(self.close_port)

        # show interface
        self.show()

    @slot_coroutine
    async def send_message(self):
        msg = self.output_field.text()
        await self.port.send(msg)
        # msg = msg.rstrip('\r')
        # self.response_field.appendPlainText(f"PC -> {msg}")

    def recv_message(self, msg):
        msg = msg.rstrip('\r')
        # self.response_field.appendPlainText(f"PLC -> {msg}")

    @slot_coroutine
    async def open_port(self):
        port = self.combo_comport.currentData()
        data_bits = self.combo_data_bits.currentData()
        stop_bits = self.combo_stop_bits.currentData()
        parity = self.combo_parity.currentData()
        bauds = self.combo_baudrate.currentData()

        self.serial_coro = create_serial_connection(self.loop,
                                                    Utils.Output,
                                                    url=port[0],
                                                    bytesize=data_bits,
                                                    stopbits=stop_bits,
                                                    parity=parity,
                                                    baudrate=bauds)

        self.transport, self.port = await self.serial_coro

        self.port.set_recv_callback(self.recv_message)

        self.btn_connect.setDisabled(True)
        self.btn_disconnect.setDisabled(False)
        # self.send_button.setDisabled(False)

    def close_port(self):
        self.loop.stop()
        self.btn_connect.setDisabled(False)
        self.btn_disconnect.setDisabled(True)
        # self.send_button.setDisabled(True)


if __name__ == "__main__":
    print('Loading user interface...')
    QApp = QtWidgets.QApplication(sys.argv)
    resources.qInitResources()
    QApp.setStyle("Fusion")

    loop = QEventLoop(QApp)

    window = MainWindow(loop)
    window.show()

    with loop:
        loop.run_forever()
    # creates global threads variables to be used through whole file
    videoThread = None
    print("All initialized")

    sys.exit(QApp.exec_) #app was not being termianted correctly with sys.exit(QApp.exec())
