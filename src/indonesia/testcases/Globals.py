#!/usr/bin/env python
# coding=UTF-8

import os
import sys

try:
    currentPath = os.path.dirname(__file__)
    rootPath = "\\".join(currentPath.split("\\")[:-3])
    if rootPath not in sys.path:
        sys.path.append(rootPath)

    from lib import settings

    settings.TESTCASE_PATH = "\\".join(__file__.split("\\")[:-2])
    # log 目录
    settings.LOG_PATH = "\\".join(__file__.split("\\")[:-2]) + "\\log"
    # print(settings.LOG_PATH)
    if not os.path.isdir(settings.LOG_PATH):
        os.mkdir(settings.LOG_PATH)
    # capture 目录
    settings.CAP_PATH = "\\".join(__file__.split("\\")[:-2]) + "\\capture"
    # print(settings.CAP_PATH)
    if not os.path.isdir(settings.CAP_PATH):
        os.mkdir(settings.CAP_PATH)
    # instruments 目录
    settings.XML_PATH = "\\".join(__file__.split("\\")[:-2]) + "\\instruments"
    # print(settings.XML_PATH)
    if not os.path.isdir(settings.XML_PATH):
        os.mkdir(settings.XML_PATH)
except:
    print("PATH Error")


SETTINGS = {
    # TCL路径（只支持8.4)
    "TCL_PATH": "C:/Tcl/bin/tclsh",

    # 仪表配置
    "STC_PATH": "C:/Program Files (x86)/Spirent Communications/Spirent TestCenter 4.95/Spirent TestCenter Application",
    "STC_IP": "10.182.32.138",

    # 仪表端口
    "UPLINK_PORTS": {'uplink': '1/13'},
    "ONU_PORTS": {'onu1': '1/5', 'onu2': ''},

    # OLT 信息
    "OLT": {
        "OLT_VERSION": "AN6000-17",
        "OLT_IP": "10.182.33.185",
        "OLT_LOGIN": {'Login:': 'GEPON', 'Password:': 'GEPON'},
        "TELNET_PORT": 23,
        "SSH_PORT": 22,
    },

    # ONU信息
    "ONU1": {
        'ONUID': (4, 8, 65),
        'ONUTYPE': '',
        'PHYSN': '',
        'SN': '',
        'PASSWORD': ''
    },

    "ONU2": {
        'ONUID': (4, 8, 1),
        'ONUTYPE': '',
        'PHYSN': '',
        'SN': '',
        'PASSWORD': ''
    },

}

# 初始化默认仪表参数
settings.TCL_PATH = SETTINGS['TCL_PATH']
settings.STC_PATH = SETTINGS['STC_PATH']
settings.STCIP = SETTINGS['STC_IP']
settings.UPLINK_PORTS = SETTINGS['UPLINK_PORTS']
settings.ONU_PORTS = SETTINGS['ONU_PORTS']
