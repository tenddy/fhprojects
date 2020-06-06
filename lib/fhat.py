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
import configparser
import os
import numpy as np
import pandas as pd
from lib import dut_connect
from lib.log import Logger
from lib import fhlib


MAX_CONNECT_TIMES = 3   # 最大连接次数


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
                if len(item) == 0:
                    continue
                print(item)
                self.tn__.write(bytes(item, encoding='utf8'))
                ret = self.tn__.read_until(promot, timeout).decode('utf-8')
                print(ret)
                self.log__.log_info(ret)
                cmd_ret = cmd_ret + ret
                time.sleep(delay)
            return cmd_ret
        except Exception as err:
            print("send cmd Error!!!")
            self.log__.log_error("Error:" + err)
            return None


class FH_OLT():
    def __init__(self, configfile=r'config/config.ini', logfie=None):
        self.configfile = configfile
        # 解析配置文件
        parser = configparser.ConfigParser()
        parser.read(os.path.join(os.getcwd(), self.configfile))

        self.oltip = parser.get('OLT', 'ip')
        self.oltport = parser.get('OLT', 'port')
        self.login_promot = {}
        self.login_promot['Login'] = parser.get('OLT', 'Login')
        self.login_promot['Password'] = parser.get('OLT', 'Password')
        self.login_promot['User'] = parser.get('OLT', 'User')

        self.version = parser.get('OLT', 'Version')

        # 登录OLT telnet对象
        self.__olttn = None
        self.connectTimes = 0
        # self.__olttn = dut_connect.dut_connect_telnet(host= self.oltip, port=self.oltport, login_promot=self.login_promot, promot='#')

        # 命令行
        self.__cmdlines = []

        # 返回命令行显示
        self.__ret = ""

        # 命令执行结果, True -- 命令行执行成功； False -- 命令行执行失败
        self.cmd_ret = True

    def __del__(self):
        self.disconnet_olt()
        del self.__cmdlines
        del self.__ret

    def __setattr__(self, name, value):
        return super().__setattr__(name, value)

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def set_hostip(self, hostip):
        self.oltip = hostip

    def get_olt_config(self):
        """
        解析配置文件/etc/config.ini
        """
        parser = configparser.ConfigParser()
        print(self.configfile)
        parser.read(os.path.join(os.getcwd(), self.configfile))
        print("Sections:", parser.sections())
        print('items:', parser.items('OLT'))

    def connect_olt(self, *args):
        """
        连接OLT
        """
        while self.__olttn is None and self.connectTimes < MAX_CONNECT_TIMES:
            self.connectTimes += 1
            print("Try to connect to %s of %d times!" % (self.oltip, self.connectTimes))
            self.__olttn = dut_connect.dut_connect_telnet(
                host=self.oltip, port=self.oltport, login_promot=self.login_promot, promot='#')

    def disconnet_olt(self):
        """
        断开连接
        """
        if self.__olttn is not None:
            print("Disconnect Host!")
            self.__olttn.close()
            self.__olttn = None

    def append_cmdlines(self, *args):
        for item in args:
            if type(item) is list:
                self.__cmdlines.extend(item)
            elif type(item) is tuple:
                self.__cmdlines.extend(list(item))
            else:
                self.__cmdlines.append(item)

    def sendcmdlines(self, cmdlines=None, promot=b"#", timeout=5, delay=0):
        """
        @函数功能
            下发命令到设备
        @函数参数

        @
        """
        try:
            if self.__olttn is None:
                self.connect_olt()
            cmdlines = self.__cmdlines if cmdlines is None else cmdlines
            cmd_rets = ""  # 返回参数
            print("send command to device...")
            for item in cmdlines:
                if len(item) == 0:
                    continue
                self.__olttn.write(bytes(item, encoding='utf8'))
                ret = self.__olttn.read_until(promot, timeout).decode("utf-8")
                # if 'Ctr+C' in ret:
                #     self.__olttn.write(bytes(" ", encoding='utf8'))
                #     ret += self.__olttn.read_until(promot, timeout).decode("utf-8")
                # self.log__.log_info(ret)
                print(ret)
                cmd_rets += ret
                time.sleep(delay)
            self.__ret += cmd_rets
            return cmd_rets
        except Exception as err:
            print("send cmd Failed!\nError:", err)
            # self.log__.log_error("Error:" + err)
            return None

    def verify_sendcmdlines(self, err_str=['failed', 'error', 'unknown command']):
        """
        @函数功能：
            校验命令执行是否成功：
            检查返回的结果中是否存在err_str中的字符串；
            如果不存在，命令执行成功，返回True；否则命令执行失败，返回False

        @函数参数：
        @err_str: 匹配的字符串
        """
        rets = self.__ret.lower()
        self.cmd_ret = not verify_string_match(rets, err_str)
        return self.cmd_ret

    def get_card_status(self, slotno):
        """
        @函数功能：获取线卡状态
        """
        if self.version == "V4":
            print("get card status of AN5516.")
            ret = self.sendcmdlines(fhlib.OLT_V4.show_card())
            slot_status = ret.split('\n')[4:][slotno-1].strip().split()

            # return {'CARD': slot_status[0], 'EXIST': slot_status[1], 'CONFIG': slot_status[2], 'DETECT': slot_status[3], 'DETAIL': slot_status[4]}
        if self.version == "V5":
            print("get card satus of AN6000.")
            ret = self.sendcmdlines(fhlib.OLT_V5.show_card())
            slot_status = ret.split('\n')[4:][slotno-1].strip().split()
        self.disconnet_olt()
        return {'CARD': slot_status[0], 'EXIST': slot_status[1], 'CONFIG': slot_status[2], 'DETECT': slot_status[3], 'DETAIL': slot_status[4]}

    def get_card_version(self, slotno):
        self.disconnet_olt()

    def get_control_version(self, backup=False):
        ret = self.sendcmdlines(fhlib.OLT_V5.show_debugversion(backup))
        version_info = ret.split('\n')[-2].strip()[-20:]
        print("compiled:", version_info)
        self.disconnet_olt()


