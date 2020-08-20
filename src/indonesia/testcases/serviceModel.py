#!/usr/bin/env python
# coding=UTF-8
"""
###############################################################################
# @FilePath    : /fhat/src/indonesia/testcases/serviceModel.py
# @Author      : ddtu
# @Version     : V1.0
# @EMAIL       : ddtu@fiberhome.com
# @License     : (c)Copyright 2019-2020, Fiberhome(ddtu)
# @Date        : 2020-08-17 08:03:03
# @LastEditors : ddtu
# @LastEditTime: 2020-08-17 08:03:41
# @Descption   : 根据ONU的业务模型，解析模型配置，生成ONU业务配置命令行，
#                并实现对应业务模型的验证方式
###############################################################################
"""
import random
from lib.public.fhTimer import waitTime
from lib.public.fhlog import logger
from lib.oltlib.oltv5 import AN6K
from lib.stclib.fhstc import FHSTC


def config_ONU_Serice(slotno, ponno, onu: dict, service_model: dict, mode=None):
    """配置ONU所有业务"""
    logger.info("配置ONU业务")
    logger.debug(onu)
    logger.debug(service_model)
    send_cmds = set_internet_service(slotno, ponno, onu, service_model)
    send_cmds += set_iptv_service(slotno, ponno, onu, service_model)
    return send_cmds


def set_internet_service(slotno, ponno, onu: dict, service_model: dict, service_type=None):
    """
    功能：
        配置ONU internet业务
    参数:
        @slotno: 槽位号
        @ponno: PON口号
        @onu: ONU基本信息及业务模型， Globals.SETTINGS['ONU']中对应的结构
        @service_model: onu业务模型，Globals.MODEL
        @ser_type: 配置的业务类型（fe, wan_dhcp, wan_pppoe, wan_static, veip）,
               默认None,下发所有业务类型
    返回值: 命令行列表
    """
    logger.info("配置ONU internet业务")
    logger.debug(onu)
    logger.info(service_model['internet'])
    onuid = onu['ONUID']
    if service_type is None:
        service_type = ('fe', 'wan_dhcp', 'wan_pppoe', 'wan_static', 'veip')
    send_cmds = []
    fe_cmds = {}        # FE业务配置
    wan_cmds = []       # WAN业务配置
    for internet in service_model['internet']:
        ser_type = internet['type']
        if ser_type not in service_type:
            continue

        if ser_type == 'fe':
            kargs = {}
            kargs['cvlan'] = (internet['mode'], *internet['vlan']['cvlan'])
            if 'tvlan' in internet['vlan']:
                kargs['translate'] = ('enable', *internet['vlan']['tvlan'])
            if 'svlan' in internet['vlan']:
                # 需要增加创建qinqprf 和 svlan_service
                kargs['qinq'] = (
                    'enable', *internet['vlan']['tsvlan'],
                    internet['vlan']['qinqprf'],
                    internet['vlan']['svlan_service'])
            for lan in internet['lan']:
                key = str(lan)
                if key not in fe_cmds.keys():
                    fe_cmds[key] = []
                fe_cmds[key].append(kargs)

        if ser_type == 'wan_dhcp' or ser_type == 'wan_pppoe' or ser_type == 'wan_static':
            wan_vid = internet['vlan']['cvlan']
            kargs = {}
            # tvlan
            if 'tvlan' in internet['vlan']:
                tvid, tcos = internet['vlan']['tvlan']
                kargs['vlanmode'] = {'mode': 'tag', 'tvlan': 'enable', 'tvid': tvid, 'tcos': tcos}
            # qinq
            if 'svlan' in internet['vlan']:
                svid, scos = internet['vlan']['svlan']
                kargs['qinq'] = ('enable', 33024, svid, scos)

            # lan & wlan
            ports = []
            for item in internet['lan']:
                ports.append('fe%d' % item)
            ports += internet['wlan']
            kargs['entries'] = ports

            if ser_type == 'wan_dhcp':
                dsp = {'mode': 'dhcp'}
            elif ser_type == 'wan_pppoe':
                dsp = {'mode': 'pppoe', 'username': 'fiberhome', 'password': 'fiberhome'}
            elif ser_type == 'wan_static':
                if 'dsp_static' not in internet:
                    logger.error(
                        "ONU配置wan_static, 需要增加dsp_static({ 'ip': '', 'mask':'', 'gate':'', 'dns_m': '', 'dns_s': ''})等参数的配置")
                else:
                    dsp = internet['dsp_static']
                    dsp['mode'] = 'static'
            else:
                logger.error("ONU 配置WAN业务模式，请配置（wan_dhcp,wan_pppoe,wan_static)字段中任意一个。")

            send_cmds += AN6K.onu_wan_service((slotno, ponno, onuid), len(wan_cmds) + 1, wan_vid, dsp, **kargs)

        # veip
        if ser_type == 'veip':
            pass

    for key in fe_cmds.keys():
        send_cmds += AN6K.onu_lan_service((slotno, ponno, onuid, key), fe_cmds[key], True)

    return send_cmds


