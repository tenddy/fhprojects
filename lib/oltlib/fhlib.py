# -*- encoding: utf-8 -*-
'''
@File    : fhlib.py
@Date    : 2019/08/13 08:18:21
@Author  : Teddy.tu
@Version : V1.0
@EMAIL   : teddy_tu@126.com
@License : (c)Copyright 2019-2020, Teddy.tu
@Desc    : None
'''


from enum import Enum


class VLAN_MODE(Enum):
    """ONU 端口业务模式"""
    UNTAG = 0
    TAG = 1
    TRANSLATE = 2
    TRANSPARENT = 3
    mode = ('untag', 'tag', 'translate', 'transparent')


class SericeType(Enum):
    """业务类型"""
    UNICAST = 0
    MULTICAST = 1
    type = ('unicast', 'multicast')


class ONUAuthType(Enum):
    """授权ONU方式"""
    PHYID = 0
    PASSWORD = 1
    LOID = 2
    LOIDPSW = 3


class PONAuthMode(Enum):
    """PON口授权模式

        @LOID             Authenticate onu by logical SN without password.

        @LOID_AND_PSW     Authenticate onu by logical SN with password.

        @NO_AUTH          Authorize onu directly, needn't authentication.

        @PASSWORD         Authenticate onu by physical password.

        @PHYID            Authenticate onu by physical ID.

        @PHYID_AND_PSW    Authenticate onu by physical ID and physical password.

        @PHYID_OR_LOID     Authenticate onu by physical ID or logical SN without password or physical password or registration ID.

        @PHYID_OR_LOIDPSW  Authenticate onu by physical ID or logical SN with password or physical password or registration ID.

        @PHYID_OR_PSW       Authenticate onu by physical ID or physical password.

        @REGID             Authenticate onu by registration ID.
    """
    NO_AUTH = 0
    PHYID = 1
    LOID = 2
    PASSWORD = 3
    PHYID_AND_PSW = 4
    LOID_ADN_PSW = 5
    PHYID_OR_LOID = 6
    PHYID_OR_PSW = 7
    PHYID_OR_LOIDPSW = 8
    REGID = 9


