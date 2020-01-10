#!/usr/bin/python3
# coding=UTF-8
'''
@Description: 
@Author:  Teddy.tu
@Date: 2019-07-07 21:53:46
@LastEditTime : 2019-12-29 22:18:20
@LastEditors  :  Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''
import sys
import time
import re
from lib import log
from lib.dut_connect import connect_olt_telnet
from lib.fhlib import OLT_V5
from lib.FHAT import ServiceConfig
from lib.FHAT import send_cmd_file
import EPON_FTTB


def testcase():
    print("test...")
    host = "10.182.32.15"
    tn = connect_olt_telnet(host)
    tn.close()


def service_config(tn, slotno, ponno, onuno, ethno, uni_vid, multi_vid=4000):
    ser_cmd1 = " interface pon 1/{0}/{1}\n".format(slotno, ponno)
    ser_cmd2 = "onu port vlan {0} eth {1} service count 0\n".format(onuno, ethno)
    ser_cmd3 = "onu port vlan {0} eth {1} service count 2\n".format(onuno, ethno)
    ser_cmd4 = "onu port vlan {0} eth {1} service 1 tag priority 1 tpid 33024 vid {2}\n".format(onuno, ethno, uni_vid)
    ser_cmd5 = "onu port vlan {0} eth {1} service 2 type multicast\n".format(onuno, ethno)
    ser_cmd6 = "onu port vlan {0} eth {1} service 2 tag priority 5 tpid 33024 vid {2}\n".format(onuno, ethno, multi_vid)
    # cmd = bytes(ser_cmd1 + ser_cmd2 + ser_cmd3 + ser_cmd4 + ser_cmd5 + ser_cmd6, encoding='utf8')
    cmds = [ser_cmd1, ser_cmd2, ser_cmd3, ser_cmd4, ser_cmd5, ser_cmd6]
    for cmd in cmds:
        byte_cmd = bytes(cmd, encoding='utf8')
        ret = tn.send_cmd(tn, byte_cmd)
        # dut_connct_telnet.log.info(ret)


def service_config_test(tn, slotno, ponno, onuno, ethno, uni_vid):
    ser_cmd1 = " interface pon 1/{0}/{1}\n".format(slotno, ponno)
    ser_cmd2 = "onu port vlan {0} eth {1} service count 0\n".format(onuno, ethno)
    ser_cmd3 = "onu port vlan {0} eth {1} service count 1\n".format(onuno, ethno)
    ser_cmd4 = "onu port vlan {0} eth {1} service 1 tag priority 1 tpid 33024 vid {2}\n".format(onuno, ethno, uni_vid)

    cmds = [ser_cmd1, ser_cmd2, ser_cmd3, ser_cmd4]
    for cmd in cmds:
        byte_cmd = bytes(cmd, encoding='utf8')
        ret = tn.send_cmd(tn, byte_cmd)
        # dut_connct_telnet.log.info(ret)


def service_config_ONUs(tn, slots):
    for slotno in slots:
        for ponno in range(1, 17):
            vid = 100 + (slotno-1)*16 + ponno-1
            for onuno in range(1, 33):
                if onuno % 10 == 0:
                    time.sleep(1)
                # print("{}/{}/{}".format(slot, ponno, onuno))
                service_config_test(tn, slotno, ponno, onuno, 4, vid)
                # service_config(tn, slotno, ponno, onuno, 1, vid, 4000)


def func1(method, onutype, *onu):
    print("method: ", method, "\nonutype: ", onutype, "\nonu: ", onu)

def config_cmds(host, file, slotno=3, ponno=16):
    tn = connect_olt_telnet(host, 23, b'admin', b'admin')
    dut_host = ServiceConfig(tn, log.Logger(r'E:/DDTU Workplace/fhprojects/log/fttb.log'))
    # dut_host.send_cmd(['config\n'])
    f = open(file, 'r')
    for line in f:
        # if "#" in line:
        #     input("press any key to continue.")
        line = re.sub(r'phy-id [0-9]* [0-9]*', 'phy-id {0} {1}'.format(slotno, ponno), line)
        line = re.sub(r'slot [0-9]* pon [0-9]*', 'slot {0} pon {1}'.format(slotno, ponno), line)
        line = re.sub(r'1/[0-9]*/[0-9]*', '1/{0}/{1}'.format(slotno, ponno), line)
        # print(line)
        dut_host.send_cmd(line)
    # dut_host.send_cmd(['quit\nquit\n'])
    tn.close()

if __name__ == "__main__":
    # EPON_FTTB.epon_service_config() 
    if len(sys.argv) <= 1:
        print("Error: 缺少文件路径")
        exit(-1)

    host = "35.35.35.109"
    config_cmds(host, sys.argv[1], 1, 1)