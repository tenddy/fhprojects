#!/usr/bin/env python
# coding=UTF-8

import os
import sys
import time
try:
    currentPath = os.path.dirname(__file__)
    rootPath = "\\".join(currentPath.split("\\")[:-3])
    if rootPath not in sys.path:
        sys.path.append(rootPath)

    from lib import settings

    settings.TESTCASE_PATH = "/".join(__file__.split("\\")[:-2])
    # log 目录
    # filename = time.strftime('%Y%m%d%H%M%S') + '.log'
    settings.LOG_PATH = "/".join(__file__.split("\\")[:-2]) + "/log"
    # print(settings.LOG_PATH)
    if not os.path.isdir(settings.LOG_PATH):
        os.mkdir(settings.LOG_PATH)
    # capture 目录
    settings.CAP_PATH = "/".join(__file__.split("\\")[:-2]) + "/capture"
    # print(settings.CAP_PATH)
    if not os.path.isdir(settings.CAP_PATH):
        os.mkdir(settings.CAP_PATH)
    # instruments 目录
    settings.XML_PATH = "/".join(__file__.split("\\")[:-2]) + "/instruments"
    # print(settings.XML_PATH)
    if not os.path.isdir(settings.XML_PATH):
        os.mkdir(settings.XML_PATH)
except:
    print("PATH Error")


# 测试场景相关配置
SETTINGS = {
    # TCL路径（只支持8.4)
    "TCL_PATH": "C:/Tcl/bin/tclsh",

    # 仪表配置
    "STC_PATH": "C:/Program Files (x86)/Spirent Communications/Spirent TestCenter 4.95/Spirent TestCenter Application",
    "STC_IP": "10.182.32.138",

    # 仪表端口
    "STC_UPLINK": {'uplink': '1/13'},
    "STC_ONU": {'onu1': '1/5', 'onu2': '1/6', 'onu3': '1/7'},
    # 上联口连接交换机
    "UPLINK_SWITCH": {},
    # ONU汇聚交换机
    "ONU_SWITCH": {
        "AGG_PORT": (48),
        "UNTAG_VLAN": 100,
        "TAG_VLAN": 200,
    },
    # OLT 信息
    "OLT": {
        "OLT_VERSION": "AN6000-17",
        "OLT_IP": "10.182.33.185",
        "OLT_LOGIN": {'Login:': 'GEPON', 'Password:': 'GEPON'},
        "TELNET_PORT": 23,
        "SSH_PORT": 22,
    },

    "UPLINK_PORTS": {'uplink': '9/2'},       # OLT上联端口
    "SLOTNO": 4,    # 槽位号
    "PONNO": 8,     # PON口号

    # ONU信息
    "ONU": [
        {
            'ONUID': 1,                 # ONU ID，授权号
            'ONUTYPE': '5506-04-F1',    # ONU授权类型
            'PHYID': 'FHTT033178b0',    # 物理SN
            'PHYPWD': 'fiberhome',      # 物理密码
            'LOGICID': 'fiberhome',     # 逻辑SN
            'PASSWORD': 'fiberhome',    # 逻辑密码
            'MODEL': ['m1', 'm2'],      # 业务模型, MODEL[key]
            'STC_PORT': {'1': "onu1", '2': "onu3", '4': "onu3"},  # 对应的仪表端口
            'SW_PORT': {"2": 2, "4": 4}  # ONU 端口是否连接仪表,  根据连接的交换机端口，配置端口业务和仪表配置
        },

        {
            'ONUID': 64,
            'ONUTYPE': 'HG6243C',
            'PHYID': 'FHTT92f445c8',
            'PHYPWD': 'fiberhome',
            'LOGICID': 'fiberhome',
            'PASSWORD': 'fiberhome',
            "MODEL": ['m1', 'm2', 'm3'],
            "STC_PORT": {'1': "onu2", '2': '', '3': '', '4': 'onu3'},
            'SW_PORT': {'3': 7, '4': 8}  # ONU 端口是否连接仪表
        },

        {
            'ONUID': 65,
            'ONUTYPE': 'HG6243C',
            'PHYID': 'FHTT91fbc5e8',
            'PHYPWD': 'fiberhome',
            'LOGICID': 'fiberhome',
            'PASSWORD': 'fiberhome',
            'MODEL': ['m1'],
            "STC_PORT": {'1': "", '2': 'onu3', '3': '', '4': 'onu3'},
            'SW_PORT': {'2': 6, '4': 8}  # ONU 端口是否连接仪表
        },

        {
            'ONUID': 128,
            'ONUTYPE': '5506-02-F',
            'PHYID': 'FHTT0274ab18',
            'PHYPWD': '',
            'LOGICID': '',
            'PASSWORD': '',
            'MODEL': [''],
            "STC_PORT": {'1': "onu3"},
            'SW_PORT': {'1': 5, '4': 8}  # ONU 端口是否连接仪表
        }

    ],

    "Threshold": 0.05,  # 流量判断阈值
}

# 初始化默认仪表参数
settings.TCL_PATH = SETTINGS['TCL_PATH']
settings.STC_PATH = SETTINGS['STC_PATH']
settings.STCIP = SETTINGS['STC_IP']
settings.UPLINK_PORTS = SETTINGS['STC_UPLINK']
settings.ONU_PORTS = SETTINGS['STC_ONU']