class TL1_CMD():
    def __init__(self):
        self.version__ = ""
        pass

    @staticmethod
    def add_onu(oltid, slotno, ponno, onuidtype, onuid, onutype, bandtype=None, **kwargs):
        """
        函数功能：TL1授权ONU
        函数参数:
        @oltid(string):olt ip
        @slotno(string/int):槽位号
        @ponno(string/int):PON口号
        @onuidtype(string):ONU标识类型（ONU_NAME、MAC、LOID、ONU_NUMBER）
        @onuid(string):ONU标识，可以取值：ONU_NAME、MAC、LOID、ONU_NUMBER 4选一，用来唯一标识PON口的ONU
        @cvlan(string/int): cvlan, 1-4095
        @**kwargs: 其他可选字段
        参考命令行：
        ADD-ONU::OLTID=olt-name,PONID=ponport_location:CTAG::[AUTHTYPE=auth-type],ONUID=onu-index[,PWD=onu password][,ONUNO=onu-no][,NAME=name][,DESC=onudescription],ONUTYPE=onu type[,BANDTYPE = BandWidthType];
        引用函数：
        使用示例:
        """
        cmdlines = []
        add_onu_cmds = 'ADD-ONU::OLTID={0},PONID=NA-NA-{1}-{2}:CTAG::AUTHTYPE={3},ONUID={4}'.format(
            oltid, slotno, ponno, onuidtype, onuid)
        kwargs['ONUTYPE'] = onutype
        for key in kwargs.keys():
            add_onu_cmds += ',{0}={1}'.format(key, kwargs[key])

        if bandtype is not None:
            add_onu_cmds += ',BANDTYPE=%s' % bandtype

        add_onu_cmds += ';\n'
        cmdlines.append(add_onu_cmds)
        return cmdlines

    @staticmethod
    def del_onu(oltid, slotno, ponno, onuidtype, onuid):
        """
        函数功能：TL1去授权ONU
        函数参数:
        @oltid(string):olt ip
        @slotno(string/int):槽位号
        @ponno(string/int):PON口号
        @onuidtype(string):ONU标识类型（ONU_NAME、MAC、LOID、ONU_NUMBER）
        @onuid(string):ONU标识，可以取值：ONU_NAME、MAC、LOID、ONU_NUMBER 4选一，用来唯一标识PON口的ONU
        参考命令行：
        DEL-ONU::OLTID=olt-name,PONID=ponport_location:CTAG::ONUIDTYPE=onuid-type,ONUID=onu-index;
        引用函数：
        使用示例:
        """
        cmdlines = []
        del_onu_cmds = 'DEL-ONU::OLTID={0},PONID=NA-NA-{1}-{2}:CTAG::ONUIDTYPE={3},ONUID={4};\n'.format(
            oltid, slotno, ponno, onuidtype, onuid)
        cmdlines.append(del_onu_cmds)
        return cmdlines

    @staticmethod
    def cfg_lanport_vlan(oltid, slotno, ponno, onuidtype, onuid, onuport, cvlan, **kwargs):
        """
        函数功能：TL1配置ONU端口VLAN
        函数参数:
        @oltid(string):olt ip
        @slotno(string/int):槽位号
        @ponno(string/int):PON口号
        @onuidtype(string):ONU标识类型（ONU_NAME、MAC、LOID、ONU_NUMBER）
        @onuid(string):ONU标识，可以取值：ONU_NAME、MAC、LOID、ONU_NUMBER 4选一，用来唯一标识PON口的ONU
        @onuport(string/int): ONU 端口号
        @cvlan(string/int): cvlan, 1-4095
        @**kwargs: 其他可选字段,SVLAN, TVLAN, SCOS, CCOS
        参考命令行：
        CFG-LANPORTVLAN::ONUIP=onu-name|OLTID=olt-name[,PONID=ponport_location,ONUIDTYPE=onuid-type,ONUID=onu-index],ONUPORT=onu-port:CTAG::[SVLAN=outer vlan],CVLAN=Inner vlan[,UV=user-vlan][,SCOS=outer qos][,CCOS=inner qos];
        引用函数：
        使用示例:
        """
        cmdlines = []
        lanportvlan_cmds = 'CFG-LANPORTVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4},ONUPORT=NA-NA-NA-{5}:CTAG::'.format(
            oltid, slotno, ponno, onuidtype, onuid, onuport)

        # SVLAN
        if 'SVLAN' in kwargs.keys():
            lanportvlan_cmds += "SVLAN={0},".format(kwargs['SVLAN'])

        # CVLAN, UV
        if 'TVLAN' in kwargs.keys():
            lanportvlan_cmds += "CVLAN={0},UV={1}".format(kwargs['TVLAN'], cvlan)
        else:
            lanportvlan_cmds += "CVLAN={0}".format(cvlan)

        if 'SCOS' in kwargs.keys():
            lanportvlan_cmds += ',SCOS={0}'.format(kwargs['SCOS'])
        if 'CCOS' in kwargs.keys():
            lanportvlan_cmds += ',CCOS={0}'.format(kwargs['CCOS'])
        lanportvlan_cmds += ';\n'

        cmdlines.append(lanportvlan_cmds)
        return cmdlines

    @staticmethod
    def del_lanport_vlan(oltid, slotno, ponno, onuidtype, onuid, onuport, cvlan=None):
        """
        函数功能：TL1删除ONU端口VLAN
        函数参数:
        @oltid(string):olt ip
        @slotno(string/int):槽位号
        @ponno(string/int):PON口号
        @onuidtype(string):ONU标识类型（ONU_NAME、MAC、LOID、ONU_NUMBER）
        @onuid(string):ONU标识，可以取值：ONU_NAME、MAC、LOID、ONU_NUMBER 4选一，用来唯一标识PON口的ONU
        @onuport(string/int): ONU 端口号
        参考命令行：
        DEL-LANPORTVLAN::OLTID=oltname,PONID=ponport_location,ONUIDTYPE=onuidtype,ONUID=onu-index,ONUPORT=onu-port:CTAG::[UV=user-vlan];
        引用函数：
        使用示例:
        """
        cmdlines = []
        lanportvlan_cmds = 'DEL-LANPORTVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4},ONUPORT=NA-NA-NA-{5}:CTAG::'.format(
            oltid, slotno, ponno, onuidtype, onuid, onuport)
        if cvlan is not None:
            lanportvlan_cmds += 'UV={0}'.format(cvlan)
        lanportvlan_cmds += ";\n"

        cmdlines.append(lanportvlan_cmds)
        return cmdlines

    @staticmethod
    def add_laniptvport(oltid, slotno, ponno, onuidtype, onuid, onuport, mvlan, **kwargs):
        """
        函数功能：TL1配置ONU端口组播VLAN
        函数参数:
        @oltid(string):olt ip
        @slotno(string/int):槽位号
        @ponno(string/int):PON口号
        @onuidtype(string):ONU标识类型（ONU_NAME、MAC、LOID、ONU_NUMBER）
        @onuid(string):ONU标识，可以取值：ONU_NAME、MAC、LOID、ONU_NUMBER 4选一，用来唯一标识PON口的ONU
        @onuport(string/int): ONU 端口号
        @**kwargs: 其他可选字段,SVLAN, UV, SCOS, CCOS
        参考命令行：
        ADD-LANIPTVPORT::ONUIP=onu-name|OLTID=olt-name,PONID=ponport_location,ONUIDTYPE=onuid-type,ONUID=onu-index,ONUPORT=onu-port:CTAG::[UV=user vlan][,MVLAN=mvlan] [,UCOS=ucos] [,MCOS=mcos][,SVCMODPROFILE=svc mod profile][,GEMPORT=0];

        引用函数：
        使用示例:
        """
        cmdlines = []
        add_iptv_cmds = "ADD-LANIPTVPORT::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4},ONUPORT=NA-NA-NA-{5}:CTAG::".format(
            oltid, slotno, ponno, onuidtype, onuid, onuport)

        if 'UV' in kwargs.keys():
            add_iptv_cmds += "UV={0},MVLAN={1}".format(kwargs['UV'], mvlan)
        else:
            add_iptv_cmds += "MVLAN={0}".format(mvlan)

        for key in kwargs.keys():
            if key == 'UV':
                continue
            add_iptv_cmds += ",{0}={1}".format(key, kwargs[key])

        add_iptv_cmds += ";\n"
        cmdlines.append(add_iptv_cmds)
        return cmdlines

    @staticmethod
    def del_laniptvport(oltid, slotno, ponno, onuidtype, onuid, onuport, **kwargs):
        """
        函数功能：TL1删除ONU端口组播VLAN
        函数参数:
        @oltid(string):olt ip
        @slotno(string/int):槽位号
        @ponno(string/int):PON口号
        @onuidtype(string):ONU标识类型（ONU_NAME、MAC、LOID、ONU_NUMBER）
        @onuid(string):ONU标识，可以取值：ONU_NAME、MAC、LOID、ONU_NUMBER 4选一，用来唯一标识PON口的ONU
        @cvlan(string/int): cvlan, 1-4095
        @**kwargs: 其他可选字段,SVLAN, UV, SCOS, CCOS
        参考命令行：
        DEL-LANIPTVPORT::ONUIP=onu-name|OLTID=olt-name[,PONID=ponport_location,ONUIDTYPE=onuid-type,ONUID=onu-index],ONUPORT=onu-port:CTAG::[UV=uservlan][,MVLAN=mvlan];

        引用函数：
        使用示例:
        """
        cmdlines = []
        del_iptv_cmds = "DEL-LANIPTVPORT::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4},ONUPORT=NA-NA-NA-{5}:CTAG::".format(
            oltid, slotno, ponno, onuidtype, onuid, onuport)
        for key in kwargs.keys():
            if key == 'UV':
                del_iptv_cmds += "{0}={1}".format(key, kwargs[key])
            else:
                del_iptv_cmds += ",{0}={1}".format(key, kwargs[key])
        del_iptv_cmds += ';\n'
        cmdlines.append(del_iptv_cmds)
        return cmdlines

    @staticmethod
    def add_ponvlan(oltid, slotno, ponno, onuidtype, onuid, cvlan, **kwargs):
        """
        函数功能：TL1配置ONUqinq域
        函数参数:
        @oltid(string):olt ip
        @slotno(string/int):槽位号
        @ponno(string/int):PON口号
        @onuidtype(string):ONU标识类型（ONU_NAME、MAC、LOID、ONU_NUMBER）
        @onuid(string):ONU标识，可以取值：ONU_NAME、MAC、LOID、ONU_NUMBER 4选一，用来唯一标识PON口的ONU
        @cvlan(string/int): cvlan, 1-4095
        @**kwargs: 其他可选字段
        参考命令行：
        ADD-PONVLAN::OLTID=olt-name,PONID=机架-框-槽-PON口号,ONUIDTYPE=onuidtype,ONUID=onu-index:CTAG::[SVLAN=outervlan,]CVLAN=Innervlan[,UV=uservlan][,SCOS=outerqos][,CCOS=innerqos][,UCOS=ucos][,SERVICETYPE=servicetype][,SVCMODPROFILE=servicemodelprofile][,GEMPORT=0]；
        引用函数：
        """
        cmdlines = []

        if 'SVLAN' in kwargs.keys():
            add_ponvlan_cmd = "ADD-PONVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4}:CTAG::SVLAN={5},CVLAN={6}".format(
                oltid, slotno, ponno, onuidtype, onuid, kwargs['SVLAN'], cvlan)
        else:
            add_ponvlan_cmd = "ADD-PONVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4}:CTAG::CVLAN={5}".format(
                oltid, slotno, ponno, onuidtype, onuid, cvlan)

        for key in kwargs.keys():
            if 'SVLAN' != key:
                add_ponvlan_cmd += ',{0}={1}'.format(key, kwargs[key])
        add_ponvlan_cmd += ';\n'

        cmdlines.append(add_ponvlan_cmd)
        return cmdlines

    @staticmethod
    def del_ponvlan(oltid, slotno, ponno, onuidtype, onuid, cvlan):
        """
        函数功能：TL1删除ONUqinq域
        函数参数:
        @oltid(string):olt ip
        @slotno(string/int):槽位号
        @ponno(string/int):PON口号
        @onuidtype(string):ONU标识类型（ONU_NAME、MAC、LOID、ONU_NUMBER）
        @onuid(string):ONU标识，可以取值：ONU_NAME、MAC、LOID、ONU_NUMBER 4选一，用来唯一标识PON口的ONU
        @cvlan(string/int): cvlan, 1-4095
        @**kwargs: 其他可选字段
        参考命令行：
        DEL-PONVLAN::OLTID=$::OLT(telnet_ip),PONID=NA-NA-$::SLOTNO-$::PONNO,ONUIDTYPE=LOID,ONUID=$::ONULOID:CTAG::UV=45;
        引用函数：
        """
        cmdlines = []

        del_ponvlan_cmd = "DEL-PONVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4}:CTAG::UV={5};\n".format(
            oltid,
            slotno,
            ponno,
            onuidtype,
            onuid,
            cvlan)

        cmdlines.append(del_ponvlan_cmd)
        return cmdlines

    @staticmethod
    def add_BWprofile(oltid, profilename, *args):
        """
        函数功能：TL1创建ONU带宽模板
        函数参数:
        @oltid(string):olt ip
        @profilename(string): 带宽模板名称
        @*args: 其他可选字段, (UPMGBW,UMABW,DMGBW,DMABW,UFBW) --> (上行最小保证带宽, 上行最大允许带宽, 下行最小保证带宽, 下行最大允许带宽, 上行固定带宽)

        参考命令行：
        ADD-BWPROFILE::ONUIP=onu-name|OLTID=olt-name:CTAG::PROFILENAME=profile name[,UPMGBW=UpMINGuaranteedBandwidth,UMABW=uplinkmaximumallowedbandwidth,DMGBW=DownMINGuaranteedBandwidth,DMABW=DownMAXAllowedBandwidth,UFBW=UpstreamFixedBandwidth];

        引用函数：
        """
        BW = ('UPMGBW', 'UMABW', 'DMGBW', 'DMABW', 'UFBW')
        cmdlines = []
        add_BWprofile_cmd = "ADD-BWPROFILE::OLTID={0}:CTAG::PROFILENAME={1}".format(oltid, profilename)
        for index in range(len(args)):
            add_BWprofile_cmd += ",{0}={1}".format(BW[index], args[index])
        add_BWprofile_cmd += ";\n"
        cmdlines.append(add_BWprofile_cmd)
        return cmdlines

    @staticmethod
    def del_BWprofile(oltid, profilename):
        """
        函数功能：TL1删除ONU带宽模板
        函数参数:
        @oltid(string):olt ip
        @profilename(string): 带宽模板名称

        参考命令行：
        DEL-BWPROFILE::ONUIP=onu-name|OLTID=olt-name:CTAG::PROFILENAME=profilename;

        引用函数：
        """
        cmdlines = []
        add_BWprofile_cmd = "DEL-BWPROFILE::OLTID={0}:CTAG::PROFILENAME={1};\n".format(oltid, profilename)
        cmdlines.append(add_BWprofile_cmd)
        return cmdlines

    @staticmethod
    def cfg_onuBW(oltid, slotno, ponno, onuidtype, onuid, up_bandwidth, dw_bandwidth):
        """
        函数功能：TL1 配置ONU上下行带宽
        函数参数:
        @oltid(string):olt ip
        @slotno(string/int):槽位号
        @ponno(string/int):PON口号
        @onuidtype(string):ONU标识类型（ONU_NAME、MAC、LOID、ONU_NUMBER）
        @onuid(string):ONU标识，可以取值：ONU_NAME、MAC、LOID、ONU_NUMBER 4选一，用来唯一标识PON口的ONU
        @up_bandwidth(string): 上行带宽模板
        @dw_bandwidth(string): 下行带宽模板

        参考命令行：
        CFG-ONUBW::OLTID=olt-name,PONID=NA-NA-slot-pon,ONUIDTYPE=onuid-type,ONUID=onu-index:CTAG::UPBW=onu-up-bandwidth,DOWNBW=onu-down-bandwidth;

        引用函数：
        """
        cmdlines = []
        cfg_onuBW_cmd = "CFG-ONUBW::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4}:CTAG::UPBW={5},DOWNBW={6};\n".format(
            oltid, slotno, ponno, onuidtype, onuid, up_bandwidth, dw_bandwidth)
        cmdlines.append(cfg_onuBW_cmd)
        return cmdlines


