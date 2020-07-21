#!/usr/bin/python3
# coding=UTF-8
'''
@Description:
@Author:  Teddy.tu
@Date: 2020-01-01 20:13:11
@LastEditTime: 2020-07-17 14:38:51
@LastEditors: Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''

from lib.public import log
from lib.oltlib import fhlib
from lib.oltlib import fhat
from lib.stclib.pystc import STC
from lib.stclib.fhstc import FHSTC
from lib import settings


@log.log_decare
def test_func():
    return "test func."


def test_auth_onu_v4():

    cmds = fhlib.OLT_V4.authorize_onu(fhlib.ONUAuthType.PHYID, 12, 1, 1, 'HG260',
                                      phyid='FHTT01010001', password='psw0001')
    print(cmds)
    cmds = fhlib.OLT_V4.authorize_onu(fhlib.ONUAuthType.PASSWORD, 12, 1, 2, 'HG260', password="S01010001")
    print(cmds)
    cmds = fhlib.OLT_V4.authorize_onu(fhlib.ONUAuthType.LOID, 12, 1, 3, 'HG260', loid='Fasdf')
    print(cmds)
    cmds = fhlib.OLT_V4.authorize_onu(fhlib.ONUAuthType.LOIDPSW, 12, 1, 4, 'HG260', loid='f0101', logicpsw='adfad')
    print(cmds)


def test_tcl_set():
    stc = STC()
    stc.tcl_set("i", 10)
    stc.tcl_puts("i")


class TestLog():
    def testLogDemo1(self):
        log_tn = log.Logger("./log/testlog.log", log.INFO)
        # log_tn = log.Logger()
        log_tn.info("info")
        log_tn.error("error")
        log_tn.debug("debug")


class TestFHAT():
    def testRussia(self):
        tn = fhat.FH_OLT(fhat.OLT_VERSION_5K)
        tn.hostip = settings.OLT_IP
        tn.login_promot = settings.OLT_LOGIN
        tn.connect_olt()
        cmds = []
        cmds += fhlib.OLT_V4_RUSSIA.del_onu_lan_service((18, 16, 1, 2), 'all')

        cmds += fhlib.OLT_V4_RUSSIA.cfg_onu_lan_service((18, 16, 1, 2), 2012,
                                                        255, fhlib.SericeType.UNICAST, fhlib.VLAN_MODE.TRANSPARENT)
        tn.sendcmdlines(cmds)
