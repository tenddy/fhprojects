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
        del_onu_cmds = 'DEL-ONU::OLTID={0},PONID=NA-NA-{1}-{2}:CTAG::ONUIDTYPE={3},ONUID={4};\n'.format(oltid, slotno, ponno, onuidtype, onuid)
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
        @**kwargs: 其他可选字段,SVLAN, UV, SCOS, CCOS
        参考命令行：
        CFG-LANPORTVLAN::ONUIP=onu-name|OLTID=olt-name[,PONID=ponport_location,ONUIDTYPE=onuid-type,ONUID=onu-index],ONUPORT=onu-port:CTAG::[SVLAN=outer vlan],CVLAN=Inner vlan[,UV=user-vlan][,SCOS=outer qos][,CCOS=inner qos];
        引用函数：
        使用示例:
        """
        cmdlines = []
        lanportvlan_cmds = 'CFG-LANPORTVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4},ONUPORT={5}:CTAG::'.format(oltid, slotno, ponno, onuidtype, onuid, onuport)
        if 'SVLAN' in kwargs.keys():
            lanportvlan_cmds += "SVLAN={0},CVLAN={1}".format(kwargs['SVLAN'], cvlan)
        else:
            lanportvlan_cmds += "CVLAN={0}".format(cvlan)
        
        if 'UV' in kwargs.keys():
            lanportvlan_cmds += ',UV={0}'.format(kwargs['UV'])
        if 'SCOS' in kwargs.keys():
            lanportvlan_cmds += ',SCOS={0}'.format(kwargs['SCOS'])
        if 'CCOS' in kwargs.keys():
            lanportvlan_cmds += ',SCOS={0}'.format(kwargs['CCOS'])
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
        DEL-LANPORTVLAN::OLTID=oltname,PONID=ponport_location,ONUIDTYPE=onuidtype,ONUID=onu-index,ONUPORT=onu-port:CTAG::[,UV=user-vlan];
        引用函数：
        使用示例:
        """
        cmdlines = []
        lanportvlan_cmds = 'CFG-LANPORTVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4},ONUPORT={5}:CTAG::'.format(oltid, slotno, ponno, onuidtype, onuid, onuport)
        if cvlan is not None:
            lanportvlan_cmds += ',UV={0}'.format(cvlan)
        lanportvlan_cmds += ";\n"

        cmdlines.append(lanportvlan_cmds)
        return cmdlines

    @staticmethod
    def add_laniptvport(oltid, slotno, ponno, onuidtype, onuid, onuport, **kwargs):
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
        add_iptv_cmds = "ADD-LANIPTVPORT::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4},ONUPORT={5}:CTAG::".format(oltid, slotno, ponno, onuidtype, onuid, onuport)
        for key in kwargs.keys():
            if key=='UV':
                add_iptv_cmds += "{0}={1}".format(key, kwargs[key])
            else:
                add_iptv_cmds += ",{0}={1}".format(key, kwargs[key])
        add_iptv_cmds += ';\n'
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
        del_iptv_cmds = "DEL-LANIPTVPORT::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4},ONUPORT={5}:CTAG::".format(oltid, slotno, ponno, onuidtype, onuid, onuport)
        for key in kwargs.keys():
            if key=='UV':
                del_iptv_cmds += "{0}={1}".format(key, kwargs[key])
            else:
                del_iptv_cmds += ",{0}={1}".format(key, kwargs[key])
        del_iptv_cmds += ';\n'
        cmdlines.append(del_iptv_cmds)
        return cmdlines          
                
    @staticmethod
    def add_ponvlan(oltid, slotno, ponno, onuidtype, onuid, cvlan,**kwargs):
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
            add_ponvlan_cmd = "ADD-PONVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4}:CTAG::SVLAN={5},CVLAN={6}".format(oltid,slotno,ponno,onuidtype,onuid,kwargs['SVLAN'],cvlan)
        else:
            add_ponvlan_cmd = "ADD-PONVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4}:CTAG::CVLAN={5}".format(oltid,slotno,ponno,onuidtype,onuid,cvlan)
        
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
        
        del_ponvlan_cmd = "DEL-PONVLAN::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4}:CTAG::UV={5};\n".format(oltid,slotno,ponno,onuidtype,onuid,cvlan)
        
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
        BW = ('UPMGBW','UMABW','DMGBW','DMABW','UFBW')
        cmdlines = []
        add_BWprofile_cmd = "ADD-BWPROFILE::OLTID={0}:CTAG::PROFILENAME={1}".format(oltid, profilename)
        for index in range(len(args)):
            add_BWprofile_cmd += ",{0}={1}".format(BW[index],args[index])
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
        cfg_onuBW_cmd = "CFG-ONUBW::OLTID={0},PONID=NA-NA-{1}-{2},ONUIDTYPE={3},ONUID={4}:CTAG::UPBW={5},DOWNBW={6};\n".format(oltid, slotno, ponno, onuidtype, onuid, up_bandwidth, dw_bandwidth)
        cmdlines.append(cfg_onuBW_cmd)
        return cmdlines