class FH_UNM():
    # 通过TL1连接UNM
    def __init__(self):
        pass

    def __del__(self):
        pass

    def connect_unm(self):
        pass

    def disconnect_unm(self):
        pass

    def sendcmd_tl1(self, cmdlines, promot=b"#", timeout=5, delay=0):
        pass


def get_data_excel(filename, sheets=0):
    """
    函数功能:通过excel文件获取ONU信息，返回格式为DataFrame
        Excel文件格式为：
    """
    data = pd.read_excel(filename, sheet_name=sheets)
    return data


def verify_string_match(dst_str, cmp_str):
    '''
    @函数功能:
     查找目的字符串dst_str中是否存在指定的字符串（字符串列表cmp_str）
    @函数参数：
        dst_str:str
        cmp_str:list
        return: bool
    '''
    ret = 0
    for s in cmp_str:
        if s in dst_str:
            ret = 1
            break

    return bool(ret == 1)


def auth_onu_auto():
    log = Logger()
    # host = "35.35.35.109"
    host = '192.168.0.168'
    tn_obj = dut_connect.dut_connect_telnet(host, 8003)
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
        tn_obj = dut_connect.dut_connect_telnet(host)
        dut_host = ServiceConfig(tn_obj, log)
        dut_host.send_cmd(lines)


def upgrad_olt_batch(filename, backup=False):
    for ip in range(8):
        fholt_obj = FH_OLT()
        fholt_obj.oltip = '10.182.33.%d' % (182+ip)
        fholt_obj.connect_olt()
        # backup_status = bool(fholt_obj.get_card_status(10)['EXIST'] == "YES")
        cmds = fhlib.OLT_V5.load_program(filename, backup=backup)
        print("upgrade %s\n" % fholt_obj.oltip, cmds)
        fholt_obj.append_cmdlines(cmds)
        fholt_obj.sendcmdlines()
        print(fholt_obj.cmd_ret)


if __name__ == "__main__":
    fholt_obj = FH_OLT()
    # fholt_obj.get_olt_config()
    fholt_obj.get_control_version()
    fholt_obj.get_control_version(True)
    # fholt_obj.oltip = '10.182.33.182'
    # fholt_obj.login_promot = {'Login': 'admin', 'Password': 'admin'}

    # cmds = ['config\n',  'show oltqinq-domain vlan_range_1\n']
    # cmds = ['']
    # fholt_obj.connect_olt()
    # print(fholt_obj.verify_sendcmdlines())
    # status = fholt_obj.get_card_status(2)
    # print(status['DETAIL'])
    # cmds = ['config\n']
    # qinq_test = 'qinq_test'

    # cmds += fhlib.OLT_V5.create_oltqinq_domain(qinq_test, {'uprule': ((7, 100, 4), (7, 200, 3)), 'vlanrule': (
    #     100, 'null', 'translation', 33024, 201, 1, 'null', 'null', 'add', 33024, 2701, 1)}, {'vlanrule': (
    #         1001, 'null', 'transparent', 33024, 'null', 'null', 'null', 'null', 'add', 33024, 2701, 1)})
    # cmds += fhlib.OLT_V5.attach_oltqinq(qinq_test, 2, 8, 65)
    # cmds += fhlib.OLT_V5.deattach_oltqinq(qinq_test, 2, 8, 65)
    # cmds += fhlib.OLT_V5.del_oltqinq(qinq_test)
    fholt_obj.disconnet_olt()

    upgrad_olt_batch('hswd_20200424.bin', True)