def set_iptv_service(slotno, ponno, onu: dict, service_model: dict):
    """
    功能：
        配置ONU 组播业务
    参数:
        @slotno: 槽位号
        @ponno: PON口号
        @onu: ONU基本信息及业务模型， Globals.SETTINGS['ONU']中对应的结构
        @service_model: onu业务模型，Globals.MODEL
    返回值: 命令行列表
    """
    logger.info("配置ONU 组播业务")
    logger.debug(onu)
    logger.debug(service_model['iptv'])
    onuid = onu['ONUID']
    send_cmds = []
    iptv = service_model['iptv']
    if iptv['type'] == 'fe':
        lan_service = []
        if 'unicast' in iptv.keys():
            unicast = {}
            unicast['cvlan'] = (iptv['unicast']['mode'], *iptv['unicast']['vlan']['cvlan'])
            # tvlan
            if 'tvlan' in iptv['unicast']:
                unicast['tvlan'] = ('enable', *iptv['unicast']['vlan']['tvlan'])
            # svlan
            if 'svlan' in iptv['unicast']:
                unicast['qinq'] = ('enable', *iptv['unicast']['vlan']['svlan'])
            lan_service.append(unicast)

        if 'multicast' in iptv.keys():
            multicast = {}
            multicast['cvlan'] = (iptv['multicast']['mode'], *iptv['multicast']['vlan']['cvlan'])
            # tvlan
            if 'tvlan' in iptv['multicast']:
                multicast['tvlan'] = ('enable', *iptv['multicast']['vlan']['tvlan'])
            # qinq
            if 'svlan' in iptv['multicast']:
                multicast['qinq'] = ('enable', *iptv['multicast']['vlan']['svlan'])
            multicast['multicast'] = True
            lan_service.append(multicast)

        for portid in iptv['lan']:
            send_cmds += AN6K.onu_lan_service((slotno, ponno, onuid, portid), lan_service, True)

    # veip
    if iptv['type'] == 'veip':
        pass

    return send_cmds


def set_voip_service():
    """配置ONU 语音业务"""
    pass


