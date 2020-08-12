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
TC_RET = True  # 测试结果, 默认为True


def configFE(*onuList):
    pass


def main():
    try:
        TC_RET = True  # 测试结果, 默认为True

        logger.info("端口添加VLAN功能测试")
        # 仪表操作对象
        stc = FHSTC()
        load = True
        if load:
            stc.stc_loadFromXml("basic.xml")
        else:
            logger.info("创建pppoE device...")
            stc.stc_createPPPoEv4Client('onu2', 'pppoe_c101', srcMAC="00:00:00:00:00:02", cvlan=(
                1002, 1),  count=1, ipv4=("192.18.10.1", "192.18.10.1"))
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
            stc.stc_apply()
            stc.stc_saveAsXML("pppoe.xml")
        # olt 命令行操作对象
        oltobj = FH_OLT()
        oltobj.init_olt(**SETTINGS['OLT'])
        slotno = SETTINGS['SLOTNO']
        ponno = SETTINGS['PONNO']
        # 去授权所有已授权ONU
        oltobj.connect_olt()
        authONUlist = oltobj.get_authorization_onu(slotno, ponno)
        # if len(authONUlist) > 0:
        for sn in authONUlist.keys():
            oltobj.sendcmdlines(fhlib.OLT_V5.unauth_onu(fhlib.ONUAuthType.PHYID, slotno, ponno, sn))
            TC_RET = oltobj.verify_cmds_exec() if TC_RET else TC_RET

        # 授权ONU待测试ONU
        for item in SETTINGS['ONU']:
            phyid = item['PHYID']
            oltobj.sendcmdlines(
                fhlib.OLT_V5.authorize_onu(
                    fhlib.ONUAuthType.PHYID, phyid, item['ONUTYPE'],
                    *(slotno, ponno, item['ONUID'])))
        oltobj.disconnet_olt()
        # waitTime(30)

        # 判断ONU是否能正常正常上线
        logger.info("验证待测试ONU是否可正常上线")
        oltobj.connect_olt()
        authONUlist = oltobj.get_authorization_onu(slotno, ponno)
        for item in SETTINGS['ONU']:
            if item['PHYID'] in authONUlist.keys():
                if authONUlist[item["PHYID"]][6] == 'up':
                    logger.error("ONU(%s)授权成功并已成功上线" % item['PHYID'])
                else:
                    logger.error("ONU(%s)授权成功,无法上线" % item['PHYID'])
                    TC_RET = False
            else:
                logger.error("待测试ONU(%s)未授权" % item['PHYID'])
                TC_RET = False

        # 下发端口业务
        cvlan = 1001
        incr = 0
        for onu in SETTINGS['ONU']:
            cmds = fhlib.OLT_V5.onu_lan_service(
                (slotno, ponno, onu['ONUID'], 1), 1, {'cvlan': ("transparent", 3, cvlan+incr)})
            oltobj.sendcmdlines(cmds)

            TC_RET = oltobj.verify_cmds_exec() if TC_RET else TC_RET
            incr += 1
        oltobj.disconnet_olt()

        # 业务验证
        logger.info("业务验证")
        # pppoe
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

            # print(stc.stc_getPPPoEServerStatus(device[0]))
            pppoe_ret = stc.stc_getPPPoEClientStatus(device[1])
            # print(pppoe_ret)
            if pppoe_ret['SessionState'] == 'CONNECTED':
                logger.info("PPPoE连接成功。验证PPPoE数据流是否正常")
                stc.stc_streamBlockStart(stream[0])
                stc.stc_streamBlockStart(stream[1])
                waitTime(5)
                result = stc.stc_get_DRV_ResulstData()
                for key in result:
                    traffic_result = result[key]
                    tx, rx = tuple(map(int, traffic_result[:2]))
                    TC_RET = bool(abs(1 - rx / (tx+0.00001)) <= 0.05) if TC_RET else TC_RET
            else:
                logger.error("PPPoE连接失败（%s，%s)" % (device))
                TC_RET = False

        # dhcp

        # igmp

        # 修改端口业务

        # 增加端口业务

        # 删除端口业务

        logger.info("测试结束!")
        oltobj.disconnet_olt()
        # stc.stc_disconnect()
    except:
        TC_RET = False
        print(traceback.format_exc())
    finally:
        result = "PASS" if TC_RET else "FAILED"
        logger.info("端口添加VALN功能测试结果：%s" % result)
        return TC_RET


def run():
    main()


if __name__ == "__main__":
    run()
