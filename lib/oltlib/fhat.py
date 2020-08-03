#!/usr/bin/env python
# coding=UTF-8
'''
@Desc: None
@Author: Teddy.tu
@Version: V1.0
@EMAIL: teddy_tu@126.com
@License: (c)Copyright 2019-2020, Teddy.tu
@Date: 2020-01-12 21:24:26
@LastEditors: Teddy.tu
@LastEditTime: 2020-07-27 13:34:55
'''

import pandas as pd
import time
import configparser
import os
import sys
import traceback

try:
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
    from lib.oltlib import fhlib
    from lib.public.fhlog import logger, log_decare
    from lib.public import dut_connect
    from lib import settings
except Exception as err:
    print("添加项目路径失败.")
    print(err)

MAX_CONNECT_TIMES = 3   # 最大连接次数
OLT_VERSION_5K = 'V4'
OLT_VERSION_6K = 'V5'


class FHATException(Exception):
    """Base class for FHSTCException"""


class FHATCMDError(FHATException):
    def __init__(self, command, error_message, stderr=''):
        self.command = command
        self.error_message = error_message.strip()
        self.stderr = stderr
        super().__init__(self.__str__())

    def __str__(self):
        msg = 'FHATCMDError raised while executing the command:"%s"\n error_message: "%s"' % (
            self.command, self.error_message)
        if self.stderr:
            msg += '\n stderr: %s' % (self.stderr)
        logger.error(msg)
        return msg


class FH_OLT():
    def __init__(self, version=OLT_VERSION_6K):
        self.hostip = None  # IP地址
        self.hostport = None  # 连接设备端口号
        self.login_promot = dict()  # 登录提示符
        self.version = version  # 版本信息

        # 登录OLT telnet对象
        self.__tn = None
        self.connectTimes = 0

        # 需要执行的命令行
        self.__cmdlines = []

        # 保存命令行运行log
        # self.__ret = ""

        # 命令执行结果, True -- 命令行执行成功； False -- 命令行执行失败
        self.cmd_ret = True

    def __del__(self):
        self.disconnet_olt()
        del self.__cmdlines

    def __setattr__(self, name, value):
        return super().__setattr__(name, value)

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def parser_fholt_logincfg(self, configfile=r'config/config.ini'):
        """
        解析配置文件/etc/config.ini, 获取OLT的登录信息
        """
        parser = configparser.ConfigParser()
        parser.read(os.path.join(os.getcwd(), self.configfile))

        self.hostip = parser.get('OLT', 'ip')
        self.hostport = parser.get('OLT', 'port')
        self.login_promot = {}
        self.login_promot['Login'] = parser.get('OLT', 'username')
        self.login_promot['Password'] = parser.get('OLT', 'password')
        self.login_promot['User'] = parser.get('OLT', 'user')

    def init_olt(self):
        """初始化OLT的配置,获取OLT的登录信息"""
        self.hostip = settings.OLT_IP
        self.hostport = settings.TELNET_PORT
        self.login_promot = settings.OLT_LOGIN

        if settings.OLT_VERSION.startswith("AN5"):
            self.version = OLT_VERSION_5K
        elif settings.OLT_VERSION.startswith("AN6"):
            self.version = OLT_VERSION_6K
        else:
            raise FHATCMDError('init_olt', "获取OLT版本异常.")

    def connect_olt(self, *args):
        """
        连接OLT
        """
        connectTimes = 0
        try:
            if self.hostip is None:  # 如果没有配置hostip,默认调用setting文件中OLT的配置
                self.init_olt()

            while self.__tn is None and connectTimes < MAX_CONNECT_TIMES:
                connectTimes += 1
                print("Trying connect  %s of %d times!" % (self.hostip, connectTimes))
                self.__tn = dut_connect.dut_connect_telnet(
                    host=self.hostip, port=self.hostport, login_promot=self.login_promot, promot='#')
            else:
                if connectTimes >= MAX_CONNECT_TIMES:
                    print("Connected to Device(%s) Timeout!" % self.hostip)
                    sys.exit(-1)
        except Exception as err:
            raise FHATCMDError('connect_olt', "连接OLT失败.")

    def disconnet_olt(self):
        """
        断开连接
        """
        if self.__tn is not None:
            print("Disconnect Device(%s)!" % self.hostip)
            self.__tn.close()
            self.__tn = None

    def append_cmdlines(self, *args):
        """ 添加命令行"""
        for item in args:
            if isinstance(item, list):
                self.__cmdlines.extend(item)
            elif isinstance(item, tuple):
                self.__cmdlines.extend(list(item))
            else:
                self.__cmdlines.append(item)

    @log_decare
    def sendcmdlines(self, cmdlines=None, promot=b"#", timeout=5, delay=0):
        """
        函数功能
            下发命令到设备
        函数参数:
            @para cmdlines:
                命令行列表， 如果为none，下发self.__cmdline中的命令
            @para promot:
                命令行之后完成之后提示符
            @para timeout:
                命令执行超时时间，单位s
            @para delay:
                命令执行间隔时间，单位s
        """
        try:
            if self.__tn is None:
                self.connect_olt()
            if cmdlines is not None:
                self.append_cmdlines(cmdlines)

            if self.version == OLT_VERSION_6K:
                self.__cmdlines.insert(0, 'config\n')
                self.__cmdlines.append("quit\n")
            logger.debug("send command to device...")

            while len(self.__cmdlines) != 0:
                item = self.__cmdlines.pop(0)
                if len(item.strip()) == 0:
                    continue
                logger.debug("cmd:"+item)
                self.__tn.write(bytes(item, encoding='utf8'))
                cmd_rets = ''
                while True:  # 判断执行命令是否执行完成
                    ret = self.__tn.read_until(promot, timeout)
                    cmd_rets += ret.decode("utf-8")
                    if promot not in ret:
                        self.__tn.write(bytes(" ", encoding='utf8'))
                    else:
                        break
                logger.info(cmd_rets)
                return cmd_rets

                time.sleep(delay)
        except Exception as err:
            raise FHATCMDError("sendcmdlines", "send cmd Failed!", traceback.format_exc())

    def verify_cmds_exec(self, err_str=['failed', 'error', 'unknown command']):
        """
        函数功能：
            校验命令执行是否成功;

        函数参数：
            @para err_str: 字符串
            校验匹配的字符串

        函数返回参数: 布尔类型
            检查返回的结果中是否存在err_str中的字符串；
            如果不存在，命令执行成功，返回True；否则命令执行失败，返回False
        """
        rets = self.__ret.lower()
        self.cmd_ret = not verify_string_match(rets, err_str)
        return self.cmd_ret

    def get_card_status(self, slotno):
        """
        获取线卡状态
        """
        show_card_cmd = []
        if self.version == "V4":
            show_card_cmd = fhlib.OLT_V4.show_card()
        if self.version == "V5":
            show_card_cmd = fhlib.OLT_V5.show_card()

        ret = self.sendcmdlines(show_card_cmd)
        slot_status = ret.split('\n')[4:][slotno-1].strip().split()
        self.disconnet_olt()
        return dict(zip(('CARD', 'EXIST', 'CONFIG', 'DETECT', 'DETAIL'), slot_status))

    def get_card_version(self, slotno):
        self.disconnet_olt()

    def get_maincard_version(self, backup=False):
        ret = self.sendcmdlines(fhlib.OLT_V5.show_debugversion(backup))
        version_info = ret.split('\n')[-2].strip()[-20:]
        print("compiled:", version_info)
        self.disconnet_olt()

        return version_info

    # def get_cmds_execute(self, cmds_func, *args, **kargs):
    #     """ 获取返回状态信息 """
    #     try:
    #         exec_cmds = cmds_func(*args, **kargs)
    #         ret = self.sendcmdlines(exec_cmds)
    #         self.disconnet_olt()
    #         return ret
    #     except Exception as err:
    #         raise FHATCMDError('get_cnds_execute', '获取执行命令返回状态信息失败', traceback.format_exc())


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


