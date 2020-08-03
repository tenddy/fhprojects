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
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
        # print(sys.path)
    from lib import settings
    from lib.oltlib import fhlib
    from lib.oltlib.fhat import FH_OLT
    from lib.stclib.fhstc import FHSTC
    from lib.public.fhlog import logger
except Exception as err:
    print("导入模块异常")
    print(err)

TC_RET = "PASSED"  # 测试结果, 默认为PASSED

fhstc = FHSTC(settings.STCIP)


def tc_connect_stc():
    logger.info("初始化仪表端口...")
    ports = dict(settings.UPLINK_PORTS)
    ports.update(settings.ONU_PORTS)

    fhstc.stc_init()
    fhstc.stc_connect()
    fhstc.stc_createProject()
    fhstc.stc_createPorts(**ports)
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
        fhstc.stc_createTrafficRaw(
            'dw_1_%d' % count, 'uplink', cvlan=(2012, 5),
            srcMac="00:00:00:01:01:%0X" % count, dstMac="00:01:94:00:01:%0X" % count, Load=1)
        fhstc.stc_createTrafficRaw(
            'up_1_%d' % count, 'onu1', cvlan=(2012, 5),
            dstMac="00:00:00:01:01:%0X" % count, srcMac="00:01:94:00:01:%0X" % count, Load=2)


def tc_creatDevice():
    fhstc.stc_createBasicDevice("h1", 'uplink')
    fhstc.stc_createBasicDevice("h_up", 'onu1')
    fhstc.stc_apply()


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
    # fhstc.stc_captureStart('onu1')


def tc_capture_stop(path='./capture/capture1.pcap'):
    fhstc.stc_captureStop('uplink', path)
    # fhstc.stc_captureStop('onu1')


def tc_traffic_start():
    fhstc.stc_DRVConfig(LimitSize=100)
    fhstc.stc_generator_start()
    # fhstc.stc_generator_start('uplink')
    # fhstc.stc_streamBlockStart('up_1_1')
    # fhstc.stc_streamBlockStart('up_2_1')


def tc_traffic_clear():
    time.sleep(5)
    fhstc.stc_ClearAllResults('uplink')
    fhstc.stc_ClearAllResults('onu1')
    # fhstc.stc_ClearAllResults('onu2')


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
        # tc_creatDevice()
        fhstc.stc_saveAsXML()
        tc_generatorConfig()
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


if __name__ == "__main__":
    # tc_service_config()
    tc_main()
    # capture_analaye()
