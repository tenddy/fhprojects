#!/usr/bin/env python
# coding=UTF-8
"""
###############################################################################
# @FilePath    : /fhat/src/indonesia/testcases/tc3.py
# @Author      : ddtu
# @Version     : V1.0
# @EMAIL       : ddtu@fiberhome.com
# @License     : (c)Copyright 2019-2020, Fiberhome(ddtu)
# @Date        : 2020-08-12 10:39:51
# @LastEditors : ddtu
# @LastEditTime: 2020-08-12 10:40:10
# @Descption   :  AN5506-04F/HG6243C/HG5255ST模型1
                1.上网/VPN业务——PPPoE WAN:ssid1
                    三层限速
                    up:100M down:100M
                    up:2253k down:11264k
                    up:4506k down:22528k
                2.组播业务——端口配置:lan1/2/3/4
                    组播tag vlan110/cos4
                    单播tag vlan111/cos4
                    端口绑定限速模板:
                    DOWN6144K UP512K
                    DOWN8M UP2253K"

            说明，由于无法验证功能WiFi业务，上网业务增加绑定FE1，组播配置2，3，4
###############################################################################
"""

import time
import os
import sys
import traceback
import re
import random
from Globals import SETTINGS
from Globals import MODEL
import serviceModel
from serviceModel import config_ONU_Serice
from lib.oltlib.oltv5 import AN6K
from lib.oltlib.common import *
from lib.oltlib.fhat import FH_OLT
from lib.stclib.fhstc import FHSTC
from lib.public.fhlog import logger
from lib.public.fhTimer import waitTime
from lib.public.packet import AnalyzePacket

# print(sys.path)
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
    stc.stc_connect()
    if load:
        stc.stc_loadFromXml("basic.xml")
    else:
        pass


def olt_init():
    """OLT 初始化配置"""
    global TC_RET
    slotno = SETTINGS['SLOTNO']
    ponno = SETTINGS['PONNO']
    #  去授权ONU
    logger.info("去授权ONU")
    oltobj.connect_olt()
    authONUlist = oltobj.get_authorization_onu(slotno, ponno)
    for key in authONUlist.keys():
        oltobj.sendcmdlines(AN6K.unauth_onu(ONUAuthType.PHYID, authONUlist[key][0], authONUlist[key][1], key))
        if TC_RET:
            TC_RET = oltobj.verify_cmds_exec()

    # 授权待测试ONU，如果已经授权将不进行授权，只更新onuid
    logger.info("授权待测ONU")
    # oltobj.connect_olt()
    # authONUlist = oltobj.get_authorization_onu(slotno, ponno)
    # authONUIDs = []
    # for sn in authONUlist.keys():
    #     authONUIDs.append(int(authONUlist[sn][2]))
    # 授权待测试ONU
    # for item in SETTINGS['ONU']:
    #     phyid = item['PHYID']
    #     onuid = int(item['ONUID'])
    #     if phyid not in authONUlist.keys():
    #         while onuid in authONUIDs:
    #             onuid = random.randint(1, 128)  # 如果ONU id冲突，将随机分配一个未被占用的onuid
    #         oltobj.sendcmdlines(
    #             AN6K.authorize_onu(
    #                 ONUAuthType.PHYID, phyid, item['ONUTYPE'],
    #                 *(slotno, ponno, onuid)))
    #         waitTime(5)

    for item in SETTINGS['ONU']:
        phyid = item['PHYID']
        onuid = int(item['ONUID'])
        oltobj.sendcmdlines(AN6K.authorize_onu(ONUAuthType.PHYID, phyid, item['ONUTYPE'], *(slotno, ponno, onuid)))
        # waitTime(5)

    oltobj.disconnet_olt()

    # 判断ONU是否能正常上线
    logger.info("验证待测试ONU是否可正常上线")
    online = 1
    while online > 0:
        online = len(SETTINGS['ONU'])   # 待测ONU个数
        oltobj.connect_olt()
        authONUlist = oltobj.get_authorization_onu(slotno, ponno)
        oltobj.disconnet_olt()
        for item in SETTINGS['ONU']:
            if item['PHYID'] in authONUlist.keys():
                item['ONUID'] = int(authONUlist[item['PHYID']][2])       # 更新ONUID
                if authONUlist[item["PHYID"]][6] == 'up':
                    logger.info("ONU(%s)授权成功并已成功上线" % item['PHYID'])
                    online -= 1
                else:
                    logger.error("ONU(%s)授权成功,无法上线" % item['PHYID'])
                    waitTime(30)
                    break
            else:
                logger.error("待测试ONU(%s)未授权" % item['PHYID'])
                TC_RET = False
                online = 0
                break
    # logger.info(SETTINGS['ONU'])
    return (TC_RET and bool(online == 0))


