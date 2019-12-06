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
        pass
        # if self.tn__ is not None:
        #     self.tn__.close()
        # del self.filelog__
        # del self.console__
        # self.log__.close()

        print("__del__ func....")
        del self

    def send_cmd(self, cmdline,  promot=b"#", timeout=5):
        """
        函数功能：通过Telnet下发命令到设备
        """
        try:
            cmd_ret = "Admin# "  # 返回参数
            for item in cmdline:
                # print("debug:", item)
                self.tn__.write(item.encode('utf-8'))
                cmd_ret = cmd_ret + self.tn__.read_until(promot, timeout).decode('utf-8')
                if len(item) == 0:
                    continue

            print("debug:info log")
            self.log__.log_info(cmd_ret)
            # print(cmd_ret)
            return cmd_ret
        except Exception as err:
            print("send cmd Error!!!")
            # log__ = log.Logger(self.filelog)
            # log__.log_info("Error!")
            self.log__.log_error("Error!")
            return None


def verify_string_match(dst_str, cmp_str):
    '''
    '''
    ret = 0
    for s in cmp_str:
        if s in dst_str:
            ret = 1
            break

    if ret == 1:
        return True
    else:
        return False


def tc_reboot_system(host):
    tn_obj = connect_olt_telnet(host)
    # log = Logger(logfile="log_test.log")
    log = Logger()

    if tn_obj is None:
        time.sleep(60)
        tn_obj = connect_olt_telnet(host)
    else:
        dut = ServiceConfig(tn_obj, log)
        dut.send_cmd(OLT_V4.reboot_system())
        tn_obj.close()
        del dut


if __name__ == "__main__":
    log = Logger()
    host = "35.35.35.109"
    tn_obj = connect_olt_telnet(host)
    dut_host = ServiceConfig(tn_obj, log)
    # dut_host.send_cmd('config\n')

    cli = OLT_V5.add_uplink_vlan(uplinkslot=9, uplinkport=1, vlan_mode="tag", vlan_begin=100, vlan_end=100)
    dut_host.send_cmd(cli)

    # reboot OLT
    # while (True):
    #     tc_reboot_system("10.182.5.81")
    #     time.sleep(600)
    #     print("waiting for 600s...")

    # read config cli and send to DUT
    # config = r'E:/中试项目/5000转6000/广西/config_bak/6000config/10.182.5.68_FTTB_AN6000_s3p5.txt'
    # with open(config, 'r') as f:
    #     # print(f)
    #     commandlines = f.readlines()
    #     for command in commandlines:
    #         print("command:", command)
    #         ret = dut_host.send_cmd(command)
    #         print(ret)
    #         if verify_string_match(str(ret), ['Unknown', 'error', 'failed']) or ret is None:
    #             print("Error!---" + command)
    #             input("press ENTER to continue...")
    # tn_obj.close()
