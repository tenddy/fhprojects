#!/usr/bin/env python
# coding=UTF-8
"""
###############################################################################
# @FilePath    : /fhat/lib/oltlib/oltv5.py
# @Author      : ddtu
# @Version     : V1.0
# @EMAIL       : ddtu@fiberhome.com
# @License     : (c)Copyright 2019-2020, Fiberhome(ddtu)
# @Date        : 2020-08-15 15:42:35
# @LastEditors : ddtu
# @LastEditTime: 2020-08-15 15:42:54
# @Descption   :  AN6000系列 命令行配置
###############################################################################
"""

from lib.oltlib.common import *


class AN6K():
    def __init__(self, version="V5"):
        self.__version = version
        # self.tn__ = tn

    @staticmethod
    def query_debugip():
        """
        功能:
            回读debug ip
        参数:

        返回值:

        参考命令行:

        """
        return ['interface meth 1/1\n', "show ip address\n"]

    @staticmethod
    def load_program(filename, program_type='system', serverinfo=('0.0.0.0', '1', '1'), protocol='ftp', backup=False):
        """
        功能:
            升级系统版本
        参数：
            @filename: 升级文件文件
            @program_type: 升级程序类型，system,config,script,ver-file,boot,patch,cpld,fpga
            @protocol:传输协议,ftp,tftp,sftp, 默认ftp
            @serverinfo: 服务器信息，格式(ip, username, password)
            @backup: False 升级主盘， True 升级备盘
        返回值：

        参考命令行：
            Admin(config)# load program [system|config|script|ver-file|boot|patch|cpld|fpga] <filename> [tftp|ftp|sftp] <ipaddr> {<username> <password>}*1
            Admin(config)# load program backup [system|patch|cpld|boot|fpga] <filename> [tftp|ftp|sftp]<ipaddr> {<username> <password>}*1
        """
        cmdlines = []
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
        功能:查看主控编译时间
        参数：
            @backup(bool): False--主盘（默认值）； True--备盘
        返回值：
            查看版本的命令行
        参考命令行：
            Admin(diagnose)# show debugversion
        """
        if backup:
            cmdlines = ['telnet slot backup\n', 'diagnose\n', 'show debugversion\n']
        else:
            cmdlines = ['diagnose\n', 'show debugversion\n']
        return cmdlines

    @staticmethod
    def show_card():
        """查看OLT单盘状态"""
        return ['show card\n']

    @staticmethod
    def pon_auth_mode(slotno, ponno, authmode: PONAuthMode):
        """
        功能:
            配置PON口授权模式
        参数:
            @param slotno(int/string): 槽位号
            @param ponno(int/string): PON口号
            @param authmode(PONAuthMode): PON口授权模式
        返回值: 命令行列表
        命令行说明:
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
    def showDiscovery(slotno, ponno):
        """获取未授权ONU列表"""
        cmdlines = []
        cmdlines.append('show discovery 1/{s}/{p}\n'.format(s=slotno, p=ponno))
        return cmdlines

    @staticmethod
    def showAuthorization(slotno, ponno):
        """获取已授权ONU列表"""
        cmdlines = []
        cmdlines.append('show authorization 1/{s}/{p}\n'.format(s=slotno, p=ponno))
        return cmdlines

    @staticmethod
    def authorize_onu(auth_type: ONUAuthType, onu_sn, onutype, *onu):
        """
        功能:
            授权ONU
        参数:
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
        功能:
            去授权ONU
        参数:
            @auth_type(enum):ONUAuthType
            @slotno(str/int):槽位号
            @ponno(str/int):PON 口号
            @onu_sn(str):onu physics address or logic sn
            @**kwargs: checkcode

        参考命令行：
            no whitelist [phy-id|logic-id|password] <slotno> <ponno> <sn> {<checkcode>}*1
        """
        auth_mode = ('phy-id', 'password', 'logic-id')

        checkcode = kwargs['checkcode'] if 'checkcode' in kwargs.values() else ""

        cmdlines = []
        cmdlines.append("no whitelist {0} {1} {2} {3} {4}\n".format(
            auth_mode[auth_type.value], slotno, ponno, onu_sn, checkcode))
        return cmdlines

    @staticmethod
    def add_uplink_vlan(uplinkslot, uplinkport, vlan_mode: VLAN_MODE, vlanlist: str, allslot=True):
        """
        功能:
            配置上联端口VLAN
        参数:
            @uplinkslot: 上联口槽位号或者主控槽位号
            @uplinkport: 上联口端口
            @vlan_mode(enum): vlan模式
            @vlanlist(str): vlan, 例如： 1000-1010, 2000
            @allslot(bool): 将VLAN配置到槽位
        返回值: 
            命令行列表
        参考命令行：
            Admin(config)# port vlan 101 to 101 tag 1/9 1
        """
        cmdlines = []
        if len(vlanlist.rstrip()) == 0:
            return cmdlines

        for item in vlanlist.split(","):
            vids = item.split("-")
            if len(vids) == 1:
                cmdlines.append(
                    "port vlan {0} {1} 1/{2} {3} \n".format(vids[0], VLAN_MODE.mode.value[vlan_mode.value], uplinkslot, uplinkport))
                if allslot:
                    cmdlines.append(
                        "port vlan {0} allslot \n".format(vids[0]))
            if len(vids) == 2:
                cmdlines.append(
                    "port vlan {0} to {1} {2} 1/{3} {4} \n".format(
                        vids[0].rstrip(),
                        vids[1].rstrip(),
                        VLAN_MODE.mode.value[vlan_mode.value],
                        uplinkslot, uplinkport))
                if allslot:
                    cmdlines.append("port vlan {0} to {1} allslot\n".format(vids[0].rstrip(), vids[1].rstrip()))

        return cmdlines

    @staticmethod
    def show_port_vlan(slotno, portno):
        """
        功能:
            获取上联口VLAN
        参数:
            @slotno(int/string): 槽位号
            @portno(int/string): 端口号
        返回值: 
            命令行列表
        命令行说明:
            Admin(config)# show port vlan <frameid/slotid/portid>
        """
        return ['show port vlan 1/{slotid}/{portid}\n'.format(slotid=slotno, portid=portno)]

    @staticmethod
    def del_uplink_vlan(uplinkslot, uplinkport, vlanlist: str):
        """
        功能:
            删除上联口VLAN
        参数:
            @uplinkslot: 上联口槽位号或者主控槽位号
            @uplinkport: 上联口端口
            @vlanlist(str): vlan, 例如： 1000-1010, 2000

        返回值: None
        命令行说明:
            Admin(config)# no port vlan 101 1/9 2
        """
        cmdlines = []
        for item in vlanlist.split(","):
            vids = item.split("-")
            if len(vids) == 1:
                cmdlines.append(
                    "no port vlan {0} 1/{1} {2} \n".format(vids[0], uplinkslot, uplinkport))
            if len(vids) == 2:
                cmdlines.append(
                    "port vlan {0} to {1} 1/{3} {4} \n".format(vids[0].rstrip(), vids[1].rstrip(), uplinkslot, uplinkport))

        return cmdlines

    @staticmethod
    def igmp_vlan(mvlan):
        """配置组播VLAN"""
        return ['igmp\n', 'igmp vlan %d\n' % mvlan, 'quit\n']

    @staticmethod
    def onu_lan_service(onu_port, lan_service, flag=False):
        """
        函数功能:
            配置ONU端口业务

        参数:
            @onu_port: (slotno, ponno, onuno, port)
            @lan_service(list/tuple): ({'cvlan':(cvlan_mode, cvlan, ccos), 'translate':(tflag, tvlan, tcos), 'qinq':(sflag, svlan, scos, qinqprf, svlan_service), 'multicast':True},) 
            @flag: 配置业务之前，删除端口业务；默认False，不删除端口业务
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
        """

        cmdlines = []
        # if len(lan_service) < ser_count:
        #     print("Error: service count(%d) > lan_service(%d)" % (ser_count, len(lan_service)))
        #     return cmdlines
        ser_count = len(lan_service)

        onuno, port = onu_port[2:]
        # cmdlines.append('config\n')
        cmdlines.append('interface pon 1/%d/%d\n' % (onu_port[:2]))
        if flag:    # 配置端口业务之前，清空端口配置
            cmdlines.append('onu port vlan {0} eth {1} service count 0\n'.format(onuno, port))
        if ser_count != 0:
            cmdlines.append('onu port vlan {0} eth {1} service count {2}\n'.format(onuno, port, ser_count))
        for index in range(ser_count):
            # cvlan service
            cmdlines.append('onu port vlan {0} eth {1} service {2} {3} priority {5} tpid 33024 vid {4}\n'.format(
                onuno, port, index + 1, *lan_service[index]['cvlan']))

            # translate
            if 'tvlan' in lan_service[index]:
                cmdlines.append(
                    'onu port vlan {0} eth {1} service {2} translate {3} priority {5} tpid 33024 vid {4}\n'.format(
                        onuno, port, index + 1, *lan_service[index]['tvlan']))

            # qinq
            if 'qinq' in lan_service[index]:
                cmdlines.append(
                    'onu port vlan {0} eth {1} service {2} qinq {3} priority {5} tpid 33024 vid {4} {6} {7}\n'.format(
                        onuno, port, index + 1, *lan_service[index]['qinq']))

            # multicast
            if 'multicast' in lan_service[index] and lan_service[index]['multicast']:
                cmdlines.append('onu port vlan {0} eth {1} service {2} type multicast\n'.format(
                    onuno, port, index + 1))

        cmdlines.append('quit\n')

        return cmdlines

    @staticmethod
    def onu_wan_service(onu, index, cvlan, dsp, **kargs):
        """
        功能:
            配置ONU wan业务
        参数：
            @onu(tuple): ONU信息, (slotno, ponno, onuid)
            @index(int): WAN业务序号， 
            @cvlan(tuple): cvlan和cos值，(vlan, cos)
            @dsp(dict): 业务类型， 如下配置方法，三选一
                      {'mode':'dhcp', 'remoteid':''}
                      {'mode':'static', 'ip': '', 'mask':'', 'gate':'', 'dns_m': '', 'dns_s': ''} 
                      {'mode':'pppoe', 'proxy':'enable|disable', 'username':'', 'password':'', 'name':'', 'auth':'auto|payload|manual'}  

            @**kargs(dict): 
                mode: tr069|internet|tr069-internet|other|multi|voip|voip-internet|iptv|radius|radius-internet|unicast-iptv|multicast-iptv
                type: bridge|route
                nat: enable|disable
                qos: enable|disable
                vlanmode: {'mode':'tag|transparent', 'tvlan':'', 'tvid':'', 'tcos':'')} 
                qinq: ([enable|disable], stpid,svlan,scos)
                service_type: NONE|DATA|IPTV|MANAGEMENT|VOIP
                upnp_switch: enable|disable
                entries: ('fe1', 'ssid2')  fe1|fe2|fe3|fe4|ssid1|ssid2|ssid3|ssid4 ssid5|ssid6|ssid7|ssid8|10glan

                ipv6: {'ip-stack-mode': 'ipv4|ipv4&ipv6|ipv6', 'ipv6-src-type': 'ipv6', 'prefix-src-type': 'delegate' }
        返回值: None
        命令行说明:
            onu wan-cfg 1 ind 1 mode inter ty r 1000 3 nat en qos dis dsp pppoe pro dis fiberhome key:85<9,6/19 null auto entries 1 ssid1  
            onu ipv6-wan-cfg 1 ind 1 ip-stack-mode ipv4 ipv6-src-type dhcpv6 prefix-src-type delegate 

        """
        cmdlines = []
        slotno, ponno, onuid = onu
        cmdlines.append('interface pon 1/%d/%d\n' % (onu[:2]))
        mode = kargs['mode'] if "mode" in kargs.keys() else 'internet'
        s_type = kargs['type'] if 'type' in kargs.keys() else "route"
        nat = kargs['nat'] if 'nat' in kargs.keys() else 'enable'
        qos = kargs['qos'] if 'qos' in kargs.keys() else 'disable'
        wan_cmd = "onu wan-cfg {o} index {ind} mode {m} type {t} {cvlan} {ccos} nat {n} qos {q} ".format(
            o=onu[2], ind=index, m=mode, t=s_type, cvlan=cvlan[0], ccos=cvlan[1], n=nat, q=qos)

        if 'vlanmode' in kargs.keys():
            wan_cmd += 'vlanmode {mode} tvlan {tvlan} {tvid} {tcos} '.format(**kargs['vlanmode'])

        if 'qinq' in kargs.keys():
            wan_cmd += 'qinq {en} {tpid} {svlan} {scos} '.format(
                **dict(zip(('en', 'tpid', 'svlan', 'scos'), kargs['qinq'])))

        # dsp
        if dsp['mode'] == 'dhcp':
            if 'remoteid' in dsp.keys():
                wan_cmd += 'dsp dhcp dhcp-remoteid {} '.format(dsp['remoteid'])
            else:
                wan_cmd += 'dsp dhcp '

        if dsp['mode'] == 'static':
            master = dsp['dns_m'] if 'dns_m' in dsp.keys() else '0.0.0.0'
            slave = dsp['dns_s'] if 'dns_s' in dsp.keys() else '0.0.0.0'
            wan_cmd += 'dsp static ip {ip} mask {mask} gate {gate} master {dns_m} slave {dns_s} '.format(
                ip=dsp['ip'], mask=dsp['mask'], gate=dsp['gate'], dns_m=master, dns_s=slave)

        if dsp['mode'] == 'pppoe':
            proxy = dsp['proxy'] if 'proxy' in dsp.keys() else 'disable'
            name = dsp['name'] if 'name' in dsp.keys() else 'null'
            auth = dsp['auth'] if 'auth' in dsp.keys() else 'auto'
            wan_cmd += 'dsp pppoe proxy {p} {user} {pwd} {name} {auth} '.format(
                p=proxy, user=dsp['username'], pwd=dsp['password'], name=name, auth=auth)

        if 'service_type' in kargs.keys():
            wan_cmd += 'service-type {} '.format(kargs['service_type'])

        if 'upnp_switch' in kargs.keys():
            wan_cmd += 'upnp_switch {} '.format(kargs['upnp_switch'])

        entries = kargs['entries'] if 'entries' in kargs.keys() else('fe1',)
        entries = (entries,) if isinstance(entries, str) else entries
        wan_cmd += "entries {0} {1}\n".format(len(entries), " ".join(entries))

        cmdlines.append(wan_cmd)
        # print("wan:{}".format(cmdlines))
        cmdlines.append('quit\n')
        return cmdlines

    @staticmethod
    def add_bandwidth_prf(prf_name, prf_id=None, up_pir=1000000, dw_pir=1000000, **kargs):
        """
        功能：
            创建带宽模板
        参数：
            @prf_name(str): 带宽模板名称
            @prf_id(int): 模板ID（1~1024), 默认为None, 自动添加模板ID
            @up_pir(int): 上行最大带宽(kb)，默认为1000000
            @dw_pir(int): 下行最大带宽(kb)，默认为1000000
            @kargs:
                up_fir(int): 上行固定带宽(kb)
                up_cir(int): 上行保证带宽(kb)
                dw_cir(int): 下行保证带宽(kb)
        返回值：命令行列表
        说明：
            Admin(config)# bandwidth-profile add <profile-name> {[id] <profile-id>}*1 {upstream-pir <us-pir> downstream-pir
             <ds-pir>}*1 {upstream-cir <us-cir> downstream-cir <ds-cir> upstream-fir <us-fir>}*1
        """
        cmdlines = []
        profile = ["bandwidth-profile add {}".format(prf_name)]
        profile.append("id {}".format(prf_id) if prf_id is not None else "")
        profile.append("upstream-pir {} downstream-pir {}".format(up_pir, dw_pir))

        up_cir = kargs['up_cir'] if 'up_cir' in kargs.keys() else 0
        profile.append('upstream-cir {}'.format(up_cir))

        dw_cir = kargs['dw_cir'] if 'dw_cir' in kargs.keys() else 0
        profile.append('downstream-cir {}'.format(dw_cir))

        up_fir = kargs['up_fir'] if 'up_fir' in kargs.keys() else 0
        profile.append('upstream-fir {}'.format(up_fir))

        profile.append("\n")
        cmdlines.append(" ".join(profile))
        return cmdlines

    @staticmethod
    def modify_bandwidth_prf(prf_id_name, up_pir, dw_pir, **kargs):
        """
        功能：
            修改带宽模板
        参数：
            @prf_id_name(int/str): 带宽模板ID（1~1024）或者名称
            @up_pir(int): 上行最大带宽(kb)
            @dw_pir(int): 下行最大带宽(kb)
            @kargs:   
                up_fir(int): 上行固定带宽(kb)
                up_cir(int): 上行保证带宽(kb)
                dw_cir(int): 下行保证带宽(kb)
        返回值：命令行列表
        说明：
            bandwidth-profile modify [id|name] <id-or-name> {upstream-pir <us-pir> downstream-pir <ds-pir>}*1 
            {upstream-cir <us-cir> downstream-cir <ds-cir> upstream_fir <us-fir>}*1
        """
        cmdlines = []
        if isinstance(prf_id_name, int):
            profile = [
                "bandwidth-profile modify id {} upstream-pir {} downstream-pir {}".format(prf_id_name, up_pir, dw_pir)]
        else:
            profile = [
                "bandwidth-profile modify name {} upstream-pir {} downstream-pir {}".format(prf_id_name, up_pir, dw_pir)]

        up_cir = kargs['up_cir'] if 'up_cir' in kargs.keys() else 0
        profile.append('upstream-cir {}'.format(up_cir))

        dw_cir = kargs['dw_cir'] if 'dw_cir' in kargs.keys() else 0
        profile.append('downstream-cir {}'.format(dw_cir))

        up_fir = kargs['up_fir'] if 'up_fir' in kargs.keys() else 0
        profile.append('upstream_fir {}'.format(up_fir))

        profile.append("\n")
        cmdlines.append(" ".join(profile))
        return cmdlines

    @staticmethod
    def delete_bandwidth_prf(**bandwidth_prf_id_name):
        """
        功能：
            删除带宽模板
        参数：
            @bandwidth_prf_id_name: {'id': ''} 或者 {'name': ''}
                通过带宽模板id或者名称删除带宽模板
        返回值：
            命令行列表
        说明：	
            bandwidth-profile delete [id|name] <id-or-name>
        """
        cmdlines = []
        for key in bandwidth_prf_id_name:
            cmdlines.append("bandwidth-profile delete {} {}\n".format(key, bandwidth_prf_id_name[key]))
        return cmdlines

    @staticmethod
    def show_bandwidth_prf():
        """获取带宽模板"""
        return ['show bandwidth-profile all\n']

    @staticmethod
    def onu_layer3_ratelimit(slotno, ponno, onuid, bandwidth_prf_id):
        """
        功能：
            配置ONU三层流限速
        参数：
            @slotno(int):槽位号
            @ponno(int):PON 口号
            @onuid(int):ONU ID
            @bandwidth_prf_id(tuple): [(wan_index, up_prf, dw_prf)], WAN index，上行带宽模板，下行带宽模板
        返回值：
            命令行列表
        说明：	
            Admin(config-if-pon-)#onu layer3-ratelimit-profile <onuno> {<wanindex> upstream-profile-id <upbandwidthprfid> downstream-profile-id <dwbandwidthprfid>}*8
        """
        cmdlines = []
        cmdlines.append("interface pon 1/{}/{}\n".format(slotno, ponno))
        ratelimit = ["onu layer3-ratelimit-profile {}".format(onuid)]
        for item in bandwidth_prf_id:
            ratelimit.append("{0} upstream-profile-id {1} downstream-profile-id {2}".format(*item))
        ratelimit.append("\n")
        cmdlines.append(" ".join(ratelimit))
        cmdlines.append("quit\n")
        return cmdlines

    @staticmethod
    def create_oltqinq_domain(qinq_name, *vlanrule):
        """
        功能:
            创建OLT qinq域。
        参数：
            @qinq_name: olt qinq域名称
            @*vlanrule: ({
                'uprule':((filedid, value, condition),), 
                'dwrule': ((filedid, value, condition),),
                'vlanrule': ((l1oldvlan, l1oldvlan_cos, l1_action, l1_tpid, l1_newvlan, l1_newvlancos,
                            l2oldvlan, l2oldvlan_cos, l2_action, l2_tpid, l2_newvlan, l2_newvlancos),)
            },)

            # uprule 与dwrule 分别是上下行匹配规则；默认值为((2, '000000000000', 5),)
            # vlanrule 是为 VLAN转换规则，格式为（l1oldvlan, l1oldvlan_cos, l1_action, l1_tpid, l1_newvlan, l1_newvlancos, l2oldvlan, l2oldvlan_cos, l2_action, l2_tpid, l2_newvlan, l2_newvlancos）
            示例：({'upRule':((2, '000000000000', 5),), 'dwRule': ((2, '000000000000', 5),), 'vlanrule': (100, 'null', 'translation', 33024, 201, 1, 'null', 'null', 'add', 33024, 2701, 1)},)

            # 上下行匹配规则字段说明：
            fieldId:规则ID，范围(1~27), 1(Dst Mac) 2(Src Mac) 3(Ethernet Type) 4(Vlan4) 5(Vlan3) 6(Vlan2) 7(Vlan1) 8(TOS) 10(TTL)
            11(Protocol Type) 12(Src IPv4) 13(Src IPv6) 14(Dst IPv4) 15(Dst IPv6) 16(L4 Src Port) 17(L4 Dst Port) 18(Cos4) 19(Cos3)
            20(Cos2) 21(Cos1) 22(Dst IPv6 Prefix) 23(Src IPv6 Prefix)  24(IP Version) 25(IPv6 Traffic Class) 26(IPv6 Flow Label) 27(IPv6 Next Header).

            @value: 规则ID所对应值
            condition:匹配规则，范围(0~7),0(Never) 1(==) 2(!=) 3(<=) 4(>=) 5(Exist) 6(No exist) 7(Always)
        命令行：
            # oltqinq 上行匹配规则
            Admin(config)# oltqinq-domain <name> service <1-8> classification upstream {field-id <1-27> value <value> condition <condition>}*4 {serv-id <1-8>}*1

            # oltqinq 下行匹配规则
            Admin(config)# oltqinq-domain <name> service <1-8> classification downstream {field-id <1-27> value <value> condition <condition>}*4

            # 配置VLAN转换规则
            Admin(config)# oltqinq-domain <name> service <1-8> {vlan <1-4> user-vlanid [<0-4095>|null] user-cos [<0-7>|null] [add|translation|transparent]
            tpid <tpid> cos [<cos>|user-cos|null] vlanid [<vlanid>|null]}*4

        示例：
            config_oltqinq_vlanservice('qinq_test', {'uprule': ((7, 100, 4), (7, 200, 3)), 'dwrule':((2,'000000000000', 5),), 
            'vlanrule': (100, 'null', 'translation', 33024, 201, 1, 'null', 'null', 'add', 33024, 2701, 1)})
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
        功能:
            删除olt qinq 域模板

        参数：
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
        功能:
        参数：
        参考命令行：
        Admin(config)# show oltqinq-domain <name>
        """
        cmdlines = []
        cmdlines.append('show oltqinq-domain %s\n' % qinq_name)
        return cmdlines

    @staticmethod
    def attach_oltqinq(qinq_name, *portno):
        """
        功能:
        绑定oltqinq域
        参数：

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
        功能:
            去绑定oltqinq域
        参数：

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
        功能:
            配置ONU端口语音业务
        参数:
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
        功能:
            删除ONU端口语音业务
        参数:
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
        功能:
            通过线卡Telnet到MDU，并获取MDU的编译时间
        参数:
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