# def auth_onu_auto():
#     log = Logger()
#     # host = "35.35.35.109"
#     host = '192.168.0.168'
#     tn_obj = dut_connect.dut_connect_telnet(host, 8003)
#     # a = tn_obj.read_until(b"#")
#     # print(str(a, encoding='utf8'))
#     dut_host = ServiceConfig(tn_obj, log)

#     cmd_ret = dut_host.send_cmd(["config\n", "t l 0\n"])
#     # s_cmd = cmd_ret.split('\n')
#     onuid = 1
#     while True:
#         cmd_ret = dut_host.send_cmd(["show discovery 1/17/8\n"])
#         s_cmd = cmd_ret.split('\n')
#         print(len(s_cmd))
#         if len(s_cmd) >= 8:
#             for index in range(4, len(s_cmd)-3):
#                 # print(len(s_cmd),  s_cmd[index])
#                 onu_info = s_cmd[index].split()
#                 if len(onu_info) == 0:
#                     break

#                 print("onu_info:", onu_info)
#                 print("onuid:", onuid)
#                 auth_str = 'whitelist add phy-id %s type %s slot 17 pon 8 onuid %d\n' % (
#                     onu_info[2], onu_info[1], 129-onuid)
#                 ret = dut_host.send_cmd([auth_str])
#                 if -1 == ret.find("failed") or -1 == ret.find("Unknown"):
#                     onuid = onuid + 1
#                     print("onuid:", onuid)
#         time.sleep(5)
#     tn_obj.close()


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
    # debug_func()
    pass
