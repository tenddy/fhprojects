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
from lib import dut_connect
from lib.log import Logger
from lib.fhlib import OLT_V5
from lib.fhlib import OLT_V4

CONNECT_DUT_ERROR = 1


class ServiceConfig():
    def __init__(self, tn_obj, log_obj):
        self.log__ = log_obj
        self.tn__ = tn_obj
        if self.tn__ is None:
            print("connect DUT Error!")
            exit(-1)

    def __del__(self):
        pass

    def send_cmd(self, cmdline,  promot=b"#", timeout=5, delay=0):
        """
        函数功能：通过Telnet下发命令到设备
        """
        try:
            cmd_ret = "Admin# "  # 返回参数
            for item in cmdline:
                self.tn__.write(bytes(item, encoding='utf8'))
                ret = self.tn__.read_until(promot, timeout).decode('utf-8')
                print(ret)
                cmd_ret = cmd_ret + ret
                if len(item) == 0:
                    continue
                time.sleep(delay)
            self.log__.log_info(cmd_ret)
            return cmd_ret
        except Exception as err:
            print("send cmd Error!!!")
            self.log__.log_error("Error:" + err)
            return None


def verify_string_match(dst_str, cmp_str):
    '''
    @func: 查找目的字符串dst_str中是否存在指定的字符串（字符串列表cmp_str）
    @dst_str:str
    @cmp_str:list
    @return: bool
    '''
    ret = 0
    for s in cmp_str:
        if s in dst_str:
            ret = 1
            break

    return bool(ret == 1)


def tc_reboot_system(host):
    tn_obj = dut_connect.connect_olt_telnet(host)
    log = Logger()

    if tn_obj is None:
        time.sleep(60)
        tn_obj = dut_connect.connect_olt_telnet(host)
    else:
        dut = ServiceConfig(tn_obj, log)
        dut.send_cmd(OLT_V4.reboot_system())
        tn_obj.close()
        del dut


def auth_onu_auto():
    log = Logger()
    # host = "35.35.35.109"
    host = '192.168.0.168'
    tn_obj = dut_connect.connect_olt_telnet(host, 8003)
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
    tn_obj.close()


def send_cmd_file(host, file):
    with open(file) as f:
        lines = f.readlines()
        log = Logger()
        tn_obj = dut_connect.connect_olt_telnet(host)
        dut_host = ServiceConfig(tn_obj, log)
        # dut_host.send_cmd(["config\n", "t l 0\n"])
        # print(len(lines), lines)
        # for line in lines:
        dut_host.send_cmd(lines)
        # dut_host.send_cmd(["quit\n", "quit\n"])


if __name__ == "__main__":
    host = '35.35.35.109'

    config = True
    tn = dut_connect.connect_olt_telnet(host, 23, username='admin', password='admin')
    tn.close()
    # if config:
    #     olt_config = r'./config/new_config.txt'
    #     send_cmd_file(host, olt_config)
    # else:
    #     olt_config = r'./config/new_config1.txt'
    #     send_cmd_file(host, olt_config)