def verifyFEService(stc: FHSTC, stc_uplink, stc_onu, uplink_vlan: dict, onu_vlan: dict, onuinfo: dict, **kargs):
    """
    功能：
        FE 业务验证
    参数：
        @stc: FHSTC对象
        @stc_uplink: 上联仪表端口名称
        @stc_onu: ONU仪表端口名称
        @uplink_vlan: 上联仪表端口的VLAN配置，格式为{'svlan':(100, 7), 'cvlan':(1000, 255)} 或者 None（不配置VLAN）
        @onu_vlan: ONU 仪表端口 VLAN配置,格式为{'svlan':(100, 7), 'cvlan':(1000, 255)} 或者 None（不配置VLAN）
        @onuinfo：（slotno, ponno, onuno)
        @**kargs:
            stop: 测试完成之后是否停止本次测试的device和数据，默认False-不停止，True-停止
            threshold: 流量验证阈值，默认0.05
            filterStream:  过滤需要验证的数据流，默认是只验证当前PPPoE的数据流，all-所有数据流
            repeat: 重复验证次数，默认值1
            serviceType: 验证FE端口业务方式（raw,dhcp,pppoe），默认是raw
    返回值：业务验证结果
    说明：
    """
    logger.info("FE 端口业务验证")
    slotno, ponno, onuid = tuple(map(int, onuinfo))
    stream_dw = 'stream_dw_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
    stream_up = 'stream_up_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
    device_dw = 'device_dw_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
    device_up = 'device_up_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)

    srcMac = "00:02:{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}".format(slotno, ponno, onuid, random.randint(1, 255))
    dstMac = "00:95:{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}".format(slotno, ponno, onuid, random.randint(1, 255))
    ip_r = random.randint(10, 200)
    srcIPv4 = "10.180.%d.2" % ip_r
    dstIPv4 = "10.180.%d.100" % ip_r

    dw_param = dict()
    dw_param["srcMac"] = srcMac
    dw_param["dstMac"] = dstMac
    if 'svlan' in uplink_vlan.keys():
        dw_param['svlan'] = uplink_vlan['svlan']
    if 'cvlan' in uplink_vlan.keys():
        dw_param['cvlan'] = uplink_vlan['cvlan']
    dw_param["ipv4"] = (srcIPv4, dstIPv4, srcIPv4)

    up_param = dict()
    up_param["srcMac"] = dstMac
    up_param["dstMac"] = srcMac
    if 'svlan' in onu_vlan.keys():
        up_param['svlan'] = onu_vlan['svlan']
    if 'cvlan' in onu_vlan.keys():
        up_param['cvlan'] = onu_vlan['cvlan']
    up_param["ipv4"] = (dstIPv4, srcIPv4, dstIPv4)

    serviceType = kargs['serviceType'] if 'serviceType' in kargs.keys() else 'raw'
    if serviceType == 'raw':
        if stream_dw not in stc._hStreamBlock:
            stc.stc_createRawTraffic(stc_uplink, stream_dw, **dw_param)
        if stream_up not in stc._hStreamBlock:
            stc.stc_createRawTraffic(stc_onu, stream_up, **up_param)
    elif serviceType == 'pppoe':
        device_dw = 'pppDevice_dw_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
        device_up = 'pppDevice_up_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
        pppServerIP = srcIPv4
        ppp_pool = dstIPv4
        dw_param['ipv4'] = (pppServerIP, ppp_pool)
        dw_param['pool'] = (ppp_pool, 24)
        stc.stc_createPPPoEv4Server(stc_uplink, device_dw, **dw_param)

        up_param['ipv4'] = ("10.180.100.10", pppServerIP)
        stc.stc_createPPPoEv4Client(stc_onu, device_up, **up_param)

        # 创建绑定流
        stc.stc_createBoundTraffic(stream_dw, device_dw, device_up, 'pppoe')
        stc.stc_createBoundTraffic(stream_up, device_up, device_dw, 'pppoe')

    else:
        device_dw = 'dhcpDevice_dw_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
        device_up = 'dhcpDevice_up_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
        dw_param['ipv4'] = (srcIPv4, dstIPv4)
        dw_param['pool'] = (dstIPv4, 24, 10)
        stc.stc_createDHCPv4Server(stc_uplink, device_dw, **dw_param)

        up_param['ipv4'] = ('10.10.10.10', srcIPv4)
        up_param['broadcast'] = False
        stc.stc_createDHCPv4Client(stc_onu, device_up, **up_param)

        # 创建绑定流
        stc.stc_createBoundTraffic(stream_dw, device_dw, device_up, 'dhcp')
        stc.stc_createBoundTraffic(stream_up, device_up, device_dw, 'dhcp')

    stc.stc_apply()
    stc.stc_saveAsXML("fe.xml")

    if serviceType == "dhcp":
        stc.stc_startDHCPv4Server(device_dw)
        waitTime(5)
        stc.stc_DHCPv4Bind(device_up)
        waitTime(10)
        dhcp_ret = stc.stc_dhcpv4SessionResults(device_up)
        logger.info(dhcp_ret)
        for dhcp in dhcp_ret:
            if dhcp[0] == 'Bound':
                logger.info("DHCP连接成功，验证数据流")
            else:
                logger.error("DHCP 连接失败")
                return False

    if serviceType == "pppoe":
        stc.stc_PPPoEv4Connect(device_dw)
        waitTime(3)
        stc.stc_PPPoEv4Connect(device_up)
        waitTime(10)
        pppoe_ret = stc.stc_getPPPoEClientStatus(device_up)
        if pppoe_ret['SessionState'] == "CONNECTED":
            logger.info("PPPoE连接成功，验证数据流")
            # stc.stc_startStreamBlock(stream_up, arp=True)
            # stc.stc_startStreamBlock(stream_dw, arp=True)
        else:
            logger.error("PPPoE 连接失败")
            return False

    # 验证的数据流是否正常
    stc.stc_startStreamBlock(stream_up, arp=True)
    stc.stc_startStreamBlock(stream_dw, arp=True)
    waitTime(5)
    if 'filterStream' in kargs.keys():
        filter_param = None if kargs['filterStream'] == 'all' else kargs['filterStream']
    else:
        filter_param = (stream_dw,  stream_up)
    logger.debug("filter:{}".format(filter_param))
    result = stc.stc_get_DRV_ResulstData(streamNames=filter_param)
    for key in result:
        traffic_result = result[key]
        tx, rx = tuple(map(int, traffic_result[:2]))
        threshold = kargs['threshold'] if 'threshold' in kargs.keys() else 0.05
        if (abs(tx - rx) / (tx + 0.00001)) > threshold:
            logger.error("数据流(%s)异常" % key)
            return False

    if 'stop' in kargs.keys() and kargs['stop']:
        stc.stc_stopStreamBlock(stream_up)
        stc.stc_stopStreamBlock(stream_dw)
        if serviceType == 'dhcp' or serviceType == 'pppoe':
            stc.stc_stopDevice(device_dw)
            stc.stc_stopDevice(device_up)

    return True


