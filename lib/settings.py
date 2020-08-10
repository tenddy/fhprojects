#!/usr/bin/env python
# coding=UTF-8

# global Debug
DEBUG = False

TESTCASE_PATH = ""
CAP_PATH = ""
LOG_PATH = "F:/FHAT/fhprojects/log"
# TCL版本只支持8.4
TCL_PATH = "C:/Tcl/bin/tclsh"
TSHARK = ""
# Spirent TestCenter的安装目录
STC_PATH = "D:/Program Files (x86)/Spirent Communications/Spirent TestCenter 4.78/Spirent TestCenter Application"
# STC_PATH = "D:/Program Files/Spirent Communications/Spirent TestCenter 5.02/Spirent TestCenter Application"
# TestCenter仪表IP
STCIP = '172.18.1.112'
# 仪表端口
UPLINK_PORTS = {'uplink': '3/1'}
ONU_PORTS = {'onu1': '3/2', 'onu2': ''}

# OLT信息
OLT_VERSION = 'AN5516-04'
OLT_IP = '10.182.5.49'
OLT_LOGIN = {'Login:': 'fhadmin', 'Password:': 'fholt'}
TELNET_PORT = 23
SSH_PORT = 22

# ONU信息
ONU = {'onu1': (1, 128, 1), 'onu2': (1, 128, 2)}
