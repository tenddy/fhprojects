#!/usr/bin/python3
# coding=UTF-8
'''
@Description: 
@Author:  Teddy.tu
@Date: 2019-07-07 21:53:46
@LastEditTime: 2019-12-13 10:22:01
@LastEditors: Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''

import sys
import time
from FHAT import ServiceConfig
from fhlib import OLT_V5
from base_cmd import dut_connect_telnet


def testcase():
    print("test...")
    host = "10.182.32.15"
    tn = dut_connect_telnet.login_olt_telnet(host)
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
        ret = dut_connect_telnet.send_cmd(tn, byte_cmd)
        # dut_connct_telnet.log.info(ret)


def service_config_test(tn, slotno, ponno, onuno, ethno, uni_vid):
    ser_cmd1 = " interface pon 1/{0}/{1}\n".format(slotno, ponno)
    ser_cmd2 = "onu port vlan {0} eth {1} service count 0\n".format(onuno, ethno)
    ser_cmd3 = "onu port vlan {0} eth {1} service count 1\n".format(onuno, ethno)
    ser_cmd4 = "onu port vlan {0} eth {1} service 1 tag priority 1 tpid 33024 vid {2}\n".format(onuno, ethno, uni_vid)
    cmds = [ser_cmd1, ser_cmd2, ser_cmd3, ser_cmd4]
    for cmd in cmds:
        byte_cmd = bytes(cmd, encoding='utf8')
        ret = dut_connect_telnet.send_cmd(tn, byte_cmd)
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


if __name__ == "__main__":
    host = "35.35.35.109"
    tn = dut_connect_telnet.login_olt_telnet(host)
    print("test")
    test_obj = ServiceConfig(tn)
    send_cmdline = "config\n show discovery 1/17/8"
    # send_cmline = send_cmdline + OLT_V5.add_uplink_vlan(uplinkslot=9,
    #                                                     uplinkport=1, vlan_mode="tag", vlan_begin=100, vlan_end=100)

    ret = test_obj.send_cmd(send_cmdline)
    print(ret)
