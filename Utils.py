import cv2
import asyncio
import time
from PyQt5.QtGui import QImage, QPixmap
from functools import reduce
from operator import xor
from serial.tools.list_ports import comports
from serial import PARITY_EVEN, PARITY_NONE, PARITY_ODD

#opencv image conversion and display on pixmap
def img2map(image):
    height, width, channel = image.shape
    bytesPerLine = 3 * width
    qimage = QImage(image.data, width, height, bytesPerLine, QImage.Format_BGR888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap

#fcs calculation for hostlink message
def compute_fcs(msg):
    return format(reduce(xor, map(ord, msg)), 'X')

#message calculation for hostlink
def HLNK_calculate_frame(node, cmd, data):
    header = "@"
    fcs = compute_fcs(f'@{node}{cmd}{data}')
    terminator = "*\r"
    fullmsg = f"{header}{node}{cmd}{data}{fcs}{terminator}"
    return fullmsg

#make plc enter monitor mode
def plc_monitor_mode_msg(app):
    app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "SC", "02")
    app.send_message()


def plc_modo_automatico_msg(stage, app, flag):
    mem_number = "0098"                                                 #memory number to be read written
    mem_pos = 0                                                         #memory position
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number)
        app.send_message()                                              #send reading command
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_modo_automatico_msg                  #read function callback
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[5:9]                                #read data on the memory
        integer = int(data, 16)                                         #convert data to integer
        mask = pow(2, mem_pos)                                          #create a mask for bit operation
        if flag == True:                                                #bit operation
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD", mem_number + format(integer, "X").zfill(4))
        app.send_message()                                              #send the correct bit changed


def plc_dispensador_massa_msg(stage, app, flag):
    mem_number = "95"
    mem_pos = 0
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_dispensador_massa_msg
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[5:9]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag == True:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD", mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_dispensador_recheio_msg(stage, app, flag):
    mem_number = "0095"
    mem_pos = 1
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_dispensador_recheio_msg
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[5:9]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag == True:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD", mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_forno_msg(stage, app, flag):
    mem_number = "0095"
    mem_pos = 2
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_forno_msg
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[5:9]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag == True:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD", mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_tapete_msg(stage, app, flag):
    mem_number = "0095"
    mem_pos = 4
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_tapete_msg
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[5:9]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag == True:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD", mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_seletor_bolacha_msg(stage, app, flag):
    mem_number = "0095"
    mem_pos = 3
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_seletor_bolacha_msg
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[5:9]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag == True:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD", mem_number + format(integer, "X").zfill(4))
        app.send_message()


def plc_cookie_ok_nok(stage, app, flag):
    mem_number = "0090"
    mem_pos = 7
    if ((app.cur_fun_busy == False) and (stage == 0)):
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_cookie_ok_nok
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[5:9]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag == True:
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
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_cookie_inspection_end
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        data = app.message_received[5:9]
        integer = int(data, 16)
        mask = pow(2, mem_pos)
        if flag == True:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD", mem_number + format(integer, "X").zfill(4))
        app.send_message()


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
