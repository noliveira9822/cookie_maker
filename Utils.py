import asyncio
import time
from functools import reduce
from operator import xor

import cv2
from PyQt5 import Qt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QErrorMessage
from serial import PARITY_EVEN, PARITY_NONE, PARITY_ODD
from serial.tools.list_ports import comports

CAMERA_CLOSED_IMAGE = ":/icon/images/black.png"
IPCA_IMAGE = ":/icon/images/ipca.png"
STATE_GREEN = ":/state_lights/images/green.png"
STATE_YELLOW = ":/state_lights/images/yellow.png"
STATE_RED = ":/state_lights/images/red.png"


# opencv image conversion and display on pixmap
def img2map(image):
    height, width, channel = image.shape
    bytesPerLine = 3 * width
    qimage = QImage(image.data, width, height, bytesPerLine, QImage.Format_BGR888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


# fcs calculation for hostlink message
def compute_fcs(msg):
    return format(reduce(xor, map(ord, msg)), 'X')


# message calculation for hostlink
def HLNK_calculate_frame(node, cmd, data):
    header = "@"
    fcs = compute_fcs(f'@{node}{cmd}{data}')
    terminator = "*\r"
    fullmsg = f"{header}{node}{cmd}{data}{fcs}{terminator}"
    return fullmsg


# make plc enter monitor mode
def plc_monitor_mode_msg(app):
    app.txt_logger.append("PLC Monitor Mode:")
    app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "SC", "02")
    app.send_message()


def plc_modo_automatico_msg(stage, app, flag):
    mem_number = "0098"  # memory number to be read written
    mem_pos = 0  # memory position
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Automatic Mode:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()  # send reading command
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_modo_automatico_msg  # read function callback
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]  # read data on the memory
        integer = int(data, 16)  # convert data to integer
        mask = pow(2, mem_pos)  # create a mask for bit operation
        if flag:  # bit operation
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()  # send the correct bit changed


