#!/usr/bin/env python
# coding=UTF-8
'''
@Desc: None
@Author: Teddy.tu
@Version: V1.0
@EMAIL: teddy_tu@126.com
@License: (c)Copyright 2019-2020, Teddy.tu
@Date: 2019-08-12 16:47:01
@LastEditors: Teddy.tu
@LastEditTime: 2020-07-09 09:55:36
'''


import time
import pandas as pd
from lib import dut_connect, log
from lib.fhat import ServiceConfig, FH_OLT, send_cmd_file
from lib import fhlib
import EPON_FTTB
import gpon


def epon_service_cfg():
    # 广西场景业务配置

    # telnet OLT
    oltip = '10.182.5.109'
    tn_obj = dut_connect.dut_connect_telnet(oltip, 23, {'Login': 'admin', 'Password': 'admin'}, '#')
    log_obj = log.Logger(r'./log/service.log')
    cmd_send_obj = ServiceConfig(tn_obj, log_obj)

    # TL1
    unm_ip = '10.182.1.161'
    unm_user, unm_pwd = 'admin', 'admin123'
    unm_tn = dut_connect.dut_connect_tl1(unm_ip, username=unm_user, password=unm_pwd)
    tl1_cmd_obj = ServiceConfig(unm_tn, log.Logger(r'./log/tl1_log.log'))

    slotno = 17
    ponno = 4

    # EPON
    eponfile = r"./config/epon.xls"
    # send_tl1_cmds = EPON_FTTB.get

    # GPON
    gponfile = r"./config/gpon.xlsx"

    print("命令行.")
    for index in gpon.get_linecmds():
        print(index, end='')
    # cmd_send_obj.send_cmd(gpon.get_linecmds())

    print("TL1")
    for index in gpon.get_linecmds_tl1():
        print(index, end='')
    tl1_cmd_obj.send_cmd(gpon.get_linecmds_tl1(), promot=b';')

    # disconnet TL1
    dut_connect.dut_disconnect_tl1(unm_tn)


def russia_cfg():
    russiaOLT = FH_OLT("V4")
    russiaOLT.hostip = '10.182.5.156'
    russiaOLT.login_promot = {'Login:': 'fhadmin', 'Password:': 'fholt'}
    russiaOLT.connect_olt()
    slot, pon = 18, 16
    onulists = [1, 2, 3, 4]
    onu_pwd = ('oso_hw', 'oso9d', 'oso2', 'sercom126')
    wan_vlan = 350
    voice_vlan = 7

    for onu in onulists:
        cmds = []
        # 去授权ONU
        cmds += fhlib.OLT_V4_RUSSIA.unauth_onu((slot, pon, onu))
        # 授权ONU
        cmds += fhlib.OLT_V4_RUSSIA.authorize_onu(fhlib.ONUAuthType.PASSWORD,
                                                  slot, pon, onu, "HG260", password=onu_pwd[onu-1])
        # 配置WAN业务
        cmds += fhlib.OLT_V4_RUSSIA.cfg_internet_wan(slot, pon, onu, wan_vlan)
        # 配置语音业务
        cmds += fhlib.OLT_V4_RUSSIA.cfg_voice(slot, pon, onu, voice_vlan, phone_prefix="66", servicename='voip')
        # 配置组播业务
        cmds += fhlib.OLT_V4_RUSSIA.cfg_onu_lan_service((slot, pon, onu, 4),
                                                        600, 3, fhlib.SericeType.MULTICAST, fhlib.VLAN_MODE.TAG)
        # 单播业务
        un_vlan = 1010 + onu
        cmds += fhlib.OLT_V4_RUSSIA.cfg_onu_lan_service((slot, pon, onu, 4), un_vlan,
                                                        3, fhlib.SericeType.UNICAST, fhlib.VLAN_MODE.TAG)
        russiaOLT.sendcmdlines(cmds)
        # print(cmds)


def unauth_onu(slot, pon, onu):
    """no whitelist slot 1 pon 1 onu 1"""
    cmds = ['cd /onu\n']
    unauth_cmds = 'no whitelist slot {0} pon {1} onu {2} \n'.format(slot, pon, onu)
    cmds.append(unauth_cmds)
    return cmds


def auth_onu(slot, pon, onu, sn):
    """
    set whitelist password password GC82EA59D action add slot 11 pon 16 onu 60 type HG260
    """
    cmds = ['cd /onu\n']
    auth_cmds = 'set whitelist password password {3} action add slot {0} pon {1} onu {2} type HG260\n'.format(
        slot, pon, onu, sn)
    cmds.append(auth_cmds)
    return cmds


