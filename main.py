#!/usr/bin/python3
# coding=UTF-8
'''
@Description: 
@Author:  Teddy.tu
@Date: 2019-07-07 21:53:46
@LastEditTime : 2020-01-01 22:13:31
@LastEditors  :  Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''
import sys
import time
from lib import log
from lib.dut_connect import dut_connect_telnet
from lib.fhlib import OLT_V5
# from lib import fhat
import EPON_FTTB


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


def func1(method, onutype, *onu):
    print("method: ", method, "\nonutype: ", onutype, "\nonu: ", onu)


if __name__ == "__main__":
    host = "127.0.0.1"
    tn = dut_connect_telnet(host, port=2001, promot=b']')
    print("test")
    tn.write(b"disp current\n")
    ret = tn.read_until(b']')
    print(ret.decode('utf-8'))
    tn.close()
    # test_obj = ServiceConfig(tn, log.Logger())
    # send_cmdline = ["config\n", "show discovery 1/3/16\n"]

    # ret = test_obj.send_cmd(send_cmdline)
    # print(ret)
    # func1("add", "other2", *(9, 9, 1))
    # func1("add", "other2", {'a': 1}, {'b': 2})
    # cmd = OLT_V5.authorize_onu("phy-id", "FHTT01010001", "5006-10", 1, 1, 1)
    # print(cmd)
    cmd = OLT_V5.onu_lan_service(
        (1, 1, 1, 1),
        2,
        {'cvlan': ('tag', 1, 2001),
         'translate': ('enable', 3, 301),
         'qinq': ('enable', 3, 2701, 'FTTB_QINQ', 'SVLAN')},
        {'cvlan': ('transparent', 1, 302),
         'qinq': ('enable', 3, 2701, 'FTTB_QINQ', 'SVLAN')})
    # print(cmd)
    cmd1 = OLT_V5.onu_lan_service((2, 1, 1, 1), 0)
    # print(cmd1)
    cmd = EPON_FTTB.service_model1_cmd(1, 1, (1, 24), (2, 8))
    # for item in cmd:
    #     print(item)
