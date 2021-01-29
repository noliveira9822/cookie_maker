from PyQt5.QtGui import QPixmap

import Utils
from Utils import HLNK_calculate_frame


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
        app.cur_fun_stage = 0
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
        app.cur_fun_stage = 0
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
        app.cur_fun_stage = 0
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
        app.cur_fun_stage = 0
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
        app.cur_fun_stage = 0
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
        app.txt_logger.append("PLC Seletor Bolacha OK:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_seletor_bolacha_OK
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_stage = 0
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


def plc_selector_bolacha_NOK(stage, app, flag):
    mem_number = "0095"
    mem_pos = 8
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Seletor Bolacha NOK:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_selector_bolacha_NOK
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_busy = False
        app.cur_fun_stage = 0
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
def bolacha_insp(stage, app, resultado):
    mem_number = "0090"
    if (app.cur_fun_busy == False) and (stage == 0):
        app.cur_fun_busy = True
        app.cur_fun_callback = bolacha_insp
        app.cur_fun_stage = 1
        app.cur_fun_flag = resultado
        if resultado:
            app.txt_logger.append("PLC Bolacha OK:")
        else:
            app.txt_logger.append("PLC Bolacha NOK:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()

    elif stage == 1:  # send the result bit to the plc
        app.cur_fun_busy = True
        app.cur_fun_callback = bolacha_insp
        app.cur_fun_stage = 2
        app.cur_fun_flag = resultado

        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, 7)
        if resultado:
            integer = integer | mask
        else:
            integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()

    elif stage == 2:  # read the memory from the PLC
        app.cur_fun_busy = True
        app.cur_fun_callback = bolacha_insp
        app.cur_fun_stage = 3

        app.txt_logger.append("PLC Inspeção Completa Enable:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()

    elif stage == 3:  # write the memory with the inspection complete flag
        app.cur_fun_busy = True
        app.cur_fun_callback = bolacha_insp
        app.cur_fun_stage = 4

        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, 8)
        integer = integer | mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()

    elif stage == 4:  # read the memory again
        app.cur_fun_busy = True
        app.cur_fun_callback = bolacha_insp
        app.cur_fun_stage = 5

        app.txt_logger.append("PLC Inspeção Completa Disable:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", mem_number + "0001")
        app.send_message()

    elif stage == 5:  # place the inspection complete flag back to zero
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        app.cur_fun_stage = 0

        data = app.message_received[7:11]
        integer = int(data, 16)
        mask = pow(2, 8)
        integer = integer & ~mask

        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "WD",
                                                   mem_number + format(integer, "X").zfill(4))
        app.send_message()


'''
Functions for maintenance
'''


def plc_refresh(stage, app, flag):
    mem_number = "00000012"  # read 6 registers =  12 words
    if (app.cur_fun_busy == False) and (stage == 0):
        app.txt_logger.append("PLC Ler Counters:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RH", mem_number)
        app.send_message()
        app.cur_fun_busy = True
        app.cur_fun_callback = plc_refresh
        app.cur_fun_stage = 1
        app.cur_fun_flag = flag
    elif stage == 1:
        app.cur_fun_stage = 2
        app.cur_fun_callback = plc_refresh
        data_massa = app.message_received[7:15]
        data_recheio = app.message_received[15:23]
        data_hours = app.message_received[23:31]
        data_man_massa = app.message_received[31:39]
        data_man_recheio = app.message_received[39:47]
        data_man_hours = app.message_received[47:55]
        horas_count = int(data_hours, 16)
        horas_manutencao = int(data_man_hours, 16)
        app.lbl_horas_trabalho.setText(str(round(horas_count / 60)))
        app.lbl_horas_manutencao.setText(str(round(horas_manutencao / 60)))
        app.lbl_numero_descargas_massa.setText(str(int(data_massa, 16)))
        app.lbl_massa_manutencao.setText(str(int(data_man_massa, 16)))
        app.lbl_numero_descargas_recheio.setText(str(int(data_recheio, 16)))
        app.lbl_recheio_manutencao.setText(str(int(data_man_recheio, 16)))
        #mem_temp = "0105"
        massa_type = "0100"
        app.txt_logger.append("PLC Temperatura Forno:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", massa_type + "0006")
        app.send_message()
    elif stage == 2:
        app.cur_fun_busy = True
        app.cur_fun_stage = 3
        app.cur_fun_callback = plc_refresh

        data_massa = app.message_received[7:11]
        tipo_massa = str(int(data_massa, 16))
        app.lbl_tipo_massa.setText(tipo_massa)

        data_rech = app.message_received[11:15]
        tipo_rech = str(int(data_rech, 16))
        app.lbl_tipo_recheio.setText(tipo_rech)

        temp_target = app.message_received[15:19]
        target = str(int(temp_target, 16))

        data_tmp = app.message_received[27:31]
        tipo_tmp = str(int(data_tmp, 16))
        app.lbl_valor_temperatura.setText(tipo_tmp)

        app.txt_logger.append("PLC Ler Alarmes:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", "0095" + "0001")
        app.send_message()
    elif stage == 3:
        app.cur_fun_busy = True
        app.cur_fun_stage = 4
        app.cur_fun_callback = plc_refresh
        data = app.message_received[7:11]
        integer = int(data, 16)
        alarme_massa = pow(2, 5) & integer
        alarme_recheio = pow(2, 6) & integer
        alarme_temp = pow(2, 7) & integer
        if alarme_massa > 0:
            app.lbl_estado_massa.setPixmap(QPixmap(Utils.STATE_RED))
        else:
            app.lbl_estado_massa.setPixmap(QPixmap(Utils.STATE_GREEN))
        if alarme_recheio > 0:
            app.lbl_estado_recheio.setPixmap(QPixmap(Utils.STATE_RED))
        else:
            app.lbl_estado_recheio.setPixmap(QPixmap(Utils.STATE_GREEN))
        if alarme_temp > 0:
            app.lbl_estado_temperatura.setPixmap(QPixmap(Utils.STATE_RED))
        else:
            app.lbl_estado_temperatura.setPixmap(QPixmap(Utils.STATE_GREEN))

        app.txt_logger.append("PLC Estado Atual:")
        app.message_to_send = HLNK_calculate_frame(app.edt_num_plc.text(), "RD", "0000" + "0001")
        app.send_message()

    elif stage == 4:
        app.cur_fun_busy = False
        app.cur_fun_callback = None
        app.cur_fun_stage = 0
        data = app.message_received[7:11]
        app.lbl_estado_atual.setText(str(int(data, 16)))


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


def refresh_interface(app):
    plc_refresh(0, app, True)