# ONU 业务模型
MODEL = {
    # 业务模型demo，相关参数说明
    "m0": {
        'internet': [
            {
                'type': 'wan_pppoe',        # fe, wan_dhcp, wan_pppoe, wan_static, veip
                'mode': 'transparent',
                'vlan': {
                    'cvlan': (100, 3),          # cvlan, (cvid, cos)
                    'tvlan': (1001, 4),       # tvlan, (tvid, tcos)
                    'svlan': (2000, 4),        # onu qinq:(svlan, scos)
                    'qinqprf': {},            # ONU 业务模式为FE，并且使能了svlan,即使能ONU qinq， 需要配置qinqprf和svlan_service
                    'svlan_service': {},       # ONU 业务模式为FE，并且使能了svlan,即使能ONU qinq， 需要配置qinqprf和svlan_service
                },
                'wan_static': {'ip': '', 'mask': '', 'gate': '', 'dns_m': '', 'dns_s': ''},  # 如果业务类型为wan_static,需要增加该字段
                'lan': [1],
                'wlan': ['ssid1'],
                'oltqinq': [                  # olt qinq
                    {
                        'upRule': [
                            (2, '000000000000', 5),       # ("filedid", "value", "condition"),
                        ],
                        'dwRule':[
                            (2, '000000000000', 5),  # ("filedid", "value", "condition"),
                        ],
                        'vlanrule':[
                            # ("l1oldvlan", "l1oldvlan_cos", "l1_action", "l1_newvlan", "l1_newvlancos", "l2oldvlan", "l2oldvlan_cos", "l2_action", "l2_newvlan", "l2_newvlancos"),
                            (100, 'null', 'translation', 201, 1, 'null', 'null', 'add', 2701, 1),
                        ]
                    },
                ],
                'rate_limit':"",
            },
            {
                'type': 'wan_dhcp',        # fe, wan_dhcp, wan_pppoe, wan_static, veip
                'mode': 'transparent',
                'vlan': {
                    'cvlan': (1001, 3),          # cvlan, (cvid, cos)
                    # 'tvlan': (1101, 4),       # tvlan, (tvid, tcos)
                    # 'svlan': (2000, 4),        # onu qinq:(svlan, scos)
                    # 'qinqprf': {},            # ONU 业务模式为FE，并且使能了svlan,即使能ONU qinq， 需要配置qinqprf和svlan_service
                    # 'svlan_service':{},       # ONU 业务模式为FE，并且使能了svlan,即使能ONU qinq， 需要配置qinqprf和svlan_service
                },
                # 'wan_static": {'ip': '', 'mask':'', 'gate':'', 'dns_m': '', 'dns_s': ''} # 如果业务类型为wan_static,需要增加该字段
                'lan': [],
                'wlan': ['ssid2'],
            },
        ],

        'iptv': {
            'type': 'fe',        # 端口业务方式
            'multicast': {       # 组播流业务
                'mode': 'tag',
                "vlan": {
                    'cvlan': (110, 4),
                    # 'tvlan': (1110, 4),               # tvlan, (tvid, tcos)
                    # 'svlan':(2000, 4, 'FHMDU', 'data'),      # 'qinq':(svlan, scos, qinqprf, svlan_service)
                },
            },
            'unicast': {        # 单播业务，组播协议
                'mode': 'tag',
                "vlan": {
                    'cvlan': (111, 4),
                    # 'tvlan': (1111, 4),
                },
            },
            'lan': [2, 3, 4],
        },

        'voip': {}
    },
    # 业务模型1
    "m1": {
        'internet': [
            {
                'type': 'wan_pppoe',        # fe, wan_dhcp, wan_pppoe, wan_static, veip
                'mode': 'tag',
                'vlan': {
                    'cvlan': (1000, 3),  # ,      # cvlan, (cvid, cos)
                },

                'lan': [1],
                'wlan': ['ssid1'],
            },
        ],

        'iptv': {           # 组播
            'type': 'fe',        # 端口业务方式
            'multicast': {
                    'mode': 'tag',
                    "vlan": {
                        'cvlan': (3049, 4),
                    },
            },
            'unicast': {
                'mode': 'tag',
                "vlan": {
                    'cvlan': (3048, 4),
                },
            },
            'lan': [4],
        },
        'voip': {}
    },
    # 业务模型 2
    "m2": {
        'internet': [
            {
                'type': 'wan_pppoe',        # fe, wan_dhcp, wan_pppoe, wan_static, veip
                'mode': 'tag',
                'vlan': {
                    'cvlan': (1000, 3),  # ,      # cvlan, (cvid, cos)
                },
                'lan': [3],
                'wlan': ['ssid1'],
            },

            {
                'type': 'fe',        # fe, wan_dhcp, wan_pppoe, wan_static, veip
                'mode': 'tag',
                'vlan': {
                    'cvlan': (1010, 4),  # ,      # cvlan, (cvid, cos)
                },

                'lan': [2],
                'wlan': [],
            },
        ],
        'iptv': {
            'type': 'fe',        # 端口业务方式
            'multicast': {
                'mode': 'tag',
                "vlan": {
                    'cvlan': (110, 4),
                },
            },
            'unicast': {
                'mode': 'tag',
                "vlan": {
                    'cvlan': (111, 4),
                    # 'tvlan': (1111, 4),
                },
            },
            'lan': [4],
        },
        'voip': {}
    },

    "m3": {
        'internet': [
            {
                'type': 'wan_pppoe',        # fe, wan_dhcp, wan_pppoe, wan_static, veip
                'mode': 'transparent',
                'vlan': {
                    'cvlan': (1000, 3),      # cvlan, (cvid, cos)
                },
                'lan': [1],
                'wlan': ['ssid1']
            },
        ],
        'iptv': {
            'type': 'fe',        # 端口业务方式
            'multicast': {
                'mode': 'tag',
                "vlan": {
                    'cvlan': (110, 4),
                },
            },
            'unicast': {
                'mode': 'tag',
                "vlan": {
                    'cvlan': (111, 4),
                },
            },
            'lan': []
        },
        'voip': {}
    },
}
