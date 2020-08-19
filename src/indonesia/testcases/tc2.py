#!/usr/bin/env python
# coding=UTF-8
"""
##################################################
# @FilePath    : /fhat/src/indonesia/testcases/tc2.py
# @Author      : ddtu
# @Version     : V1.0
# @EMAIL       : ddtu@fiberhome.com
# @License     : (c)Copyright 2019-2020, Fiberhome(ddtu)
# @Date        : 2020-08-12 10:39:51
# @LastEditors : ddtu
# @LastEditTime: 2020-08-12 10:40:10
# @Descption   :  ONU 端口业务配置
##################################################
"""

import time
import os
import sys
import traceback
import re
from Globals import SETTINGS
from lib.oltlib import fhlib
from lib.oltlib.fhat import FH_OLT
from lib.stclib.fhstc import FHSTC
from lib.public.fhlog import logger
from lib.public.fhTimer import waitTime


TC_RET = True

# 仪表操作对象
stc = None

# olt 命令行操作对象
oltobj = FH_OLT()
oltobj.init_olt(**SETTINGS['OLT'])


def stc_init(load=True):
    """仪表初始化，导入仪表配置，或者创建仪表配置"""
    global stc
    stc = FHSTC()
    if load:
        stc.stc_loadFromXml("basic.xml")
    else:
        logger.info("创建pppoE device...")
        stc.stc_createPPPoEv4Client('onu2', 'pppoe_c101', srcMAC="00:00:00:00:00:02",
                                    cvlan=(1002, 1),  count=1, ipv4=("192.18.10.1", "192.18.10.1"))
        stc.stc_createPPPoEv4Server(
            'uplink', 'pppoe_s101', srcMAC="00:00:00:00:00:01", cvlan=(1002, 1),
            count=1, ipv4=("192.168.20.1", "192.168.20.1"),
            pool=("192.168.20.1", '192.168.20.2', 24))
        stc.stc_createBoundTraffic("pppoe_up101", 'pppoe_c101', 'pppoe_s101', 'pppoe')
        stc.stc_createBoundTraffic("pppoe_dw101", 'pppoe_s101', 'pppoe_c101', 'pppoe')

        stc.stc_createPPPoEv4Client('onu1', 'pppoe_c201', srcMAC="00:00:00:00:01:02", cvlan=(
            1001, 1),  count=1, ipv4=("192.18.20.1", "192.18.20.1"))
        stc.stc_createPPPoEv4Server(
            'uplink', 'pppoe_s201', srcMAC="00:00:00:00:01:01", cvlan=(1001, 1),
            count=1, ipv4=("192.168.20.1", "192.168.20.1"),
            pool=("192.168.30.1", '192.168.30.2', 24))
        stc.stc_createBoundTraffic("pppoe_up201", 'pppoe_c201', 'pppoe_s201', 'pppoe')
        stc.stc_createBoundTraffic("pppoe_dw201", 'pppoe_s201', 'pppoe_c201', 'pppoe')

        logger.info("创建DHCP device...")

        stc.stc_apply()
        stc.stc_saveAsXML("pppoe.xml")