def cfg_voice(slot, pon, onu, vlan, phone_prefix="", servicename='eluosisip'):
    """
    \onu\ngn#
    set ngn_uplink_user_new slot 11 pon 16 onu 128 servicename voip vid 7 ip_mode dhcp domainname @russia.voip protocol_port 5060
    set ngn_voice_service_new slot 11 pon 16 onu 128 pots 1 username 8888800001 sip_user_name 8888800001 sip_user_password 8888800001
    set ngn_voice_service_new slot 11 pon 16 onu 128 pots 2 username 8888800002 sip_user_name 8888800002 sip_user_password 8888800002
    """
    prefix = "{phone_prefix}{slot:02}{pon:02}{onu:03}".format(
        phone_prefix=phone_prefix, slot=slot, pon=pon, onu=onu)
    # print(prefix)
    cmds = ['cd /onu/ngn\n']
    cmds.append(
        'set ngn_uplink_user_new slot {0} pon {1} onu {2} servicename {4} vid {3} ip_mode dhcp domainname @russia.voip protocol_port 5060\n'.
        format(slot, pon, onu, vlan, servicename))
    cmds.append(
        'set ngn_voice_service_new slot {0} pon {1} onu {2} pots 1 username {3}1 sip_user_name {3}1 sip_user_password {3}1\n'.
        format(slot, pon, onu, prefix))
    cmds.append(
        'set ngn_voice_service_new slot {0} pon {1} onu {2} pots 2 username {3}2 sip_user_name {3}2 sip_user_password {3}2\n'.
        format(slot, pon, onu, prefix))
    return cmds


def bactch_cfg():
    slots = range(2, 8)
    # pon = range(1, 17)
    # onu = range(1, 129)
    cfg_cmds = []
    wan_vlan = 350
    mvlan = 3049
    voice_vlan = 7
    for s in slots:
        for p in range(1, 17):
            cfg_cmds += OLT_V4_RUSSIA.pon_auth_mode(s, p, pontype.PHYID_OR_PSW.value)
            for o in range(1, 65):
                sn = 'RS%02d%02d%03d' % (s, p, o)
                cfg_cmds += auth_onu(s, p, o, sn)
                cfg_cmds += cfg_internet_wan(s, p, o, wan_vlan)
                cfg_cmds += cfg_iptv(s, p, o, 4, mvlan)
                cfg_cmds += cfg_voice(s, p, o, voice_vlan, '%02d%03d%03d0' % (s, p, o))

    # for item in cfg_cmds:
    #     print(item)

    oltip = '10.182.5.156'
    tn_obj = dut_connect.dut_connect_telnet(oltip, 23, {'Login': 'admin', 'Password': 'admin'}, '#')
    log_obj = log.Logger(r'./log/russia_cfg.log')
    cmd_send_obj = ServiceConfig(tn_obj, log_obj)
    cmd_send_obj.send_cmd(cfg_cmds)


def del_batch_config():
    slots = [1, 18]
    # pon = range(1, 17)
    # onu = range(1, 129)
    cfg_cmds = []
    wan_vlan = 350
    mvlan = 3049
    voice_vlan = 7
    for s in slots:
        for p in range(1, 17):
            for o in range(1, 129):
                cfg_cmds += unauth_onu(s, p, o)

    # for item in cfg_cmds:
    #     print(item)

    oltip = '10.182.5.156'
    tn_obj = dut_connect.dut_connect_telnet(oltip, 23, {'Login': 'admin', 'Password': 'admin'}, '#')
    log_obj = log.Logger(r'./log/russia_cfg.log')
    cmd_send_obj = ServiceConfig(tn_obj, log_obj)
    cmd_send_obj.send_cmd(cfg_cmds)


def bridge_service_cfg():
    slotno = 12
    ponnno = range(5, 17)
    cmd_cfg = []
    russia_cfg_file = r'./etc/russia_cfg.txt'
    for p in range(5, 17):
        for o in range(1, 33):
            cmd_cfg += fhlib.OLT_V4_RUSSIA.cfg_onu_lan_service((slotno, p, o, 1), 1000+p-5, 5, 'unicast', 'tag')
            cmd_cfg += fhlib.OLT_V4_RUSSIA.cfg_onu_lan_service((slotno, p, o, 1), 3049, 5, 'multicast', 'tag')
    with open(russia_cfg_file, 'w') as f:
        for cmd in cmd_cfg:
            f.write(cmd)


def test_demo():
    testolt = FH_OLT()
    testolt.hostip = '10.182.1.81'
    testolt.login_promot = {'Login:': 'admin123', 'Password:': 'admin123'}
    testolt.connect_olt()
    cmds = []
    cmds += fhlib.OLT_V5.pon_auth_mode(1, 1, fhlib.PONAuthMode.PHYID_OR_LOID)
    cmds += fhlib.OLT_V5.unauth_onu(fhlib.ONUAuthType.PHYID, 1, 1, "FHTT01010001")
    # cmds += fhlib.OLT_V5.unauth_onu(fhlib.ONUAuthType.PHYID, 1, 1, "FHTT01010002")
    # cmds += fhlib.OLT_V5.authorize_onu(fhlib.ONUAuthType.PHYID, 'FHTT01010002', "5506-04-F1", 1, 1, 2)
    # cmds += fhlib.OLT_V5.add_uplink_vlan(8, 4, fhlib.VLAN_MODE.TAG, 80, 81)
    testolt.sendcmdlines(cmds)

    testolt.get_cmds_execute(fhlib.OLT_V5.show_port_vlan, 8, 4)
    # testolt.get_maincard_version()


if __name__ == "__main__":
    russia_cfg()
    # bactch_cfg()
    # print(pontype.NO_AUTH.value)
    # test_demo()
