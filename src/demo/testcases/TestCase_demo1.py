# -*- encoding: utf-8 -*-
''' 
@File    : TestCase_demo1.py
@Date    : 2020/07/13 15:37:04
@Author  : Teddy.tu
@Version : V1.0
@EMAIL   : teddy_tu@126.com
@License : (c)Copyright 2019-2020, Teddy.tu
@Desc    : 
    测试步骤：
    1. OLT公用配置（可多个用例公用同一个, 或者已有预配置，可不考虑）
    2. 连接仪表，占用仪表端口
    3. 创建/加载 仪表配置
    4. OLT业务配置（后续可增加回读验证业务配置)
    5. 仪表发送流量,验证业务是否正常。（单播，组播，协议等）
    6. OLT，ONU的操作（测试用例测试的目的）
    7. 验证业务是否正常，流量是否正常
    8. 如有多个/多次操作，重复步骤6~7
    9. 测试结束，断流，断开仪表，（清空OLT业务配置，可选）
    10.返回测试结果（FASS，Failed)
'''

import time
import os
import sys
import traceback
try:
    print("sys path", os.getcwd())
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
        
    from lib import settings
    #
    settings.TESTCASE_PATH = "/".join(__file__.split("/")[:-2])
    settings.LOG_PATH = "/".join(__file__.split("/")[:-2]) + "/log"
    settings.CAP_PATH = "/".join(__file__.split("/")[:-2]) + "/capture"
    
    from lib.oltlib import fhlib
    from lib.oltlib.fhat import FH_OLT
    from lib.stclib.fhstc import FHSTC
    from lib.public.fhlog import logger
except Exception as err:
    print(__name__ +"导入模块异常")
    print(err)

TC_RET = "PASSED"  # 测试结果, 默认为PASSED

# 初始化测试环境
# init(__file__)

fhstc = FHSTC(settings.STCIP)


def waitTime(t):
    for i in range(t, 0, -1):
    # print("\r", "倒计时{}秒！".format(i), end="", flush=True)
        logger.info("倒计时{}秒！".format(i))
        time.sleep(1)

def tc_connect_stc():
    logger.info("初始化仪表端口...")
    ports = dict(settings.UPLINK_PORTS)
    ports.update(settings.ONU_PORTS)

    # fhstc.stc_init()
    # fhstc.stc_connect()
    # fhstc.stc_createProject()
    # fhstc.stc_createPorts(**ports)
    # fhstc.stc_loadFromXml()
    fhstc.stc_autoAttachPorts()


def tc_traffic_config():
    dw_1_1 = dict()
    dw_1_1["srcMac"] = "00:00:01:00:00:01"
    dw_1_1["dstMac"] = "00:01:94:00:00:01"
    # dw_1_1["svlan"] = (20, 1)
    dw_1_1["cvlan"] = (2011, 7)
    dw_1_1["IPv4"] = ("10.10.10.10", "20.20.20.20", "10.10.10.1")
    # fhstc.stc_createTrafficRaw('dw_1_1', 'uplink', **dw_1_1)
    # fhstc.stc_createTrafficRaw(
    #     'dw_1_2', 'uplink', cvlan=(2011, 5),
    #     srcMac="00:00:00:01:01:02", dstMac="00:01:94:00:01:02")

    # onu1_up1 = "up_1_1"
    up_1_1 = dict()
    up_1_1["srcMac"] = "00:01:94:00:00:01"
    up_1_1["dstMac"] = "00:00:01:00:00:01"
    # onu_up['svlan'] = (20, 1)
    up_1_1["cvlan"] = (2011, 7)
    up_1_1["IPv4"] = ("10.10.10.10", "20.20.20.20", "10.10.10.1")
    # fhstc.stc_createTrafficRaw('up_1_1', 'onu1', **up_1_1)
    stream_count = 10
    for count in range(1, stream_count+1):
        fhstc.stc_createRawTraffic(
            'uplink', 'dw_1_%d' % count,  cvlan=(2012, 5),
            srcMac="00:00:00:01:01:%0X" % count, dstMac="00:01:94:00:01:%0X" % count, Load=1)
        fhstc.stc_createRawTraffic(
           'onu1', 'up_1_%d' % count,  cvlan=(2012, 5),
            dstMac="00:00:00:01:01:%0X" % count, srcMac="00:01:94:00:01:%0X" % count, Load=2)


