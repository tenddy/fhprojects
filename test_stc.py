#!/usr/bin/env python
# coding=UTF-8
'''
@Desc: None
@Author: Teddy.tu
@Version: V1.0
@EMAIL: teddy_tu@126.com
@License: (c)Copyright 2019-2020, Teddy.tu
@Date: 2020-07-13 10:11:28
@LastEditors: Teddy.tu
@LastEditTime: 2020-07-16 09:17:47
'''
from lib.stclib import fhstc
from lib.stclib.fhstc import FHSTC

# from stclib.fhstc import STC
import time


# def test_generatorstart():
#     stcip = "172.18.1.55"
#     fhstc = FHSTC(stcip)
#     fhstc.stc_generator_start()

def test_stcTCL():
    stc = fhstc.STC()
    # assert stc.tclsh is lib.stclib.tclwrapper.TCLWrapper
    stc.a = 10
    # assert 'a' in stc.__dict__.keys()
    assert stc.a == 10
    stc.b = 'abc'
    assert stc.b == 'abc'
    stc.c = dict()
    stc.c['p1'] = 'hport'
    assert stc.c['p1'] == 'hport'
    # assert stc.c['p1'] == 'hport'


def test_demo():
    stcip = "172.18.1.55"

    ports = dict()
    ports["uplink"] = "1/9"
    ports["onu1"] = "2/9"
    ports["onu2"] = "2/10"
    # stc = STC()
    fhstc = FHSTC(stcip)
    fhstc.stc_init()
    fhstc.stc_connect()
    fhstc.stc_createProject()
    fhstc.stc_createPorts(**ports)
    fhstc.stc_autoAttachPorts()

    dw_1_1 = dict()
    dw_1_1["srcMac"] = "00:00:01:00:00:01"
    dw_1_1["dstMac"] = "00:01:94:00:00:01"
    dw_1_1["svlan"] = (20, 1)
    dw_1_1["cvlan"] = (100, 7)
    dw_1_1["IPv4"] = ("10.10.10.10", "20.20.20.20", "10.10.10.1")

    onu1_up1 = "up_1_1"
    up_1_1 = dict()
    up_1_1["srcMac"] = "00:01:94:00:00:01"
    up_1_1["dstMac"] = "00:00:01:00:00:01"
    # onu_up['svlan'] = (20, 1)
    up_1_1["cvlan"] = (100, 7)
    up_1_1["IPv4"] = ("10.10.10.10", "20.20.20.20", "10.10.10.1")

    up_2_1 = up_1_1.copy()
    up_2_1["srcMac"] = "00:01:94:00:00:02"

    fhstc.stc_createTraffiRaw('dw_1_1', 'uplink', **dw_1_1)
    fhstc.stc_createTraffiRaw('up_1_1', 'onu1', **up_1_1)
    fhstc.stc_createTraffiRaw('up_2_1', 'onu2', **up_2_1)
    fhstc.stc_generatorConfig('uplink')
    fhstc.stc_generatorConfig('onu1')
    fhstc.stc_generatorConfig('onu2')
    fhstc.apply()
    fhstc.stc_saveAsXML()

    fhstc.stc_DRVConfig()
    fhstc.stc_generator_start('uplink')
    fhstc.stc_streamBlockStart('up_1_1')
    fhstc.stc_streamBlockStart('up_2_1')
    time.sleep(3)
    fhstc.stc_ClearAllResults('uplink')
    fhstc.stc_ClearAllResults('onu1')
    fhstc.stc_ClearAllResults('onu2')
    result = fhstc.stc_get_DRV_ResulstData()
    print(result)
    fhstc.stc_generator_stop('uplink')
    fhstc.stc_streamBlockStop('up_1_1')
    fhstc.stc_streamBlockStop('up_2_1')
