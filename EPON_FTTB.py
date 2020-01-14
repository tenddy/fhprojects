#!/usr/bin/python3
# coding=UTF-8
'''
@Description: 
广西EPON MDU 业务模型配置
@Author:  Teddy.tu
@Date: 2019-12-29 20:22:02
@LastEditTime : 2020-01-12 20:36:25
@LastEditors  :  Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''

from lib.fhlib import OLT_V5
from lib.fhlib import TL1_CMD
from lib.dut_connect import dut_connect_telnet
from lib import dut_connect
from lib.fhat import ServiceConfig
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

def get_cmd(**kwargs):
    """"""
    onufile = r'./config/epon.xls'
    if 'FILE' in kwargs.keys():
        onufile = kwargs['FILE']
    onu = get_onu_info(onufile)

    slotno = 4
    ponno = 8
    cvlan, ccos, cstep = 301, 1, 1
    tvlan, tcos, tstep = 301, 1, 24
    svlan, scos = 2701, 3
    onuidtype = 'MAC'
    qinqprf = "FTTB_QINQ"
    # qinqprf = "qinq_ippon"
    svlan_service = "SVLAN2"

    lanportno = 2 #配置业务端口号
    if 'PORTNO' in kwargs.keys():
        portno = kwargs['PORTNO']

    cmdlines = []
    
    cmdlines.append("config\ninterface pon 1/{0}/{1}\n".format(slotno, ponno))
    for index in range(len(onu)):
        if 'ONU_LANPORT' in kwargs.keys():   # 配置端口业务配置
            for portno in range(onu.loc[index]['PORTNUM']):
                if kwargs['ONU_LANPORT'] == 0: # del
                    cmdlines += OLT_V5.onu_lan_service((slotno,ponno,onu.loc[index]['ONU'], portno+1), 0)
                if kwargs['ONU_LANPORT'] == 1:   # TAG
                    cmdlines += OLT_V5.onu_lan_service((slotno,ponno,onu.loc[index]['ONU'], portno+1), ccos, 
                    {'cvlan': ('transparent', tcos, 2001+index*cstep)}) 
                if kwargs['ONU_LANPORT'] == 2: # transparent
                    cmdlines += OLT_V5.onu_lan_service((slotno,ponno,onu.loc[index]['ONU'], portno+1), 1, 
                    {'cvlan': ('tag', ccos, cvlan+portno+index*tstep)})
                if kwargs['ONU_LANPORT'] == 3: # tag+ONU qinq模板
                    cmdlines += OLT_V5.onu_lan_service((slotno,ponno,onu.loc[index]['ONU'], portno+1), 1, 
                    {'cvlan': ('tag', ccos, cvlan+portno+index*tstep), 
                    'qinq':('enable', scos, svlan, qinqprf, svlan_service)})
                if kwargs['ONU_LANPORT'] == 4: # transparent+ONU qinq模板
                    cmdlines += OLT_V5.onu_lan_service((slotno,ponno,onu.loc[index]['ONU'], portno+1), 1, 
                    {'cvlan': ('transparent', tcos, 2001+index*cstep),
                     'qinq':('enable', scos, svlan, "qinq_ippon", svlan_service)} )
    
    cmdlines.append("quit\nquit\n")
    return cmdlines


def tl1_cmd(**kwargs):
    """
    @kwargs:
        OLTIP: OLT ip 地址;
        FILE: ONU 列表;
        slotno: 槽位号
        ponno: PON口号
        ONU: True--> 授权ONU, False--> 去授权ONU
        ONU_LANPORT: 配置端口业务; 0-->删除端口业务, 1-->TAG, 2-->TAG+ONU qinq域, 3-->透传+翻译 + ONU qinq域
        PORTNO: ONU端口号;
        QINQ: True 添加qinq域， False 删除qinq域;
        ADDBW: 带宽模板名，创建新的带宽模板;
        CFGBW: 绑定带宽模板; 与参数ADDBW结合使用
    """
    oltip = kwargs['OLTIP'] if "OLTIP" in kwargs.keys() else '10.182.5.109'
    onufile = kwargs['FILE'] if 'FILE' in kwargs.keys() else r'./config/epon.xls'
    onu = get_onu_info(onufile)
    
    slotno = kwargs['SLOTNO'] if 'SLOTNO' in kwargs.keys() else 4
    ponno = kwargs['PONNO'] if 'PONNO' in kwargs.keys() else 7
    cvlan, ccos, cstep = 301, 1, 24     # CVLAN
    tvlan, tcos, tstep = 301, 1, 24     # TVALN
    svlan, scos = 2701, 3       # SVLAN
    mvlan = kwargs['mvlan'] if 'mvlan' in kwargs.keys() else 33 # 组播VLAN
    onuidtype = 'MAC'   # ONU认证方式

    lanportno = 2 #配置业务端口号
    if 'PORTNO' in kwargs.keys():
        portno = kwargs['PORTNO']
   
    cmdlines = []   # 保存TL1 命令行

    if "ONU" in kwargs.keys():
        print("授权/去授权ONU") 
        for index in range(len(onu)):   # 遍历ONU
            if onu.loc[index]['ONUTYPE'] == "OTHER2":
                onutype = "OTHER_ONU2"
            else:
                onutype = onu.loc[index]['ONUTYPE']

            if kwargs['ONU']:
               
                cmdlines += TL1_CMD.add_onu(oltip, slotno, ponno, onu.loc[index]['ONUIDTYPE'], onu.loc[index]['SN'], onutype)
            else:
                cmdlines += TL1_CMD.del_onu(oltip, slotno, ponno, onu.loc[index]['ONUIDTYPE'], onu.loc[index]['SN'])

    if "ONU_LANPORT" in kwargs.keys():   # 配置端口业务
        print("配置ONU端口业务，模型%d" % kwargs['ONU_LANPORT'])
        for index in range(len(onu)):   # 遍历ONU
            for portno in range(onu.loc[index]['PORTNUM']): #遍历ONU LAN口
                if kwargs['ONU_LANPORT'] == 0: # 删除端口业务
                    cmdlines += TL1_CMD.del_lanport_vlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], portno+1, cvlan+portno+index*tstep)

                if kwargs['ONU_LANPORT'] == 1: # model1（TAG）
                    cmdlines += TL1_CMD.cfg_lanport_vlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], portno+1, cvlan+portno+index*tstep, CCOS=ccos)
                    cmdlines += TL1_CMD.add_laniptvport(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], portno+1, mvlan, MCOS=5)

                if kwargs['ONU_LANPORT'] == 2: # model2 （TAG+ONU qinq域）
                    cmdlines += TL1_CMD.cfg_lanport_vlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], portno+1, cvlan+portno+index*tstep, SVLAN=svlan, SCOS=scos, CCOS=ccos)
                
                if kwargs['ONU_LANPORT'] == 3: # model3 （透传+翻译 + ONU qinq域）
                    cmdlines += TL1_CMD.cfg_lanport_vlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], portno+1, cvlan+portno+index*tstep, SVLAN=svlan, UV=cvlan+portno+index*tstep, SCOS=scos, CCOS=ccos)
    
    if "ONU_IPTVPORT" in kwargs.keys():
        print("配置ONU端口组播业务")
        for index in range(len(onu)):   # 遍历ONU
            for portno in range(onu.loc[index]['PORTNUM']): #遍历ONU LAN口
                if kwargs['ONU_IPTVPORT']:
                    cmdlines += TL1_CMD.add_laniptvport(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], portno+1, mvlan, MCOS=5)
                else:
                    cmdlines += TL1_CMD.del_laniptvport(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], portno+1)

    
    if 'QINQ' in kwargs.keys():
        print("="*20)
        print("配置QinQ")
        for index in range(len(onu)):   # 遍历ONU
            if onu.loc[index]['ONUTYPE'] == 'AN5006-20':
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 3001, SVLAN=2701, UV=3001, SCOS=scos, CCOS=ccos)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 3002, SVLAN=2701, UV=3002, SCOS=scos, CCOS=ccos)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 33, UV=50)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 251, UV=251)
            
            elif onu.loc[index]['ONUTYPE'] == 'OTHER2':
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 41, SVLAN=2401, UV=41, SCOS=scos, CCOS=ccos)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 45, SVLAN=2401, UV=45, SCOS=scos, CCOS=ccos)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 33, UV=33)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 250, UV=250)
            
            else:
                # 根据端口数量和需要配置端口号，选择需要配置的端口
                port = min(onu.loc[index]['PORTNUM'], lanportno) 
                if kwargs['QINQ']:  # True, 添加QinQ
                    cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], tvlan+port-1+index*tstep, SVLAN=svlan, UV=cvlan+port-1+index*cstep, SCOS=scos, CCOS=ccos)
                else:   # False, 删除QinQ
                    cmdlines += TL1_CMD.del_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], cvlan+port-1+index*cstep)
                    cmdlines += TL1_CMD.del_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], mvlan)
    
    # 配置ONU带宽
    if "ADDBW" in kwargs.keys():
        print("="*20)
        print("配置ONU带宽")
        default_bw = (64,1000000,64,1000000,64)
        bandwidth = (256,1000,256,5000,512)
        # cmdlines += TL1_CMD.add_BWprofile(oltip, bw_prfname, *bandwidth) 
        cmdlines += TL1_CMD.add_BWprofile(oltip, kwargs['ADDBW'], *default_bw)  # 创建带宽模板
        if 'CFGBW' in kwargs.keys() and kwargs['CFGBW']:
            for index in range(len(onu)):   # 遍历ONU
                cmdlines += TL1_CMD.cfg_onuBW(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], kwargs['ADDBW'], kwargs['ADDBW'])        # ONU绑定带宽模板
        
    return cmdlines


if __name__ == "__main__":
    # telnet OLT   
    oltip = '10.182.5.109'     
    tn_obj = dut_connect.dut_connect_telnet('10.182.5.109', 23, 'admin', 'admin')
    log_obj = Logger(r'./log/issues.log')
    cmd_send_obj = ServiceConfig(tn_obj, log_obj)
    
    # TL1 
    unm_ip = '10.182.1.161'
    unm_user, unm_pwd = 'admin', 'admin123'
    unm_tn = dut_connect.dut_connect_tl1(unm_ip, username=unm_user, password=unm_pwd)
    tl1_cmd_obj = ServiceConfig(unm_tn, Logger(r'./log/tl1_log.log'))
    
    slotno = 17
    ponno = 4
    onuno_step = 0
    
    # cmds = issue_test(model, slotno, ponno, onuno_step)
    # cmds = get_cmd(ONU_LANPORT=0)
    # cmd_send_obj.send_cmd(cmds,delay=0.1)

    #### TL1 #####
    bwprf1 = "EPON_1000M"
    bwprf2 = "EPON_1M_5M"
    tl1_sendline_cmds = []
    tl1_sendline_cmds += tl1_cmd(OLTIP='10.182.5.109', SLOTNO=7, PONNO=5, ONU=False)
    tl1_sendline_cmds += tl1_cmd(OLTIP='10.182.5.109', SLOTNO=slotno, PONNO=ponno, ONU=True)

    # tl1_sendline_cmds += tl1_cmd(OLTIP='10.182.5.109', ONU_LANPORT=False, QINQ=True, ADDBW='EPON_1M_5M', CFGBW=True)
    # tl1_sendline_cmds += tl1_cmd(OLTIP='10.182.5.109', ONU_LANPORT=0)
    tl1_sendline_cmds += tl1_cmd(OLTIP='10.182.5.109', SLOTNO=slotno, PONNO=ponno, ONU_LANPORT=1)
    tl1_sendline_cmds += tl1_cmd(OLTIP='10.182.5.109', SLOTNO=slotno, PONNO=ponno, ONU_IPTVPORT=True)

    tl1_sendline_cmds += tl1_cmd(OLTIP='10.182.5.109', SLOTNO=slotno, PONNO=ponno, QINQ=True)
    tl1_sendline_cmds += tl1_cmd(OLTIP='10.182.5.109', SLOTNO=slotno, PONNO=ponno, ADDBW=bwprf1, CFGBW=True)

    # for item in tl1_sendline_cmds:
    #     print(item, end='')
    tl1_cmd_obj.send_cmd(tl1_sendline_cmds, promot=b';', delay=0.1)
    
    dut_connect.dut_disconnect_tl1(unm_tn)