class OLT_V4():
    def __init__(self):
        self.cmdlines__ = ""

    @staticmethod
    def pon_auth_mode(slotno, ponno, authmode: PONAuthMode):
        """
        函数功能：
            配置PON口授权模式
        函数参数：
            @param slotno: int
            槽位号， AN5516范围1~8，11~18; AN6000-17范围：1~8，11~19
            @param ponno: int
            PON口号， 1~16
            @param authmode：enum class (PONAuthMode)
            PON口授权模式, 枚举值 或者 phy_id|phy_id+psw|password|loid+psw|phy_id/loid+psw|no_auth|loid|phy_id/loid|phy_id/psw|reg_id
        参考命令行:
            # set pon_auth slot <slotno> pon <ponno> mode [phy_id|phy_id+psw|password|loid+psw|phy_id/loid+psw|no_auth|loid|phy_id/loid|phy_id/psw|reg_id]
            Admin\card
        使用说明:
            pon_auth_mode(1, 1, PONAuthMode.PHYID)
        """
        ponauthmode = ('no_auth', 'phy_id', 'loid', 'password', 'phy_id+psw', 'loid+psw',
                       'phy_id/loid', 'phy_id/psw', 'phy_id/loid+psw', 'reg_id')
        cmdlines = []
        cmdlines.append('cd card\n')
        cmdlines.append('set pon_auth slot {slotno} pon {ponno} mode {authmode}\n'.format(
            slotno=slotno, ponno=ponno, authmode=ponauthmode[authmode.value]))
        cmdlines.append('cd ..\n')

        return cmdlines

    @staticmethod
    def authorize_onu(authtype: ONUAuthType, slotno, ponno, onuid, onutype, **onu_sn):
        """
        函数功能：
            授权ONU;
            授权ONU方式: phy-id, password, loid, loidpsw

        函数参数:
            @param auth_type: Enum class
                OnuAuthType
            @param slotno:int
                槽位号, 范围1~19，根据不同的系统槽位号范围不相同
            @param ponno:int
                PON口号, 范围1~16
            @param onuid:int
                ONU ID， 范围1~128
            @param onutype: string
                ONU 类型， 例如OTHER2， HG260， 5506-04F1等
            @**onu_sn: dict
                onu 的SN信息， 根据授权方式不一样，分别需要配置phyid， password， loid， logicpsw

        参考命令行：
            Admin/onu# set whitelist <phy-id/logic-id/password> address <sn> password null  action add slot 7 pon 7 onu 1 type 5006-07A
            set whitelist {[phy_addr] address <address> password [<pwd_str>|null]}*1 {[password] password <pwd_str>}*1 {[logic_sn] sn <sn_str> password [<pswd_str>|null]}*1 action [add|delete|lock|unlock] {slot <slotno> pon <ponno> onu <onuno> type <onutype>}*1

        函数说明:
            authorize_onu(ONUAuthType.PHYID, 1, 1, 1, 'HG260', phyid='FHTT01010001', loid='li1212', password='oso1')
        """
        try:
            cmdlines = []
            cmdlines.append('cd onu\n')
            if ONUAuthType.PHYID == authtype:  # phy id
                if 'password' not in onu_sn.keys():
                    onu_sn['password'] = 'null'
                cmdlines.append("set whitelist phy_addr address {phyid} password {password} action add slot {slotno} pon {ponno} onu {onuid} type {onutype}\n".format(
                    phyid=onu_sn['phyid'], password=onu_sn['password'], slotno=slotno, ponno=ponno, onuid=onuid, onutype=onutype))

            if ONUAuthType.PASSWORD == authtype:  # password
                cmdlines.append("set whitelist  password password {password} action add slot {slotno} pon {ponno} onu {onuid} type {onutype}\n".format(
                    password=onu_sn['password'], slotno=slotno, ponno=ponno, onuid=onuid, onutype=onutype))

            if (ONUAuthType.LOID == authtype) or (ONUAuthType.LOIDPSW == authtype):  # loid without passowrd / loid with passowrd
                if 'logicpsw' not in onu_sn.keys():
                    onu_sn['logicpsw'] = 'null'
                cmdlines.append("set whitelist logic_sn sn {loid} password {logicpsw} action add slot {slotno} pon {ponno} onu {onuid} type {onutype}\n".format(
                    loid=onu_sn['loid'], logicpsw=onu_sn['logicpsw'], slotno=slotno, ponno=ponno, onuid=onuid, onutype=onutype))
        except KeyError as err:
            print("Authorize ONU Failed!!!")
            print("KeyError: ", err)
            print(
                "Key of onu_sn need one of 'phyid', 'password', 'loid', 'logicpsw'.\n But keys of onu_sn:{0}".format(
                    onu_sn.keys()))

        return cmdlines

    @staticmethod
    def unauth_onu(slotno, ponno, onuid, onutype, authmode, **onu_sn):
        """
        函数功能:
            去授权ONU
        函数参数:
            @param
        返回值: None
        使用说明:
        """
        # TODO

    @staticmethod
    def reboot_onu(slotno, ponno, onuid):
        """复位ONU"""
        try:
            cmdlines = ['cd maintenance\n']
            cmdlines.append('reboot slot {s} pon {p} onu {o}\n'.format(s=slotno, p=ponno, o=onuid))
            return cmdlines
        except Exception as err:
            print("复位ONU命令失败")
            print(err)


