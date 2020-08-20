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

import time
import os
import sys
import traceback
import re

try:
    # print("cwd:", os.getcwd())
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
    from lib.oltlib.oltv5 import AN6K
    from lib.oltlib.oltv4 import AN5K
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
    def __init__(self, version=OLT_VERSION_6K, oltinfo=None):
        self.hostip = None  # IP地址
        self.hostport = None  # 连接设备端口号
        self.login_promot = dict()  # 登录提示符
        self.version = version  # 版本信息

        # 登录OLT telnet对象
        self.__tn = None
        self.connectTimes = 0

        # 需要执行的命令行
        self.__cmdlines = []

        # 命令行执行log记录
        self.__exec_cmd_ret = ""

        # 命令执行结果, True -- 命令行执行成功； False -- 命令行执行失败
        self.cmd_ret = True

    def __del__(self):
        self.disconnet_olt()
        del self.__cmdlines

    def __setattr__(self, name, value):
        return super().__setattr__(name, value)

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def init_olt(self, **kargs):
        """从配置文件中获取OLT信息，并初始化OLT的相关参数；
        格式如下：
            "OLT": {
                "OLT_VERSION": "AN6000-17",
                "OLT_IP": "10.182.33.185",
                "OLT_LOGIN": {'Login:': 'GEPON', 'Password:': 'GEPON'},
                "TELNET_PORT": 23,
            }
        """
        try:
            self.hostip = kargs['OLT_IP']
            self.hostport = kargs['TELNET_PORT']
            self.login_promot = kargs['OLT_LOGIN']

            if kargs['OLT_VERSION'].startswith("AN5"):
                self.version = OLT_VERSION_5K
            elif kargs['OLT_VERSION'].startswith("AN6"):
                self.version = OLT_VERSION_6K
            else:
                raise FHATCMDError('init_olt', "获取OLT版本异常.")

        except:
            raise FHATCMDError("init_olt", "初始化OLT失败")

    def connect_olt(self, **kargs):
        """
        连接OLT
        """
        connectTimes = 0
        try:
            if self.hostip is None:  # 如果没有配置hostip,默认调用setting文件中OLT的配置
                self.init_olt(**kargs)

            while self.__tn is None and connectTimes < MAX_CONNECT_TIMES:
                connectTimes += 1
                print("Trying connect  %s of %d times!" % (self.hostip, connectTimes))
                self.__tn = dut_connect.dut_connect_telnet(
                    host=self.hostip, port=self.hostport, login_promot=self.login_promot, promot='#')
            else:
                if connectTimes >= MAX_CONNECT_TIMES:
                    print("Connected to Device(%s) Timeout!" % self.hostip)
                    sys.exit(-1)
        except:
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

    def sendcmdlines(self, cmdlines=None, promot=b"#", timeout=5, delay=0.1):
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
                # raise FHATCMDError("sendcmdlines", "Please connect OLT before sendcmdlines.", traceback.format_exc()

            if cmdlines is not None:
                self.append_cmdlines(cmdlines)

            if self.version == OLT_VERSION_6K:
                self.__cmdlines.insert(0, 'config\n')
                self.__cmdlines.append("quit\n")
            logger.debug("send command to device...")

            self.__exec_cmd_ret = ""
            while len(self.__cmdlines) != 0:
                item = self.__cmdlines.pop(0)
                if len(item.strip()) == 0:
                    continue
                logger.debug("cmd:"+item)
                self.__tn.write(bytes(item, encoding='utf8'))

                while True:  # 判断执行命令是否执行完成
                    ret = self.__tn.read_until(promot, timeout)
                    self.__exec_cmd_ret += ret.decode("utf-8")
                    if promot not in ret:
                        self.__tn.write(bytes(" ", encoding='utf8'))
                    else:
                        break
                time.sleep(delay)

            logger.info(self.__exec_cmd_ret)
            return self.__exec_cmd_ret
        except:
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
        rets = self.__exec_cmd_ret.lower()
        self.cmd_ret = not verify_string_match(rets, err_str)
        if not self.cmd_ret:
            logger.error("命令执行失败")

        return self.cmd_ret

    def get_card_status(self, slotno):
        """
        获取线卡状态
        """
        show_card_cmd = []
        if self.version == "V4":
            show_card_cmd = AN5K.show_card()
        if self.version == "V5":
            show_card_cmd = AN6K.show_card()

        ret = self.sendcmdlines(show_card_cmd)
        slot_status = ret.split('\n')[4:][slotno-1].strip().split()
        self.disconnet_olt()
        return dict(zip(('CARD', 'EXIST', 'CONFIG', 'DETECT', 'DETAIL'), slot_status))

    def get_card_version(self, slotno):
        self.disconnet_olt()

    def get_maincard_version(self, backup=False):
        ret = self.sendcmdlines(AN6K.show_debugversion(backup))
        version_info = ret.split('\n')[-2].strip()[-20:]
        print("compiled:", version_info)
        self.disconnet_olt()

        return version_info

    def get_discovery_onu(self, slotno, ponno):
        """
        功能：
            获取未授权列表
        参数：
            @slotno：槽位号
            @ponno：pon口号
        返回值：dict()
            返回未授权ONU信息，格式为{"PhyId":("No", "OnuType", "PhyId", "PhyPwd", "LogicId", "LogicPwd", "Why")}
        """
        ret = self.sendcmdlines(AN6K.showDiscovery(slotno, ponno))
        ret_lines = ret.split("\r\n")
        p_len = list(map(len, ret_lines[4].split()))  # 获取占位长度
        unauthList = ret_lines[5:-4]  # 未授权ONU列表
        # title = ("No", "OnuType", "PhyId", "PhyPwd", "LogicId", "LogicPwd", "Why")
        unauthONU = dict()
        for item in unauthList:
            onuInfo = []
            start = end = 0
            for index in p_len:
                end = start + index
                onuInfo.append(item[start:end].rstrip())
                start = end + 1
            unauthONU[onuInfo[2]] = tuple(onuInfo)
        self.disconnet_olt()
        return unauthONU

    def get_authorization_onu(self, slotno, ponno):
        """
        功能：
            获取未授权列表
        参数：
            @slotno：槽位号
            @ponno：pon口号
        返回值：dict()
            返回已授权ONU信息，格式为{"PhyId":("Slot","Pon","Onu","OnuType","ST","Lic", "OST", "PhyId","PhyPwd","LogicId","LogicPwd")}
        """
        try:
            ret = self.sendcmdlines(AN6K.showAuthorization(slotno, ponno))
            authnum = re.findall(r'Total ITEM = (\d*)', ret)[0]
            if authnum == "0":    # 如果已授权ONU列表为空，则直接返回空字典
                return {}

            ret_lines = ret.split("\r\n")
            # print(ret_lines)
            p_len = list(map(len, ret_lines[8].split()))  # 获取占位长度
            authList = ret_lines[9:-3]  # 未授权ONU列表
            # print(authList)
            authONU = {}
            for item in authList:
                onuInfo = []
                start = end = 0
                for index in p_len:
                    end = start + index
                    onuInfo.append(item[start:end].rstrip())
                    start = end + 1
                authONU[onuInfo[7]] = tuple(onuInfo)
            self.disconnet_olt()
            return authONU
        except:
            logger.info("获取已授权ONU失败")
            return None

    def get_bandwithProfile(self):
        """获取所有的带宽模板"""
        try:
            ret = self.sendcmdlines(AN6K.show_bandwidth_prf())
            ret_lines = ret.split("\r\n")
            print(ret_lines)
            band_prf = {}
            return band_prf
        except:
            logger.info("获取带宽模板失败")
            return None


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


# def get_data_excel(filename, sheets=0):
#     """
#     函数功能:通过excel文件获取ONU信息，返回格式为DataFrame
#         Excel文件格式为：
#     """
#     data = pd.read_excel(filename, sheet_name=sheets)
#     return data


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


def upgrad_olt_batch(filename, backup=False):
    for ip in range(8):
        fholt_obj = FH_OLT()
        fholt_obj.hostip = '10.182.33.%d' % (182+ip)
        fholt_obj.connect_olt()
        # backup_status = bool(fholt_obj.get_card_status(10)['EXIST'] == "YES")
        cmds = AN6K.load_program(filename, backup=backup)
        print("upgrade %s\n" % fholt_obj.oltip, cmds)
        fholt_obj.append_cmdlines(cmds)
        fholt_obj.sendcmdlines()
        print(fholt_obj.cmd_ret)


if __name__ == "__main__":
    # debug_func()
    pass
