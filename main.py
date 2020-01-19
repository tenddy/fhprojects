#!/usr/bin/python3
# coding=UTF-8
'''
@Description: 
@Author:  Teddy.tu
@Date: 2019-07-07 21:53:46
@LastEditTime : 2020-01-10 22:10:45
@LastEditors  :  Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''

import pandas as pd
from lib import log
from lib import dut_connect
from lib.fhlib import OLT_V5
from lib.fhat import ServiceConfig
from lib.fhat import send_cmd_file
import gpon
import EPON_FTTB

if __name__ == "__main__":
    # telnet OLT   
    oltip = '10.182.5.109'     
    tn_obj = dut_connect.dut_connect_telnet(oltip, 23, 'admin', 'admin')
    log_obj = log.Logger(r'./log/service.log')
    cmd_send_obj = ServiceConfig(tn_obj, log_obj)
    
    # TL1 
    unm_ip = '10.182.1.161'
    unm_user, unm_pwd = 'admin', 'admin123'
    unm_tn = dut_connect.dut_connect_tl1(unm_ip, username=unm_user, password=unm_pwd)
    tl1_cmd_obj = ServiceConfig(unm_tn, log.Logger(r'./log/tl1_log.log'))
    
    slotno = 17
    ponno = 4

    # EPON
    eponfile = r"./config/epon.xls"
    # send_tl1_cmds = EPON_FTTB.get
    
    # GPON
    gponfile = r"./config/gpon.xlsx"
    
    print("命令行.")
    for index in gpon.get_linecmds():
        print(index, end='')
    # cmd_send_obj.send_cmd(gpon.get_linecmds())
    
    print("TL1")
    for index in gpon.get_linecmds_tl1():
        print(index, end='')
    # tl1_cmd_obj.send_cmd(gpon.get_linecmds_tl1())
    
    

    # disconnet TL1
    dut_connect.dut_disconnect_tl1(unm_tn)

    