class OLT_V5():
    def __init__(self, tn=None, version="V5"):
        self.__version = version
        # self.tn__ = tn

    @staticmethod
    def query_debugip():
        """
        函数功能：回读debug ip

        函数参数:

        参考命令行：

        引用函数：
        """
        cmdlines = []
        cmdlines.append(['config\n', 'interface meth 1/1\n', "show ip address\n"])
        return cmdlines

    @staticmethod
    def load_program(
            filename, program_type='system', protocol='ftp', serverinfo=('10.182.5.213', '1', '1'),
            backup=False):
        '''
        函数功能：升级系统版本

        函数参数：
            @filename: 升级文件文件
            @program_type: 升级程序类型，system,config,script,ver-file,boot,patch,cpld,fpga
            @protocol:传输协议,ftp,tftp,sftp
            @serverinfo: 服务器信息，格式(ip, username, password)
            @backup: False 不升级备盘， True 升级备盘

        函数返回值：

        参考命令行：
        # load program [system|config|script|ver-file|boot|patch|cpld|fpga] <filename> [tftp|ftp|sftp] <ipaddr> {<username> <password>}*1
        Admin(config)
        # load program backup [system|patch|cpld|boot|fpga] <filename> [tftp|ftp|sftp]<ipaddr> {<username> <password>}*1
        Admin(config)
        '''
        cmdlines = ['config\n']
        if backup:
            cmdlines.append("load  program backup {0} {1} {2} {3} {4} {5}\n".format(
                program_type, filename, protocol, *serverinfo))
        else:
            cmdlines.append("load program {0} {1} {2} {3} {4} {5}\n".format(
                program_type, filename, protocol, *serverinfo))
        return cmdlines

    @staticmethod
    def show_debugversion(backup=False):
        """
        函数功能： 查看主控编译时间
        函数参数：
            @backup(boolean): False--主盘（默认值）； True--备盘
        函数返回值：
            查看版本的命令行
        参考命令行：
            Admin(diagnose)# show debugversion
        """
        if backup:
            cmdlines = ['config\n', 'telnet slot backup\n', 'diagnose\n', 'show debugversion\n']
        else:
            cmdlines = ['diagnose\n', 'show debugversion\n']
        return cmdlines

    @staticmethod
    def show_card():
        """
        函数功能：查看OLT单盘状态
        函数参数：
        函数返回值：
        参考命令行：
        Admin(config)# show card
        """
        cmdlines = ['config\n', 'show card\n']
        return cmdlines

    @staticmethod
    def pon_auth_mode(slotno, ponno, authmode: PONAuthMode):
        """
        函数功能:
            配置PON口授权模式
        函数参数:
            @param slotno(int/string): 槽位号
            @param ponno(int/string): PON口号
            @param authmode(PONAuthMode): PON口授权模式
        返回值: 命令行列表
        使用说明:
            Admin(config-if-pon-1/1)#  port authentication-mode [phyid|phy-id+psw|password|log-id|log-id+psw|no-auth|phy-id/psw|phy-id/log-id/psw|phy-id/log-id+psw/psw]
        """
        ponauthmode = ('no-auth', 'phyid', 'log-id', 'password', 'phy-id+psw', 'log-id+psw',
                       'phy-id/log-id/psw', 'phy-id/psw', 'phy-id/log-id+psw/psw')
        cmdlines = []
        cmdlines.append('interface pon 1/{s}/{p}\n'.format(s=slotno, p=ponno))
        cmdlines.append('port authentication-mode {mode}\n'.format(mode=ponauthmode[authmode.value]))
        cmdlines.append('quit\n')
        return cmdlines

    @staticmethod
    def authorize_onu(auth_type: ONUAuthType, onu_sn, onutype, *onu):
        """
        函数功能：授权ONU
        函数参数:
        @auth_type(string):phy-id,logic-id,password
        @onu_sn(string):onu physics address or logic sn
        @onutye: Type of onu, eg. 5006-10, OTHER2
        @*onu: (slotno, ponno, onuno)
        参考命令行：
        whitelist add <phy-id/logic-id/password> <sn> [type <onutype>] slot [slotno] pon <ponno> onuid <onuno>

        引用函数：
        """
        auth_mode = ('phy-id', 'password', 'logic-id')
        cmdlines = []
        try:
            cmdlines.append(
                "whitelist add {0} {1} type {2} slot {3} pon {4} onuid {5}\n".format(
                    auth_mode[auth_type.value], onu_sn, onutype, *onu))
        except SyntaxError as err:
            print(err)
        except IndexError as indexerr:
            print(indexerr)

        return cmdlines

    @staticmethod
    def unauth_onu(auth_type: ONUAuthType, slotno, ponno, onu_sn, **kwargs):
        """
        函数功能：去授权ONU

        函数参数:
        @auth_type(enum):ONUAuthType
        @slotno(str/int):槽位号
        @ponno(str/int):PON 口号
        @onu_sn(str):onu physics address or logic sn
        @**kwargs: checkcode

        参考命令行：
        no whitelist [phy-id|logic-id|password] <slotno> <ponno> <sn> {<checkcode>}*1

        引用函数：
        """

        auth_mode = ('phy-id', 'password', 'logic-id')

        checkcode = kwargs['checkcode'] if 'checkcode' in kwargs.values() else ""

        cmdlines = []
        cmdlines.append("no whitelist {0} {1} {2} {3} {4}\n".format(
            auth_mode[auth_type.value], slotno, ponno, onu_sn, checkcode))
        return cmdlines

    @staticmethod
    def add_uplink_vlan(uplinkslot, uplinkport, vlan_mode: VLAN_MODE, vlan_begin, vlan_end):
        """
        函数功能：
            配置上联端口VLAN

        函数参数:
            @uplinkslot: 上联口槽位号或者主控槽位号
            @uplinkport: 上联口端口
            @vlan_mode(enum): vlan模式，VLAN_MODE
            @vlan_begin: 起始VLAN (0~4095)
            @vlan_end: 终止VLAN (0~4095)
        参考命令行：
            Admin(config)# port vlan 101 to 101 tag 1/9 1
        引用函数：
        """
        cmdlines = []
        # cmdlines.append("config\n")
        cmdlines.append("port vlan {0} to {1} {2} 1/{3} {4} \n".format(
            vlan_begin, vlan_end, VLAN_MODE.mode.value[vlan_mode.value], uplinkslot, uplinkport))

        return cmdlines

    @staticmethod
    def show_port_vlan(slot, port):
        """
        函数功能:
            获取上联口VLAN
        函数参数:
            @param
        返回值: None
        使用说明:
        Admin(config)# show port vlan <frameid/slotid/portid>
        """
        return ['show port vlan 1/{slotid}/{portid}\n'.format(slotid=slot, portid=port)]

    @staticmethod
    def del_uplink_vlan(uplinkslot: int, uplinkport, vlan_mode: VLAN_MODE, vlan_begin, vlan_end):
        """
        函数功能:
            删除上联口VLAN
        函数参数:
            @param
        返回值: None
        使用说明:
        """
        # Todo

    @staticmethod
    def onu_lan_service(onu_port, ser_count, *lan_service):
        """
        函数功能:
            配置ONU端口业务

        函数参数:
            @onu_port: (slotno, ponno, onuno, port)
            @ser_count : ONU端口业务数量，0表示删除端口业务
            @lan_service: ({'cvlan':(cvlan_mode, ccos, cvlan), 'translate':(tflag, tcos, tvid), 'qinq':(sflag, scos, svlan, qinqprf, svlan_service)},)

        参考命令行:
            Admin(config-pon)#
            onu port vlan 1 eth 1 service count 3
            onu port vlan 1 eth 1 service 1 transparent priority 1 tpid 33024 vid 41
            onu port vlan 1 eth 1 service 1 translate enable priority 1 tpid 33024 vid 301
            onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2

            onu port vlan 1 eth 1 service 2 tag priority 3 tpid 33024 vid 45
            onu port vlan 1 eth 1 service 2 qinq enable priority 3 tpid 33024 vid 2701 iptv SVLAN2

            onu port vlan 1 eth 1 service 3 tag priority 7 tpid 33024 vid 46
            onu port vlan 1 eth 1 service 3 qinq enable priority 7 tpid 33024 vid 2701 voip SVLAN2

        引用函数:

        """
        cmdlines = []
        if len(lan_service) < ser_count:
            print("Error: service count(%d) > lan_service(%d)" % ser_count, len(lan_service))
            return cmdlines

        onuno, port = onu_port[2:]
        # cmdlines.append('config\n')
        # cmdlines.append('interface pon 1/%d/%d\n' % (slotno, ponno))
        cmdlines.append('onu port vlan {0} eth {1} service count {2}\n'.format(onuno, port, ser_count))
        for index in range(ser_count):
            # cvlan service
            cmdlines.append('onu port vlan {0} eth {1} service {2} {3} priority {4} tpid 33024 vid {5}\n'.format(
                onuno, port, index + 1, *lan_service[index]['cvlan']))

            # translate
            if 'translate' in lan_service[index]:
                cmdlines.append(
                    'onu port vlan {0} eth {1} service {2} translate {3} priority {4} tpid 33024 vid {5}\n'.format(
                        onuno, port, index + 1, *lan_service[index]['translate']))

            # qinq
            if 'qinq' in lan_service[index]:
                cmdlines.append(
                    'onu port vlan {0} eth {1} service {2} qinq {3} priority {4} tpid 33024 vid {5} {6} {7}\n'.format(
                        onuno, port, index + 1, *lan_service[index]['qinq']))

        return cmdlines

    @staticmethod
    def create_oltqinq_domain(qinq_name, *vlanrule):
        """
        函数功能：
            创建OLT qinq域。

        函数参数：
            @qinq_name: olt qinq域名称
            @*vlanrule: ({'uprule':((filedid, value, condition),), 'dwrule': ((filedid, value, condition),),
            'vlanrule': (l1oldvlan, l1oldvlan_cos, l1_action, l1_tpid, l1_newvlan, l1_newvlancos, l2oldvlan, l2oldvlan_cos, l2_action, l2_tpid, l2_newvlan, l2_newvlancos)},)

            @uprule 与dwrule 分别是上下行匹配规则；默认值为((2, '000000000000', 5),)
            vlanrule 是为 VLAN转换规则，格式为（l1oldvlan, l1oldvlan_cos, l1_action, l1_tpid, l1_newvlan, l1_newvlancos, l2oldvlan, l2oldvlan_cos, l2_action, l2_tpid, l2_newvlan, l2_newvlancos）

            @示例：({'upRule':((2, '000000000000', 5),), 'dwRule': ((2, '000000000000', 5),), 'vlanrule': (100, 'null', 'translation', 33024, 201, 1, 'null', 'null', 'add', 33024, 2701, 1)},)

            @上下行匹配规则字段说明：
            fieldId:规则ID，范围(1~27), 1(Dst Mac) 2(Src Mac) 3(Ethernet Type) 4(Vlan4) 5(Vlan3) 6(Vlan2) 7(Vlan1) 8(TOS) 10(TTL)
            11(Protocol Type) 12(Src IPv4) 13(Src IPv6) 14(Dst IPv4) 15(Dst IPv6) 16(L4 Src Port) 17(L4 Dst Port) 18(Cos4) 19(Cos3)
            20(Cos2) 21(Cos1) 22(Dst IPv6 Prefix) 23(Src IPv6 Prefix)  24(IP Version) 25(IPv6 Traffic Class) 26(IPv6 Flow Label) 27(IPv6 Next Header).

            @value: 规则ID所对应值
            condition:匹配规则，范围(0~7),0(Never) 1(==) 2(!=) 3(<=) 4(>=) 5(Exist) 6(No exist) 7(Always)

        参考命令行：
        # oltqinq 上行匹配规则
        # oltqinq-domain <name> service <1-8> classification upstream {field-id <1-27> value <value> condition <condition>}*4 {serv-id <1-8>}*1
        Admin(config)

        # oltqinq 下行匹配规则
        # oltqinq-domain <name> service <1-8> classification downstream {field-id <1-27> value <value> condition <condition>}*4
        Admin(config)

        # 配置VLAN转换规则
        # oltqinq-domain <name> service <1-8> {vlan <1-4> user-vlanid [<0-4095>|null] user-cos [<0-7>|null] [add|translation|transparent]
        Admin(config)
        tpid <tpid> cos [<cos>|user-cos|null] vlanid [<vlanid>|null]}*4

        示例：
        config_oltqinq_vlanservice('qinq_test', {'uprule': ((7, 100, 4), (7, 200, 3)), 'dwrule':(
            (2,'000000000000', 5),), 'vlanrule': (100, 'null', 'translation', 33024, 201, 1, 'null', 'null', 'add', 33024, 2701, 1)})
        """
        cmdlines = []
        # 添加oltqinq域
        cmdlines.append('oltqinq-domain add %s\n' % qinq_name)
        # 配置OLTqinq域 VLAN业务数
        ser_count = len(vlanrule)
        cmdlines.append('oltqinq-domain modify %s service-count %d\n' % (qinq_name, ser_count))

        vlan_service_id = 1
        for qinqrule in vlanrule:
            # 配置上行匹配规则
            up_classfication = ((2, '000000000000', 5),) if 'uprule' not in qinqrule.keys() else qinqrule['uprule']
            uprule_cmds = 'oltqinq-domain {0} service {1} classification upstream '.format(qinq_name, vlan_service_id)
            for uprule in up_classfication:
                uprule_cmds += 'field-id {0} value {1} condition {2} '.format(*uprule)
            uprule_cmds += '\n'
            cmdlines.append(uprule_cmds)

            # 配置下行匹配规则
            dw_classfication = ((2, '000000000000', 5),) if 'dwrule' not in qinqrule.keys() else qinqrule['dwrule']
            dwrule_cmds = 'oltqinq-domain {0} service {1} classification downstream '.format(qinq_name, vlan_service_id)
            for dwrule in dw_classfication:
                dwrule_cmds += 'field-id {0} value {1} condition {2} '.format(*dwrule)
            dwrule_cmds += '\n'
            cmdlines.append(dwrule_cmds)

            # 配置VLAN转换规则
            vlan_service_cmds = 'oltqinq-domain {0} service {1} vlan 1 user-vlanid {2} user-cos {3} {4} tpid {5} cos {7} vlanid {6} vlan 2 user-vlanid {8} user-cos {9} {10} tpid {11} cos {13} vlanid {12}\n'.format(
                qinq_name, vlan_service_id, *qinqrule['vlanrule'])
            cmdlines.append(vlan_service_cmds)
            vlan_service_id += 1

        return cmdlines

    @staticmethod
    def del_oltqinq(qinq_name):
        """
        函数功能：
            删除olt qinq 域模板

        函数参数：
            @qinq_name: OLT qinq 模板
            @ser_count: OLT qinq 模板需要创建的业务个数

        参考命令行：
            Admin(config)# oltqinq-domain delete <name>
        """
        cmdlines = []
        cmdlines.append('oltqinq-domain delete %s\n' % qinq_name)
        return cmdlines

    @staticmethod
    def get_oltqinq_name(qinq_name):
        """
        函数功能：
        函数参数：
        参考命令行：
        Admin(config)# show oltqinq-domain <name>
        """
        cmdlines = []
        cmdlines.append('show oltqinq-domain %s\n' % qinq_name)
        return cmdlines

    @staticmethod
    def attach_oltqinq(qinq_name, *portno):
        """
        函数功能：
        绑定oltqinq域
        函数参数：

        参考命令行：
        Admin(config-if-pon-)# oltqinq-domain <name>
        Admin(config-if-pon-)# onu oltqinq-domain <onuid> <name>
        """
        cmdlines = []
        if len(portno) == 2:  # 线卡PON 口绑定OLTqinq域
            cmdlines.append('interface pon 1/{0}/{1}\n'.format(*portno))
            cmdlines.append('oltqinq-domain {0}\n'.format(qinq_name))

        if len(portno) == 3:  # ONU PON口绑定OLTqinq域
            cmdlines.append('interface pon 1/{0}/{1}\n'.format(*portno[:2]))
            cmdlines.append('onu oltqinq-domain {0} {1}\n'.format(portno[2], qinq_name))

        cmdlines.append('quit\n')
        return cmdlines

    @staticmethod
    def deattach_oltqinq(qinq_name, *portno):
        """
        函数功能：
        去绑定oltqinq域
        函数参数：

        参考命令行：
        Admin(config-if-pon-)# oltqinq-domain <name>
        Admin(config-if-pon-)# onu oltqinq-domain <onuid> <name>
        """
        cmdlines = []
        if len(portno) == 2:  # 线卡PON口去绑定OLTqinq域
            cmdlines.append('interface pon 1/{0}/{1}\n'.format(*portno))
            cmdlines.append('no oltqinq-domain {0}\n'.format(qinq_name))

        if len(portno) == 3:  # ONU PON口去绑定OLTqinq域
            cmdlines.append('interface pon 1/{0}/{1}\n'.format(*portno[:2]))
            cmdlines.append('no onu oltqinq-domain {0} {1}\n'.format(portno[2], qinq_name))

        cmdlines.append('quit\n')
        return cmdlines

    @staticmethod
    def onu_ngn_voice_service(onu, pots, phonenum, **kwargs):
        """
        函数功能: 配置ONU端口语音业务
        函数参数:
        @onu: (slotno, ponno, onuno)
        参考命令行:
        Admin(config-if-pon-)# onu ngn-voice-service <onuno> pots <portno> phonenum <num>
        引用函数:
        """
        # slotno, ponno, onuno = onu
        cmdlines = []
        # cmdlines.append('interface pon 1/{0}/{1}\n'.format(onu[0], onu[1]))

        onu_ngn_voice_cmd = 'onu ngn-voice-service {0} pots {1} phonenum {2}'.format(onu[2], pots, phonenum)
        for key in kwargs.keys():
            onu_ngn_voice_cmd.join(' {0} {1}'.format(key, kwargs[key]))
        onu_ngn_voice_cmd += '\n'

        cmdlines.append(onu_ngn_voice_cmd)
        print("ngn:", cmdlines)
        return cmdlines

    @staticmethod
    def del_ngn_voice_service(*onu_pots):
        """
        函数功能: 删除ONU端口语音业务
        函数参数:
        @onu_pots: (slotno, ponno, onuno, pots)
        参考命令行:
        Admin(config-if-pon-)# no onu ngn-voice-service <onuno> pots <portno>
        引用函数:
        """
        slotno, ponno, onuno, pots = onu_pots
        cmdlines = []
        cmdlines.append('interface pon 1/{0}/{1}\n'.format(slotno, ponno))
        cmdlines.append('no onu ngn-voice-service {0} pots {1}\n'.format(onuno, pots))
        return cmdlines

    @staticmethod
    def get_onu_version(*onu):
        """
        函数功能: 通过线卡Telnet到MDU，并获取MDU的编译时间
        函数参数:
        @onu: (slotno, ponno, onuno)
        参考命令行:
        引用函数:
        """
        slotno, ponno, onuno = onu

        cmdlines = []
        cmdlines.append("config\n")
        cmdlines.append('t l 512\n')
        cmdlines.append('telnet slot 1/%s' % slotno)
        cmdlines.append('cd service\n')
        cmdlines.append('telnetdata pon %d onu %d \n' % (ponno, onuno))
        cmdlines.append('')
        # TODO

    @staticmethod
    def get_MDU_ngn_ip(slot, pon, onu, ip):
        cmdlines = []
        cmdlines.append('telnet slot 1/%d \n' % slot)
        # TODO

    @staticmethod
    def add_ngn_uplink():
        '''
        ngn-uplink-user service <name> {[vid] <vid>}*1 {[potsqinqstate] [enable|disable] svlanid <0-4085>}*1 {[service-cos] <value>}*1 {[customer-cos] <value>}*1 {[ip-mode] [static|pppoe|dhcp|pppoev6|dhcpv6]}*1 {[public-ip] [ipv4|ipv6] <ipaddress/prefix>}*1 {[public-gate] [ipv4|ipv6] <ipaddress>}*1 {[pppoeuser] <name> }*1 {[password] <pwd>}*1 {[dhcp-option60] [enable|disable]}*1 {[dhcp-value] <value>}*1 {[domainname] <name>}*1 {[protocol-port] <0-65535>}*1 {[user-index] <value>}*1

        ngn-uplink-user serv H248 vid 251 serv 0 cus 0 ip-m static public-ip ipv4 10.52.152.207/26 public-gate ipv4 10.52.152.193 pro 2944 user-in 1007
        ngn-uplink-user-port phone 2015220701 usern aaln/0 user-in 1007
        ngn-uplink-user-port phone 2015220702 usern aaln/1 user-in 1007
        ngn-uplink-user-port phone 2015220703 usern aaln/2 user-in 1007
        ngn-uplink-user-port phone 2015220704 usern aaln/3 user-in 1007
        ngn-uplink-user-port phone 2015220705 usern aaln/4 user-in 1007
        ngn-uplink-user-port phone 2015220706 usern aaln/5 user-in 1007
        ngn-uplink-user-port phone 2015220707 usern aaln/6 user-in 1007
        ngn-uplink-user-port phone 2015220708 usern aaln/7 user-in 1007
        '''
        pass


