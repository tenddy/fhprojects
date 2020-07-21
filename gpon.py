#!/usr/bin/python3
# coding=UTF-8
'''
@Description:
GPON ONU业务模型配置
@Author:  Teddy.tu
@Date: 2020-01-19 10:07:02
@LastEditTime: 2020-07-15 13:31:12
@LastEditors: Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''
from lib.oltlib import fhat
from lib.oltlib.fhlib import TL1_CMD
from lib.oltlib.fhlib import OLT_V5


def gpon_service_config_cmd(**kwargs):
    """
    函数功能：通过命令行配置业务(GPON)
    函数参数：@kwargs:
            FILE: ONU信息文件
            ONU_LANPORT: 端口业务模型
    """
    onufile = r'./config/gpon.xlsx'
    if 'FILE' in kwargs.keys():
        onufile = kwargs['FILE']
    onu = fhat.get_data_excel(onufile)

    slotno = kwargs['slotno'] if 'slotno' in kwargs.keys() else 1
    ponno = kwargs['ponno'] if 'ponno' in kwargs.keys() else 6
    cvlan, ccos, cstep = 101, 1, 1
    cvlan_trans = 1401
    tvlan, tcos, tstep = 401, 1, 24
    svlan, scos = 2741, 3
    # onuidtype = 'MAC'
    qinqprf = "FTTB_QINQ"
    # qinqprf = "qinq_ippon"
    svlan_service = "SVLAN2"

    lanportno = kwargs['PORTNO'] if 'PORTNO' in kwargs.keys() else 1  # 配置业务端口号

    cmdlines = []

    cmdlines.append("config\ninterface pon 1/{0}/{1}\n".format(slotno, ponno))
    # lanport_index = range(5)
    for index in range(len(onu)):
        if 'ONU_LANPORT' in kwargs.keys():   # 配置端口业务配置
            for portno in range(onu.loc[index]['PORTNUM']):
                if kwargs['ONU_LANPORT'] == 0:  # del
                    cmdlines += OLT_V5.onu_lan_service((slotno, ponno, onu.loc[index]['ONU'], portno+1), 0)
                if kwargs['ONU_LANPORT'] == 1:   # transparent
                    cmdlines += OLT_V5.onu_lan_service((slotno, ponno, onu.loc[index]['ONU'], portno+1), ccos,
                                                       {'cvlan': ('transparent', tcos, cvlan_trans+index*cstep)})
                if kwargs['ONU_LANPORT'] == 2:  # Tag
                    cmdlines += OLT_V5.onu_lan_service((slotno, ponno, onu.loc[index]['ONU'], portno+1), 1,
                                                       {'cvlan': ('tag', ccos, cvlan+portno+index*cstep)})
                if kwargs['ONU_LANPORT'] == 3:  # tag+ONU qinq模板
                    cmdlines += OLT_V5.onu_lan_service((slotno, ponno, onu.loc[index]['ONU'], portno+1), 1,
                                                       {'cvlan': ('tag', ccos, cvlan+portno+index*tstep),
                                                        'qinq': ('enable', scos, svlan, qinqprf, svlan_service)})
                if kwargs['ONU_LANPORT'] == 4:  # transparent+ONU qinq模板
                    cmdlines += OLT_V5.onu_lan_service((slotno, ponno, onu.loc[index]['ONU'], portno+1), 1,
                                                       {'cvlan': ('transparent', tcos, cvlan_trans+index*cstep),
                                                        'qinq': ('enable', scos, svlan, "qinq_ippon", svlan_service)})
                if kwargs['ONU_LANPORT'] == 5:  # transparent+translate+qinq
                    cmdlines += OLT_V5.onu_lan_service(
                        (slotno, ponno, onu.loc[index]['ONU'],
                         portno + 1),
                        1,
                        {'cvlan': ('transparent', tcos, cvlan_trans + index * cstep),
                         'translate': ('enable', tcos, tvlan + portno + index * tstep),
                         'qinq': ('enable', scos, svlan, "qinq_ippon", svlan_service)})

    cmdlines.append("quit\nquit\n")
    return cmdlines


def gpon_service_config_tl1(**kwargs):
    """
    函数功能: 通过TL1下业务配置（GPON）
    """
    oltip = kwargs['OLTIP'] if "OLTIP" in kwargs.keys() else '10.182.5.109'
    onufile = kwargs['FILE'] if 'FILE' in kwargs.keys() else r'./config/gpon.xlsx'
    onu = fhat.get_data_excel(onufile)

    slotno = kwargs['SLOTNO'] if 'SLOTNO' in kwargs.keys() else 12
    ponno = kwargs['PONNO'] if 'PONNO' in kwargs.keys() else 4
    cvlan, ccos, cstep = 1501, 1, 24     # CVLAN
    tvlan, tcos, tstep = 1501, 1, 24     # TVALN
    svlan, scos = 2740, 3       # SVLAN
    mvlan = kwargs['mvlan'] if 'mvlan' in kwargs.keys() else 33  # 组播VLAN
    onuidtype = 'MAC'   # ONU认证方式

    lanportno = kwargs['PORTNO'] if 'PORTNO' in kwargs.keys() else 2  # 配置业务端口号

    cmdlines = []   # 保存TL1 命令行

    if "ONU" in kwargs.keys():
        print("授权/去授权ONU")
        for index in range(len(onu)):   # 遍历ONU
            if onu.loc[index]['ONUTYPE'] == "OTHER2":
                onutype = "OTHER_ONU2"
            else:
                onutype = onu.loc[index]['ONUTYPE']

            if kwargs['ONU']:
                cmdlines += TL1_CMD.add_onu(oltip, slotno, ponno,
                                            onu.loc[index]['ONUIDTYPE'], onu.loc[index]['SN'], onutype)
            else:
                cmdlines += TL1_CMD.del_onu(oltip, slotno, ponno, onu.loc[index]['ONUIDTYPE'], onu.loc[index]['SN'])

    if "ONU_LANPORT" in kwargs.keys():   # 配置端口业务
        print("配置ONU端口业务，模型%d" % kwargs['ONU_LANPORT'])
        for index in range(len(onu)):   # 遍历ONU
            for portno in range(onu.loc[index]['PORTNUM']):     # 遍历ONU LAN口
                if kwargs['ONU_LANPORT'] == 0:  # 删除端口业务
                    cmdlines += TL1_CMD.del_lanport_vlan(oltip, slotno, ponno, onuidtype,
                                                         onu.loc[index]['SN'], portno+1, cvlan+portno+index*cstep)

                if kwargs['ONU_LANPORT'] == 1:  # model1（TAG）
                    cmdlines += TL1_CMD.cfg_lanport_vlan(oltip, slotno, ponno, onuidtype,
                                                         onu.loc[index]['SN'], portno+1, cvlan+portno+index*cstep, CCOS=ccos)

                if kwargs['ONU_LANPORT'] == 2:  # model2 （TAG+ONU qinq域）
                    cmdlines += TL1_CMD.cfg_lanport_vlan(
                        oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'],
                        portno + 1, cvlan + portno + index * cstep, SVLAN=svlan, SCOS=scos, CCOS=ccos)

                if kwargs['ONU_LANPORT'] == 3:  # model3 （透传+翻译 + ONU qinq域）
                    cmdlines += TL1_CMD.cfg_lanport_vlan(
                        oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'],
                        portno + 1, cvlan + portno + index * tstep, SVLAN=svlan, UV=cvlan + portno + index * cstep,
                        SCOS=scos, CCOS=ccos)

    if "ONU_IPTVPORT" in kwargs.keys():
        print("配置ONU端口组播业务")
        for index in range(len(onu)):   # 遍历ONU
            for portno in range(onu.loc[index]['PORTNUM']):  # 遍历ONU LAN口
                if kwargs['ONU_IPTVPORT']:
                    cmdlines += TL1_CMD.add_laniptvport(oltip, slotno, ponno, onuidtype,
                                                        onu.loc[index]['SN'], portno+1, mvlan, MCOS=5)
                else:
                    cmdlines += TL1_CMD.del_laniptvport(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], portno+1)

    if 'QINQ' in kwargs.keys():
        print("="*20)
        print("配置QinQ")
        for index in range(len(onu)):   # 遍历ONU
            if onu.loc[index]['ONUTYPE'] == 'AN5006-20':  # AN5006-20 业务模型
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype,
                                                onu.loc[index]['SN'], 3001, SVLAN=2701, UV=3001, SCOS=scos, CCOS=ccos)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype,
                                                onu.loc[index]['SN'], 3002, SVLAN=2701, UV=3002, SCOS=scos, CCOS=ccos)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 33, UV=50)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 251, UV=251)

            elif onu.loc[index]['ONUTYPE'] == 'OTHER2':  # EPON HGU
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype,
                                                onu.loc[index]['SN'], 41, SVLAN=2401, UV=41, SCOS=scos, CCOS=ccos)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype,
                                                onu.loc[index]['SN'], 45, SVLAN=2401, UV=45, SCOS=scos, CCOS=ccos)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 33, UV=33)
                cmdlines += TL1_CMD.add_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], 250, UV=250)

            else:  # FTTB&SFU业务模型
                # 根据端口数量和需要配置端口号，选择需要配置的端口
                port = min(onu.loc[index]['PORTNUM'], lanportno)
                if kwargs['QINQ']:  # True, 添加QinQ
                    cmdlines += TL1_CMD.add_ponvlan(
                        oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'],
                        tvlan + port - 1 + index * tstep, SVLAN=svlan, UV=cvlan + port - 1 + index * cstep, SCOS=scos,
                        CCOS=ccos)
                else:   # False, 删除QinQ
                    cmdlines += TL1_CMD.del_ponvlan(oltip, slotno, ponno, onuidtype,
                                                    onu.loc[index]['SN'], cvlan+port-1+index*cstep)
                    cmdlines += TL1_CMD.del_ponvlan(oltip, slotno, ponno, onuidtype, onu.loc[index]['SN'], mvlan)

    # 配置ONU带宽
    if "ADDBW" in kwargs.keys():
        print("="*20)
        print("配置ONU带宽")
        bandwidth = kwargs['bandwidth'] if 'bandwidth' in kwargs.keys() else (64, 1000000, 64, 1000000, 64)
        # bandwidth = (256,1000,256,5000,512)
        # 创建带宽模板
        cmdlines += TL1_CMD.add_BWprofile(oltip, kwargs['ADDBW'], *bandwidth)
        # cmdlines += TL1_CMD.add_BWprofile(oltip, kwargs['ADDBW'], *default_bw)
        if 'CFGBW' in kwargs.keys() and kwargs['CFGBW']:
            for index in range(len(onu)):   # 遍历ONU
                cmdlines += TL1_CMD.cfg_onuBW(oltip, slotno, ponno, onuidtype,
                                              onu.loc[index]['SN'], kwargs['ADDBW'], kwargs['ADDBW'])        # ONU绑定带宽模板

    return cmdlines


def get_linecmds():
    cmds = []
    cmds += gpon_service_config_cmd(ONU_LANPORT=0)
    return cmds


def get_linecmds_tl1():
    cmds = []
    # cmds += gpon_service_config_tl1(ONU=True)
    cmds += gpon_service_config_tl1(ONU_LANPORT=1)
    return cmds


if __name__ == "__main__":

    # tl1_cmds = []
    # tl1_cmds += gpon_service_config_tl1(ONU=False)
    # for c in tl1_cmds:
    #     print(c, end='')
    # cmds = gpon_service_config_cmd(FILE='./etc/gpon1.xlsx', slotno=1, ponno=6, ONU_LANPORT=0)
    cmds = gpon_service_config_cmd(FILE='./etc/gpon1.xlsx', slotno=1, ponno=6, ONU_LANPORT=2)

    oltobj = fhat.FH_OLT()
    oltobj.oltip = '10.182.1.81'
    oltobj.login_promot = {'Login': 'admin123', 'Password': 'admin123'}
    print(oltobj.login_promot)
    oltobj.connect_olt()
    oltobj.sendcmdlines(cmds)
