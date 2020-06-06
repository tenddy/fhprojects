#!/usr/bin/python3
# coding=UTF-8
'''
@Description:
@Author:  Teddy.tu
@Date: 2019-07-07 21:53:46
@LastEditTime: 2020-06-05 19:13:08
@LastEditors: Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''

import time
import pandas as pd
from lib import log
from lib import dut_connect
from lib.fhlib import OLT_V5
from lib.fhlib import OLT_V4_RUSSIA
from lib.fhat import ServiceConfig
from lib.fhat import send_cmd_file
import gpon
import EPON_FTTB


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
    oltip = '10.182.5.156'
    tn_obj = dut_connect.dut_connect_telnet(oltip, 23, {'Login': 'admin', 'Password': 'admin'}, '#')
    log_obj = log.Logger(r'./log/russia_cfg.log')
    cmd_send_obj = ServiceConfig(tn_obj, log_obj)
    slotno = 11
    ponno = 16
    onuno = 66
    portno = 1
    cmd_cfg = OLT_V4_RUSSIA.cfg_onu_lan_service((slotno, ponno, onuno, portno), 1002, 3, 'unicast', 'tag')
    cmd_cfg += OLT_V4_RUSSIA.cfg_onu_lan_service((slotno, ponno, onuno, 4), 3048, 5, 'unicast', 'tag')
    cmd_cfg += OLT_V4_RUSSIA.cfg_onu_lan_service((slotno, ponno, onuno, 4), 3049, 5, 'multicast', 'tag')
    cmd_del = OLT_V4_RUSSIA.del_onu_lan_service((slotno, ponno, onuno, portno), 1002)
    cmd_del += OLT_V4_RUSSIA.del_onu_lan_service((slotno, ponno, onuno, 4), 'all')
    while True:
        cmd_send_obj.send_cmd(cmd_cfg)
        time.sleep(10)
        cmd_send_obj.send_cmd(cmd_del)
        time.sleep(10)


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


def cfg_internet_wan(slot, pon, onu, vlan):
    """
    OLT_FH_1\onu\lan#
    set veip_mgr_par slot 11 pon 16 onu 128 veip_port 1 port_type veip mgr_channel enable model tr069 item 1
    set veip_mgr_vlan slot 11 pon 16 onu 128 veip_port 1 mgr_id 1 protocol udp priority 0 tag_type tag svlan_label 0x8100 svlanid null svlan_cos null cvlan_label 0x8100 cvlanid 900 cvlan_cos 7
    apply veip_mgr_vlan slot 11 pon 16 onu 128
    """
    cmds = ['cd /onu/lan\n']
    cmds.append('set veip_mgr_par slot {0} pon {1} onu {2} veip_port 1 port_type veip mgr_channel enable model tr069 item 1\n'.format(
        slot, pon, onu))
    cmds.append(
        'set veip_mgr_vlan slot {0} pon {1} onu {2} veip_port 1 mgr_id 1 protocol udp priority 0 tag_type tag svlan_label 0x8100 svlanid null svlan_cos null cvlan_label 0x8100 cvlanid {3} cvlan_cos 7\n'.
        format(slot, pon, onu, vlan))
    cmds.append('apply veip_mgr_vlan slot {0} pon {1} onu {2}\n'.format(slot, pon, onu))
    return cmds


def cfg_iptv(slot, pon, onu, port, vlan):
    """
    OLT_FH_1\onu\lan#
    onu-lan slot 11 pon 16 onu 1 port 2 vlan 1103 priority 3 type unicast mode tag
    onu-lan slot 11 pon 16 onu 1 port 2 vlan 3999 priority 3 type multicast mode tag
    apply onu 11 16 1 vlan
    """
    cmds = ['cd /onu/lan\n']
    cmds.append(
        'onu-lan slot {0} pon {1} onu {2} port {3} vlan {4} priority 3 type unicast mode tag\n'.format(slot, pon, onu, port, vlan))
    cmds.append(
        'onu-lan slot {0} pon {1} onu {2} port {3} vlan {4} priority 3 type multicast mode tag\n'.format(slot, pon, onu, port, vlan))
    cmds.append('apply onu {0} {1} {2} vlan\n'.format(slot, pon, onu))
    return cmds


def cfg_voice(slot, pon, onu, vlan, phone_prefix):
    """
    \onu\ngn#
    set ngn_uplink_user_new slot 11 pon 16 onu 128 servicename voip vid 7 ip_mode dhcp domainname @russia.voip protocol_port 5060
    set ngn_voice_service_new slot 11 pon 16 onu 128 pots 1 username 8888800001 sip_user_name 8888800001 sip_user_password 8888800001
    set ngn_voice_service_new slot 11 pon 16 onu 128 pots 2 username 8888800002 sip_user_name 8888800002 sip_user_password 8888800002
    """
    cmds = ['cd /onu/ngn\n']
    cmds.append(
        'set ngn_uplink_user_new slot {0} pon {1} onu {2} servicename voip vid {3} ip_mode dhcp domainname @russia.voip protocol_port 5060\n'.
        format(slot, pon, onu, vlan))
    cmds.append(
        'set ngn_voice_service_new slot {0} pon {1} onu {2} pots 1 username {3}1 sip_user_name {3}1 sip_user_password {3}1\n'.
        format(slot, pon, onu, phone_prefix))
    cmds.append(
        'set ngn_voice_service_new slot {0} pon {1} onu {2} pots 2 username {3}2 sip_user_name {3}2 sip_user_password {3}2\n'.
        format(slot, pon, onu, phone_prefix))
    return cmds


def bactch_cfg():
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


if __name__ == "__main__":
    # russia_cfg()
    # bactch_cfg()
    del_batch_config()
