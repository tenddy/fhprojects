#!/usr/bin/env python
# coding=UTF-8

# global Debug
DEBUG = True

LOG_PATH = "E:/FHATP/fhprojects/log"
# LOG_PATH = "E:/log"
# Tshark安装目录
TSHARK = "C:/Program Files/Wireshark/tshark"
# TCL版本只支持8.4
TCL_PATH = "C:/Tcl/bin/tclsh"
# Spirent TestCenter的安装目录
STC_PATH = "D:/Program Files/Spirent Communications/Spirent TestCenter 4.81/Spirent TestCenter Application"
# TestCenter仪表IP
STCIP = '172.18.1.55'
# 仪表端口
UPLINK_PORTS = {'uplink': '1/9'}
ONU_PORTS = {'onu1': '2/9', 'onu2': ''}

# OLT信息
OLT_VERSION = 'AN5516-01'
OLT_IP = '10.182.5.156'
OLT_LOGIN = {'Login': 'fhadmin', 'Password': 'fholt'}
TELNET_PORT = 23
SSH_PORT = 22

# ONU信息
ONU = {'onu1': (18, 16, 1), 'onu2': (18, 16, 2)}