def olt_init():
    """OLT 初始化配置"""
    slotno = SETTINGS['SLOTNO']
    ponno = SETTINGS['PONNO']
    # 去授权所有已授权ONU
    oltobj.connect_olt()
    authONUlist = oltobj.get_authorization_onu(slotno, ponno)
    # if len(authONUlist) > 0:
    for sn in authONUlist.keys():
        oltobj.sendcmdlines(fhlib.OLT_V5.unauth_onu(fhlib.ONUAuthType.PHYID, slotno, ponno, sn))
        global TC_RET
        TC_RET = oltobj.verify_cmds_exec() if TC_RET else TC_RET

    # 授权ONU待测试ONU
    for item in SETTINGS['ONU']:
        phyid = item['PHYID']
        oltobj.sendcmdlines(
            fhlib.OLT_V5.authorize_onu(
                fhlib.ONUAuthType.PHYID, phyid, item['ONUTYPE'],
                *(slotno, ponno, item['ONUID'])))
    oltobj.disconnet_olt()
    waitTime(30)
    # 判断ONU是否能正常上线
    logger.info("验证待测试ONU是否可正常上线")
    oltobj.connect_olt()
    authONUlist = oltobj.get_authorization_onu(slotno, ponno)
    for item in SETTINGS['ONU']:
        if item['PHYID'] in authONUlist.keys():
            if authONUlist[item["PHYID"]][6] == 'up':
                logger.info("ONU(%s)授权成功并已成功上线" % item['PHYID'])
            else:
                logger.error("ONU(%s)授权成功,无法上线" % item['PHYID'])
                TC_RET = False
        else:
            logger.error("待测试ONU(%s)未授权" % item['PHYID'])
            TC_RET = False
    oltobj.disconnet_olt()
    return TC_RET


def serviceVerify():
    """业务验证"""
    global TC_RET
    logger.info("PPPoE业务验证")
    pppoe_pair = [('pppoe_s101', 'pppoe_c101'), ('pppoe_s201', 'pppoe_c201')]
    pppoe_stream = [('pppoe_dw101', 'pppoe_up101'), ('pppoe_dw201', 'pppoe_up201')]
    pairCount = len(pppoe_pair)
    for index in range(pairCount):
        device = pppoe_pair[index]
        stream = pppoe_stream[index]
        logger.info("device：{}".format(device))
        stc.stc_PPPoEv4Connect(device[0])
        stc.stc_PPPoEv4Connect(device[1])
        waitTime(5)

        pppoe_ret = stc.stc_getPPPoEClientStatus(device[1])
        if pppoe_ret['SessionState'] == 'CONNECTED':
            logger.info("PPPoE(%s)连接成功" % device[1])
            stc.stc_startStreamBlock(stream[0])
            stc.stc_startStreamBlock(stream[1])
            waitTime(5)
            # logger.info("验证PPPoE数据流是否正常")
            # result = stc.stc_get_DRV_ResulstData()
            # for key in result:
            #     traffic_result = result[key]
            #     tx, rx = tuple(map(int, traffic_result[:2]))
            #     if (abs(tx - rx) / (tx + 0.00001)) > 0.005:
            #         logger.error("PPPoE数据流异常")
            #         TC_RET = False
        else:
            logger.error("PPPoE连接失败（%s，%s)" % (device))
            TC_RET = False

    # dhcp
    logger.info("验证DHCP业务")
    dhcp_pair = [('dhcp_s101', 'dhcp_c101'), ('dhcp_s201', 'dhcp_c201')]
    dhcp_stream = [('dhcp_up101', 'dhcp_dw101'), ('dhcp_up201', 'dhcp_dw201')]
    for index in range(len(dhcp_pair)):
        pair = dhcp_pair[index]
        stream = dhcp_stream[index]
        logger.info("启动DHCP服务器和客户端")
        stc.stc_startDHCPv4Server(pair[0])
        waitTime(3)
        stc.stc_DHCPv4Bind(pair[1])
        waitTime(5)
        logger.info("验证DHCP客户端是否可正常获取IP")
        dhcp_ret = stc.stc_dhcpv4SessionResults(pair[1])
        logger.info("dhcp_ret:{}".format(dhcp_ret))
        for ret in dhcp_ret:        # 根据创建的Device个数获取结果
            if ret[0] == "Bound":
                logger.info("DHCP 客户端(%s)获取IP成功" % pair[1])
                stc.stc_startStreamBlock(stream[0], arp=True)
                stc.stc_startStreamBlock(stream[1], arp=True)

                # logger.info("验证DHCP 数据流是否正常")
                # result = stc.stc_get_DRV_ResulstData()
                # # print("dhcp stream:{}".format(result))
                # for key in result:
                #     traffic_result = result[key]
                #     tx, rx = tuple(map(int, traffic_result[:2]))
                #     if (abs(tx - rx) / (tx + 0.00001)) > 0.005:
                #         logger.error("DHCP数据流异常")
                #         TC_RET = False
            else:
                logger.error("DHCP客户端(%s)获取IP失败" % pair[1])
                TC_RET = False

    # igmp
    logger.info("开启igmp server服务器")
    stc.stc_startDevice('igmp_s101')
    stc.stc_startStreamBlock('igmpstream101')
    stc.stc_startStreamBlock('igmpstream201')
    waitTime(3)
    logger.info("加入组播组")
    igmp_device = ['igmp_c101', 'igmp_c201']
    for device in igmp_device:
        logger.info("%s 加入组播组" % device)
        stc.stc_igmpJoin(device)
        waitTime(3)

    logger.info("验证业务流是否正常")
    result = stc.stc_get_DRV_ResulstData()
    for key in result:
        traffic_result = result[key]
        tx, rx = tuple(map(int, traffic_result[:2]))
        if (abs(tx - rx) / (tx + 0.00001)) > SETTINGS['Threshold']:
            logger.error("数据流(%s)异常" % key)
            TC_RET = False

    return TC_RET


