#!/usr/bin/python3
# coding=UTF-8
'''
@Description: 
广西EPON MDU 业务模型配置
@Author:  Teddy.tu
@Date: 2019-12-29 20:22:02
@LastEditTime : 2019-12-29 22:20:59
@LastEditors  :  Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''

from lib.fhlib import OLT_V5


def service_model1_cmd(slotno, ponno, *onu_info):
    '''
    函数功能: FTTB 业务模型1
    ONU端口 TAG + ONU qinq模板
    函数参数: 
    @slotno: 槽位号
    @ponno: PON口号
    @onu_info: ONU信息, 格式为((onuno, onuports),), onuid为ONU授权ID; onuports，需要配置的端口业务
    引用命令行:
    Admin(config-pon)#
    onu port vlan 1 eth 1 service count 1
    onu port vlan 1 eth 1 service 1 tag priority 1 tpid 33024 vid 301 
    onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
    使用说明:
    '''
    send_cmdlines = []
    print("EPON FTTB Model 1.")
    onu_num = len(onu_info)
    if onu_num == 0:
        print("WARNING: onu_info is None. No onu services to config!")
        return send_cmdlines

    ser_count = 1
    cvlan = 301
    ccos = 1
    step = 24
    svlan = 2701
    scos = 3
    qinqprf = "FTTB_QINQ"
    svlan_service = "SVLAN2"

    onu_id = 0

    for index in range(onu_num):
        onuno, portnum = onu_info[index]

        for portno in range(1, portnum+1):
            cmd = OLT_V5.onu_lan_service(
                (slotno, ponno, onuno, portno), ser_count,
                {'cvlan': ('transparent', ccos, cvlan+onu_id*step+portno-1),
                 'qinq': ('enable', scos, svlan, qinqprf, svlan_service)})
            send_cmdlines += cmd

        onu_id += 1

    # print("send cmd lines:", send_cmdlines)
    return send_cmdlines