class OLT_V4_RUSSIA(OLT_V4):
    """俄罗斯命令"""

    def __init__(self):
        pass

    @staticmethod
    def unauth_onu(onuinfo: tuple):
        """
        函数功能:
            去授权ONU，俄罗斯MGTS 命令
        函数参数:
            @para onuinfo(tuple)：
        返回值: None
        使用说明:
        OLT_FH_1\onu# no whitelist slot 18 pon 16 onu 1
        """
        cmdlines = ['cd /onu\n']
        cmdlines.append("no whitelist slot {0} pon {1} onu {2}\n".format(*onuinfo))
        return cmdlines

    @staticmethod
    def cfg_onu_lan_service(onu_port_info: tuple, cvlan: int, cos: int, service_type: SericeType, mode: VLAN_MODE):
        """
        函数功能:
            配置端口业务

        函数参数：
            @para onu_port_info(tuple): (槽位，PON口，ONU，端口) -- (slotno, ponno, onuno, portno)
            @para cvlan(int): 业务VLAN
            @para cos(int): 优先级
            @para service_type(enum): 业务类型
            @para mode(enum): VLAN模式
        返回值：list
            配置命令行
        参考命令行：
             onu-lan slot <slotno> pon <ponno> onu <onuno> port <portno> vlan <vlanlist> priority <priority_value> type [unicast|multicast] mode [tag|transparent] {[translate] svlan <vlan_id>} *
        使用示例：
        """

        cmdlines = ['cd /onu/lan\n']
        cmdlines.append('onu-lan slot {0} pon {1} onu {2} port {3} vlan {4} priority {5} type {6} mode {7}\n'.format(
            *onu_port_info, cvlan, cos, SericeType.type.value[service_type.value], VLAN_MODE.mode.value[mode.value]))
        cmdlines.append('apply onu {0} {1} {2} vlan\n'.format(*onu_port_info[:3]))
        cmdlines.append('cd / \n')
        return cmdlines

    @staticmethod
    def del_onu_lan_service(onu_port_info, vlan):
        """
        函数功能:
            删除端口业务

        函数参数：
            @para onu_port_info(tuple): (槽位，PON口，ONU，端口) -- (slotno, ponno, onuno, portno)
            @para vlan(string): vlanlist | all
        返回值：

        参考命令行：
            no onu-lan slot <slotno> pon <ponno> onu <onuno> port <portno> vlan [<vlanlist>|all]
        使用示例：
        """
        cmdlines = ['cd /onu/lan\n']
        cmdlines.append('no onu-lan slot {0} pon {1} onu {2} port {3} vlan {4}\n'.format(*onu_port_info, vlan))
        cmdlines.append('apply onu {0} {1} {2} vlan\n'.format(*onu_port_info[:3]))
        cmdlines.append('cd /\n')

        return cmdlines

    @staticmethod
    def cfg_internet_wan(slotno: int, ponno: int, onuuid: int, vlan: int):
        """
        函数功能:
            配置ONU Internet WAN业务

        函数参数:
            @param slotno(int): 槽位号
            @param ponno(int): PON口号
            @param onuno(int): ONU号
            @parma vlan(int): VLAN
        返回值: 
            命令行列表

        使用说明:
        OLT_FH_1\onu\lan#
        set veip_mgr_par slot 11 pon 16 onu 128 veip_port 1 port_type veip mgr_channel enable model tr069 item 1
        set veip_mgr_vlan slot 11 pon 16 onu 128 veip_port 1 mgr_id 1 protocol udp priority 0 tag_type tag svlan_label 0x8100 svlanid null svlan_cos null cvlan_label 0x8100 cvlanid 900 cvlan_cos 7
        apply veip_mgr_vlan slot 11 pon 16 onu 128
        """
        cmdlines = ['cd /onu/lan\n']
        cmdlines.append('set veip_mgr_par slot {0} pon {1} onu {2} veip_port 1 port_type veip mgr_channel enable model tr069 item 1\n'.format(
            slotno, ponno, onuid))
        cmdlines.append(
            'set veip_mgr_vlan slot {0} pon {1} onu {2} veip_port 1 mgr_id 1 protocol udp priority 0 tag_type tag svlan_label 0x8100 svlanid null svlan_cos null cvlan_label 0x8100 cvlanid {3} cvlan_cos 7\n'.
            format(slotno, ponno, onuno, onuid))
        cmdlines.append('apply veip_mgr_vlan slot {0} pon {1} onu {2}\n'.format(slotno, ponno, onuuid))
        return cmdlines

    @staticmethod
    def cfg_voice(slotno, ponno, onuno, voice_vlan, servicename, phone_prefix="", potsnum=2):
        """
        函数功能:
            配置ONU语音业务
        函数参数:
            @param slotno(int): 槽位号
            @param ponno(int): PON口号
            @param onuno(int): ONU号
            @parma voice_vlan(int): VLAN 
            @parma servicename(string): 业务名称
            @parma phone_prefixe(string):电话号码前缀
            @parma potsnum(int): pots端口数量，默认为2.
        返回值: 
            命令行列表
        使用说明:
            Admin\onu\ngn#
            set ngn_uplink_user_new slot 11 pon 16 onu 128 servicename voip vid 7 ip_mode dhcp domainname @russia.voip protocol_port 5060
            set ngn_voice_service_new slot 11 pon 16 onu 128 pots 1 username 8888800001 sip_user_name 8888800001 sip_user_password 8888800001
            set ngn_voice_service_new slot 11 pon 16 onu 128 pots 2 username 8888800002 sip_user_name 8888800002 sip_user_password 8888800002
        """
        # phone number prefix
        prefix = "{phone_prefix}{slot:02}{pon:02}{onu:03}".format(
            phone_prefix=phone_prefix, slot=slotno, pon=ponno, onu=onuno)
        cmdlines = ['cd /onu/ngn\n']
        cmdlines.append(
            'set ngn_uplink_user_new slot {0} pon {1} onu {2} servicename {4} vid {3} ip_mode dhcp domainname @russia.voip protocol_port 5060\n'.
            format(slotno, ponno, onuno, voice_vlan, servicename))

        for pots in range(potsnum):
            cmdlines.append(
                'set ngn_voice_service_new slot {0} pon {1} onu {2} pots {4} username {3}{4:02} sip_user_name {3}{4:02} sip_user_password {3}{4:02}\n'.
                format(slotno, ponno, onuno, prefix, pots+1))

        return cmdlines

    @staticmethod
    def set_lacp_sys_pri():
        """
        函数功能：
            配置lacp系统优先级 <0-65534>
        函数参数：
            @param protocol： 布尔类型
                True --- 从协议栈获取状态
                False --- 从数据库中获取状态
        返回值：
            命令行列表

        参考命令行:
            协议栈：Admin\protocol\lacp# show lacp channel-group trunks看协议栈
            数据库：Admin# show running-config module rcal_lacp
                   Admin(DEBUG_H)> show lacp running-config
        """
        pass

    @staticmethod
    def set_lacp_port_pri(parameter_list):
        """
        函数功能：
            配置端口优先级 <0-65534>
        函数参数：
            @param protocol： 布尔类型
                True --- 从协议栈获取状态
                False --- 从数据库中获取状态
        返回值：
            命令行列表

        参考命令行:
            协议栈：Admin\protocol\lacp# show lacp channel-group trunks看协议栈
            数据库：Admin# show running-config module rcal_lacp
                   Admin(DEBUG_H)> show lacp running-config
        """
        # TODO
        pass

    @staticmethod
    def set_lacp_port_key():
        """
        函数功能：
            配置端口key值 <1-32768>
        函数参数：
            @param protocol： 布尔类型
                True --- 从协议栈获取状态
                False --- 从数据库中获取状态
        返回值：
            命令行列表

        参考命令行:
            协议栈：Admin\protocol\lacp# show lacp channel-group trunks看协议栈
            数据库：Admin# show running-config module rcal_lacp
                   Admin(DEBUG_H)> show lacp running-config
        """
        # TODO
        pass

    @staticmethod
    def set_lacp_timer():
        pass

    @staticmethod
    def get_lacp_status(protocol=True):
        """
        函数功能：
            获取lacp状态
        函数参数：
            @param protocol： 布尔类型
                True --- 从协议栈获取状态
                False --- 从数据库中获取状态
        返回值：
            命令行列表

        参考命令行:
            协议栈：Admin\protocol\lacp# show lacp channel-group trunks看协议栈
            数据库：Admin# show running-config module rcal_lacp
                   Admin(DEBUG_H)> show lacp running-config
        """
        # TODO
        pass
