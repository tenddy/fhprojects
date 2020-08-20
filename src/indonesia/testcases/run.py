
import os
import sys
import traceback
import re
import random
from Globals import SETTINGS
from Globals import MODEL
from serviceModel import config_ONU_Serice
import serviceModel

from lib.oltlib.oltv5 import AN6K
from lib.oltlib.common import *
from lib.oltlib.fhat import FH_OLT
from lib.stclib.fhstc import FHSTC
from lib.public.fhlog import logger
from lib.public.fhTimer import waitTime
from lib.public.packet import AnalyzePacket

import tc1
import tc3


class Indonesia_TC():
    def __init__(self):
        self._tc_ret = True     # 测试结果
        self._slotno = SETTINGS["SLOTNO"]
        self._ponno = SETTINGS["PONNO"]
        self._olt = FH_OLT()
        self._olt.init_olt(**SETTINGS['OLT'])
        self._stc = None

    def init_stc(self):
        """初始化仪表"""
        self._stc = FHSTC()
        self._stc.stc_connect()

    def init_olt(self, unauthONU=True):
        """初始化OLT配置, 基于物理SN授权ONU"""
        # 去授权已授权ONU
        if unauthONU:
            logger.info("去授权ONU")
            self._olt.connect_olt()
            authONUlist = self._olt.get_authorization_onu(self._slotno, self._ponno)
            for key in authONUlist.keys():
                self._olt.sendcmdlines(AN6K.unauth_onu(
                    ONUAuthType.PHYID, authONUlist[key][0],
                    authONUlist[key][1],
                    key))
                self._tc_ret &= self._olt.verify_cmds_exec()
            logger.info("授权待测ONU")
            for item in SETTINGS['ONU']:
                phyid = item['PHYID']
                onuid = int(item['ONUID'])
                self._olt.sendcmdlines(AN6K.authorize_onu(
                    ONUAuthType.PHYID, phyid, item['ONUTYPE'],
                    *(self._slotno, self._ponno, onuid)))
            self._olt.disconnet_olt()

        # 判断ONU是否能正常上线
        logger.info("验证待测试ONU是否可正常上线")
        online = 1
        while online > 0:
            online = len(SETTINGS['ONU'])   # 待测ONU个数
            self._olt.connect_olt()
            authONUlist = self._olt.get_authorization_onu(self._slotno, self._ponno)
            self._olt.disconnet_olt()
            for item in SETTINGS['ONU']:
                if item['PHYID'] in authONUlist.keys():
                    # item['ONUID'] = int(authONUlist[item['PHYID']][2])       # 更新ONUID
                    if authONUlist[item["PHYID"]][6] == 'up':
                        logger.info("ONU(%s)授权成功并已成功上线" % item['PHYID'])
                        online -= 1
                    else:
                        logger.error("ONU(%s)授权成功,无法上线" % item['PHYID'])
                        waitTime(30)
                        break
                else:
                    logger.error("待测试ONU(%s)未授权" % item['PHYID'])
                    self._tc_ret = False
                    online = 0
                    break
        return self._tc_ret

    def create_PPPWAN_STC(self, stc_uplink, stc_onu, vlan_uplink, vlan_onu, onuinfo, **kargs):
        """
        功能：
            创建PPPoE WAN 三层业务仪表配置
        参数：
            @stc_uplink(str): 上联仪表端口名称
            @stc_onu(str): ONU仪表端口名称
            @vlan_uplink(dict): 上联仪表端口的VLAN配置，格式为{'svlan':(100, 7), 'cvlan':(1000, 255)} 
            @vlan_onu(dict): ONU 仪表端口 VLAN配置,格式为{'svlan':(100, 7), 'cvlan':(1000, 255)}
            @onuinfo(tuple)：ONU信息，格式为（slotno, ponno, onuid)
            @**kargs:
                onuGate(str): ONU网关，默认192.168.1.1
                client(bool): 是否需要创建客户端device
        返回值：
            成功-True，失败-False
        说明：
            PPPoE WAN业务仪表配置,命名规范：
            pppoe server： pppwan_server_[slotno][ponno][onuid], 例如pppwan_server_0101001
            pppoe client： pppwan_client_[slotno][ponno][onuid], 例如pppwan_client_0101001
            pppoe wan下行数据流: pppwan_dw_[slotno][ponno][onuid], 例如pppwan_dw_0101001
            pppoe wan上行行数据流: pppwan_up_[slotno][ponno][onuid], 例如pppwan_up_0101001

            DHCP WAN业务仪表配置,命名规范：
            DHCP server： pppwan_server_[slotno][ponno][onuid], 例如pppwan_server_0101001
            pppoe wan下行数据流: pppwan_dw_[slotno][ponno][onuid], 例如pppwan_dw_0101001
            pppoe wan上行行数据流: pppwan_up_[slotno][ponno][onuid], 例如pppwan_up_0101001
        """
        # 创建PPPoE 服务器
        slotno, ponno, onuid = tuple(map(int, onuinfo))
        logger.info("创建pppoE服务器配置...")
        pppwan_server = 'pppwan_server_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
        pppServerMac = "00:01:{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}".format(slotno, ponno, onuid, random.randint(1, 255))

        service_param = {}
        service_param['srcMAC'] = pppServerMac
        if 'svlan' in vlan_uplink.keys():
            service_param['svlan'] = vlan_uplink['svlan']
        if 'cvlan' in vlan_uplink.keys():
            service_param['cvlan'] = vlan_uplink['cvlan']
        ip_r = random.randint(10, 200)
        pppServerIP = "10.185.%d.2" % ip_r
        ppp_pool = '10.185.%d.100' % ip_r
        service_param['ipv4'] = (pppServerIP, ppp_pool)
        service_param['pool'] = (ppp_pool, 24)
        logger.debug("device:{}".format(self._stc._hDevices))
        self._stc.stc_createPPPoEv4Server(stc_uplink, pppwan_server, **service_param)

        # client
        # pppwan_client = 'pppwan_client_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
        pppwan_client = None

        logger.info("创建下行三层数据流")
        pppwan_dw_stream = 'pppwan_dw_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
        traffic_param = {}
        traffic_param['srcMac'] = pppServerMac
        traffic_param['dstMac'] = "00:00:00:00:00:00"
        if 'svlan' in vlan_uplink.keys():
            traffic_param['svlan'] = vlan_uplink['svlan']
        if 'cvlan' in vlan_uplink.keys():
            traffic_param['cvlan'] = vlan_uplink['cvlan']
        traffic_param['pppoeSession'] = {}
        traffic_param['ipv4'] = (pppServerIP, ppp_pool, ppp_pool)
        udp_dw = (random.randint(1025, 49151), random.randint(1025, 49151))
        traffic_param['udp'] = udp_dw
        self._stc.stc_createRawTraffic(stc_uplink, pppwan_dw_stream, **traffic_param)

        logger.info("创建上行三层数据流")
        up_traffic_param = {}
        pppwan_up_stream = 'pppwan_up_{:0>2}{:0>2}{:0>3}'.format(slotno, ponno, onuid)
        up_traffic_param['srcMac'] = "00:94:{:0>2X}:{:0>2X}:{:0>2X}:{:0>2X}".format(
            slotno, ponno, onuid, random.randint(1, 255))
        up_traffic_param['dstMac'] = pppServerMac
        if 'svlan' in vlan_onu.keys():
            up_traffic_param['svlan'] = vlan_onu['svlan']
        if 'cvlan' in vlan_onu.keys():
            up_traffic_param['cvlan'] = vlan_onu['cvlan']
        onugate = kargs['onuGate'] if 'onuGate' in kargs.keys() else '192.168.1.1'
        up_traffic_param['ipv4'] = ('192.168.1.%d' % random.randint(2, 199), pppServerIP, onugate)
        up_traffic_param['udp'] = tuple(reversed(udp_dw))
        self._stc.stc_createRawTraffic(stc_onu, pppwan_up_stream, **up_traffic_param)

        self._stc.stc_apply()

        return (pppwan_server, pppwan_client, pppwan_dw_stream, pppwan_up_stream)

    def verify_PPPWAN_Service(self, pppwan_server, pppwan_client, pppwan_dw_stream, pppwan_up_stream, **kargs):
        logger.info("WAN业务验证")
        check_count = 3   # PPPoe 需要重连标志位
        self._stc.stc_PPPoEv4Connect(pppwan_server)
        while check_count > 0:
            logger.info("检查PPPoE是否连接成功")
            check_count -= 1

            waitTime(20)
            result = self._stc.stc_getPPPoEServerStatus(pppwan_server)
            logger.info(result)
            if result['SessionState'] == "CONNECTED":
                pppoes = {'sessionId': result['PppoeSessionId']}
                srcPort, dstPort = (random.randint(1025, 49151), random.randint(1025, 49151))
                self._stc.stc_modifyTraffic(
                    pppwan_dw_stream, srcMac=result['MacAddr'],
                    dstMac=result['PeerMacAddr'],
                    pppoeSession=pppoes, IPv4=(result['Ipv4Addr'],
                                               result['PeerIpv4Addr'],
                                               result['PeerIpv4Addr']),
                    udp=(srcPort, dstPort))
                self._stc.stc_modifyTraffic(pppwan_up_stream, udp=(dstPort, srcPort))
                logger.info("验证数据流")
                self._stc.stc_startStreamBlock(pppwan_up_stream, arp=True)  # 必须先开始上行流，再开始下行流
                waitTime(3)
                self._stc.stc_startStreamBlock(pppwan_dw_stream, arp=True)
                waitTime(5)
                # 需验证的数据流
                if 'filterStream' in kargs.keys():
                    filter_param = None if kargs['filterStream'] == 'all' else kargs['filterStream']
                else:
                    filter_param = (pppwan_dw_stream, pppwan_up_stream)
                logger.debug("filter:{}".format(filter_param))
                result = self._stc.stc_get_DRV_ResulstData(streamNames=filter_param)
                for key in result:
                    traffic_result = result[key]
                    tx, rx = tuple(map(int, traffic_result[:2]))
                    threshold = kargs['threshold'] if 'threshold' in kargs.keys() else 0.05
                    if (abs(tx - rx) / (tx + 0.00001)) > threshold:
                        logger.error("数据流(%s)异常" % key)
                        self._tc_ret &= False
                        return self._tc_ret

                logger.info("pppoe WAN 业务验证通过！")
                return self._tc_ret

        logger.error("pppoe 连接失败")
        self._tc_ret = False
        return self._tc_ret

    def Basic_test_case(self):
        pass

    def oltlib_test(self):
        self._olt.connect_olt()
        cmds = AN6K.delete_bandwidth_prf(name="test")
        cmds += AN6K.add_bandwidth_prf("test", 100, 20000, 30000)
        # cmds += AN6K.modify_bandwidth_prf("test", 50000, 40000)
        # cmds += AN6K.delete_bandwidth_prf(id=100)
        cmds += AN6K.onu_layer3_ratelimit(4, 8, 64, [(1, 100, 100)])
        self._olt.sendcmdlines(cmds)
        self._olt.disconnet_olt()


if __name__ == "__main__":
    tc_demo = Indonesia_TC()
    tc_demo.oltlib_test()