def main():
    try:
        global TC_RET
        logger.info("AN5506-04F/HG6243C/HG5255ST模型1测试")
        # 待测试ONU信息
        # slotno = SETTINGS['SLOTNO']
        # 仪表初始化
        stc_init(False)
        # OLT初始化
        # olt_init()

        # 业务模型
        ser_type = 'm3'
        step = 0
        slotno = SETTINGS['SLOTNO']
        ponno = SETTINGS['PONNO']
        stc_uplink = 'uplink'
        for onu in SETTINGS['ONU']:
            if ser_type not in onu['MODEL']:
                continue
            onuid = onu['ONUID']

            # 根据ONUid，修改vlan配置（避免因VLAN冲突，导致业务不通）
            internet_services = MODEL[ser_type]['internet']
            vlanlists = ""
            for internet in internet_services:
                cvlan = internet['vlan']['cvlan']
                internet['vlan']['cvlan'] = ((cvlan[0] + slotno + ponno + onuid) % 4096, random.randint(0, 7))
                vlanlists += ",%d" % internet['vlan']['cvlan'][0]

                svlan = internet['vlan']['svlan'] if 'svlan' in internet['vlan'] else None
                if svlan is not None:
                    internet['vlan']['svlan'] = ((svlan[0] + slotno + ponno + onuid) % 4096, random.randint(0, 7))
                    vlanlists += ",%d" % internet['vlan']['svlan'][0]

            # igmp vlan配置
            iptv_service = MODEL[ser_type]['iptv']
            mvlan = iptv_service['multicast']['vlan']['cvlan'][0]  # 组播VLAN
            if 'tvlan' in iptv_service['multicast']['vlan']:
                mvlan = iptv_service['multicast']['vlan']['tvlan'][0]
            if 'svlan' in iptv_service['multicast']['vlan']:
                mvlan = iptv_service['multicast']['vlan']['svlan'][0]
            vlanlists += ",%d" % mvlan

            pvlan = iptv_service['unicast']['vlan']['cvlan'][0]  # 组播协议VLAN
            if 'tvlan' in iptv_service['unicast']['vlan']:
                pvlan = iptv_service['unicast']['vlan']['tvlan'][0]
            if 'svlan' in iptv_service['unicast']['vlan']:
                pvlan = iptv_service['unicast']['vlan']['svlan'][0]
            vlanlists += ",%d" % pvlan

            # logger.info(MODEL[ser_type])

            oltobj.connect_olt()
            uplink_slot, uplink_port = SETTINGS['UPLINK_PORTS']['uplink'].split("/")
            send_cmds = AN6K.add_uplink_vlan(uplink_slot, uplink_port, VLAN_MODE.TAG, vlanlists[1:])
            send_cmds += config_ONU_Serice(slotno, ponno, onu, MODEL[ser_type])
            oltobj.sendcmdlines(send_cmds)
            oltobj.disconnet_olt()
            TC_RET = oltobj.verify_cmds_exec() if TC_RET else TC_RET

            print(TC_RET)
            #　Internet 业务验证
            for internet in internet_services:
                # print(internet)
                if internet['type'] == 'wan_pppoe':  # PPPoE WAN业务验证
                    for lan in internet['lan']:
                        lan_str = str(lan)
                        if lan_str in onu['STC_PORT'].keys() and onu['STC_PORT'][lan_str].rstrip() != "":
                            stc_onu = onu['STC_PORT'][lan_str]
                            onu_vlan = {}
                            if lan_str in onu['SW_PORT'].keys():       # ONU端口连接交换机
                                onu_vlan = {'cvlan': (100+onu['SW_PORT'][lan_str], 1)}

                            TC_RET &= serviceModel.verifyPPPoEWanService(
                                stc, stc_uplink, stc_onu, internet['vlan'],
                                onu_vlan, (slotno, ponno, onuid), stop=False)
                            # up:100M down:100M
                            # up:2253k down:11264k
                            # up:4506k down:22528k
                            rates = [(100000, 100000), (2253, 11264), (4506, 22528)]
                            for index in range(len(rates)):
                                rate_limit = rates[index]
                                prf_id = 100+index
                                if 1 <= prf_id <= 1024:
                                    cmds = AN6K.add_bandwidth_prf(
                                        "b_prf_%d" % prf_id, prf_id, rate_limit[0],
                                        rate_limit[1])
                                    cmds += AN6K.onu_layer3_ratelimit(slotno, ponno, onuid, [(1, prf_id, prf_id)])
                                else:
                                    cmds = AN6K.onu_layer3_ratelimit(slotno, ponno, onuid, [(1, 65535, 65535)])

                                oltobj.connect_olt()
                                oltobj.sendcmdlines(cmds)
                                oltobj.disconnet_olt()
                                TC_RET &= oltobj.verify_cmds_exec()
                                TC_RET &= serviceModel.wan_ratelimit(
                                    stc, 'pppoe', (slotno, ponno, onuid),
                                    rate_limit, load=(200, 200))

                                # 去绑定限速模板
                                oltobj.connect_olt()
                                cmds = AN6K.onu_layer3_ratelimit(slotno, ponno, onuid, [(1, 65535, 65535)])
                                cmds += AN6K.delete_bandwidth_prf(name="b_prf_%d" % prf_id)
                                oltobj.sendcmdlines(cmds)
                                oltobj.disconnet_olt()
                                TC_RET &= oltobj.verify_cmds_exec()

                            break  # wan 业务只验证一个端口

                elif internet['type'] == 'wan_dhcp':
                    pass
                elif internet['type'] == 'wan_static':
                    pass
                elif internet['type'] == 'fe':
                    for lan in internet['lan']:
                        lan_str = str(lan)
                        if lan_str in onu['STC_PORT'].keys() and onu['STC_PORT'][lan_str].rstrip() != "":
                            stc_onu = onu['STC_PORT'][lan_str]
                            onu_vlan = {}
                            if lan_str in onu['SW_PORT'].keys():
                                onu_vlan = {'cvlan': (100 + onu['SW_PORT'][lan_str], 1)}        # tag 模式

                                if internet['mode'] == 'transparent':   # transparent模式
                                    onu_vlan = {'cvlan': (200 + onu['SW_PORT'][lan_str], 1)}
                                    # ONU 端口为transparent模式，需要根据交换机的配置，更新端口业务配置
                                    internet['vlan']['cvlan'] = onu_vlan['cvlan']
                                    oltobj.connect_olt()
                                    send_cmds = AN6K.add_uplink_vlan(
                                        uplink_slot, uplink_port, VLAN_MODE.TAG, str(onu_vlan['cvlan'][0]))
                                    send_cmds += serviceModel.set_internet_service(
                                        slotno, ponno, onu, MODEL[ser_type], "fe", stop=True)
                                    oltobj.sendcmdlines(send_cmds)
                                    oltobj.disconnet_olt()

                            ret = serviceModel.verifyFEService(
                                stc, stc_uplink, stc_onu, internet['vlan'],
                                onu_vlan,
                                (slotno, ponno, onuid), serviceType='dhcp')
                            TC_RET = ret if TC_RET else TC_RET
                else:
                    pass

            # iptv 业务
            oltobj.connect_olt()
            oltobj.sendcmdlines(AN6K.igmp_vlan(mvlan))
            oltobj.disconnet_olt()
            stc_uplink = 'uplink'
            for lan in iptv_service['lan']:
                lan_str = str(lan)
                if lan_str in onu['STC_PORT'].keys() and onu['STC_PORT'][lan_str].rstrip() != "":
                    stc_onu = onu['STC_PORT'][lan_str]
                    onu_vlan = {}  # 如果有单播，onu侧的vlan将配置单播VLAN
                    # 如果LAN口连接交换机
                    if lan_str in onu['SW_PORT'].keys():
                        onu_vlan = {'cvlan': (100 + onu['SW_PORT'][lan_str], 1)}  # TAG

                        if iptv_service['multicast']['mode'] == 'transparent':
                            onu_vlan = {'cvlan': (200 + onu['SW_PORT'][lan_str], 1)}
                            # ONU 端口为transparent模式，需要根据交换机的配置，更新端口业务配置及组播VLAN配置
                            iptv_service['multicast']['cvlan'] = onu_vlan['cvlan']
                            oltobj.connect_olt()
                            send_cmds = AN6K.add_uplink_vlan(
                                uplink_slot, uplink_port, VLAN_MODE.TAG, str(onu_vlan['cvlan'][0]))
                            send_cmds += AN6K.igmp_vlan(onu_vlan['cvlan'][0])
                            send_cmds += serviceModel.set_internet_service(
                                slotno, ponno, onu, MODEL[ser_type], "fe")
                            oltobj.sendcmdlines(send_cmds)
                            oltobj.disconnet_olt()

                    igmpgroup = "225.10.{0}.1-225.10.{0}.5".format(onuid)
                    ret = serviceModel.verifyIGMPService(
                        stc, stc_uplink, stc_onu, iptv_service['multicast']['vlan'],
                        onu_vlan, (slotno, ponno, onuid), igmpgroup, filterStream="all")
                    TC_RET = ret if TC_RET else TC_RET

        stc.stc_stopAllStreamBlock()
        stc.stc_stopAllDevice()
        stc.stc_disconnect()
        logger.info("测试结束!")
    except:
        TC_RET = False
        logger.error(traceback.format_exc())
    finally:
        stc.stc_apply()
        stc.stc_saveAsXML("tc3.xml")
        result = "PASS" if TC_RET else "FAILED"
        logger.info("AN5506-04F/HG6243C/HG5255ST模型1 测试结果:%s" % result)
        return TC_RET


def run():
    main()


if __name__ == "__main__":
    run()