def verifyPPPoEWanService(stc: FHSTC, stc_uplink, stc_onu, uplink_vlan: dict, onu_vlan: dict, onuinfo: dict, **kargs):
    """
    功能：
        PPPoE WAN 三层业务验证
    参数：
        @stc: FHSTC对象
        @stc_uplink: 上联仪表端口名称
        @stc_onu: ONU仪表端口名称
        @uplink_vlan: 上联仪表端口的VLAN配置，格式为{'svlan':(100, 7), 'cvlan':(1000, 255)} 或者 None（不配置VLAN）
        @onu_vlan: ONU 仪表端口 VLAN配置,格式为{'svlan':(100, 7), 'cvlan':(1000, 255)} 或者 None（不配置VLAN）
        @onuinfo：（slotno, ponno, onuno)
        @**kargs:
            stop: 测试完成之后是否停止本次测试的device和数据，默认False-不停止，True-停止
            threshold: 流量验证阈值，默认0.05
            filterStream:  过滤需要验证的数据流，默认是只验证当前PPPoE的数据流，all-所有数据流
            pppoeTimes: 重复验证次数，默认值1
            onuGate: ONU网关，默认192.168.1.1
    返回值：业务验证结果
    说明：
    """
    # 创建PPPoE 服务器
    # logger.info(onuinfo)
    slotno, ponno, onuid = tuple(map(int, onuinfo))
    logger.info("创建pppoE服务器配置...")
    pppoeDeviceName = 'pppwan_server_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
    pppServerMac = "00:01:{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}".format(slotno, ponno, onuid, random.randint(1, 255))

    service_param = {}
    service_param['srcMAC'] = pppServerMac
    if 'svlan' in uplink_vlan.keys():
        service_param['svlan'] = uplink_vlan['svlan']
    if 'cvlan' in uplink_vlan.keys():
        service_param['cvlan'] = uplink_vlan['cvlan']
    ip_r = random.randint(10, 200)
    pppServerIP = "10.185.%d.2" % ip_r
    ppp_pool = '10.185.%d.100' % ip_r
    service_param['ipv4'] = (pppServerIP, ppp_pool)
    service_param['pool'] = (ppp_pool, 24)
    logger.debug("device:{}".format(stc._hDevices))

    # 创建PPPoE server Device
    if pppoeDeviceName not in stc._hDevices.keys():
        stc.stc_createPPPoEv4Server(stc_uplink, pppoeDeviceName, **service_param)

    logger.info("创建下行三层数据流")
    pppoedwName = 'pppwan_dw_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
    traffic_param = {}
    traffic_param['srcMac'] = pppServerMac
    traffic_param['dstMac'] = "00:00:00:00:00:00"
    if 'svlan' in uplink_vlan.keys():
        traffic_param['svlan'] = uplink_vlan['svlan']
    if 'cvlan' in uplink_vlan.keys():
        traffic_param['cvlan'] = uplink_vlan['cvlan']
    traffic_param['pppoeSession'] = {}
    traffic_param['ipv4'] = (pppServerIP, ppp_pool, ppp_pool)
    udp_dw = (random.randint(1025, 49151), random.randint(1025, 49151))
    traffic_param['udp'] = udp_dw

    # 创建下行数据流
    if pppoedwName not in stc._hStreamBlock:
        stc.stc_createRawTraffic(stc_uplink, pppoedwName, **traffic_param)
    else:
        stc.stc_modifyTraffic(pppoedwName, **traffic_param)

    logger.info("创建上行三层数据流")
    up_traffic_param = {}
    pppoeupName = 'pppwan_up_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
    up_traffic_param['srcMac'] = "00:94:{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}".format(
        slotno, ponno, onuid, random.randint(1, 255))
    up_traffic_param['dstMac'] = pppServerMac
    if 'svlan' in onu_vlan.keys():
        up_traffic_param['svlan'] = onu_vlan['svlan']
    if 'cvlan' in onu_vlan.keys():
        up_traffic_param['cvlan'] = onu_vlan['cvlan']
    onugate = kargs['onuGate'] if 'onuGate' in kargs.keys() else '192.168.1.1'
    up_traffic_param['ipv4'] = ('192.168.1.%d' % random.randint(2, 199), pppServerIP, onugate)
    up_traffic_param['udp'] = tuple(reversed(udp_dw))
    if pppoeupName not in stc._hStreamBlock:
        stc.stc_createRawTraffic(stc_onu, pppoeupName, **up_traffic_param)
    else:
        stc.stc_modifyTraffic(pppoeupName, **traffic_param)

    stc.stc_apply()

    logger.info("业务验证")
    # pppoe_test_ret = True  # PPPoE 验证测试结果
    pppoe_test_times = 1   # 业务验证次数
    while pppoe_test_times > 0:     # 业务验证测试
        pppoe_test_times -= 1
        check_count = 0
        stc.stc_PPPoEv4Connect(pppoeDeviceName)
        pppoe_state = True  # PPPoe 需要重连标志位
        while pppoe_state and check_count < 3:
            logger.info("检查PPPoE是否连接成功")
            check_count += 1
            waitTime(20)
            result = stc.stc_getPPPoEServerStatus(pppoeDeviceName)
            logger.info(result)
            if result['SessionState'] == "CONNECTED":
                pppoe_state = False
                pppoes = {'sessionId': result['PppoeSessionId']}
                srcPort, dstPort = (random.randint(1025, 49151), random.randint(1025, 49151))
                stc.stc_modifyTraffic(pppoedwName, srcMac=result['MacAddr'], dstMac=result['PeerMacAddr'], pppoeSession=pppoes, IPv4=(
                    result['Ipv4Addr'], result['PeerIpv4Addr'], result['PeerIpv4Addr']), udp=(srcPort, dstPort))
                stc.stc_modifyTraffic(pppoeupName, udp=(dstPort, srcPort))
                logger.info("验证数据流")
                stc.stc_startStreamBlock(pppoeupName, arp=True)  # 必须先开始上行流，再开始下行流
                waitTime(3)
                stc.stc_startStreamBlock(pppoedwName, arp=True)
                waitTime(5)
                # 需验证的数据流
                if 'filterStream' in kargs.keys():
                    filter_param = None if kargs['filterStream'] == 'all' else kargs['filterStream']
                else:
                    filter_param = (pppoedwName, pppoeupName)
                logger.debug("filter:{}".format(filter_param))
                result = stc.stc_get_DRV_ResulstData(streamNames=filter_param)
                for key in result:
                    traffic_result = result[key]
                    tx, rx = tuple(map(int, traffic_result[:2]))
                    threshold = kargs['threshold'] if 'threshold' in kargs.keys() else 0.05
                    if (abs(tx - rx) / (tx + 0.00001)) > threshold:
                        logger.error("数据流(%s)异常" % key)
                        if 'stop' in kargs.keys() and kargs['stop']:
                            stc.stc_stopStreamBlock(pppoedwName)
                            stc.stc_stopStreamBlock(pppoeupName)
                            stc.stc_PPPoEv4Disconnect(pppoeDeviceName)
                        return False

        if pppoe_test_times > 0 or (pppoe_test_times == 0 and 'stop' in kargs.keys() and kargs['stop']):
            stc.stc_stopStreamBlock(pppoedwName)
            stc.stc_stopStreamBlock(pppoeupName)
            stc.stc_PPPoEv4Disconnect(pppoeDeviceName)
            waitTime(5)

        if pppoe_state and check_count == 3:
            logger.error("pppoe 连接失败")
            return False

    stc.stc_saveAsXML("pppoe_wan.xml")
    logger.info("pppoe WAN 业务验证通过！")
    return True