def tc_creatDHCPDevice():
    fhstc.stc_createDHCPv4Client('onu1', 'client', srcMAC="00:00:00:00:00:02", cvlan=(102,1), svlan=(2001,4), count=1, ipv4=("192.18.10.1", "192.18.10.1"))
    fhstc.stc_createDHCPv4Server('uplink', 'server', srcMAC="00:00:00:00:00:01", cvlan=(102,1), svlan=(2001,4), count=1, ipv4=("192.168.20.1", "192.168.20.1"), pool=("192.168.20.2", 24, 200))
    
    fhstc.stc_createBoundTraffic("DHCP_client", 'client', 'server', 'dhcp')
    fhstc.stc_createBoundTraffic("DHCP_server", 'server', 'client', 'dhcp')
    fhstc.stc_apply()
    fhstc.stc_saveAsXML('DHCP.xml')
    # fhstc.stc_deviceStart('server')
    fhstc.stc_startDHCPv4Server('server')
    fhstc.stc_DHCPv4Bind('client')
    waitTime(5)
    fhstc.stc_getDHCPv4BlockResult('client')
    fhstc.stc_dhcpv4SessionResults('client')
    fhstc.stc_streamBlockStart("DHCP_client")
    fhstc.stc_streamBlockStart("DHCP_server")
    waitTime(5)
    tc_get_result()
    fhstc.stc_DHCPv4Release('client')
    waitTime(5)
    fhstc.stc_getDHCPv4BlockResult('client')
    waitTime(3)
    fhstc.stc_stopDHCPv4Server('server')


def tc_createPPPoEdevice():
    fhstc.stc_createPPPoEv4Client('onu1', 'client', srcMAC="00:00:00:00:00:02", cvlan=(102,1), svlan=(2001,4), count=10, ipv4=("192.18.10.1", "192.18.10.1"))
    fhstc.stc_createPPPoEv4Server('uplink', 'server', srcMAC="00:00:00:00:00:01", cvlan=(102,1), svlan=(2001,4), count=10, ipv4=("192.168.20.1", "192.168.20.1"), pool=("192.168.20.1", '192.168.20.2', 24))
    fhstc.stc_createBoundTraffic("pppoe_client", 'client', 'server', 'pppoe')
    fhstc.stc_createBoundTraffic("pppoe_server", 'server', 'client', 'pppoe')
    fhstc.stc_apply()
    fhstc.stc_PPPoEv4Connect('client')
    fhstc.stc_PPPoEv4Connect('server')
    waitTime(3)
    fhstc.stc_getPPPoEClientStatus("client")
    fhstc.stc_streamBlockStart("pppoe_client")
    fhstc.stc_streamBlockStart("pppoe_server")
    waitTime(5)
    tc_get_result()
    

def tc_createIGMPdeveice():
    fhstc.stc_createIGMPClient('onu1', 'client', srcMAC="00:00:00:00:00:02", cvlan=(102,1), svlan=(2001,4), count=1, ipv4=("192.18.10.1", "192.18.10.1", 24), version=2, membership='225.0.0.1')
    fhstc.stc_createIGMPServer('uplink', 'server', srcMAC="00:00:00:00:00:01", cvlan=(102,1), svlan=(2001,4), count=1, ipv4=("192.168.20.1", "192.168.20.1", 24), query=100, robustnesss=1, lastQuery=1)
    fhstc.stc_createTrafficRaw('uplink', 'igmp1', dstMac='01:00:5e:00:00:01', cvlan=(102,1), svlan=(2002,5), IPv4=("10.185.10.1", "225.0.0.1","10.185.10.1"))
    fhstc.stc_apply()
    fhstc.stc_saveAsXML("igmp.xml")
    fhstc.stc_streamBlockStart('igmp1')
    tc_get_result()
    fhstc.stc_streamBlockStop('igmp1')

def tc_generatorConfig():
    fhstc.stc_generatorConfig('uplink')
    fhstc.stc_generatorConfig('onu1')
    # fhstc.stc_generatorConfig('onu2')
    fhstc.stc_apply()


def tc_service_config():
    russiaOLT = FH_OLT()
    russiaOLT.connect_olt()
    cmds = []
    slot, pon, onu = settings.ONU['onu1']
    # cmds += fhlib.OLT_V4_RUSSIA.reboot_onu(slot, pon, onu)
    russiaOLT.sendcmdlines(fhlib.OLT_V4_RUSSIA.reboot_onu(*settings.ONU['onu1']))
    # cmds += fhlib.OLT_V4_RUSSIA.del_onu_lan_service((*settings.ONU['onu1'], 2), 'all')

    # cmds += fhlib.OLT_V4_RUSSIA.cfg_onu_lan_service((18, 16, 1, 2), 2012,
    #                                                 255, fhlib.SericeType.UNICAST, fhlib.VLAN_MODE.TRANSPARENT)
    russiaOLT.sendcmdlines(cmds)
    russiaOLT.disconnet_olt()


def tc_capture_start():
    fhstc.stc_captureStart('uplink')
    fhstc.stc_captureStart('onu1')


def tc_capture_stop():
    # print(fhstc.stc_captureStop('uplink', "/".join(__file__.split("/")[:-2]) + '/capture/uplink.pacp'))
    # print(fhstc.stc_captureStop('onu1', "/".join(__file__.split("/")[:-2]) + '/capture/onu1.pacp'))
    print("capture stop...")
    print(fhstc.stc_captureStop('onu1', 'onu1.pacp'))


