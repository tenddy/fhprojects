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
import dut_connect
from log import Logger
from log import log_decare
from fhlib import OLT_V5
from fhlib import OLT_V4


class ServiceConfig():
    def __init__(self, tn_obj, log_obj=None):
        self.tn__ = tn_obj
        if log_obj is None:
            self.log__ = Logger()
        else:
            self.log__ = log_obj

        self.cmd_ret = "Admin# "
        if self.tn__ is None:
            print("connect DUT Error!")
            exit(-1)

    def __del__(self):
        self.tn__.close()
        del self.log__

    
    def send_cmd(self, cmdline, delay=0, promot=b"#", timeout=5):
        """
        功能：下发命令到设备
        参数：
        @cmdline (list): 需要下发的命令行
        @delay (int): 下发命令的间隔时间（单位s)
        @promot (byte): 命令行等待返回字符
        @timout (int): 命令下发超时时间
        返回值： cmd_ret 或者 None
        """
        try:
            for item in cmdline:
                if len(item) == 0:
                    continue
                self.tn__.write(bytes(item, encoding='utf8'))
                ret = self.tn__.read_until(promot, timeout).decode('utf-8')
                self.log__.info(ret)
                self.cmd_ret += ret
                time.sleep(delay)
        except Exception as err:
            self.cmd_ret  += "Error: %s" % err
        
        return self.cmd_ret

    @log_decare
    def notify(self):
        return self.cmd_ret


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


def auth_onu_auto():
    '''
    @功能: 自动授权ONU 
    @参数:
    @返回值: 
    '''
    log = log.Logger()
    host = '192.168.0.168'
    tn_obj = dut_connect.connect_olt_telnet(host, 8003)
    dut_host = ServiceConfig(tn_obj, log)
    cmd_ret = dut_host.send_cmd(["config\n", "t l 0\n"])
    onuid = 1
    while True:
        cmd_ret = dut_host.send_cmd(["show discovery 1/17/8\n"])
        s_cmd = cmd_ret.split('\n')
        print(len(s_cmd))
        if len(s_cmd) >= 8:
            for index in range(4, len(s_cmd)-3):
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


if __name__ == "__main__":
    print('test:', 'FHAT.py')
    host = '35.35.35.109'
    config = True
    # tn = dut_connect.connect_olt_telnet(host, 23, username='admin', password='admin')
    # tn.close()
    # if config:
    #     olt_config = r'./config/new_config.txt'
    #     send_cmd_file(host, olt_config)
    # else:
    #     olt_config = r'./config/new_config1.txt'
    #     send_cmd_file(host, olt_config)

    # tn.close()
    print("finish")