def wan_ratelimit(stc: FHSTC, wanType, onuinfo, ratelimit, load=None, **kargs):
    """
    功能：
        测试WAN业务三层限速
    参数：
        @stc: FHSTC对象
        @wanType: 三层业务类型，pppoe，dhcp，static
        @onuinfo：（slotno, ponno, onuno)
        @ratelimit(tuple): 上下行限速速率(kb)
        @load(tuple):上下行仪表打流速率（Mb）,默认都是100Mb
        @**kargs:
            stop: 测试完成之后是否停止本次测试的device和数据，默认False-不停止，True-停止
            threshold: 流量验证阈值，默认0.05
    返回值：None
    说明：
        测试wan_ratelimit, 需要先verifyPPPoEWanService
    """
    if wanType == "pppoe":
        pppoeupName = 'pppwan_up_{:0>2}{:0>2}{:0>3}'.format(*onuinfo)
        pppoedwName = 'pppwan_dw_{:0>2}{:0>2}{:0>3}'.format(*onuinfo)
    elif wanType == "dhcp":
        pppoeupName = 'dhcpwan_up_{:0>2}{:0>2}{:0>3}'.format(*onuinfo)
        pppoedwName = 'dhcpwan_dw_{:0>2}{:0>2}{:0>3}'.format(*onuinfo)
    else:
        pppoeupName = 'staticwan_up_{:0>2}{:0>2}{:0>3}'.format(*onuinfo)
        pppoedwName = 'staticwan_dw_{:0>2}{:0>2}{:0>3}'.format(*onuinfo)

    if load is not None:
        logger.info("修改数据流大小")
        up_load, dw_load = load
        stc.stc_stopStreamBlock(pppoeupName)
        stc.stc_stopStreamBlock(pppoedwName)
        stc.stc_modifyTraffic(pppoeupName, Load=up_load)
        stc.stc_modifyTraffic(pppoedwName, Load=dw_load)
        waitTime(10)
        stc.stc_apply()

    logger.info("验证限速结果")
    # up_limit, dw_limit = ratelimit
    rate_limit = dict(zip((pppoeupName, pppoedwName), ratelimit))
    stc.stc_startStreamBlock(pppoeupName, arp=True)
    stc.stc_startStreamBlock(pppoedwName, arp=True)
    waitTime(10)
    filter_param = (pppoedwName, pppoeupName)
    logger.debug("filter:{}".format(filter_param))
    result = stc.stc_get_DRV_ResulstData(streamNames=filter_param)
    traffic_result = {}
    for key in result:
        streamName = key.split(".")[1]
        traffic_result[streamName] = result[key][5]
        threshold = kargs['threshold'] if 'threshold' in kargs.keys() else 0.05
        tx, rx = int(traffic_result[streamName]), rate_limit[streamName] * 1000
        print(tx, rx, abs(tx - rx) / (rx + 0.00001))
        if (abs(tx - rx) / (rx + 0.00001)) > threshold:
            logger.error("三层限速测试正常,业务类型：{}，数据流{}, 限速值{}".format(wanType, key, rx))
            if 'stop' in kargs.keys() and kargs['stop']:
                stc.stc_stopStreamBlock(pppoedwName)
                stc.stc_stopStreamBlock(pppoeupName)
            return False
    logger.info("三层限速测试正常,业务类型：{}，限速值{}".format(wanType, ratelimit))
    return True


