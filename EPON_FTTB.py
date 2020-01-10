#!/usr/bin/python3
# coding=UTF-8
'''
@Description: 
广西EPON MDU 业务模型配置
@Author:  Teddy.tu
@Date: 2019-12-29 20:22:02
@LastEditTime : 2019-12-29 22:36:28
@LastEditors  :  Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''

from lib.fhlib import OLT_V5
from lib.fhlib import TL1_CMD
from lib.dut_connect import connect_olt_telnet
from lib import dut_connect
from lib.FHAT import ServiceConfig
from lib.log import Logger
import sys
import pandas as pd
import math

def get_onu_info(filename):
    """
    获取ONU信息，返回格式为DataFrame
    """
    data = pd.read_excel(filename)
    return data

def service_del_cmd(slotno, ponno, *onu_info):
    '''
    函数功能: FTTB 端口业务删除
    ONU端口 
    函数参数: 
    @slotno: 槽位号
    @ponno: PON口号
    @onu_info: ONU信息, 格式为((onuno, onuports),), onuid为ONU授权ID; onuports，需要配置的端口业务
    引用命令行:
    Admin(config-pon)#
    onu port vlan 1 eth 1 service count 0
    使用说明:
    '''
    send_cmdlines = []
    print("EPON FTTB service delete.")
    onu_num = len(onu_info)
    if onu_num == 0:
        print("WARNING: onu_info is None. No onu services to config!")
        return send_cmdlines

    ser_count = 0
    # cvlan = 301
    # ccos = 1
    # step = 24
    # svlan = 2701
    # scos = 3
    # qinqprf = "FTTB_QINQ"
    # svlan_service = "SVLAN2"

    onu_id = 0
    # send_cmdlines.append('config\n')
    # send_cmdlines.append('interface pon 1/%d/%d\n' % (slotno, ponno))

    for index in range(onu_num):
        onuno, portnum = onu_info[index]
        for portno in range(1, int(portnum)+1):
            cmd = OLT_V5.onu_lan_service((slotno, ponno, onuno, portno), ser_count)
            send_cmdlines += cmd

        onu_id += 1

    # send_cmdlines.append('quit\n')
    return send_cmdlines


def service_model0_cmd(slotno, ponno, *onu_info):
    '''
    函数功能: FTTB 业务模型0
    ONU端口 TAG
    函数参数: 
    @slotno: 槽位号
    @ponno: PON口号
    @onu_info: ONU信息, 格式为((onuno, onuports),), onuid为ONU授权ID; onuports，需要配置的端口业务
    引用命令行:
    Admin(config-pon)#
    onu port vlan 1 eth 1 service count 1
    onu port vlan 1 eth 1 service 1 tag priority 1 tpid 33024 vid 301 
    使用说明:
    '''
    send_cmdlines = []
    print("EPON FTTB Model 0.")
    onu_num = len(onu_info)
    if onu_num == 0:
        print("WARNING: onu_info is None. No onu services to config!")
        return send_cmdlines

    ser_count = 1
    cvlan = 301
    ccos = 1
    step = 24
    # svlan = 2701
    # scos = 3
    # qinqprf = "FTTB_QINQ"
    # svlan_service = "SVLAN2"

    onu_id = 0
    # send_cmdlines.append('config\n')
    # send_cmdlines.append('interface pon 1/%d/%d\n' % (slotno, ponno))

    for index in range(onu_num):
        onuno, portnum = onu_info[index]
        for portno in range(1, int(portnum)+1):
            cmd = OLT_V5.onu_lan_service(
                (slotno, ponno, onuno, portno), ser_count,
                {'cvlan': ('tag', ccos, cvlan+onu_id*step+portno-1)})

            send_cmdlines += cmd

        onu_id += 1

    # send_cmdlines.append('quit\n')
    return send_cmdlines


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
    # send_cmdlines.append('config\n')
    # send_cmdlines.append('interface pon 1/%d/%d\n' % (slotno, ponno))

    for index in range(onu_num):
        onuno, portnum = onu_info[index]
        for portno in range(1, int(portnum)+1):
            # 删除端口业务
            cmd_del = OLT_V5.onu_lan_service((slotno, ponno, onuno, portno), 0)
            send_cmdlines += cmd_del
            cmd = OLT_V5.onu_lan_service(
                (slotno, ponno, onuno, portno), ser_count,
                {'cvlan': ('tag', ccos, cvlan+onu_id*step+portno-1),
                 'qinq': ('enable', scos, svlan, qinqprf, svlan_service)})
            send_cmdlines += cmd

        onu_id += 1

    # print("send cmd lines:", send_cmdlines)
    # send_cmdlines.append('quit\n')
    return send_cmdlines


def service_model2_cmd(slotno, ponno, *onu_info):
    '''
    函数功能: FTTB 业务模型2
    ONU端口 transparent + ONU qinq模板
    函数参数: 
    @slotno: 槽位号
    @ponno: PON口号
    @onu_info: ONU信息, 格式为((onuno, onuports),), onuid为ONU授权ID; onuports，需要配置的端口业务
    引用命令行:
    Admin(config-pon)#
    onu port vlan 1 eth 1 service count 1
    onu port vlan 1 eth 1 service 1 transparent priority 1 tpid 33024 vid 2001 
    onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
    使用说明:
    '''
    send_cmdlines = []
    print("EPON FTTB Model 1.")
    # print(onu_info)
    onu_num = len(onu_info)
    if onu_num == 0:
        print("WARNING: onu_info is None. No onu services to config!")
        return send_cmdlines

    ser_count = 1
    cvlan = 2001
    ccos = 1
    step = 1
    svlan = 2701
    scos = 3
    qinqprf = "FTTB_QINQ"
    svlan_service = "SVLAN2"

    onu_id = 0
    # send_cmdlines.append('config\n')
    # send_cmdlines.append('interface pon 1/%d/%d\n' % (slotno, ponno))

    for index in range(onu_num):
        onuno, portnum = onu_info[index]

        for portno in range(1, int(portnum)+1):
            # cmd_del = OLT_V5.onu_lan_service((slotno, ponno, onuno, portno), 0)
            # send_cmdlines += cmd_del
            cmd = OLT_V5.onu_lan_service(
                (slotno, ponno, onuno, portno), ser_count,
                {'cvlan': ('transparent', ccos, cvlan+onu_id*step),
                 'qinq': ('enable', scos, svlan, qinqprf, svlan_service)})
            send_cmdlines += cmd

        onu_id += 1

    # print("send cmd lines:", send_cmdlines)
    # send_cmdlines.append('quit\n')
    return send_cmdlines


def service_model3_cmd(slotno, ponno, *onu_info):
    '''
    函数功能: FTTB 业务模型2
    ONU端口 transparent + 翻译 + ONU qinq模板
    函数参数: 
    @slotno: 槽位号
    @ponno: PON口号
    @onu_info: ONU信息, 格式为((onuno, onuports),), onuid为ONU授权ID; onuports，需要配置的端口业务
    引用命令行:
    Admin(config-pon)#
    onu port vlan 1 eth 1 service count 1
    onu port vlan 1 eth 1 service 1 transparent priority 1 tpid 33024 vid 2001
    onu port vlan 1 eth 1 service 1 translate enable priority 1 tpid 33024 vid 301 
    onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
    使用说明:
    '''
    send_cmdlines = []
    print("EPON FTTB Model 3.")
    onu_num = len(onu_info)
    if onu_num == 0:
        print("WARNING: onu_info is None. No onu services to config!")
        return send_cmdlines

    ser_count = 1
    cvlan, ccos, step = 2001, 1, 1
    tvlan, tcos, tstep = 301, 1, 24
    svlan, scos = 2701, 3

    qinqprf = "FTTB_QINQ"
    svlan_service = "SVLAN2"

    onu_id = 0
    # send_cmdlines.append('config\n')
    # send_cmdlines.append('interface pon 1/{0}/{1}\n'.format(slotno, ponno))

    for index in range(onu_num):
        onuno, portnum = onu_info[index]
        for portno in range(1, int(portnum)+1):
            cmd_del = OLT_V5.onu_lan_service((slotno, ponno, onuno, portno), 0)
            send_cmdlines += cmd_del
            cmd = OLT_V5.onu_lan_service(
                (slotno, ponno, onuno, portno), ser_count,
                {'cvlan': ('transparent', ccos, cvlan+onu_id*step),
                 'translate': ('enable', tcos, tvlan+onu_id*tstep+portno-1),
                 'qinq': ('enable', scos, svlan, qinqprf, svlan_service)})
            send_cmdlines += cmd

        onu_id += 1

    # print("send cmd lines:", send_cmdlines)
    # send_cmdlines.append('quit\n')
    return send_cmdlines


def epon_service_config():
    # model1
    onu_list = open(r'./config/epon_onu.txt', 'r', encoding='utf8')
    slotno = 13
    ponno = 12
    onu_info = []
    onutype = []
    sn = []
    voip_ip = []
    voip_user = []

    for line in onu_list:
        onu = line.split()
        if onu[0] == '#':
            continue

        onu_info.append((onu[2], onu[5]))
        onutype.append(onu[3])
        sn.append(onu[4])
        voip_ip.append(onu[6])
        voip_user.append(onu[7])
    onu_list.close()

    config_del = service_del_cmd(slotno, ponno, *tuple(onu_info))
    with open(r'./config/config_del.txt', 'w') as f:
        for item in config_del:
            f.write(item)

    configs = service_model1_cmd(slotno, ponno, *tuple(onu_info[:14]))
    configs += service_model0_cmd(slotno, ponno, *tuple(onu_info[14:20]))
    with open(r'./config/epon_model1.txt', 'w') as f:
        for item in configs:
            f.write(item)


def issue_test(model=1, slotno=3, ponno=16, onuno_begin=0):
    onu_info = []
    onutype = []
    sn = []
    voip_ip = []
    voip_user = []
    # 回读EPON ONU 信息， 返回ONU信息格式如下：
    # 槽位号,PON口号,ONU号,设备类型,物理地址,端口个数,语音IP1,语音用户名1,语音IP2,语音用户名2
    onu_list = open(r'./config/epon_onu.txt', 'r', encoding='utf8')
    for line in onu_list:
        onu = line.split()
        if onu[0] == '#':
            continue

        onu_info.append(((int(onu[2]) + onuno_begin)%128, int(onu[5]))) # ONU信息(onuid, onuports)
        onutype.append(onu[3])      # ONU 类型
        sn.append(onu[4])           # ONU sn(mac)
        voip_ip.append(onu[6])      # 语音IP1
        voip_user.append(onu[7])    # 语音用户名1

    onu_list.close()

    config_cmds = [] 
    config_cmds.append('config\n')
    # config_cmds += service_del_cmd(slotno, ponno, *tuple(onu_info[:14]))
    
    onu_count = len(onu_info)   # ONU 数量
   
    # 去授权ONU
    del_onu_flag = False
    if del_onu_flag:
        for index in range(onu_count):
         config_cmds += OLT_V5.unauth_onu('phy-id', slotno, ponno, sn[index])

    # 授权ONU
    add_onu_flag = False
    if add_onu_flag:
        for index in range(onu_count):
            config_cmds += OLT_V5.authorize_onu('phy-id', sn[index], onutype[index][2:], slotno, ponno, onu_info[index][0])

    config_cmds.append('interface pon 1/%d/%d\n' % (slotno, ponno))
    # 配置端口业务
    lan_service_flag = True
    if lan_service_flag:
        if 0 == model: # 模型0 
            config_cmds += service_model0_cmd(slotno, ponno, *tuple(onu_info[:onu_count-2]))
        if 1 == model: # 模型1
            config_cmds += service_model1_cmd(slotno, ponno, *tuple(onu_info[:onu_count-2]))
        if 3 == model: # 模型3
            config_cmds += service_model3_cmd(slotno, ponno, *tuple(onu_info[:onu_count-2]))

    # 配置语音业务
    add_voice_flag = False
    if add_voice_flag:
         for index in range(12, onu_count):
            print("voip1", voip_ip[index])
            if voip_ip[index] == 'NaN':
                 continue
            # print("voip2", voip_ip[index])
            print("voip1", voip_ip[index])
            for pots in range(1, 9):
                config_cmds += OLT_V5.onu_ngn_voice_service((slotno, ponno, onu_info[index][0]), pots, int(voip_user[index])+pots-1)

    config_cmds.append('quit\n')
    return config_cmds


def tl1_cmd():
    unm_ip = '10.182.1.161'
    unm_user, unm_pwd = 'admin', 'admin123'
    unm_tn = dut_connect.dut_connect_tl1(unm_ip, username=unm_user, password=unm_pwd)

    onufile = r'E:/DDTU Workplace/测试项目/2020Q1/epon.xls'
    onu = get_onu_info(onufile)
    print(onu.head())
    cmdlines = []
    cvlan, ccos, step = 301, 1, 1
    tvlan, tcos, tstep = 301, 1, 24
    svlan, scos = 2701, 3
    portno = 2 #配置业务端口号
    for index in range(len(onu)):
        if onu.loc[index]['ONUTYPE'] == 'AN5006-20':
            print("AN5006-20")
            continue
        
        # 根据端口数量和需要配置端口号，选择需要配置的端口
        port = min(onu.loc[index]['PORTNUM'], portno)       
        # 配置qinq域
        add_cmds = TL1_CMD.add_ponvlan('10.182.5.109', 4, 8, 'MAC', onu.loc[index]['SN'], cvlan+port-1+index*24,SVLAN=svlan, UV=cvlan+port-1+index*24,SCOS=scos,CCOS=ccos)
        # 删除qinq域
        del_cmds = TL1_CMD.del_ponvlan('10.182.5.109', 4, 8, 'MAC', onu.loc[index]['SN'], cvlan+port-1+index*24)
        cmds  = add_cmds
        print(cmds)
        unm_tn.write(bytes(cmds, encoding="utf8"))
        ret = unm_tn.read_until(b';', 5)
        print(str(ret, encoding="utf8"))

    dut_connect.dut_disconnect_tl1(unm_tn)



if __name__ == "__main__":
    # tn_obj = connect_olt_telnet('10.182.5.109', 23, b'admin', b'admin')
    # log_obj = Logger(r'./log/issues.log')
    # send_cmd_obj = ServiceConfig(tn_obj, log_obj)
    # print(sys.argv[0])
    slotno = 4
    ponno = 8
    onuno_step = 0
    if len(sys.argv) <= 1:
        model = 0
    else:
        model = int(sys.argv[1])
    
    cmds = issue_test(model, slotno, ponno, onuno_step)
    # print(cmds)
    # send_cmd_obj.send_cmd(cmds,delay=0.5)
    tl1_cmd()
