import sys
import threading
import time
import asyncio
import traceback

import cv2
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer
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


# Function that allows a function to be executed assincronously
def slot_coroutine(async_func):
    if not asyncio.iscoroutinefunction(async_func):
        raise RuntimeError('Must be a coroutine!')

    def log_error(future):
        try:
            future.result()
        except Exception as err:
            Utils.display_error(traceback.format_exc())

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
    # serial tcommunitaction to enable automatic mode
    Utils.plc_modo_automatico_msg(0, window, 1)


def stopVideo():
    global videoThread
    if videoThread.isRunning():
        videoThread.stop()
    window.btn_start.setEnabled(True)
    window.btn_stop.setEnabled(False)
    window.lbl_image.setPixmap(QPixmap(Utils.CAMERA_CLOSED_IMAGE))
    # serial tcommunitaction to disable automatic mode
    Utils.plc_modo_automatico_msg(0, window, 0)


def refresh_interface():
    print("timer tick tick...")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, loop):
        super(MainWindow, self).__init__()
        uic.loadUi("ui_files/MainWindow.ui", self)
        self.setWindowTitle("Manual Remote Control")
        self.setWindowIcon(QIcon(Utils.IPCA_IMAGE))
        self.lbl_image.setPixmap(QPixmap(Utils.CAMERA_CLOSED_IMAGE))
        self.lbl_image.setScaledContents(True)

        self.lbl_estado_massa.setPixmap(QPixmap(Utils.STATE_GREEN))
        self.lbl_estado_recheio.setPixmap(QPixmap(Utils.STATE_YELLOW))
        self.lbl_estado_temperatura.setPixmap(QPixmap(Utils.STATE_RED))

        self.tab.setCurrentIndex(0)

        # setup variables needed for callbacks
        self.loop = loop
        self.cur_fun_callback = None
        self.message_received = ""
        self.cur_fun_busy = False
        self.cur_fun_stage = 0
        self.cur_fun_flag = False

        # signals & slots
        # camera
        self.btn_start.clicked.connect(startVideo)
        self.btn_stop.clicked.connect(stopVideo)
        self.combo_indice_camera.addItems(Utils.list_ports())

        self.btn_clear_log.clicked.connect(lambda: self.txt_logger.setText(""))
        # automatico
        # the lambda is here because the function needs to be callable
        self.btn_bolacha_ok.clicked.connect(lambda: Utils.bolacha_insp(self, True))
        self.btn_bolacha_not_ok.clicked.connect(lambda: Utils.bolacha_insp(self, False))
        # serial
        Utils.setup_serial(self)

        self.btn_connect.clicked.connect(self.open_port)
        self.btn_disconnect.clicked.connect(self.close_port)

        # manual
        self.btn_activar_massa.clicked.connect(lambda: Utils.plc_dispensador_massa_msg(0, self, True))
        self.btn_desactivar_massa.clicked.connect(lambda: Utils.plc_dispensador_massa_msg(0, self, False))
        self.btn_ativar_recheio.clicked.connect(lambda: Utils.plc_dispensador_recheio_msg(0, self, True))
        self.btn_desativar_recheio.clicked.connect(lambda: Utils.plc_dispensador_massa_msg(0, self, False))
        self.btn_ativar_tapete.clicked.connect(lambda: Utils.plc_tapete_msg(0, self, True))
        self.btn_desativar_tapete.clicked.connect(lambda: Utils.plc_tapete_msg(0, self, False))
        self.btn_ativar_saida_forno.clicked.connect(lambda: Utils.plc_forno_msg(0, self, True))
        self.btn_desativar_saida_forno.clicked.connect(lambda: Utils.plc_forno_msg(0, self, False))
        self.btn_ativar_separador.clicked.connect(lambda: Utils.plc_seletor_bolacha_msg(0, self, True))
        self.btn_desativar_separador.clicked.connect(lambda: Utils.plc_seletor_bolacha_msg(0, self, False))

        # show interface
        self.show()

    @slot_coroutine
    async def send_message(self):
        msg = self.message_to_send
        await self.port.send(msg)
        self.txt_logger.append("PC   --> " + msg.rstrip('\r'))

    def recv_message(self, msg):
        self.message_received = msg
        if self.cur_fun_callback is not None:
            self.cur_fun_callback(self.cur_fun_stage, self, self.cur_fun_flag)
            self.cur_fun_callback = None
            self.cur_fun_stage = 0
        self.txt_logger.append("PLC --> " + self.message_received)

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
        Utils.plc_monitor_mode_msg(window)
        refresh_timer.start(self.spin_tempo_atualizacao.value())

    def close_port(self):
        self.loop.stop()
        self.btn_connect.setDisabled(False)
        self.btn_disconnect.setDisabled(True)
        refresh_timer.stop()


if __name__ == "__main__":
    print('Loading user interface...')
    QApp = QtWidgets.QApplication(sys.argv)
    resources.qInitResources()
    QApp.setStyle("Fusion")

    loop = QEventLoop(QApp)
    window = MainWindow(loop)
    window.show()

    refresh_timer = QTimer()
    refresh_timer.timeout.connect(refresh_interface)

    videoThread = None
    print("All initialized")

    with loop:
        loop.run_forever()
    # creates global threads variables to be used through whole file

    sys.exit(QApp.exec_)  # app was not being terminated correctly with sys.exit(QApp.exec())