def verifyIGMPService(stc: FHSTC, stc_uplink, stc_onu, mvlan, onu_vlan, onuinfo, igmpgroup, **kargs):
    """
    功能：
        PPPoE WAN 三层业务验证
    参数：
        @stc: FHSTC对象
        @stc_uplink: 上联仪表端口名称
        @stc_onu: ONU仪表端口名称
        @mvlan: 上联仪表端口IGMP组播服务器vlan，格式为{'svlan':(100, 7), 'cvlan':(1000, 255)} 或者 {}（不配置VLAN）
        @onu_vlan: ONU 仪表端口 VLAN配置,格式为{'svlan':(100, 7), 'cvlan':(1000, 255)} 或者 {}（不配置VLAN）
        @onuinfo：（slotno, ponno, onuno)
        @igmpgroup(str): 组播组,"225.0.0.1" 或者 "225.0.0.6-225.0.0.10"
        @**kargs:
            stop: 测试完成之后是否停止本次测试的device和数据，默认False-不停止，True-停止
            threshold: 流量验证阈值，默认0.05
            filterStream: 过滤需要验证的数据流，默认是只验证当前PPPoE的数据流，all-所有数据流
    返回值：业务验证结果
    说明：
    """
    slotno, ponno, onuid = tuple(map(int, onuinfo))
    logger.info("IGMP服务器配置...")
    igmpServerName = "igmpServer_{:0>2}{:0>2}{:0>3}".format(slotno, ponno, onuid)
    server = {}
    server['srcMAC'] = "00:{:0>2X}:{:0>2X}:{:0>2X}:5e:{:0>2X}".format(slotno, ponno, onuid, random.randint(1, 255))
    if 'svlan' in mvlan.keys():
        server['svlan'] = mvlan['svlan']
    if 'cvlan' in mvlan.keys():
        server['cvlan'] = mvlan['cvlan']
    server_ipv4 = '10.94.50.%d' % random.randint(2, 199)
    server['ipv4'] = (server_ipv4, server_ipv4, 24)
    stc.stc_createIGMPServer(stc_uplink, igmpServerName, **server)

    logger.info("IGMP客户端配置...")
    igmpClientName = "igmpClient_{:0>2}{:0>2}{:0>3}".format(slotno, ponno, onuid)
    client = {}
    client['srcMAC'] = "00:00:{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}".format(
        slotno + 94, ponno + 94, onuid + 94, random.randint(1, 255))
    if 'svlan' in onu_vlan.keys():
        client['svlan'] = onu_vlan['svlan']
    if 'cvlan' in onu_vlan.keys():
        client['cvlan'] = onu_vlan['cvlan']

    client_ipv4 = '10.94.28.%d' % random.randint(2, 199)
    client['ipv4'] = (client_ipv4, client_ipv4, 24)
    groups = igmpgroup.split("-")
    if len(groups) == 1:
        client['membership'] = groups[0]
    else:
        startIP = list(map(int, groups[0].split(".")))
        start_val = startIP[0]*256*256*256 + startIP[1]*256*256 + startIP[2]*256 + startIP[3]
        endIP = list(map(int, groups[1].split(".")))
        end_val = endIP[0]*256*256*256 + endIP[1]*256*256 + endIP[2]*256 + endIP[3]
        client['membership'] = (groups[0], 1, end_val-start_val+1, 32)

    stc.stc_createIGMPClient(stc_onu, igmpClientName, **client)

    # 创建组播流
    igmpStreamName = "igmpStream_{:0>2}{:0>2}{:0>3}".format(slotno, ponno, onuid)
    # stc.stc_createRawTraffic(stc_uplink, 'igmp1', dstMac='01:00:5e:00:00:01', cvlan=(
    #     102, 1), svlan=(2002, 5), IPv4=("10.185.10.1", "225.0.0.1", "10.185.10.1"))
    stc.stc_createBoundTraffic(igmpStreamName, igmpServerName, igmpClientName, protocol='igmp')
    stc.stc_apply()
    stc.stc_saveAsXML("igmp.xml")

    # 组播业务流验证
    stc.stc_startDevice(igmpServerName)
    stc.stc_startStreamBlock(igmpStreamName)
    waitTime(3)
    logger.info("加入组播组")
    stc.stc_igmpJoin(igmpClientName)
    waitTime(5)

    # 过滤需验证的数据流
    if 'filterStream' in kargs.keys():
        filter_param = None if kargs['filterStream'] == 'all' else kargs['filterStream']
    else:
        filter_param = (igmpStreamName,)
    logger.debug("filter:{}".format(filter_param))
    result = stc.stc_get_DRV_ResulstData(streamNames=filter_param)
    for key in result:
        traffic_result = result[key]
        tx, rx = tuple(map(int, traffic_result[:2]))
        threshold = kargs['threshold'] if 'threshold' in kargs.keys() else 0.05
        if (abs(tx - rx) / (tx + 0.00001)) > threshold:
            logger.error("数据流(%s)异常" % key)
            return False

    if 'stop' in kargs.keys() and kargs['stop']:
        stc.stc_igmpLeave(igmpClientName)
        stc.stc_stopStreamBlock(igmpStreamName)
        stc.stc_stopDevice(igmpServerName)

    return True
