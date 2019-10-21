# -*- encoding: utf-8 -*-
''' 
@File    : FHAT.py
@Date    : 2019/08/13 08:18:10
@Author  : Teddy.tu
@Version : V1.0
@EMAIL   : teddy_tu@126.com
@License : (c)Copyright 2019-2020, Teddy.tu
@Desc    : None
'''

import time
import argparse
from dut_connct import connect_olt_telnet
from base_cmd.log import Logger
from fhlib import OLT_V5
from fhlib import OLT_V4

CONNECT_DUT_ERROR = 1


class ServiceConfig():
    def __init__(self, tn_obj, log_obj):
        self.log__ = log_obj
        self.tn__ = tn_obj
        if self.tn__ is None:
            print("connect DUT Error!")
            return None

    def __del__(self):
        if self.tn__ is not None:
            self.tn__.close()
            # del self.filelog__
            # del self.console__
            # self.log__.close()
            print("__del__ func....")

    def send_cmd(self, cmdline, promot=b"#", timeout=5):
        """
        函数功能：通过Telnet下发命令到设备
        """
        try:
            cmd_ret = "Admin#"          # 返回参数
            cli_s = cmdline.split("\n")
            for cmd in cli_s:
                if len(cmd) == 0:
                    continue
                self.tn__.write(bytes(cmd + '\n', encoding='utf8'))
                cmd_ret = cmd_ret + self.tn__.read_until(promot, timeout).decode('utf-8')

            self.log__.log_info(cmd_ret)
            print(cmd_ret)
            return cmd_ret
        except Exception as err:
            print("send cmd Error")
            # log__ = log.Logger(self.filelog)
            # log__.log_info("Error!")
            self.log__.log_info("Error!")
            return None


def tc_reboot_system(host):
    tn_obj = connect_olt_telnet(host)
    log = Logger(logfile="log_test.log")

    if tn_obj is None:
        time.sleep(60)
        tn_obj = connect_olt_telnet(host)
    else:
        dut = ServiceConfig(tn_obj, log)
        dut.send_cmd(OLT_V4.reboot_system())
    time.sleep(900)


if __name__ == "__main__":
    # test_at = ServiceConfig("10.182.5.71")

    # cli = OLT_V5.add_uplink_vlan(uplinkslot=9, uplinkport=1, vlan_mode="tag", vlan_begin=100, vlan_end=100)

    # cli = OLT_V4.reboot_system()
    # test_at.send_cmd(cli)
    while(True):
        tc_reboot_system("10.182.5.71")