def tc_traffic_start():
    fhstc.stc_DRVConfig(LimitSize=100)
    fhstc.stc_generator_start()
    # fhstc.stc_generator_start('uplink')
    # fhstc.stc_streamBlockStart('up_1_1')
    # fhstc.stc_streamBlockStart('up_2_1')


def tc_traffic_clear():
    time.sleep(5)
    # fhstc.stc_ClearAllResults('uplink')
    # fhstc.stc_ClearAllResults('onu1')
    fhstc.stc_ClearAllResults()


def tc_get_result():
    result = fhstc.stc_get_DRV_ResulstData()
    for key in result:
        traffic_result = result[key]
        tx, rx = tuple(map(int, traffic_result[2:4]))
        if abs(1 - rx / tx) > 0.05:
            global TC_RET
            TC_RET = "Failed"


def tc_get_DataSetResult():
    print("dataSet")
    fhstc.stc_get_ResultDataSet()


def tc_traffic_stop():
    print("traffic stop")
    fhstc.stc_generator_stop('uplink')
    fhstc.stc_streamBlockStop('up_1_1')
    # fhstc.stc_streamBlockStop('up_2_1')


def tc_traffic_disconnect():
    fhstc.stc_release()
    # fhstc.stc_release('uplink')
    # fhstc.stc_release('onu1')
    fhstc.stc_disconnect()


def tc_main():
    try:
        logger.info("step 1. connect STC...")
        tc_connect_stc()
        # logger.info("STC traffic config...")
        tc_traffic_config()
        # tc_creatDHCPDevice()
        fhstc.stc_saveAsXML()
        # tc_generatorConfig()
        tc_capture_start()
        logger.info("start traffic....")
        tc_traffic_start()
        tc_traffic_clear()
        logger.info("get traffic result")
        tc_get_result()
        tc_get_DataSetResult()

        logger.info("Service config...")
        # tc_service_config()
        # logger.info("延时60s")
        # time.sleep(60)
        # logger.info("get traffic result")
        # tc_get_result()

        logger.info("stop traffic...")
        tc_traffic_stop()
        tc_capture_stop()
        logger.info("release ports and disconnet stc.")
        tc_traffic_disconnect()

    except:
        logger.error("用例执行失败")
        global TC_RET
        TC_RET = "Failed"
    else:
        logger.info("用例执行成功")
    finally:
        logger.info("\n=======Result=========\n{:^20}\n======================".format(TC_RET))
    # logger.info("%s用例执行完成" % __name__)


def capture_analaye():
    pcap = r'E:/FHATP/fhprojects/capture/capture.pcap'
    display_filter = 'vlan.id==22'
    fhstc.package_analyze(pcap, display_filter)

def dhcp_test():
    logger.info("DHCP test...")
    tc_connect_stc()
    # tc_capture_start()
    # logger.info("STC traffic config...")
    # tc_traffic_config()
    tc_creatDHCPDevice()
    # tc_capture_stop()
    # fhstc.stc_saveAsXML("/".join(__file__.split("/")[:-2]) + '/instruments/DHCP.xml')
   

def PPPoe_test():
    logger.info("DHCP test...")
    tc_connect_stc()
    # tc_capture_start()
    # logger.info("STC traffic config...")
    # tc_traffic_config()
    tc_createPPPoEdevice()
    # tc_capture_stop()
    fhstc.stc_saveAsXML('pppoe.xml')
    fhstc.stc_PPPoEv4Connect('server')
    fhstc.stc_PPPoEv4Connect('client')
    time.sleep(5)
    print(fhstc.stc_getPPPoEServerStatus('server'))
    print(fhstc.stc_getPPPoEClientStatus('client'))
    fhstc.stc_PPPoEv4Disconnect('server')
    fhstc.stc_PPPoEv4Disconnect('client')
    print(fhstc.stc_getPPPoESimpleResult('server'))
    print(fhstc.stc_getPPPoESimpleResult('client'))
    # tc_capture_start()

if __name__ == "__main__":
    # tc_service_config()
    # tc_main()
    # print(sys.argv)
    if len(sys.argv) > 1:
        if sys.argv[1] == 'dhcp':
            dhcp_test()
            tc_traffic_disconnect()
          
        if sys.argv[1] == 'pppoe':
            PPPoe_test()
            tc_traffic_disconnect()
           
        if sys.argv[1] == 'igmp':
            tc_createIGMPdeveice()
            tc_traffic_disconnect()
        if sys.argv[1] == 'load':
            fhstc.stc_loadFromXml('DHCP.xml')
    else:
        dhcp_test()
        # tc_main()
    # capture_analaye()
    # print(__file__)
    # path = __file__
    # path_s = path.split("/")
    # print(path_s[:-2])
    # print(settings.LOG_PATH)
    # settings.LOG_PATH = os.path.join("/".join(__file__.split("/")[:-2]), 'log')
    # print(settings.LOG_PATH)
