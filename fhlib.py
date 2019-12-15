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
        self.cmdline__ = ""

    @classmethod
    def reboot_system(cls):
        cmdline = ""
        cmdline = cmdline.join("reboot\ny\n")
       # self.cmdline__ = cmdline__.join(cmdline)
        return cmdline


class OLT_V5():
    def __init__(self):
        self.cmdline__ = "version"

    @classmethod
    def query_debugip(cls):
        cmdline = ""
        cmdline += "show debugip\n"
        return cmdline

    @classmethod
    def add_uplink_vlan(cls, uplinkslot, uplinkport, vlan_mode, vlan_begin, vlan_end):
        """
        函数功能：配置上联端口VLAN
        函数参数: 
        参考命令行：

        引用函数：Admin(config)# port vlan 101 to 101 tag 1/9 1
        """
        cmdline = []
        cmdline.append("config\n")
        cmdline.append("port vlan {0} to {1} {2} 1/{3} {4} \n".format(
            vlan_begin, vlan_end, vlan_mode, uplinkslot, uplinkport))

        return cmdline

    @classmethod
    def config_onu_lan_service(cls, slotno, ponno, onuno):
        """
        """
        cmdline = ""

        return cmdline

    @classmethod
    def get_onu_version(cls, slotno, ponno, onuno):
        """
        函数功能： 通过线卡Telnet到MDU，并获取MDU的编译时间
        """
        cmdline = []
        cmdline.append("config\n")
        cmdline.append('t l 0 \n')
        cmdline.append('telnet slot 1/%s' % slotno)
        cmdline.append('cd service \n')
        cmdline.append('telnetdata pon % onu % \n')
        cmdline.append('')

    @classmethod
    def create_config():
        '''
        onu port vlan 1 eth 1 service count 3
        onu port vlan 1 eth 1 service 1 transparent priority 1 tpid 33024 vid 41 
        onu port vlan 1 eth 1 service 1 translate enable priority 1 tpid 33024 vid 301
        onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2

        onu port vlan 1 eth 1 service 2 tag priority 3 tpid 33024 vid 45 
        onu port vlan 1 eth 1 service 2 qinq enable priority 3 tpid 33024 vid 2701 FTTB_QINQ SVLAN2

        onu port vlan 1 eth 1 service 3 tag priority 7 tpid 33024 vid 46 
        onu port vlan 1 eth 1 service 3 qinq enable priority 7 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
        '''
        ONUID = [1, 2, 3, 6, 7, 10, 15, 20, 30, 58, 59, 60, 61, 62]
        PORTNO = [8, 24, 24, 16, 16, 16, 24, 16, 16, 24, 16, 16, 24, 24]

        ser_count = 3
        svlan = 2701
        send_cmd = []
        for index in range(14):
            onuid = ONUID[index]
            portno = PORTNO[index]
            ser_count = 3
            for p in range(portno):

                cmd0 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, 0)
                send_cmd.append(cmd0)
                cmd1 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, ser_count)
                send_cmd.append(cmd1)
                cmd2 = 'onu port vlan %d eth %d service %d transparent priority 1 tpid 33024 vid %d\n' % (
                    onuid, p + 1, 1, 41)
                send_cmd.append(cmd2)
                cmd3 = 'onu port vlan %d eth %d service %d translate enable priority 1 tpid 33024 vid %d\n' % (
                    onuid, p + 1, 1, 301 + (onuid - 1) * 24 + p)
                send_cmd.append(cmd3)
                cmd4 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (
                    onuid, p + 1, 1, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd4)
                cmd5 = 'onu port vlan %d eth %d service %d transparent priority 1 tpid 33024 vid %d\n' % (
                    onuid, p + 1, 2, 45)
                send_cmd.append(cmd5)
                cmd6 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (
                    onuid, p+1, 2, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd6)
                cmd7 = 'onu port vlan %d eth %d service %d transparent priority 7 tpid 33024 vid %d\n' % (
                    onuid, p + 1, 3, 46)
                send_cmd.append(cmd7)
                cmd8 = 'onu port vlan %d eth %d service %d qinq enable priority 7 tpid 33024 vid %d %s %s\n' % (
                    onuid, p+1, 3, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd8)

            with open(r'E:/config.txt', 'w') as f:
                f.write(''.join(send_cmd))
        return send_cmd

    @classmethod
    def create_config1():
        '''
        onu port vlan 1 eth 1 service count 3
        onu port vlan 1 eth 1 service 1 tag priority 1 tpid 33024 vid 41 
        onu port vlan 1 eth 1 service 1 translate enable priority 1 tpid 33024 vid 301
        onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2

        onu port vlan 1 eth 1 service 2 tag priority 3 tpid 33024 vid 45 
        onu port vlan 1 eth 1 service 2 qinq enable priority 3 tpid 33024 vid 2701 FTTB_QINQ SVLAN2

        onu port vlan 1 eth 1 service 3 tag priority 7 tpid 33024 vid 46 
        onu port vlan 1 eth 1 service 3 qinq enable priority 7 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
        '''
        ONUID = [1, 2, 3, 6, 7, 10, 15, 20, 30, 58, 59, 60, 61, 62]
        PORTNO = [8, 24, 24, 16, 16, 16, 24, 16, 16, 24, 16, 16, 24, 24]

        ser_count = 3
        # trans_ser_vlan = 41
        svlan = 2701
        for index in range(14):
            onuid = ONUID[index]
            portno = PORTNO[index]
            ser_count = 3
            for p in range(portno):
                send_cmd = []
                cmd0 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, 0)
                send_cmd.append(cmd0)
                cmd1 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, ser_count)
                send_cmd.append(cmd1)
                cmd2 = 'onu port vlan %d eth %d service %d tag priority 1 tpid 33024 vid %d\n' % (
                    onuid, p+1, 1, 41)
                send_cmd.append(cmd2)
                cmd3 = 'onu port vlan %d eth %d service %d translate enable priority 1 tpid 33024 vid %d\n' % (
                    onuid, p+1, 1, 301 + (onuid - 1) * 24 + p)
                send_cmd.append(cmd3)
                cmd4 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (
                    onuid, p+1, 1, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd4)
                cmd5 = 'onu port vlan %d eth %d service %d transparent priority 1 tpid 33024 vid %d\n' % (
                    onuid, p+1, 2, 45)
                send_cmd.append(cmd5)
                cmd6 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (
                    onuid, p+1, 2, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd6)
                cmd7 = 'onu port vlan %d eth %d service %d transparent priority 7 tpid 33024 vid %d\n' % (
                    onuid, p + 1, 3, 46)
                send_cmd.append(cmd7)
                cmd8 = 'onu port vlan %d eth %d service %d qinq enable priority 7 tpid 33024 vid %d %s %s\n' % (
                    onuid, p+1, 3, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd8)

                with open(r'E:/config1.txt', 'w') as f:
                    f.write(''.join(send_cmd))
                return send_cmd