def configFEService(vlanMode='transparent'):
    # 下发端口业务, transparent
    global TC_RET
    slotno = SETTINGS['SLOTNO']
    ponno = SETTINGS['PONNO']
    cvlan = 1001
    incr = 0
    mvlan = 3049
    oltobj.connect_olt()
    for onu in SETTINGS['ONU']:
        cmds = fhlib.OLT_V5.onu_lan_service((slotno, ponno, onu['ONUID'], 1), 2, {'cvlan': (
            vlanMode, 3, cvlan+incr)}, {'cvlan': (vlanMode, 5, mvlan), 'multicast': True})
        oltobj.sendcmdlines(cmds)
        TC_RET = oltobj.verify_cmds_exec() if TC_RET else TC_RET
        incr += 1
    oltobj.disconnet_olt()
    return TC_RET


def configWANSerice():

    slotno = SETTINGS['SLOTNO']
    ponno = SETTINGS['PONNO']
    wan_vlan = (1000, 3)
    onuid = 1
    dsp_pppoe = {'mode': 'pppoe', 'username': 'fiberhome', 'password': 'fiberhome'}
    dsp_dhcp = {'mode': 'dhcp'}
    dsp_static = {'mode': 'static', 'ip': '10.10.10.10',
                  'mask': "255.255.255.0", 'gate': '10.10.10.1', 'dns_m': "8.8.8.8"}
    kargs = {'entries': 'ssid1'}
    # kargs['vlanmode'] = {'mode': 'tag', 'tvlan': 'enable', 'tvid': 1001, 'tcos': 1}
    wan_cmds = fhlib.OLT_V5.onu_wan_service((slotno, ponno, onuid), 1, wan_vlan, dsp_static, **kargs)
    # logger.info(wan_cmds)
    oltobj.connect_olt()
    oltobj.sendcmdlines(wan_cmds)
    oltobj.disconnet_olt()


def main():
    try:
        global TC_RET
        logger.info("端口添加VLAN功能测试")
        # 仪表初始化
        # stc_init()
        # OLT初始化
        olt_init()
        # 配置端口业务
        # configFEService()
        # 验证业务
        # serviceVerify()

        # 配置WAN业务
        configWANSerice()

        logger.info("测试结束!")
        # stc.stc_disconnect()
    except:
        TC_RET = False
        logger.error(traceback.format_exc())
    finally:
        result = "PASS" if TC_RET else "FAILED"
        logger.info("端口添加VLAN功能测试结果：%s" % result)
        return TC_RET


def run():
    main()


if __name__ == "__main__":
    run()
