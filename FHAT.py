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
from dut_connect import connect_olt_telnet
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
                self.tn__.write(bytes(item, encoding='utf8'))
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


def auth_onu():
    log = Logger()
    # host = "35.35.35.109"
    host = '192.168.0.168'
    tn_obj = connect_olt_telnet(host, 8003)
    # a = tn_obj.read_until(b"#")
    # print(str(a, encoding='utf8'))
    dut_host = ServiceConfig(tn_obj, log)

    cmd_ret = dut_host.send_cmd(["config\n", "t l 0\n"])
    # s_cmd = cmd_ret.split('\n')
    onuid = 1
    while True:
        cmd_ret = dut_host.send_cmd(["show discovery 1/17/8\n"])
        s_cmd = cmd_ret.split('\n')
        print(len(s_cmd))
        if len(s_cmd) >= 8:
            for index in range(4, len(s_cmd)-3):
                # print(len(s_cmd),  s_cmd[index])
                onu_info = s_cmd[index].split()
                if len(onu_info) == 0:
                    break

                print("onu_info:", onu_info)
                print("onuid:", onuid)
                auth_str = 'whitelist add phy-id %s type %s slot 17 pon 8 onuid %d\n' % (
                    onu_info[2], onu_info[1], 129-onuid)
                ret = dut_host.send_cmd([auth_str])
                if -1 == ret.find("failed") or -1 == ret.find("Unknown"):
                    onuid = onuid + 1
                    print("onuid:", onuid)
        time.sleep(5)

    # for index in s_cmd:
    #     print(index)
    # time.sleep(10)

    tn_obj.close()


def send_cmd_file(file):
    with open(file) as f:
        lines = f.readlines()
        log = Logger()
        host = '35.35.35.109'
        tn_obj = connect_olt_telnet(host)
        dut_host = ServiceConfig(tn_obj, log)
        dut_host.send_cmd(["config\n", "t l 0\n"])
        # print(len(lines), lines)
        # for line in lines:
        dut_host.send_cmd(lines)


if __name__ == "__main__":
    olt_config = r'e:/old_config.txt'
    send_cmd_file(olt_config)
