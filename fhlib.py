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
