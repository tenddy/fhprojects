#!/usr/bin/env python
# coding=UTF-8

# global Debug
DEBUG = True

TESTCASE_PATH = ""
CAP_PATH = ""
LOG_PATH = ""
# TCL版本只支持8.4
TCL_PATH = "C:/Tcl/bin/tclsh"
TSHARK = ""
# Spirent TestCenter的安装目录
STC_PATH = "C:/Program Files (x86)/Spirent Communications/Spirent TestCenter 4.95/Spirent TestCenter Application"
# TestCenter仪表IP
STCIP = '10.182.32.138'
# 仪表端口
UPLINK_PORTS = {'uplink': '1/13'}
ONU_PORTS = {'onu1': '1/5', 'onu2': ''}

# OLT信息
# OLT_VERSION = 'AN5516-04'
# OLT_IP = '10.182.33.185'
# OLT_LOGIN = {'Login:': 'GEPON', 'Password:': 'GEPON'}
# TELNET_PORT = 23
# SSH_PORT = 22

# # ONU信息
# ONU = {'onu1': (4, 8, 65), 'onu2': (4, 8, 128)}
