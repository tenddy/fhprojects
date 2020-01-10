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
    def __init__(self):
        self.cmdlines__ = "version"

    @classmethod
    def query_debugip(cls):
        """
        函数功能：回读debug ip
        函数参数: 
        参考命令行：

        引用函数：
        """
        cmdlines = []
        cmdlines.append['config\n', 'interface meth 1/1\n', "show ip address\n"]
        return cmdlines

    @classmethod
    def authorize_onu(cls, auth_type, onu_sn, onutype, *onu):
        """
        函数功能：授权ONU
        函数参数:
        @slotno(string):phy-id,log-id
        @onu_sn(string):onu physics address or logic sn 
        @onutye: Type of onu, eg. 5006-10, OTHER2
        @*onu: (slotno, ponno, onuno)
        参考命令行：
        whitelist add <phy-id/log-id> <sn> [type <onutype>] slot [slotno] pon <ponno> onuid <onuno>

        引用函数：
        """
        cmdlines = []
        try:
            cmdlines.append("config\n")
            cmdlines.append("whitelist add {0} {1} type {2} slot {3} pon {4} onuid {5}\n".format(auth_type, onu_sn,onutype, *onu))
        except Exception as err:
            print("Error:", err)

        return cmdlines


    @classmethod
    def add_uplink_vlan(cls, uplinkslot, uplinkport, vlan_mode, vlan_begin, vlan_end):
        """
        函数功能：配置上联端口VLAN                
        函数参数: 
        参考命令行：
            Admin(config)# port vlan 101 to 101 tag 1/9 1
        引用函数：
        """
        cmdlines = []
        cmdlines.append("config\n")
        cmdlines.append("port vlan {0} to {1} {2} 1/{3} {4} \n".format(
            vlan_begin, vlan_end, vlan_mode, uplinkslot, uplinkport))

        return cmdlines

    @classmethod
    def onu_lan_service(cls, onu_port, ser_count, *lan_service):
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
        slotno, ponno, onuno, port = onu_port
        # cmdlines.append('config\n')
        # cmdlines.append('interface pon 1/%d/%d\n' % (slotno, ponno))
        cmdlines.append('onu port vlan %d eth %d service count %d\n' % (onuno, port, ser_count))
        for index in range(ser_count):
            # cvlan service
            cmdlines.append('onu port vlan %d eth %d service %d %s priority %d tpid 33024 vid %d\n' % (onuno, port, index+1, *lan_service[index]['cvlan']))

            # translate
            if 'translate' in lan_service[index]:
                cmdlines.append('onu port vlan %d eth %d service %d translate %s priority %d tpid 33024 vid %d\n' % (onuno, port, index+1, *lan_service[index]['translate']))
            
            # qinq
            if 'qinq' in lan_service[index]:
                cmdlines.append('onu port vlan %d eth %d service %d qinq %s priority %d tpid 33024 vid %d %s %s\n' % (onuno, port, index+1, *lan_service[index]['qinq']))
    
        return cmdlines

    @classmethod
    def get_onu_version(cls, *onu):
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

    @classmethod
    def get_MDU_ngn_ip(cls, slot, pon, onu, ip):
        cmdlines = []
        cmdlines.append('config\n')
        cmdlines.append('telnet slot 1/%d \n' % slot)
        cmdlines.append('')

    @classmethod
    def model1_config(cls):
        '''
        onu port vlan 1 eth 1 service count 1
        onu port vlan 1 eth 1 service 1 tag priority 1 tpid 33024 vid 301 
        onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
        '''
        onu_count = 18
        ONUID_NEW = range(1,onu_count+1)
        PORTNO = [16,16,8,24,24,16,24,24,16,16,16,16,24,24,4,4,4,8]

        with open(r'E:/config_model1.txt','w') as f:
            # onu1
            # onuid = 1
            # portno = 8
            ser_count = 1
            # trans_ser_vlan = 41
            svlan = 2701
            send_cmd = []
            for index in range(onu_count):
                onuid = ONUID_NEW[index]
                portno = PORTNO[index]
                for p in range(portno):
                    
                    cmd0 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, 0)
                    send_cmd.append(cmd0)
                    cmd1 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, ser_count)
                    send_cmd.append(cmd1)
                    cmd2 = 'onu port vlan %d eth %d service %d tag priority 1 tpid 33024 vid %d\n' % (onuid, p+1, 1, 301+(onuid-1)*24 + p)
                    send_cmd.append(cmd2)
                    cmd4 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 1, svlan, 'FTTB_QINQ', 'SVLAN2')
                    send_cmd.append(cmd4)
                    send_cmd.append(cmd2)
            f.write(''.join(send_cmd))