def plc_dispensador_massa_msg(stage, app, flag):
    mem_number = "0095"
    mem_pos = 0
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Dispensar Massa:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_dispensador_massa_msg
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_dispensador_recheio_msg(stage, app, flag):
    mem_number = "0095"
    mem_pos = 1
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Dispensar Recheio:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_dispensador_recheio_msg
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_forno_msg(stage, app, flag):
    mem_number = "0095"
    mem_pos = 2
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Output Forno:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_forno_msg
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag == True:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_tapete_msg(stage, app, flag):
    mem_number = "0095"
    mem_pos = 4
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.txt_logger.append("PLC Output Tapete:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_tapete_msg
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_seletor_bolacha_OK(stage, app, flag):
    mem_number = "0095"
    mem_pos = 3
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Seletor Bolacha:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_seletor_bolacha_OK
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()


# function to control ok and nok cookies
def bolacha_insp(app, resultado):
    plc_cookie_ok_nok(0, app, resultado)
    plc_cookie_inspection_end(0, app, True)
    time.sleep(0.1)
    plc_cookie_inspection_end(0, app, False)


def plc_cookie_ok_nok(stage, app, flag):
    mem_number = "0090"
    mem_pos = 7
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Bolacha OK NOK:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_cookie_ok_nok
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_cookie_inspection_end(stage, app, flag):
    mem_number = "0090"
    mem_pos = 8
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.txt_logger.append("PLC Inspeção Completa:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_cookie_inspection_end
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()


'''
Functions for maintenance
'''


def plc_work_hours(stage, app, flag):
    mem_number = "00040002"  # read 2 bytes
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Work Hours:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RH", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_work_hours
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:15]
        integer = int(data, 16)
        if integer == 0:
            integer = 1
        app.lbl_horas_trabalho.setText(round(integer / 60))


def plc_counters(stage, app, flag):
    mem_number = "00000006"  # read 2 bytes
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Counters:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RH", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_counters
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data_massa = app.message_received[7:15]
        data_recheio = app.message_received[15:23]
        app.lbl_numero_descargas_massa.setText(int(data_massa, 16))
        app.lbl_numero_descargas_recheio.setText(int(data_recheio, 16))


def plc_counter_recheio(stage, app, flag):
    mem_number = "00020002"  # read 2 bytes
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.txt_logger.append("PLC Counter recheio:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RH", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_counter_recheio
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:15]
        integer = int(data, 16)
        app.lbl_numero_descargas_recheio.setText(integer)


'''
Function for normal modes
'''


def plc_current_state(stage, app, flag):
    mem_number = "0000"
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.txt_logger.append("PLC Estado Atual:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_current_state
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        app.lbl_estado_atual.setText(integer)


def plc_temperatura_forno(stage, app, flag):
    mem_number = "0105"
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Temperatura Forno:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_temperatura_forno
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        app.lbl_valor_temperatura.setText(integer)


def plc_alarmes(stage, app, flag):
    mem_number = "0095"  # read 2 bytes
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Alarmes:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_alarmes
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:15]
        integer = int(data, 16)
        alarme_massa = pow(2, 5) & integer
        alarme_recheio = pow(2, 6) & integer
        ãlarme_temp = pow(2, 7) & integer
        if alarme_massa > 0:
            app.lbl_estado_massa.setPixmap(QPixmap(":/state_lights/images/red.png"))
        else:
            app.lbl_estado_massa.setPixmap(QPixmap(":/state_lights/images/green.png"))
        if alarme_recheio > 0:
            app.lbl_estado_recheio.setPixmap(QPixmap(":/state_lights/images/red.png"))
        else:
            app.lbl_estado_recheio.setPixmap(QPixmap(":/state_lights/images/green.png"))
        if alarme_recheio > 0:
            app.lbl_estado_temperatura.setPixmap(QPixmap(":/state_lights/images/red.png"))
        else:
            app.lbl_estado_temperatura.setPixmap(QPixmap(":/state_lights/images/green.png"))


def list_ports():
    '''
    Test the ports and returns a tuple with the available ports and the ones that are working.
    '''
    is_working = True
    dev_port = 0
    working_ports = []
    available_ports = []
    while is_working:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            is_working = False
            print("Port %s is not working." % dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print("Port %s is working and reads images (%s x %s)" % (dev_port, h, w))
                working_ports.append(str(dev_port))
        dev_port += 1
    return working_ports


'''
Class and setup for serial comms
'''


def setup_serial(item):
    for port in comports(include_links=False):
        item.combo_comport.addItem(f"{port[0]} {port.description}", port)

    for baud_rate in (9600, 19200, 38400, 57600, 115200):
        item.combo_baudrate.addItem(str(baud_rate), baud_rate)

    item.combo_data_bits.addItem("7", 7)
    item.combo_data_bits.addItem("8", 8)

    item.combo_parity.addItem("None", PARITY_NONE)
    item.combo_parity.addItem("Odd", PARITY_ODD)
    item.combo_parity.addItem("Even", PARITY_EVEN)

    item.combo_stop_bits.addItem("1", 1)
    item.combo_stop_bits.addItem("2", 2)

    item.edt_num_plc.setText("00")


'''
Function to output and receive data from serial port
'''


class Output(asyncio.Protocol):
    def __init__(self):
        super(Output, self).__init__()
        self.recv_callback = None

    def connection_made(self, transport):
        self.transport = transport
        self.buf = bytes()

        print('port opened')
        print(transport)

    def set_recv_callback(self, func):
        self.recv_callback = func

    def test_comm(self):
        node = '00'
        header = 'TS'
        data = 'TEST'
        message = f'@{node}{header}{data}'
        fcs = compute_fcs(message)
        terminator = '*\r'

        # transport.serial.rts = False  # You can manipulate Serial object via transport
        self.transport.serial.write(message.encode('ascii'))
        self.transport.serial.write(fcs.encode('ascii'))
        self.transport.serial.write(terminator.encode('ascii'))

    def data_received(self, data):
        """Store characters until a newline is received.
        """
        self.buf += data
        if b'\r' in self.buf:
            lines = self.buf.split(b'\r')
            self.buf = lines[-1]  # whatever was left over
            for line in lines[:-1]:
                print(f'Reader received: {line.decode()}')
                self.recv_callback(line.decode())

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        print('resume writing')

    async def send(self, message):
        self.transport.serial.write(message.encode('ascii'))
        print(f'Writer sent: {message}')


# This code shows a window if any error occurs in the program
def display_error(err):
    app = QApplication.instance()
    window = app.activeWindow()
    dialog = QErrorMessage(window)
    dialog.setWindowModality(Qt.WindowModal)
    dialog.setWindowTitle("Error")
    dialog.showMessage(err)


def plc_selector_bolacha_NOK(stage, app, flag):
    mem_number = "0095"
    mem_pos = 8
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Seletor Bolacha:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_selector_bolacha_NOK
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()