class OLT_V4():
    def __init__(self):
        self.cmdlines__ = ""

    @classmethod
    def reboot_system(cls):
        cmdlines = ""
        cmdlines = cmdlines.join("reboot\ny\n")
       # self.cmdlines__ = cmdlines__.join(cmdlines)
        return cmdlines


class OLT_V5():
    def __init__(self, tn=None):
        self.cmdlines__ = "version"
        self.tn__ = tn

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
    def authorize_onu(auth_type, onu_sn, onutype, *onu):
        """
        函数功能：授权ONU
        函数参数:
        @auth_type(string):phy-id,log-id
        @onu_sn(string):onu physics address or logic sn 
        @onutye: Type of onu, eg. 5006-10, OTHER2
        @*onu: (slotno, ponno, onuno)
        参考命令行：
        whitelist add <phy-id/log-id> <sn> [type <onutype>] slot [slotno] pon <ponno> onuid <onuno>

        引用函数：
        """
        cmdlines = []
        try:
            cmdlines.append("whitelist add {0} {1} type {2} slot {3} pon {4} onuid {5}\n".format(auth_type, onu_sn,onutype, *onu))
        except Exception as err:
            print("Error:", err)

        return cmdlines

    @staticmethod
    def unauth_onu(auth_type, slotno, ponno, onu_sn, **kwargs):
        """
        函数功能：去授权ONU
        函数参数:
        @auth_type(string):phy-id,log-id
        @slotno(string/int):槽位号
        @ponno(string/int):PON 口号
        @onu_sn(string):onu physics address or logic sn 
        @**kwargs: checkcode
        参考命令行：
        no whitelist [phy-id|logic-id|password] <slotno> <ponno> <sn> {<checkcode>}*1
        引用函数：
        """
        checkcode = ""
        if 'checkcode' in kwargs.values():
            checkcode = kwargs['checkcode']

        cmdlines = []
        cmdlines.append("no whitelist {0} {1} {2} {3} {4}\n".format(auth_type, slotno, ponno, onu_sn, checkcode))

        return cmdlines 

    @staticmethod
    def add_uplink_vlan(uplinkslot, uplinkport, vlan_mode, vlan_begin, vlan_end):
        """
        函数功能：配置上联端口VLAN                
        函数参数: 
        参考命令行：
            Admin(config)# port vlan 101 to 101 tag 1/9 1
        引用函数：
        """
        cmdlines = []
        # cmdlines.append("config\n")
        cmdlines.append("port vlan {0} to {1} {2} 1/{3} {4} \n".format(
            vlan_begin, vlan_end, vlan_mode, uplinkslot, uplinkport))

        return cmdlines

    @staticmethod
    def onu_lan_service(onu_port, ser_count, *lan_service):
        """
        函数功能: 配置ONU端口业务                
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

        # print("debug:", lan_service)
        onuno, port = onu_port[2:]
        # cmdlines.append('config\n')
        # cmdlines.append('interface pon 1/%d/%d\n' % (slotno, ponno))
        cmdlines.append('onu port vlan {0} eth {1} service count {2}\n'.format(onuno, port, ser_count))
        for index in range(ser_count):
            # cvlan service
            cmdlines.append('onu port vlan {0} eth {1} service {2} {3} priority {4} tpid 33024 vid {5}\n'.format(onuno, port, index+1, *lan_service[index]['cvlan']))

            # translate
            if 'translate' in lan_service[index]:
                cmdlines.append('onu port vlan {0} eth {1} service {2} translate {3} priority {4} tpid 33024 vid {5}\n'.format(onuno, port, index+1, *lan_service[index]['translate']))
            
            # qinq
            if 'qinq' in lan_service[index]:
                cmdlines.append('onu port vlan {0} eth {1} service {2} qinq {3} priority {4} tpid 33024 vid {5} {6} {7}\n'.format(onuno, port, index+1, *lan_service[index]['qinq']))
    
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
        slotno, ponno, onuno = onu
        cmdlines = []
        # cmdlines.append('interface pon 1/{0}/{1}\n'.format(slotno, ponno))

        onu_ngn_voice_cmd = 'onu ngn-voice-service {0} pots {1} phonenum {2}'.format(onuno, pots, phonenum) 
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
        cmdlines.append('config\n')
        cmdlines.append('telnet slot 1/%d \n' % slot)
        cmdlines.append('')

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
