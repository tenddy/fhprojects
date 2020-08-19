#!/usr/bin/env python
# coding=UTF-8
"""
@Desc: FH Sprient TestCenter API function
@Author: Teddy.tu
@Version: V1.0
@EMAIL: teddy_tu@126.com
@License: (c)Copyright 2019-2020, Teddy.tu
@Date: 2020-07-13 08:31:06
@LastEditors: Teddy.tu
@LastEditTime: 2020-07-23 16:50:32
"""

import time
import os
import traceback
import re
from lib import settings
from lib.stclib.pystc import STC
from lib.public import fhlog


class FHSTCException(Exception):
    """Base class for FHSTCException"""
    pass


class FHSTCCmdError(FHSTCException):
    def __init__(self, command, error_message, stderr=''):
        self.command = command
        self.error_message = error_message.strip()
        self.stderr = stderr
        super().__init__(self.__str__())

    def __str__(self):
        msg = 'FHSTCCmdError raised while executing the command:"%s"\n error_message: "%s"' % (
            self.command, self.error_message)
        if self.stderr:
            msg += '\n stderr: %s' % (self.stderr)
        fhlog.logger.error(msg)
        return msg


class FHSTC:
    def __init__(self, stcip=None):
        self._stc = STC(tcl=settings.TCL_PATH, stcpath=settings.STC_PATH)  # TC 安装路径
        self._stcip = settings.STCIP if stcip is None else stcip  # TC IP
        self._project = None
        self._ports = dict()
        self._hPorts = dict()
        self._hStreamBlock = dict()
        self._hStreamBlockIf = dict()
        self._hDevices = dict()
        # self._hDHCPBlockConfig = dict()
        # self._hPPPoXBlockConfig = dict()
        self._hdrv = None
        self._hStreamBlockResult = dict()
        self.stc_init()

    def __del__(self):
        del self._stc

    def stc_init(self, ports=None):
        """ 初始化仪表, 导入仪表库文件 """
        try:
            fhlog.logger.info("初始化仪表，导入仪表库文件...")
            self._stc.load_stc_lib()
            fhlog.logger.info("连接仪表...")
            self.stc_connect()
            self.stc_createProject()
            fhlog.logger.info("初始化仪表端口...")
            if ports is None:
                ports = dict(settings.UPLINK_PORTS)
                ports.update(settings.ONU_PORTS)
            self.stc_createPorts(**ports)
            self.stc_AttachPorts()
            fhlog.logger.info("初始化仪表成功！")
        except:
            raise FHSTCCmdError('stc_init', '初始化仪表失败', traceback.format_exc())

    def stc_connect(self):
        """连接STC仪表"""
        try:
            fhlog.logger.info("连接仪表STC,仪表IP(%s)" % self._stcip)
            self._stc.connect(self._stcip)
            # fhlog.logger.info("占用仪表端口...")
            # self.stc_AttachPorts()
        except:
            raise FHSTCCmdError('stc_connect', '连接仪表失败.', traceback.format_exc())

    def stc_disconnect(self):
        """端口仪表连接"""
        try:
            fhlog.logger.info("断开仪表连接")
            self._stc.perform("DetachPorts", PortList="{%s}" % (' '.join(self._hPorts.values())))
            self._stc.disconnect(self._stcip)
        except:
            raise FHSTCCmdError('stc_disconnect', '断开仪表失败.', traceback.format_exc())

    def stc_apply(self):
        try:
            fhlog.logger.info("Apply")
            self._stc.apply()
        except:
            raise FHSTCCmdError('stc_apply', 'Apply仪表配置失败.', traceback.format_exc())

    def stc_createProject(self):
        """创建仪表根工程名称"""
        try:
            # fhlog.logger.info("创建仪表工程")
            self._project = self._stc.create("Project")
        except:
            raise FHSTCCmdError('stc_createProject', '创建仪表操作工程失败.', traceback.format_exc())

    def stc_createPorts(self, **ports):
        """初始化端口，并创建操作端口句柄(handle)"""
        try:
            fhlog.logger.info("初始化端口，并创建端口操作句柄(handle)")
            for portName in ports.keys():
                if len(ports[portName]) == 0:
                    continue

                portLoc = "//{stcip}/{port}".format(stcip=self._stcip, port=ports[portName])
                self._ports[portName] = portLoc

                if '_hPorts' not in self.__dict__.keys():
                    self._hPorts = dict()
                self._hPorts[portName] = self._stc.create(
                    "port", under=self._project, location=portLoc, Name=portName, useDefaultHost=False,
                    AppendLocationToPortName=False)

                # 创建端口，初始化端口generator的配置参数
                self.stc_generatorConfig(portName)
        except:
            raise FHSTCCmdError('stc_createPorts', '初始化端口失败', stderr=traceback.format_exc())

    def stc_modify_port(self, portName: str, ethernetType: str, **portSpeed):
        """
        函数功能：
            配置仪表端口协商速率属性
        函数参数：
            @portName: 端口名称
            @ethernetType: 端口属性 (EthernetCopper, EthernetFiber, EthernetFiber10G, EthernetFiber40G)
        """
        try:
            fhlog.logger.info("修改端口({0})属性为{1}".format(portName, ethernetType))
            self._stc.create(ethernetType, under=self._hPorts[portName], **portSpeed)
        except:
            raise FHSTCCmdError('stc_createPorts', "修改端口({0})属性为{1}失败".format(
                portName, ethernetType), stderr=traceback.format_exc())

    def stc_reserve(self, portName=None):
        """ 占用仪表端口"""
        try:
            if portName is None:
                self._stc.reserve(list(self._ports.values()))

            else:
                fhlog.logger.info("占用端口{0}-{1}".format(portName, self._ports[portName]))
                self._stc.reserve((self._ports[portName],))
        except Exception as err:
            raise FHSTCCmdError('stc_reserve', '占用端口{0}-{1}失败'.format(portName, self._ports[portName]),
                                stderr=traceback.format_exc())

    def stc_release(self, portName=None):
        """释放仪表端口"""
        try:
            if portName is None:
                for value in self._hPorts.values():
                    fhlog.logger.debug(value)
                    online = self._stc.get(value, "Online")
                    fhlog.logger.debug("%s:%s" % (value, online))
                    if "TRUE" == online.upper():
                        self._stc.release(tuple(self._ports.values()))
            else:
                if "TRUE" == self._stc.get(self._hPorts[portName], "Online").upper():
                    self._stc.release((self._ports[portName],))
        except Exception as err:
            raise FHSTCCmdError("stc_release", "释放端口失败")

    def stc_AttachPorts(self, **kargs):
        """绑定端口属性，并连接端口"""
        try:
            fhlog.logger.info("占用仪表端口...")
            self._stc.perform("AttachPorts", AutoConnect="True", **kargs)
        except Exception as err:
            raise FHSTCCmdError('stc_autoAttachPorts', '绑定端口失败', traceback.format_exc())

    def stc_createRawTraffic(self, portName: str, streamName: str, **kargs):
        """
        函数功能:
            创建裸流
        函数参数:
            @portName: 创建数据流的仪表端口命令
            @streamName: 数据流名称
            @ **kargs(dict):
                srcMac:源MAC地址，默认值00:00:10:00:00:01
                dstMac:目的MAC地址，默认值00:00:94:00:00:01
                cvlan(tuple): CVLAN, 格式为(cvlan-id, cvlan-pri)
                svlan(tuple):SVLAN, 格式为(svlan-id, svlan-pri)
                pppoeSession(dict): pppoe Session, 格式为 {'version': 1, 'type': 1, 'code': 0, 'sessionId': 2}
                ppp(str): ipv4|ipv6|mpls, 如果创建pppSession,默认值ipv4; protocolType,0021-IPv4, 0057-IPv6, 0281-MPLS
                ipv4(tuple): IPv4报文头, 格式为(srcIPv4, dstIpv4, gateway)
                ipv6(tuple): #TODO
                udp(tuple):UDP 报文头，格式(sourcePort, dstPort)

                FrameLengthMode(str)：报文长度模式，(FIXED/INCR/DECR/IMIX/RANDOM/AUTO)
                FixedFrameLength(int)：报文长度为Fixed模式，报文长度
                MinFrameLength(int): 报文最小长度
                MaxFrameLength(int): 报文最大长度
                Load(int): 流量大小
                LoadUnit(str): 流量单位 (percent/fps/bps/Kbps/Mbps)

        返回值: None

        使用说明:
        """
        try:
            fhlog.logger.info("创建数据流，端口名称-{0},数据流名称-{1}".format(portName, streamName))

            if '_ports' in self.__dict__.keys() and portName not in self._ports.keys():
                fhlog.logger.error("port %s not reserved!!!" % self._ports[portName])
                raise FHSTCCmdError(
                    'stc_createTrafficRaw', "创建数据流，端口名称-{0},数据流名称-{1}失败".format(portName, streamName),
                    stderr=traceback.format_exc())

            keys = kargs.keys()
            # 设置数据流基本属性
            stream_basic = dict()
            stream_basic['insertSig'] = kargs['insertSig'] if 'insertSig' in keys else 'True'
            stream_basic['frameConfig'] = ' "" '
            stream_basic['Name'] = streamName
            stream_basic['FrameLengthMode'] = kargs['FrameLengthMode'] if 'FrameLengthMode' in keys else 'FIXED'
            stream_basic['FixedFrameLength'] = kargs['FixedFrameLength'] if 'FixedFrameLength' in keys else '512'
            stream_basic['MinFrameLength'] = kargs['MinFrameLength'] if 'MinFrameLength' in keys else '128'
            stream_basic['MaxFrameLength'] = kargs['MaxFrameLength'] if 'MaxFrameLength' in keys else '1518'
            stream_basic['Load'] = kargs['Load'] if 'Load' in keys else '100'
            loadUnit = {'percent': 'PERCENT_LINE_RATE', 'fps': 'FRAMES_PER_SECOND', 'bps': 'BITS_PER_SECOND',
                        'Kbps': 'KILOBITS_PER_SECOND', 'Mbps': 'MEGABITS_PER_SECOND'}
            stream_basic['LoadUnit'] = loadUnit[kargs['LoadUnit']] if 'LoadUnit' in keys else 'MEGABITS_PER_SECOND'

            self._hStreamBlock[streamName] = self._stc.create(
                'streamBlock', under=self._hPorts[portName], **stream_basic)

            streamBlockHeader = dict()
            # L2 header
            srcMac = kargs['srcMac'] if 'srcMac' in keys else '00:00:10:00:00:01'
            dstMac = kargs['dstMac'] if 'dstMac' in keys else '00:10:94:00:00:01'
            streamBlockHeader['ethii'] = self._stc.create('ethernet:EthernetII', under=self._hStreamBlock[streamName],
                                                          srcMac=srcMac, dstMac=dstMac)

            if 'cvlan' in keys or 'svlan' in keys:
                _hVlanContainer = self._stc.create('vlans', under=streamBlockHeader['ethii'])
                if 'svlan' in keys:
                    svlan = kargs["svlan"][0]
                    scos = bin(kargs["svlan"][1])[2:]
                    hSvlan = 'hSvlan_%s' % streamName
                    if '_hSvlan' not in self.__dict__.keys():
                        self._hSvlan = dict()
                    streamBlockHeader['svlan'] = self._stc.create('Vlan', under=_hVlanContainer,
                                                                  pri=scos, cfi=0, id=svlan, name=hSvlan)
                if 'cvlan' in keys:
                    cvlan = kargs["cvlan"][0]
                    ccos = bin(kargs["cvlan"][1])[2:]
                    hCvlan = 'hCvlan_%s' % streamName
                    streamBlockHeader['cvlan'] = self._stc.create('Vlan', under=_hVlanContainer,
                                                                  pri=ccos, cfi=0, id=cvlan, name=hCvlan)
            # pppoe Session
            if 'pppoeSession' in keys:
                # {'version': 1, 'type': 1, 'code': 0, 'sessionId': 2}
                pppoes = kargs['pppoeSession']
                pppoes_dict = {}
                pppoes_dict['version'] = pppoes['version'] if 'version' in pppoes.keys() else 1
                pppoes_dict['type'] = pppoes['type'] if 'type' in pppoes.keys() else 1
                pppoes_dict['code'] = pppoes['code'] if 'code' in pppoes.keys() else 0
                pppoes_dict['sessionId'] = pppoes['sessionId'] if 'sessionId' in pppoes.keys() else 0
                streamBlockHeader['pppoeSession'] = self._stc.create(
                    'pppoe:PPPoESession', under=self._hStreamBlock[streamName],
                    **pppoes_dict)
                # ppp header
                ppptypes = {'ipv4': '0021', 'ipv6': '0057', 'mpls': '0281'}
                protocolType = ppptypes[kargs['ppp']] if 'ppp' in keys else ppptypes['ipv4']
                streamBlockHeader['ppp'] = self._stc.create(
                    'ppp:PPP', under=self._hStreamBlock[streamName],
                    protocolType=protocolType)
            # ipv4
            if 'ipv4' in keys:
                srcIPv4, dstIPv4, gateway = kargs['ipv4']
                streamBlockHeader['ipv4'] = self._stc.create('ipv4:IPv4', under=self._hStreamBlock[streamName],
                                                             sourceAddr=srcIPv4, destAddr=dstIPv4, gateway=gateway)
            # UDP
            if 'udp' in keys:
                streamBlockHeader['udp'] = self._stc.create(
                    'udp:UDP', under=self._hStreamBlock[streamName],
                    sourcePort=kargs['udp'][0],
                    destPort=kargs['udp'][1])

            self._hStreamBlockIf[streamName] = streamBlockHeader

        except:
            raise FHSTCCmdError(
                'stc_createRawTraffic', "创建数据流，端口名称-{0},数据流名称-{1}失败".format(portName, streamName),
                stderr=traceback.format_exc())

    def stc_modifyTraffic(self, streamName, **kargs):
        """
        功能：
            修改数据流参数
        参数：
            @streamName: 数据流名称
            @**kargs: 修改参数
                srcMac:源MAC地址，默认值00:00:10:00:00:01
                dstMac:目的MAC地址，默认值00:00:94:00:00:01
                cvlan(tuple): CVLAN, 格式为(cvlan-id, cvlan-pri)
                svlan(tuple):SVLAN, 格式为(svlan-id, svlan-pri)
                pppoeSession(dict): pppoe Session, 格式为 {'version': 1, 'type': 1, 'code': 0, 'session_id': 2}
                ppp(str): ipv4|ipv6|mpls, 如果创建pppSession,默认值ipv4; protocolType,0021-IPv4, 0057-IPv6, 0281-MPLS
                ipv4(tuple): IPv4报文头, 格式为(srcIPv4, dstIpv4, gateway)
                ipv6(tuple): #TODO
                udp(tuple):UDP 报文头，格式(sourcePort, dstPort)

                FrameLengthMode(str)：报文长度模式，(FIXED/INCR/DECR/IMIX/RANDOM/AUTO)
                FixedFrameLength(int)：报文长度为Fixed模式，报文长度
                MinFrameLength(int): 报文最小长度
                MaxFrameLength(int): 报文最大长度
                Load(int): 流量大小
                LoadUnit(str): 流量单位 (percent/fps/bps/Kbps/Mbps)
        返回值：None
        说明：
        """
        try:
            fhlog.logger.info("修改数据流{}配置".format(streamName))
            hstreamBlock = self._hStreamBlock[streamName]
            hChildrenHeader = self._stc.get(hstreamBlock, "children")
            fhlog.logger.debug("header:{}".format(hChildrenHeader))
            hstreamHeader = dict()
            for item in hChildrenHeader.split():
                if item.startswith('ethernet:ethernetii'):
                    hstreamHeader['ethii'] = item.rstrip()
                if item.startswith('pppoe:pppoesession'):
                    hstreamHeader['pppoeSession'] = item.rstrip()
                if item.startswith('ppp:ppp'):
                    hstreamHeader['ppp'] = item.rstrip()
                if item.startswith('ipv4:ipv4'):
                    hstreamHeader['ipv4'] = item.rstrip()
                if item.startswith('udp:udp'):
                    hstreamHeader['udp'] = item.rstrip()

            fhlog.logger.debug(hstreamHeader)
            keys = kargs.keys()
            # ethernet
            ethernetIf = dict()
            if 'srcMac' in keys:
                ethernetIf['srcMac'] = kargs['srcMac']
            if 'dstMac' in keys:
                ethernetIf['dstMac'] = kargs['dstMac']
            if len(ethernetIf) > 0:
                if 'ethii' in hstreamHeader.keys():
                    self._stc.config(hstreamHeader['ethii'], **ethernetIf)
                else:
                    hstreamHeader['ethii'] = self._stc.create('ethernet:EthernetII', under=hstreamBlock, **ethernetIf)
            # vlan
            # pppoeSession
            if 'pppoeSession' in keys:
                if 'pppoeSession' in hstreamHeader.keys():
                    self._stc.config(hstreamHeader['pppoeSession'], **kargs['pppoeSession'])
                else:
                    hstreamHeader['pppoeSession'] = self._stc.create('pppoe:PPPoESession', under=hstreamBlock,
                                                                     **kargs['pppoeSession'])
                    hstreamHeader['ppp'] = self._stc.create('ppp:PPP', under=hstreamBlock, protocolType="0021")
            # ppp
            if 'ppp' in keys and 'ppp' in hstreamHeader.keys():
                ppptypes = {'ipv4': '0021', 'ipv6': '0057', 'mpls': '0281'}
                self._stc.config(hstreamHeader['ppp'], protocolType=ppptypes[kargs['ppp']])

            # ipv4
            if 'ipv4' in keys:
                srcIPv4, dstIPv4, gateway = kargs['ipv4']
                if 'ipv4' in hstreamHeader.keys():
                    self._stc.config(hstreamHeader['ipv4'], sourceAddr=srcIPv4, destAddr=dstIPv4, gateway=gateway)
                else:
                    self._stc.create('ipv4:IPv4', under=hstreamBlock, sourceAddr=srcIPv4,
                                     destAddr=dstIPv4, gateway=gateway)

            # udp
            if 'udp' in keys:
                if 'udp' in hstreamHeader.keys():
                    self._stc.config(hstreamHeader['udp'], sourcePort=kargs['udp'][0], destPort=kargs['udp'][1])
                else:
                    hstreamHeader['udp'] = self._stc.create(
                        'udp:UDP', under=hstreamBlock, sourcePort=kargs['udp'][0],
                        destPort=kargs['udp'][1])
            fhlog.logger.debug("generatorConfig")
            generatorConfig = dict()
            # FrameLengthMode(str)：报文长度模式，(FIXED/INCR/DECR/IMIX/RANDOM/AUTO)
            if "FrameLengthMode" in keys:
                generatorConfig['FrameLengthMode'] = kargs['FrameLengthMode']
            # FixedFrameLength(int)：报文长度为Fixed模式，报文长度
            if "FixedFrameLength" in keys:
                generatorConfig['FixedFrameLength'] = kargs['FixedFrameLength']
            # MinFrameLength(int): 报文最小长度
            if "MinFrameLength" in keys:
                generatorConfig['MinFrameLength'] = kargs['MinFrameLength']
            # MaxFrameLength(int): 报文最大长度
            if "MaxFrameLength" in keys:
                generatorConfig['MaxFrameLength'] = kargs['MaxFrameLength']
            # Load(int): 流量大小
            if "Load" in keys:
                generatorConfig['Load'] = kargs['Load']
            # LoadUnit(str): 流量单位 (percent/fps/bps/Kbps/Mbps)
            if "LoadUnit" in keys:
                generatorConfig['LoadUnit'] = kargs['LoadUnit']
            if len(generatorConfig) > 0:
                self._stc.config(hstreamBlock, **kargs)
            fhlog.logger.debug("apply...")
            self._stc.apply()
            fhlog.logger.debug("修改数据流{}配置成功".format(streamName))
        except:
            raise FHSTCCmdError('stc_modifyTraffic', "修改数据流{}失败".format(streamName), traceback.format_exc())

    def stc_RangeModifer(self, streamName, reference):
        pass

    def stc_createBoundTraffic(self, streamName: str, srcDevice: str, dstDevice: str, protocol="l2", **kargs):
        """
        函数功能:
            创建绑定流
        函数参数:
            @streamName: 数据流名称
            @srcDevice:源device
            @dstDevice:目的device
            @protocl: 协议类型（l2, dhcp, pppoe, igmp)
            @param **kargs(dict):
                udp: UDP 报文头，格式(sourcePort, dstPort)
                FrameLengthMode(str)：报文长度模式，(FIXED/INCR/DECR/IMIX/RANDOM/AUTO)
                FixedFrameLength(int)：报文长度为Fixed模式，报文长度
                MinFrameLength(int): 报文最小长度
                MaxFrameLength(int): 报文最大长度
                Load(int): 流量大小
                LoadUnit(str): 流量单位 (percent/fps/bps/Kbps/Mbps)
        返回值: None

        使用说明:
        """
        try:
            portName = self._stc.get(self._hDevices[srcDevice], "affiliationport-Targets")
            fhlog.logger.info("创建绑定流，数据流名称-{0}".format(streamName))
            keys = kargs.keys()
            # 设置数据流基本属性
            stream_basic = dict()
            stream_basic['insertSig'] = kargs['insertSig'] if 'insertSig' in keys else 'True'
            stream_basic['frameConfig'] = ' "" '
            stream_basic['Name'] = streamName
            stream_basic['FrameLengthMode'] = kargs['FrameLengthMode'] if 'FrameLengthMode' in keys else 'FIXED'
            stream_basic['FixedFrameLength'] = kargs['FixedFrameLength'] if 'FixedFrameLength' in keys else '512'
            stream_basic['MinFrameLength'] = kargs['MinFrameLength'] if 'MinFrameLength' in keys else '128'
            stream_basic['MaxFrameLength'] = kargs['MaxFrameLength'] if 'MaxFrameLength' in keys else '1518'
            stream_basic['Load'] = kargs['Load'] if 'Load' in keys else '100'
            loadUnit = {'percent': 'PERCENT_LINE_RATE', 'fps': 'FRAMES_PER_SECOND', 'bps': 'BITS_PER_SECOND',
                        'Kbps': 'KILOBITS_PER_SECOND', 'Mbps': 'MEGABITS_PER_SECOND'}
            stream_basic['LoadUnit'] = loadUnit[kargs['LoadUnit']] if 'LoadUnit' in keys else 'MEGABITS_PER_SECOND'

            self._hStreamBlock[streamName] = self._stc.create('streamBlock', under=portName, **stream_basic)
            streamBlockHeader = dict()

            if protocol.lower() == "l2":
                srcDeviceIf = self._stc.get(self._hDevices[srcDevice], "Children-ethiiIf")
                dstDeviceIf = self._stc.get(self._hDevices[dstDevice], "Children-ethiiIf")
            elif protocol.lower() == 'dhcp' or protocol.lower() == "pppoe":
                srcDeviceIf = self._stc.get(self._hDevices[srcDevice], "Children-Ipv4If")
                dstDeviceIf = self._stc.get(self._hDevices[dstDevice], "Children-Ipv4If")
                if protocol.lower() == "pppoe":
                    self._stc.create("pppoe:PPPoESession", under=self._hStreamBlock[streamName])
            elif protocol.lower() == "igmp":
                srcDeviceIf = self._stc.get(self._hDevices[srcDevice], "Children-Ipv4If")
                # igmp 获取客户端中的 Ipv4NetworkBlock
                igmpHostConfig = self._stc.get(self._hDevices[dstDevice], "Children-igmphostconfig")
                igmpMembership = self._stc.get(igmpHostConfig, "Children-IgmpGroupMembership")
                ipv4group = self._stc.get(igmpMembership, "SubscribedGroups-targets")
                dstDeviceIf = self._stc.get(ipv4group, "Children-Ipv4NetworkBlock")  # Ipv4NetworkBlock
            else:
                raise FHSTCCmdError('stc_createTrafficRaw', "创建绑定流失败,请选择协议类型（l2, dhcp, pppoe, igmp)",
                                    stderr=traceback.format_exc())

            self._stc.config(self._hStreamBlock[streamName], SrcBinding=srcDeviceIf, DstBinding=dstDeviceIf)
            ifHeaders = self._stc.get(self._hStreamBlock[streamName])
            # fhlog.logger.info("hearder:{}".format(ifHeaders))

            if 'udp' in kargs.keys():
                streamBlockHeader['udp'] = self._stc.create(
                    'udp:UDP', under=self._hStreamBlock[streamName],
                    sourcePort=kargs['udp'][0],
                    destPort=kargs['udp'][1])

            self._hStreamBlockIf[streamName] = streamBlockHeader

        except:
            raise FHSTCCmdError('stc_createTrafficRaw', "创建绑定流失败", stderr=traceback.format_exc())

    def stc_generatorConfig(self, portName, **generatorConfig):
        """配置仪表端口Generator 参数"""
        try:
            fhlog.logger.info('配置仪表端口(%s)Generator参数' % portName)
            if '_hGenerator' not in self.__dict__.keys():
                self._hGenerator = dict()
            self._hGenerator[portName] = self._stc.get(self._hPorts[portName], "children-Generator")
            if '_hGeneratorConfig' not in self.__dict__.keys():
                self._hGeneratorConfig = dict()
            self._hGeneratorConfig[portName] = self._stc.get(self._hGenerator[portName], "children-GeneratorConfig")

            keys = generatorConfig.keys()
            config = dict()
            config['DurationMode'] = generatorConfig['DurationMode'] if 'DurationMode' in keys else "CONTINUOUS"
            config['BurstSize'] = generatorConfig['BurstSize'] if 'BurstSize' in keys else "1"
            config['SchedulingMode'] = generatorConfig['SchedulingMode'] if 'SchedulingMode' in keys else "RATE_BASED"
            self._stc.config(self._hGeneratorConfig[portName], **config)
        except Exception as err:
            raise FHSTCCmdError('stc_generatorConfig', '配置仪表端口(%s)Generator参数失败' %
                                portName, stderr=traceback.format_exc())

    def stc_saveAsXML(self, filepath="config.xml"):
        try:
            fhlog.logger.info("保存仪表配置为XML文件(%s)" % filepath)
            filename = os.path.basename(filepath)
            path = settings.TESTCASE_PATH + "/instruments" if os.path.dirname(
                filepath) == "" else os.path.dirname(filepath)
            if not os.path.exists(path):
                os.makedirs(path)
            self._stc.perform("SaveAsXml", FileName=path + "/" + filename)
        except:
            raise FHSTCCmdError('stc_saveAsXML', '保存仪表配置为XML文件(%s)失败', traceback.format_exc())

    def stc_loadFromXml(self, filepath):
        """导入仪表配置，并初始化仪表参数
            TODO: Device 对象的获取
        """
        try:
            fhlog.logger.info("导入仪表配置文件")
            self._stc.perform("LoadFromXml", FileName=settings.TESTCASE_PATH + "/instruments/"+filepath)
            # 获取仪表
            ports = self._stc.get("project1", "Children-Port")
            fhlog.logger.debug(ports)

            for port in ports.split():
                # 获取端口名称
                fhlog.logger.debug("port handle: {}".format(port))
                portLocation = self._stc.get(port, "Location")
                portName = self._stc.get(port, "PortName")
                state = self._stc.get(port, "Online")
                if state == "false":
                    portName = portName[:-10]
                fhlog.logger.debug(portName)
                # 获取端口信息
                self._ports[portName] = portLocation
                # 获取端口操作句柄
                self._hPorts[portName] = port
                fhlog.logger.debug(self._hPorts)

                # 获取每个端口下数据流的名称及操作句柄
                streamBlock = self._stc.get(port, "Children-StreamBlock")
                fhlog.logger.debug(streamBlock)
                # 获取数据流名称和对应的操作句柄
                for item in streamBlock.split():
                    streamName = self._stc.get(item, "Name")
                    self._hStreamBlock[streamName] = item
                fhlog.logger.debug(self._hStreamBlock)

            # 获取Device
            objectLists = self._stc.perform("GetObjects", ClassName='EmulatedDevice',
                                            Direction="ALL", Rootlist='project1')

            fhlog.logger.debug(objectLists)
            devices = re.findall("-ObjectList {(.*)} -State", objectLists)
            fhlog.logger.debug(devices[0].split())
            if len(devices) != 0:
                for device in devices[0].split():
                    deviceName = self._stc.get(device, 'Name')
                    if deviceName in self._hDevices.keys():
                        self._hDevices[deviceName] += " " + device
                    else:
                        self._hDevices[deviceName] = device
            fhlog.logger.debug(self._hDevices)

            self.stc_AttachPorts()

        except:
            raise FHSTCCmdError('stc_loadFromXml', '导入仪表配置文件(%s)失败', traceback.format_exc())

    def stc_analyzer(self, portName):
        """
        功能：
            STC 仪表流量分析功能，
            # ToDo
        参数：

        返回值：None
        说明：
        """
        pass

    def stc_generator_start(self, portName=None):
        """基于端口启动generator"""
        try:
            self.stc_DRVConfig(LimitSize=100)
            if portName is None:
                for name in self._hGenerator.keys():
                    fhlog.logger.info('端口(%s)发送流量' % name)
                    self._stc.perform("GeneratorStart", GeneratorList=self._hGenerator[name])
            else:
                fhlog.logger.info('端口(%s)发送流量' % portName)
                self._stc.perform("GeneratorStart", GeneratorList=self._hGenerator[portName])
        except Exception as err:
            raise FHSTCCmdError('stc_generator_start', "端口发送流量失败", traceback.format_exc())

    def stc_generator_stop(self, portName):
        """基于端口停止generator"""
        # hGenerator = "hGenerator_{0}".format(portName)
        self._stc.perform("GeneratorStop", GeneratorList=self._hGenerator[portName])

    def stc_startStreamBlock(self, streamName, arp=False):
        """基于streamBlock发送流量"""
        try:
            fhlog.logger.info("发送流量{}".format(streamName))
            if self._hdrv is None:
                self.stc_DRVConfig(LimitSize=100)
            self._stc.perform("StreamBlockStart", StreamBlockList=self._hStreamBlock[streamName])
            if arp:
                self.stc_startARP(streamName)
        except:
            raise FHSTCCmdError("stc_startStreamBlock", "基于streamBlock发送流量失败", traceback.format_exc())

    def stc_stopStreamBlock(self, streamName):
        """基于streamBlock停止generator"""
        try:
            if isinstance(streamName, str):
                self._stc.perform("StreamBlockStop", StreamBlockList=self._hStreamBlock[streamName])
            elif isinstance(streamName, tuple) or isinstance(streamName, list):
                for stream in streamName:
                    self._stc.perform("StreamBlockStop", StreamBlockList=self._hStreamBlock[streamName])
        except:
            raise FHSTCCmdError("stc_stopStreamBlockStop", "流量({})停止失败".format(streamName), traceback.format_exc())

    def stc_stopAllStreamBlock(self):
        """停止所有数据流"""
        try:
            fhlog.logger.info("停止所有数据流")
            for stream in self._hStreamBlock.keys():
                self._stc.perform("StreamBlockStop", StreamBlockList=self._hStreamBlock[stream])
        except:
            raise FHSTCCmdError("stc_stopAllStreamBlock", "停止所有流量失败", traceback.format_exc())

    def stc_ClearAllResults(self, portName=None):
        """基于端口清空仪表流量统计"""
        try:
            if portName is None:
                for name in self._hPorts.keys():
                    self._stc.perform('ResultsClearAllCommand', PortList=self._hPorts[name])
            else:
                self._stc.perform('ResultsClearAllCommand', PortList=self._hPorts[portName])
        except:
            raise FHSTCCmdError("stc_ClearAllResults", "清空仪表端口流量统计失败", traceback.format_exc())

    def stc_DRVConfig(self, **kargs):
        """配置DynamicResultView"""
        self._hdrv = self._stc.create('DynamicResultView', under=self._project,
                                      ResultSourceClass='StreamBlock', Name='DRV1')
        # 配置select 参数
        self.selectProperties = [
            'Port.Name', 'StreamBlock.Name', 'StreamBlock.TxFrameRate', 'StreamBlock.RxFrameRate',
            'StreamBlock.TxL1BitRate', 'StreamBlock.RxL1BitRate', 'StreamBlock.TxBitRate',
            'StreamBlock.RxBitRate', 'StreamBlock.DroppedFrameCount', 'StreamBlock.DroppedFramePercent']
        selectParams = "{%s}" % (' '.join(self.selectProperties))

        # 配置仪表显示的数据流的个数，默认是100
        limitSize = kargs['LimitSize'] if 'LimitSize' in kargs.keys() else 100
        self.hprq = self._stc.create("PresentationResultQuery", under=self._hdrv,
                                     SelectProperties=selectParams, LimitSize=limitSize, FromObjects=self._project)
        self._stc.perform('SubscribeDynamicResultView', DynamicResultView=self._hdrv)

    def stc_get_DRV_ResulstData(self, ports=None, streamNames=None, loops=5):
        """
        功能：
            获取DynamicResultView结果,通过DynamicResultView获取结果，不需要停流;
            通过DynamicResultView获取结果，需要先调用stc_DRVConfig函数。
        参数：
            @ports(tuple):基于端口过滤数据流，例如("uplink", "onu1")
            @streamNames(tuple): 基于数据流的名称过滤数据流, 例如（"dw", "up")
            @loops(int): 刷新结果次数，默认为5
        返回值：None
        """
        try:
            fhlog.logger.info("获取实时流量统计(DynamicResultView)...")
            self._hDRVData = self._stc.get(self._hdrv, 'children-PresentationResultQuery')

            for loop in range(loops):
                # Since these are not realtime results, the view has to be manually updated
                self._stc.perform('UpdateDynamicResultView', DynamicResultView=self._hdrv)
                time.sleep(2)

            _hrvd = self._stc.get(self._hDRVData, 'children-ResultViewData')
            _hrvd = _hrvd.split()

            resultsData = {}
            placeholder = 16  # 结果打印占位符
            for index in _hrvd:
                ret = self._stc.get(index, 'ResultData').split()
                # ret_s = ret.split()
                if ports is not None and ret[0] not in ports:
                    continue
                if streamNames is not None and ret[1] not in streamNames:
                    continue

                key = "%s.%s" % (tuple(ret[:2]))
                value = tuple(ret[2:-2])
                resultsData[key] = value
                # 占位符空间
                placeholder = placeholder if len(key) < placeholder else len(key)+4

            fhlog.logger.info("holder:%d" % placeholder)
            # 打印 DRV_ResulstData结果
            title = ('StreamName', 'TxFrameRate', 'RxFrameRate', 'TxL1Rate',
                     'RxL1Rate', 'TxRate', 'RxRate', 'DropFrame', 'DropPct')

            result = '\n' + "{:<{}}".format(title[0], placeholder) + " ".join(
                list(map(lambda x: "{:<16}".format(x), title[1:])))
            for key in resultsData:
                raw_result = " ".join(list(map(lambda x: "{:<16}".format(x), resultsData[key])))
                result += "\n{0:<{1}}{2}".format(key, placeholder, raw_result)
                self._hStreamBlockResult[key] = dict(zip(title[1:], raw_result))    # 保存当前获取的流量统计
            fhlog.logger.info(result)

            return resultsData
        except:
            raise FHSTCCmdError("stc_get_DRV_ResulstData", "获取端口实时流量统计失败", traceback.format_exc())

    def stc_verifyStreamResult(self, streamName, realValue=None):
        streamResult = self.stc_get_DRV_ResulstData()

    def stc_get_ResultDataSet(self, **kargs):
        """通过ResultDataSet获取流量统计，待完善"""
        # print("Create and subscribe a ResultDataSet...")
        self._hRDSTx = self._stc.subscribe(Parent=self._project, resultType='txstreamresults', configType='streamblock')
        totoalPage = int(self._stc.get(self._hRDSTx, 'TotalPageCount'))
        # currentPage = 1
        for currentPage in range(1, totoalPage + 1):
            lstResults = self._stc.get(self._hRDSTx, 'ResultHandleList')
            # print("list:", lstResults)
            lstResults = lstResults.split()
            fhlog.logger.info("page:%d" % currentPage)
            for hResult in lstResults:
                bitrate = self._stc.get(hResult, 'bitrate')
                # print(bitrate)
                fhlog.logger.info(bitrate)

    def stc_captureStart(self, portName, **kargs):
        """启动抓包"""
        try:
            fhlog.logger.info("开始抓包({})".format(portName))
            if '_hCapture' not in self.__dict__.keys():
                self._hCapture = dict()
            # Create a capture object. Automatically created.
            self._hCapture[portName] = self._stc.get(self._hPorts[portName], 'children-Capture')
            self._stc.config(self._hCapture[portName], mode='REGULAR_MODE', srcMode='TX_RX_MODE')
            self._stc.perform("CaptureStart", captureProxyId=self._hCapture[portName])
        except Exception as err:
            raise FHSTCCmdError("stc_captureStart", "启动抓包失败", traceback.format_exc())

    def stc_captureStop(self, portName, filepath=None):
        """停止抓包，并保存抓包结果"""
        try:
            fhlog.logger.info("停止抓包...")
            self._stc.perform('CaptureStop', captureProxyId=self._hCapture[portName])
            if filepath is None:
                filename = time.strftime("%Y%M%m%H%m%S") + 'capature.pacp'
                path = settings.CAP_PATH
            else:
                filename = os.path.basename(filepath)
                path = settings.CAP_PATH if os.path.dirname(filepath) == "" else os.path.dirname(filepath)

            self._stc.perform(
                'CaptureDataSave', captureProxyId=self._hCapture[portName],
                FileName=filename, FileNamePath=path, FileNameFormat='PCAP')

            return self._stc.get(self._hCapture[portName], "PktCount")
        except:
            raise FHSTCCmdError("stc_captureStop", "停止并保存抓包失败", traceback.format_exc())

    def stc_captureFilter(self, portName, filterExp=''):
        """过滤报文"""
        if "_hCaptureFilter" not in self.__dict__.keys():
            self._hCaptureFilter = dict()
        self._hCaptureFilter[portName] = self._stc.get(self._hCapture[portName], 'children-CaptureFilter')
        self._stc.config(self._hCaptureFilter[portName], FilterExpression=filterExp)

    def package_analyze(self, pcapfile, filter_exp):
        """
        功能：
            仪表报文分析（暂时未实现该功能）
        参数：
            @pcapfile: pcap文件
            @fileter_exp: 过滤表达式
        返回值：None
        说明：	
        """
        filename = os.path.basename(pcapfile)
        if os.path.dirname(pcapfile) == "":
            path = settings.CAP_PATH
            analyzeFile = path + '/' + filename
        else:
            analyzeFile = pcapfile
        cap_general = self._stc._tclsh.eval("exec {%s} -r {%s} -Y %s" % (settings.TSHARK, analyzeFile, filter_exp))
        print(cap_general)

    def stc_createBasicDevice(self, portName, deviceName, **kargs):
        """
        函数功能:
            创建基本Device
        函数参数:
            @deviceName(str): device名称
            @portName(str): port名称
            @**kargs:
                @srcMAC(str): source MAC(00:10:94:00:00:01)
                @cvlan(tuple): CVLAN配置,(cvlan, pri)
                @svlan(tuple): SVLAN配置,(svlan, pri)
                @count(int): 创建device数量，MAC地址和IP同时递增
                @ipv4(tuple)： IPv4 地址(IPv4,网关）, 默认值（"192.18.10.1", "192.18.10.1")
                @ipv6(tuple): IPv6地址(IPv6,网关), 默认值（"2000::1", "2000::1")
        函数说明：
            2020/8/4 主要可以用于创建基本的Device, 
            TODO 待优化完善多个Device。
        """
        try:
            fhlog.logger.info("创建基本Device(port-{0}, device-{1})".format(portName, deviceName))
            # Create Device
            srcMacCount = kargs['count'] if 'count' in kargs.keys() else 1
            self._hDevices[deviceName] = self._stc.create(
                "EmulatedDevice", under=self._project, Name=deviceName, DeviceCount=srcMacCount,
                EnablePingResponse='True')

            # Ethernet header
            srcMAC = kargs['srcMAC'] if 'srcMAC' in kargs.keys() else "00:10:94:00:00:01"
            _hEthClientIf = self._stc.create(
                "EthIIIf", under=self._hDevices[deviceName],
                IsRange="TRUE", SourceMac=srcMAC, SrcMacRepeatCount=0, SrcMacStep="00:00:00:00:00:01",
                SrcMacStepMask="00:00:FF:FF:FF:FF")

            clientHeader = list()
            clientHeader.append(_hEthClientIf)
            # vlan header

            if 'svlan' in kargs.keys():
                _hSVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['svlan'][0],
                    Priority=kargs['svlan'][1])
                #  clientHeader["SVLAN"] = _hSVlanIf
                clientHeader.append(_hSVlanIf)

            if 'cvlan' in kargs.keys():
                _hCVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['cvlan'][0],
                    Priority=kargs['cvlan'][1])
                # clientHeader["CVLAN"] = _hCVlanIf
                clientHeader.append(_hCVlanIf)

            # ipv4 header
            if 'ipv4' in kargs.keys():
                _hIPv4ClientIf = self._stc.create(
                    "Ipv4If", under=self._hDevices[deviceName],
                    address=kargs['ipv4'][0],
                    gateway=kargs['ipv4'][1])
                # clientHeader["IPv4"] = _hIPv4ClientIf
                clientHeader.append(_hIPv4ClientIf)

            # ipv6 header
            if 'ipv6' in kargs.keys():
                _hIPv6ClientIf = self._stc.create(
                    "Ipv6If", under=self._hDevices[deviceName],
                    address=kargs['ipv6'][0],
                    gateway=kargs['ipv6'][0])
                # self._stc.config(self._hDevices[deviceName], **{'TopLevelIf-targets': _hIPv6ClientIf, 'PrimaryIf-targets': _hIPv6ClientIf})
                # clientHeader["IPv6"] = _hIPv6ClientIf
                clientHeader.append(_hIPv6ClientIf)

            for index in range(1, len(clientHeader)):
                fhlog.logger.debug("HEADER:%s" % clientHeader[index])
                self._stc.config(clientHeader[index], stackedOn=clientHeader[index-1])

            self._stc.config(
                self._hDevices[deviceName],
                **{'TopLevelIf-targets': clientHeader[-1],
                   'PrimaryIf-targets': clientHeader[-1]})

            # self._stc.config(_hIPv4ClientIf, **{"stackedOnEndpoint-targets":_hEthClientIf})
            self._stc.config(self._hDevices[deviceName], **{"AffiliationPort-targets": self._hPorts[portName]})
        except:
            raise FHSTCCmdError("stc_createBasicDevice", "创建Device失败", traceback.format_exc())

    def stc_createDHCPv4Client(self, portName, deviceName, **kargs):
        """
        函数功能:
            创建DHCP IPv4客户端
        函数参数:
            @deviceName(str): device名称
            @portName(str): port名称
            @**kargs:
                @srcMAC(str): source MAC(00:10:94:00:00:01)
                @cvlan(tuple): CVLAN配置,(cvlan, pri)
                @svlan(tuple): SVLAN配置,(svlan, pri)
                @count(int): 创建device数量，MAC地址和IP同时递增
                @ipv4(tuple)： IPv4 地址(IPv4,网关）, 默认值（"192.18.10.1", "192.18.10.1")
                @broadcast(bool): Enable/disable broadcast bit in DHCP control plane packets， 默认True
        函数说明：
            2020/8/4 主要可以用于创建基本的Device, 
            TODO 待优化完善多个Device。
        使用说明：
            stc_createDHCPv4Client('uplink', 'h1', srcMAC="00:00:00:00:00:01", cvlan=(102,1), svlan=(2001,4), count=4, ipv4=("192.168.20.1", "192.168.20.1"))
        """
        try:
            fhlog.logger.info("创建DHCP client")
            # Create Device
            srcMacCount = kargs['count'] if 'count' in kargs.keys() else 1
            self._hDevices[deviceName] = self._stc.create(
                "EmulatedDevice", under=self._project, Name=deviceName, DeviceCount=srcMacCount,
                EnablePingResponse='True')

            # Ethernet header
            srcMAC = kargs['srcMAC'] if 'srcMAC' in kargs.keys() else "00:10:94:00:00:01"
            _hEthClientIf = self._stc.create(
                "EthIIIf", under=self._hDevices[deviceName],
                IsRange="TRUE", SourceMac=srcMAC, SrcMacRepeatCount=0, SrcMacStep="00:00:00:00:00:01",
                SrcMacStepMask="00:00:FF:FF:FF:FF")

            clientHeader = list()
            clientHeader.append(_hEthClientIf)

            # vlan header
            if 'svlan' in kargs.keys():
                _hSVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['svlan'][0],
                    Priority=kargs['svlan'][1])
                clientHeader.append(_hSVlanIf)

            if 'cvlan' in kargs.keys():
                _hCVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['cvlan'][0],
                    Priority=kargs['cvlan'][1])
                clientHeader.append(_hCVlanIf)

            # ipv4 header
            ipv4Addr, ipv4gw = kargs['ipv4'] if 'ipv4' in kargs.keys() else ("192.18.0.1", "192.18.10.1")
            _hIPv4ClientIf = self._stc.create(
                "Ipv4If", under=self._hDevices[deviceName],
                address=ipv4Addr, gateway=ipv4gw)
            clientHeader.append(_hIPv4ClientIf)

            for index in range(1, len(clientHeader)):
                fhlog.logger.debug("HEADER:%s" % clientHeader[index])
                self._stc.config(clientHeader[index], stackedOn=clientHeader[index-1])

            self._stc.config(
                self._hDevices[deviceName],
                **{'TopLevelIf-targets': clientHeader[-1],
                   'PrimaryIf-targets': clientHeader[-1]})

            # 创建DHCP client
            if "broadcast" in kargs.keys() and kargs['broadcast']:
                broadcastFlag = "TRUE"
            else:
                broadcastFlag = "FALSE"
            _hDhcpIpv4Client = self._stc.create("Dhcpv4BlockConfig", under=self._hDevices[deviceName])
            self._stc.config(_hDhcpIpv4Client, UsesIf=_hIPv4ClientIf, EnableAutoRetry="True",
                             RetryAttempts=4, EnableRouterOption="True", UseBroadcastFlag=broadcastFlag)

            # self._hDHCPBlockConfig[deviceName] = _hDhcpIpv4Client
            # 绑定端口
            self._stc.config(self._hDevices[deviceName], **{"AffiliationPort-targets": self._hPorts[portName]})
        except:
            raise FHSTCCmdError("stc_createBasicDevice", "创建DHCP client失败", traceback.format_exc())

    def stc_createDHCPv4Server(self, portName, deviceName, **kargs):
        """
        函数功能:
            创建DHCP IPv4服务器
        函数参数:
            @deviceName(str): device名称
            @portName(str): port名称
            @**kargs:
                @srcMAC(str): source MAC(00:00:01:00:00:01)
                @cvlan(tuple): CVLAN配置,(cvlan, pri)
                @svlan(tuple): SVLAN配置,(svlan, pri)
                @count(int): 创建device数量，MAC地址和IP同时递增
                @ipv4(tuple): IPv4 地址(IPv4,网关）, 默认值（"10.185.10.1", "10.185.10.1")
                @pool(tuple): DHCP 服务器地址池, (startIP, mask, count)默认值（"10.185.10.2", 24, 253)
        函数说明:

        使用示例:
            fhstc.stc_createDHCPv4Server('uplink', 'h1', srcMAC="00:00:00:00:00:01", cvlan=(102,1), svlan=(2001,4), count=4, ipv4=("192.168.20.1", "192.168.20.1"), pool=("192.168.20.2", 24, 200))
        """
        try:
            fhlog.logger.info("创建DHCP Server")
            # Create Device
            srcMacCount = kargs['count'] if 'count' in kargs.keys() else 1
            self._hDevices[deviceName] = self._stc.create(
                "EmulatedDevice", under=self._project, Name=deviceName, DeviceCount=srcMacCount,
                EnablePingResponse='True')

            # Ethernet header
            srcMAC = kargs['srcMAC'] if 'srcMAC' in kargs.keys() else "00:00:01:00:00:01"
            _hEthClientIf = self._stc.create(
                "EthIIIf", under=self._hDevices[deviceName],
                IsRange="TRUE", SourceMac=srcMAC, SrcMacRepeatCount=0, SrcMacStep="00:00:00:00:00:01",
                SrcMacStepMask="00:00:FF:FF:FF:FF")

            clientHeader = list()
            clientHeader.append(_hEthClientIf)

            # vlan header
            if 'svlan' in kargs.keys():
                _hSVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['svlan'][0],
                    Priority=kargs['svlan'][1])
                clientHeader.append(_hSVlanIf)

            if 'cvlan' in kargs.keys():
                _hCVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['cvlan'][0],
                    Priority=kargs['cvlan'][1])
                clientHeader.append(_hCVlanIf)

            # ipv4 header
            ipv4Addr, ipv4gw = kargs['ipv4'] if 'ipv4' in kargs.keys() else ("10.185.10.1", "10.185.10.1")
            _hIPv4ClientIf = self._stc.create(
                "Ipv4If", under=self._hDevices[deviceName],
                address=ipv4Addr, gateway=ipv4gw)
            clientHeader.append(_hIPv4ClientIf)

            for index in range(1, len(clientHeader)):
                fhlog.logger.debug("HEADER:%s" % clientHeader[index])
                self._stc.config(clientHeader[index], stackedOn=clientHeader[index-1])

            self._stc.config(self._hDevices[deviceName], **{'TopLevelIf-targets': clientHeader[-1],
                                                            'PrimaryIf-targets': clientHeader[-1]})

            # 创建DHCP server
            # self._hDHCPv4Server = dict()
            _hDhcpv4ServerConfig = self._stc.create(
                "Dhcpv4ServerConfig", under=self._hDevices[deviceName],
                LeaseTime=1800, MinAllowedLeaseTime=60)
            _hDhcpv4ServerDefaultPool = self._stc.get(_hDhcpv4ServerConfig, "Children-Dhcpv4ServerDefaultPoolConfig")
            startIP, mask, count = kargs['pool'] if 'pool' in kargs.keys() else ("10.185.10.2", 24, 253)
            self._stc.config(_hDhcpv4ServerDefaultPool, StartIpList=startIP,
                             PrefixLength=mask, HostAddrCount=count, RouterList=ipv4Addr)
            self._stc.config(_hDhcpv4ServerConfig, UsesIf=_hIPv4ClientIf)

            # self._hDHCPBlockConfig[deviceName] = _hDhcpv4ServerConfig

            # 绑定端口
            self._stc.config(self._hDevices[deviceName], **{"AffiliationPort-targets": self._hPorts[portName]})
        except:
            raise FHSTCCmdError("stc_createBasicDevice", "创建DHCP Server失败", traceback.format_exc())

    def stc_startDevice(self, deviceName):
        """启动Device"""
        try:
            fhlog.logger.info("启动Device({})".format(deviceName))
            self._stc.perform("DeviceStart", DeviceList=self._hDevices[deviceName])
        except:
            raise FHSTCCmdError("stc_DeviceStart", "启动Device失败", traceback.format_exc())

    def stc_stopDevice(self, deviceName):
        """停止Device"""
        try:
            fhlog.logger.info("停止Device({})".format(deviceName))
            self._stc.perform("DeviceStop", DeviceList=self._hDevices[deviceName])
        except:
            raise FHSTCCmdError("stc_DeviceStop", "停止Device失败", traceback.format_exc())

    def stc_stopAllDevice(self):
        """停止所有device"""
        try:
            fhlog.logger.info("停止所有device")
            self._stc.perform("DevicesStartAll")
        except:
            raise FHSTCCmdError("stc_stopAllDevice", "所有device失败", traceback.format_exc())

    def stc_DHCPv4Bind(self, deviceName):
        """启动DHCP client, （DHCPv4Bind）"""
        _hDHCPv4BlockConfig = self._stc.get(self._hDevices[deviceName], "Children-Dhcpv4BlockConfig")
        self._stc.perform("Dhcpv4Bind", BlockList=_hDHCPv4BlockConfig)

    def stc_DHCPv4Release(self, deviceName):
        """释放DHCP client, （DHCPv4Release）"""
        _hDHCPv4BlockConfig = self._stc.get(self._hDevices[deviceName], "Children-Dhcpv4BlockConfig")
        self._stc.perform("Dhcpv4Release", BlockList=_hDHCPv4BlockConfig)

    def stc_startDHCPv4Server(self, deviceName):
        """启动DHCP server"""
        try:
            _hDhcpv4Server = self._stc.get(self._hDevices[deviceName], "children-Dhcpv4ServerConfig")
            self._stc.perform("Dhcpv4StartServer", ServerList=_hDhcpv4Server)
        except:
            raise FHSTCCmdError("stc_StartDHCPv4Server", "启动DHCP server失败", traceback.format_exc())

    def stc_stopDHCPv4Server(self, deviceName):
        """停止DHCP server"""
        try:
            fhlog.logger.info("停止DHCP Server")
            _hDhcpv4Server = self._stc.get(self._hDevices[deviceName], "children-Dhcpv4ServerConfig")
            # fhlog.logger.debug(_hDhcpv4Server)
            self._stc.perform("Dhcpv4StopServer", ServerList=_hDhcpv4Server)
        except:
            raise FHSTCCmdError("stc_stopDHCPv4Server", "停止DHCP server失败", traceback.format_exc())

    def stc_getDHCPv4BlockResult(self, deviceName):
        """
        函数功能：
            获取DHCP client Bound结果
        函数参数:
            @deviceName: deivce名称
        返回值:
                (CurrentBoundCount,CurrentIdleCount,TxDiscoverCount,TxRequestCount,RxOfferCount,RxAckCount,RxNakCount,TotalBoundCount,TotalFailedCount)
                # Todo 待优化

        """
        _hDHCPv4BlockConfig = self._stc.get(self._hDevices[deviceName], "Children-Dhcpv4BlockConfig")
        dhcpv4BlockResult = self._stc.get(_hDHCPv4BlockConfig, "Children-dhcpv4blockresults")
        dhcpResult = self._stc.get(dhcpv4BlockResult, "CurrentBoundCount")
        fhlog.logger.debug(dhcpResult)
        return dhcpResult

    def stc_dhcpv4SessionResults(self, deviceName):
        """
        功能：
            获取DHCP session详细结果
        参数：
            @deviceName: deivce名称
        返回值：
            DHCPv4Session格式：[（SessionState, ErrorStatus, Vpi, Vci, MacAddr, VlanId, InnerVlanId, Ipv4Addr, LeaseRx LeaseLeft, DiscRespTime, RequestRespTime）]
            例如：[('Bound', 'No error', '00:10:94:01:66:02', '1001', 'N/A', '192.85.10.2', '3600', '3594.25', '0.200554', '0.50158')]
        """
        try:
            fhlog.logger.info("获取DHCP Session结果")
            _hDHCPv4BlockConfig = self._stc.get(self._hDevices[deviceName], "Children-Dhcpv4BlockConfig")
            self._stc.perform("Dhcpv4SessionInfo", BlockList=_hDHCPv4BlockConfig)
            lstDhcpv4SessionResults = self._stc.get(_hDHCPv4BlockConfig, "children-dhcpv4sessionresults")
            dhcpv4SessionResults = []
            for hDhcpv4SessionResult in lstDhcpv4SessionResults.split():
                lstDhcpSessionInfo = self._stc.get(hDhcpv4SessionResult, "SessionInfo")
                # print(lstDhcpSessionInfo)
                fhlog.logger.debug(lstDhcpSessionInfo)
                dhcpv4SessionResults.append(tuple(lstDhcpSessionInfo.split(",")[3:-3]))
            fhlog.logger.debug(dhcpv4SessionResults)
            return dhcpv4SessionResults
        except:
            raise FHSTCCmdError('set_dhcpv4SessionResults', "获取DHCP Session结果失败", traceback.format_exc())

    def stc_createPPPoEv4Server(self, portName, deviceName, **kargs):
        """
        函数功能:
            创建PPPPoEv4 Server
        函数参数:
            @deviceName(str): device名称
            @portName(str): port名称
            @**kargs:
                @srcMAC(str): source MAC,默认值00:00:01:00:00:01
                @cvlan(tuple): CVLAN配置, 格式为(cvlan, pri)
                @svlan(tuple): SVLAN配置, 格式为(svlan, pri)
                @count(int): 创建device数量，MAC地址和IP同时递增
                @ipv4(tuple): IPv4 地址，格式为(IPv4,网关）, 默认值（"10.185.10.2", "10.185.10.100")
                @pool(tuple): PPPoE 服务器地址池, 格式：(poolStartIP, PrefixLength)，默认值（"10.185.10.100", 24)
                @AuthType(str): None,PAP,CHAP_MD5,AUTO
                @sessionId(int): session ID, 默认值为0
                @username(str): PPPoE 拨号用户名
                @password(str): PPPoE 拨号密码
        函数说明:

        使用示例:
            fhstc.stc_createPPPoEv4Server('uplink', 'h1', srcMAC="00:00:00:00:00:01", cvlan=(102,1), svlan=(2001,4), count=4, ipv4=("192.168.20.1", "192.168.20.1"), pool=("10.185.10.1","10.185.10.2", 24))
        """
        try:
            fhlog.logger.info("创建PPPoE Server")
            # Create Device
            srcMacCount = kargs['count'] if 'count' in kargs.keys() else 1
            self._hDevices[deviceName] = self._stc.create(
                "EmulatedDevice", under=self._project, Name=deviceName, DeviceCount=srcMacCount,
                EnablePingResponse='True')

            # Ethernet header
            srcMAC = kargs['srcMAC'] if 'srcMAC' in kargs.keys() else "00:00:01:00:00:01"
            _hEthClientIf = self._stc.create(
                "EthIIIf", under=self._hDevices[deviceName],
                IsRange="TRUE", SourceMac=srcMAC, SrcMacRepeatCount=0, SrcMacStep="00:00:00:00:00:01",
                SrcMacStepMask="00:00:FF:FF:FF:FF")

            hIf = list()
            hIf.append(_hEthClientIf)

            # vlan header
            if 'svlan' in kargs.keys():
                _hSVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['svlan'][0],
                    Priority=kargs['svlan'][1])
                hIf.append(_hSVlanIf)

            if 'cvlan' in kargs.keys():
                _hCVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['cvlan'][0],
                    Priority=kargs['cvlan'][1])
                hIf.append(_hCVlanIf)

            # pppoe header
            sessionId = kargs['sessionId'] if 'sessionId' in kargs.keys() else 0
            _hPppoeIf = self._stc.create(
                "PppoeIf", under=self._hDevices[deviceName],
                SessionId=sessionId, SessionIdStep=1)
            hIf.append(_hPppoeIf)
            # ppp header
            _hPPPIf = self._stc.create("PppIf", under=self._hDevices[deviceName])
            hIf.append(_hPPPIf)

            # ipv4 header
            ipv4Addr, ipv4gw = kargs['ipv4'] if 'ipv4' in kargs.keys() else ("10.185.10.1", "10.185.10.100")
            _hIPv4ClientIf = self._stc.create(
                "Ipv4If", under=self._hDevices[deviceName],
                address=ipv4Addr, gateway=ipv4gw)
            hIf.append(_hIPv4ClientIf)

            for index in range(1, len(hIf)):
                fhlog.logger.debug("HEADER:%s" % hIf[index])
                self._stc.config(hIf[index], stackedOn=hIf[index-1])

            authType = kargs['authType'] if 'authType' in kargs.keys() else 'AUTO'
            self._stc.config(
                self._hDevices[deviceName],
                **{'TopLevelIf-targets': hIf[-1],
                   'PrimaryIf-targets': hIf[-1]})

            username = kargs['username'] if 'username' in kargs.keys() else "fiberhome"
            password = kargs['password'] if 'password' in kargs.keys() else "fiberhome"

            _hPPPoeServerBlockConfig = self._stc.create(
                'PppoeServerBlockConfig', under=self._hDevices[deviceName],
                Authentication=authType, UserName=username, Password=password)

            # self._hPPPoXBlockConfig[deviceName] = _hPPPoeServerBlockConfig

            _hPPPoeServerPool = self._stc.get(_hPPPoeServerBlockConfig, "children-PppoeServerIpv4PeerPool")
            pool = (ipv4Addr, *kargs['pool']) if 'pool' in kargs.keys() else (ipv4Addr, "10.185.10.100", 24)
            pool_dict = dict(zip(('Ipv4PeerPoolAddr', 'StartIpList', 'PrefixLength'), pool))
            self._stc.config(_hPPPoeServerPool, **pool_dict)

            # set device as server
            _hpppoxPortConfig = self._stc.get(self._hPorts[portName], "Children-PppoxPortConfig")
            self._stc.config(_hpppoxPortConfig, EmulationType='SERVER')

            self._stc.config(self._hDevices[deviceName], AffiliatedPort=self._hPorts[portName])
        except:
            raise FHSTCCmdError("stc_createPPPoEv4Server", "创建PPPoE Server失败", traceback.format_exc())

    def stc_createPPPoEv4Client(self, portName, deviceName, **kargs):
        """
        函数功能:
            创建PPPPoEv4 Client
        函数参数:
            @portName(str): port名称
            @deviceName(str): device名称
            @**kargs:
                @srcMAC(str): source MAC,默认值00:01:94:00:00:01
                @cvlan(tuple): CVLAN配置, 格式为(cvlan, pri)
                @svlan(tuple): SVLAN配置, 格式为(svlan, pri)
                @count(int): 创建device数量，MAC地址和IP同时递增
                @ipv4(tuple): IPv4 地址，格式为(IPv4,网关）, 默认值（"10.190.185.1", "10.190.185.1")
                @AuthType(str): None,PAP,CHAP_MD5,AUTO
                @sessionId(int): session ID, 默认值为0
                @username(str): PPPoE 拨号用户名
                @password(str): PPPoE 拨号密码
        函数说明:

        使用示例:
            fhstc.stc_createPPPoEv4Server('uplink', 'h1', srcMAC="00:00:00:00:00:01", cvlan=(102,1), svlan=(2001,4), count=4, ipv4=("192.168.20.1", "192.168.20.1"), pool=("10.185.10.1","10.185.10.2", 24))
        """
        try:
            fhlog.logger.info("创建PPPoE Server")
            # Create Device
            srcMacCount = kargs['count'] if 'count' in kargs.keys() else 1
            self._hDevices[deviceName] = self._stc.create(
                "EmulatedDevice", under=self._project, Name=deviceName, DeviceCount=srcMacCount,
                EnablePingResponse='True')

            # Ethernet header
            srcMAC = kargs['srcMAC'] if 'srcMAC' in kargs.keys() else "00:01:94:00:00:01"
            _hEthClientIf = self._stc.create(
                "EthIIIf", under=self._hDevices[deviceName],
                IsRange="TRUE", SourceMac=srcMAC, SrcMacRepeatCount=0, SrcMacStep="00:00:00:00:00:01",
                SrcMacStepMask="00:00:FF:FF:FF:FF")

            hIf = list()
            hIf.append(_hEthClientIf)

            # vlan header
            if 'svlan' in kargs.keys():
                _hSVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['svlan'][0],
                    Priority=kargs['svlan'][1])
                hIf.append(_hSVlanIf)

            if 'cvlan' in kargs.keys():
                _hCVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['cvlan'][0],
                    Priority=kargs['cvlan'][1])
                hIf.append(_hCVlanIf)

            # pppoe header
            sessionId = kargs['sessionId'] if 'sessionId' in kargs.keys() else 0
            _hPppoeIf = self._stc.create(
                "PppoeIf", under=self._hDevices[deviceName],
                SessionId=sessionId, SessionIdStep=1)
            hIf.append(_hPppoeIf)
            # ppp header
            _hPPPIf = self._stc.create("PppIf", under=self._hDevices[deviceName])
            hIf.append(_hPPPIf)
            # ipv4 header
            ipv4Addr, ipv4gw = kargs['ipv4'] if 'ipv4' in kargs.keys() else ("10.190.185.1", "10.190.185.1")
            _hIPv4ClientIf = self._stc.create(
                "Ipv4If", under=self._hDevices[deviceName],
                address=ipv4Addr, gateway=ipv4gw)
            hIf.append(_hIPv4ClientIf)

            for index in range(1, len(hIf)):
                fhlog.logger.debug("HEADER:%s" % hIf[index])
                self._stc.config(hIf[index], stackedOn=hIf[index-1])

            authType = kargs['authType'] if 'authType' in kargs.keys() else 'CHAP_MD5'
            self._stc.config(
                self._hDevices[deviceName],
                **{'TopLevelIf-targets': hIf[-1],
                   'PrimaryIf-targets': hIf[-1]})
            username = kargs['username'] if 'username' in kargs.keys() else "fiberhome"
            password = kargs['password'] if 'password' in kargs.keys() else "fiberhome"
            _hPPPoeClientBlockConfig = self._stc.create(
                'PppoeClientBlockConfig', under=self._hDevices[deviceName],
                Authentication=authType, UserName=username, Password=password)
            # self._hPPPoXBlockConfig[deviceName] = _hPPPoeClientBlockConfig

            self._stc.config(self._hDevices[deviceName], AffiliatedPort=self._hPorts[portName])
        except:
            raise FHSTCCmdError("stc_createPPPoEv4Server", "创建PPPoE Client失败", traceback.format_exc())

    def stc_PPPoEv4Connect(self, deviceName):
        """PPPoE Connect"""
        try:
            deviceChildren = self._stc.get(self._hDevices[deviceName], 'Children')
            _hPPPoXBlockConfig = deviceChildren.split()[-1]
            fhlog.logger.debug("PPPoXBlocConfig:%s" % _hPPPoXBlockConfig)
            self._stc.perform("PppoxConnect", BlockList=_hPPPoXBlockConfig, ControlType="CONNECT")
        except:
            raise FHSTCCmdError("stc_PPPoEv4Connect", "PPPoE Connect 失败", traceback.format_exc())

    def stc_PPPoEv4Disconnect(self, deviceName):
        """PPPoE Connect"""
        try:
            deviceChildren = self._stc.get(self._hDevices[deviceName], 'Children')
            _hPPPoXBlockConfig = deviceChildren.split()[-1]
            fhlog.logger.debug("PPPoXBlocConfig:%s" % _hPPPoXBlockConfig)
            self._stc.perform("PppoxDisconnect", BlockList=_hPPPoXBlockConfig)
        except:
            raise FHSTCCmdError("stc_PPPoEv4Connect", "PPPoE Disconnect 失败", traceback.format_exc())

    def stc_getPPPoEServerStatus(self, deviceName):
        """
        函数功能：
            获取PPPoE Server 连接状态
        函数参数：
            @deviceName(str): device名称
        返回值:
            dict(), 格式为 
            {'parent': 'pppoeclientblockconfig1', 'Name': '{}', 'PppoeSessionId': '1', 'PeerMacAddr': '00:10:94:01:66:0a', 
            'TxPadtCount': '0', 'RxPadtCount': '0', 'TxPadiCount': '1', 'RxPadoCount': '1', 'TxPadrCount': '1', 'RxPadsCount': '1', 
            'RxPadiCount': '0', 'TxPadoCount': '0', 'RxPadrCount': '0', 'TxPadsCount': '0', 'MacAddr': '00:10:94:01:66:08', 
            'VlanId': '1002', 'InnerVlanId': '1002', 'SessionState': 'CONNECTED', 'Ipv4CpSessionState': 'CONNECTED', 
            'Ipv6CpSessionState': 'IDLE', 'FailureCode': 'NULL', 'Ipv4CpFailureCode': 'NULL', 'Ipv6CpFailureCode': 'NULL', 
            'Ipv4Addr': '192.0.1.0', 'PeerIpv4Addr': '192.85.1.3', 'Ipv6Addr': '::', 'Ipv6GlobalAddr': '::', 
            'Ipv6GlobalAddrResolveState': 'NONE', 'PeerIpv6Addr': '::', 'SetupTime': '993', 'AttemptedCount': '1', 'RetryCount': '0',
            'ConnectedSuccessCount': '1', 'DisconnectedSuccessCount': '0', 'FailedConnectCount': '0', 'FailedDisconnectCount': '0', 
            'TxLcpConfigRequestCount': '1', 'RxLcpConfigRequestCount': '1', 'TxLcpConfigRejectCount': '0', 'RxLcpConfigRejectCount': '0', 
            'TxLcpConfigAckCount': '1', 'RxLcpConfigAckCount': '1', 'TxLcpConfigNakCount': '0', 'RxLcpConfigNakCount': '0', 
            'TxLcpTermRequestCount': '0', 'RxLcpTermRequestCount': '0', 'TxLcpTermAckCount': '0', 'RxLcpTermAckCount': '0',
            'TxLcpEchoRequestCount': '0', 'RxLcpEchoRequestCount': '0', 'TxLcpEchoReplyCount': '0', 'RxLcpEchoReplyCount': '0', 
            'TxIpcpCount': '3', 'RxIpcpCount': '3', 'TxIpv6cpCount': '0', 'RxIpv6cpCount': '0', 'TxPapCount': '0', 'RxPapCount': '0',
            'TxChapCount': '1', 'RxChapCount': '2', 'Active': 'true'}
        """
        try:
            fhlog.logger.info("获取PPPoE服务器(%s)连接状态" % deviceName)
            hPPPoeServerBlockConfig = self._stc.get(self._hDevices[deviceName], 'Children-PPPoeServerBlockConfig')
            fhlog.logger.debug(hPPPoeServerBlockConfig)
            self._stc.perform("PppoxShowSessionInfo", blockList=hPPPoeServerBlockConfig)
            hSessionResult = self._stc.get(hPPPoeServerBlockConfig, "children-PppoeSessionResults")
            fhlog.logger.debug(hSessionResult)
            pppoeResult = self._stc.get(hSessionResult)
            pppoeResult = pppoeResult.split()
            key = list(map(lambda x: x[1:], pppoeResult[0:-1:2]))
            value = pppoeResult[1:len(pppoeResult):2]
            return dict(zip(key, value))
        except:
            raise FHSTCCmdError("stc_getPPPoEServerStatus", "获取PPPoE server 状态 失败", traceback.format_exc())

    def stc_getPPPoEClientStatus(self, deviceName):
        """
        函数功能：
            获取PPPoE Client 连接状态
        函数参数：
            @deviceName(str): device名称
        返回值:
            dict(), 格式为
            {'parent': 'pppoeclientblockconfig1', 'Name': '{}', 'PppoeSessionId': '1', 'PeerMacAddr': '00:10:94:01:66:0a', 
            'TxPadtCount': '0', 'RxPadtCount': '0', 'TxPadiCount': '1', 'RxPadoCount': '1', 'TxPadrCount': '1', 'RxPadsCount': '1', 
            'RxPadiCount': '0', 'TxPadoCount': '0', 'RxPadrCount': '0', 'TxPadsCount': '0', 'MacAddr': '00:10:94:01:66:08', 
            'VlanId': '1002', 'InnerVlanId': '1002', 'SessionState': 'CONNECTED', 'Ipv4CpSessionState': 'CONNECTED', 
            'Ipv6CpSessionState': 'IDLE', 'FailureCode': 'NULL', 'Ipv4CpFailureCode': 'NULL', 'Ipv6CpFailureCode': 'NULL', 
            'Ipv4Addr': '192.0.1.0', 'PeerIpv4Addr': '192.85.1.3', 'Ipv6Addr': '::', 'Ipv6GlobalAddr': '::', 
            'Ipv6GlobalAddrResolveState': 'NONE', 'PeerIpv6Addr': '::', 'SetupTime': '993', 'AttemptedCount': '1', 'RetryCount': '0',
            'ConnectedSuccessCount': '1', 'DisconnectedSuccessCount': '0', 'FailedConnectCount': '0', 'FailedDisconnectCount': '0', 
            'TxLcpConfigRequestCount': '1', 'RxLcpConfigRequestCount': '1', 'TxLcpConfigRejectCount': '0', 'RxLcpConfigRejectCount': '0', 
            'TxLcpConfigAckCount': '1', 'RxLcpConfigAckCount': '1', 'TxLcpConfigNakCount': '0', 'RxLcpConfigNakCount': '0', 
            'TxLcpTermRequestCount': '0', 'RxLcpTermRequestCount': '0', 'TxLcpTermAckCount': '0', 'RxLcpTermAckCount': '0',
            'TxLcpEchoRequestCount': '0', 'RxLcpEchoRequestCount': '0', 'TxLcpEchoReplyCount': '0', 'RxLcpEchoReplyCount': '0', 
            'TxIpcpCount': '3', 'RxIpcpCount': '3', 'TxIpv6cpCount': '0', 'RxIpv6cpCount': '0', 'TxPapCount': '0', 'RxPapCount': '0',
            'TxChapCount': '1', 'RxChapCount': '2', 'Active': 'true'}
        """
        try:
            fhlog.logger.info("获取PPPoE客户端(%s)连接状态" % deviceName)
            hPPPoeClientBlockConfig = self._stc.get(self._hDevices[deviceName], 'Children-PPPoeClientBlockConfig')
            fhlog.logger.debug(hPPPoeClientBlockConfig)
            self._stc.perform("PppoxShowSessionInfo", blockList=hPPPoeClientBlockConfig)
            hSessionResult = self._stc.get(hPPPoeClientBlockConfig, "children-PppoeSessionResults")
            fhlog.logger.debug(hSessionResult)
            pppoeResult = self._stc.get(hSessionResult)
            fhlog.logger.debug(pppoeResult)
            pppoeResult = pppoeResult.split()
            key = list(map(lambda x: x[1:], pppoeResult[0:-1:2]))
            value = pppoeResult[1:len(pppoeResult):2]
            return dict(zip(key, value))
        except:
            raise FHSTCCmdError("stc_getPPPoEClientStatus", "获取PPPoE client 状态 失败", traceback.format_exc())

    def stc_getPPPoESimpleResult(self, deviceName):
        """
        函数功能：
            获取PPPoE连接状态
        函数参数：
            @deviceName(str): device名称
        返回值:
            str, 可能的返回值有：NONE，IDLE，CONNECTING，CONNECTED，DISCONNECTING，TERMINATING
        """
        try:
            deviceChildren = self._stc.get(self._hDevices[deviceName], 'Children')
            _hPPPoXBlockConfig = deviceChildren.split()[-1]
            pppoeResult = self._stc.get(_hPPPoXBlockConfig, "BlockState")

            return pppoeResult
        except:
            raise FHSTCCmdError("stc_getPPPoESimpleResult", "获取PPPoE连接状态 失败", traceback.format_exc())

    def stc_createIGMPServer(self, portName, deviceName, **kargs):
        """
        功能：
            创建IGMP server for qurier
        参数：
            @portName：
            @deviceName：
            @kargs:
                @srcMAC(str): source MAC,默认值00:01:94:00:00:01
                @cvlan(tuple): CVLAN配置, 格式为(cvlan, pri)
                @svlan(tuple): SVLAN配置, 格式为(svlan, pri)
                @count(int): 创建device数量，MAC地址和IP同时递增
                @ipv4(tuple): IPv4 地址，格式为(IPv4,网关,掩码）, 默认值（"10.190.185.1", "10.190.185.1", 24)
                @version(int): IGMP version(V1/V2/V3)
                @query(int): 查询周期，默认125
                @robustnesss(int): 查询次数，默认2
                @lastQuery(int): 特定组查询次数，默认为2
        返回值：None
        说明：	
        """
        try:
            fhlog.logger.info("创建IGMP Server")
            # Create Device
            srcMacCount = kargs['count'] if 'count' in kargs.keys() else 1
            self._hDevices[deviceName] = self._stc.create(
                "EmulatedDevice", under=self._project, Name=deviceName, DeviceCount=srcMacCount,
                EnablePingResponse='True')

            # Ethernet header
            srcMAC = kargs['srcMAC'] if 'srcMAC' in kargs.keys() else "00:01:94:00:00:01"
            _hEthClientIf = self._stc.create(
                "EthIIIf", under=self._hDevices[deviceName],
                IsRange="TRUE", SourceMac=srcMAC, SrcMacRepeatCount=0, SrcMacStep="00:00:00:00:00:01",
                SrcMacStepMask="00:00:FF:FF:FF:FF")

            hIf = list()
            hIf.append(_hEthClientIf)

            # vlan header
            if 'svlan' in kargs.keys():
                _hSVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['svlan'][0],
                    Priority=kargs['svlan'][1])
                hIf.append(_hSVlanIf)

            if 'cvlan' in kargs.keys():
                _hCVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['cvlan'][0],
                    Priority=kargs['cvlan'][1])
                hIf.append(_hCVlanIf)

            # ipv4 header
            ipv4Addr, ipv4gw, mask = kargs['ipv4'] if 'ipv4' in kargs.keys() else ("10.190.185.1", "10.190.185.1", 24)
            _hIPv4If = self._stc.create(
                "Ipv4If", under=self._hDevices[deviceName],
                address=ipv4Addr, gateway=ipv4gw, PrefixLength=mask)
            hIf.append(_hIPv4If)

            for index in range(1, len(hIf)):
                fhlog.logger.debug("HEADER:%s" % hIf[index])
                self._stc.config(hIf[index], stackedOn=hIf[index-1])
            self._stc.config(self._hDevices[deviceName], TopLevelIf=_hIPv4If, PrimaryIf=_hIPv4If)

            version = kargs['version'] if 'version' in kargs.keys() else 2
            queryInterval = kargs['query'] if 'query' in kargs.keys() else 125
            robustnessVariable = kargs['robustness'] if 'robustness' in kargs.keys() else 2
            lastMemberQueryCount = kargs['lastQuery'] if 'lastQuery' in kargs.keys() else 2

            hIgmpRouterConfig = self._stc.create("IgmpRouterConfig", under=self._hDevices[deviceName])
            self._stc.config(hIgmpRouterConfig, Version='IGMP_V%d' % version, QueryInterval=queryInterval,
                             RobustnessVariable=robustnessVariable, LastMemberQueryCount=lastMemberQueryCount)

            self._stc.config(hIgmpRouterConfig, UsesIf=_hIPv4If)
            self._stc.config(self._hDevices[deviceName], AffiliatedPort=self._hPorts[portName])
        except:
            raise FHSTCCmdError("stc_createIGMPServer", "创建IGMP server 失败", traceback.format_exc())

    def stc_createIGMPClient(self, portName, deviceName, **kargs):
        """
        功能：
            创建IGMP Client
        参数：
            @portName：
            @deviceName：
            @kargs:
                @srcMAC(str): source MAC,默认值00:01:94:00:00:01
                @cvlan(tuple): CVLAN配置, 格式为(cvlan, pri)
                @svlan(tuple): SVLAN配置, 格式为(svlan, pri)
                @count(int): 创建device数量，MAC地址和IP同时递增
                @ipv4(tuple): IPv4 地址，格式为(IPv4,网关,掩码）, 默认值（"10.190.185.1", "10.190.185.1", 24)
                @version(int): IGMP version(V1/V2/V3)， 默认为2
                @membership(str): IGMP组地址，格式(StartIpList,AddrIncrement,NetworkCount,PrefixLength), 
                                    默认("225.0.0.1", 1, 10, 24)
        返回值：None
        说明：	
        """
        try:
            fhlog.logger.info("创建IGMP client")
            # Create Device
            srcMacCount = kargs['count'] if 'count' in kargs.keys() else 1
            self._hDevices[deviceName] = self._stc.create(
                "EmulatedDevice", under=self._project, Name=deviceName, DeviceCount=srcMacCount,
                EnablePingResponse='True')

            # Ethernet header
            srcMAC = kargs['srcMAC'] if 'srcMAC' in kargs.keys() else "00:01:94:00:00:01"
            _hEthClientIf = self._stc.create(
                "EthIIIf", under=self._hDevices[deviceName],
                IsRange="TRUE", SourceMac=srcMAC, SrcMacRepeatCount=0, SrcMacStep="00:00:00:00:00:01",
                SrcMacStepMask="00:00:FF:FF:FF:FF")

            hIf = list()
            hIf.append(_hEthClientIf)

            # vlan header
            if 'svlan' in kargs.keys():
                _hSVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['svlan'][0],
                    Priority=kargs['svlan'][1])
                hIf.append(_hSVlanIf)

            if 'cvlan' in kargs.keys():
                _hCVlanIf = self._stc.create(
                    'VlanIf', under=self._hDevices[deviceName],
                    Tpid=33024, VlanId=kargs['cvlan'][0],
                    Priority=kargs['cvlan'][1])
                hIf.append(_hCVlanIf)

            # ipv4 header
            ipv4Addr, ipv4gw, mask = kargs['ipv4'] if 'ipv4' in kargs.keys() else ("10.190.185.1", "10.190.185.1", 24)
            _hIPv4If = self._stc.create(
                "Ipv4If", under=self._hDevices[deviceName],
                address=ipv4Addr, gateway=ipv4gw, PrefixLength=mask)
            hIf.append(_hIPv4If)

            for index in range(1, len(hIf)):
                fhlog.logger.debug("HEADER:%s" % hIf[index])
                self._stc.config(hIf[index], stackedOn=hIf[index-1])
            self._stc.config(self._hDevices[deviceName], TopLevelIf=_hIPv4If, PrimaryIf=_hIPv4If)

            version = kargs['version'] if 'version' in kargs.keys() else 2
            # robustnessVariable = kargs['queryInterval'] if 'queryInterval' in kargs.keys() else 2

            hIgmpHostConfig = self._stc.create("IgmpHostConfig", under=self._hDevices[deviceName])
            self._stc.config(hIgmpHostConfig, Version='IGMP_V%d' % version)
            self._stc.config(hIgmpHostConfig, UsesIf=_hIPv4If)

            hIgmpGroupMembership = self._stc.create("IgmpGroupMembership", under=hIgmpHostConfig)
            

            hIpv4Group = self._stc.create("Ipv4Group", under=self._project)
            hIpv4NetworkBlockGroup = self._stc.get(hIpv4Group, "children-Ipv4NetworkBlock")
            if 'membership' in kargs.keys():
                if isinstance(kargs['membership'], str):
                    membership = (kargs['membership'], 1, 1, 24)
                else:
                    membership = kargs['membership']
            else:
                membership = ("225.0.0.1", 1, 10, 24)

            self._stc.config(hIpv4NetworkBlockGroup, **
                             dict(zip(('StartIpList', 'AddrIncrement', 'NetworkCount', 'PrefixLength'), membership)))
            
            # if 'membership' in kargs.keys():
            #     for group in kargs['membership'].split(","):


            self._stc.config(hIgmpGroupMembership, MulticastGroup=hIpv4Group)

            self._stc.config(self._hDevices[deviceName], AffiliatedPort=self._hPorts[portName])
        except:
            raise FHSTCCmdError("stc_createIGMPServer", "创建IGMP server 失败", traceback.format_exc())

    def stc_igmpJoin(self, deviceName):
        """组播组加入"""
        try:
            fhlog.logger.info("加入组播组")
            hIgmpHostConfig = self._stc.get(self._hDevices[deviceName], "Children-IgmpHostConfig")
            self._stc.perform("IgmpMldJoinGroups", BlockList=hIgmpHostConfig)
        except:
            raise FHSTCCmdError("stc_igmpJoin", "加入组播组 失败", traceback.format_exc())

    def stc_igmpLeave(self, deviceName):
        """组播组离开"""
        try:
            fhlog.logger.info("离开组播组")
            hIgmpHostConfig = self._stc.get(self._hDevices[deviceName], "Children-IgmpHostConfig")
            self._stc.perform("IgmpMldLeaveGroups", BlockList=hIgmpHostConfig)
        except:
            raise FHSTCCmdError("stc_igmpJoin", "离开组播组 失败", traceback.format_exc())

    def stc_startARP(self,  objName: str):
        """
        功能：
            开启ARP
        参数：
            objName(str): device或者stream名称
        返回值：None
        说明：	
        """
        try:
            fhlog.logger.info("启动ARP（%s)" % objName)
            if objName in self._hDevices.keys():
                self._stc.perform("ArpNdStart", HandleList=self._hDevices[objName])
            if objName in self._hStreamBlock.keys():
                self._stc.perform("ArpNdStart", HandleList=self._hStreamBlock[objName])
        except:
            raise FHSTCCmdError("stc_startARP", "开启ARP 失败", traceback.format_exc())

    def stc_stopARP(self, objName: str):
        """
        功能：
            停止ARP
        参数：
            objName(str): device或者stream名称
        返回值：None
        说明：	
        """
        try:
            fhlog.logger.info("停止ARP（%s)" % objName)
            if objName in self._hDevices.keys():
                self._stc.perform("ArpNdStop", HandleList=self._hDevices[objName])
            if objName in self._hStreamBlock.keys():
                self._stc.perform("ArpNdStop", HandleList=self._hStreamBlock[objName])
        except:
            raise FHSTCCmdError("stc_startDeviceARP", "停止ARP 失败", traceback.format_exc())

    def stc_getDeviceARPResult(self, deviceName):
        """
        功能：
            获取ARP解析结果
        参数：

        返回值：None
        说明：	
        """
        try:
            arpstate = bool("RESOLVE_DONE" == self._stc.get(
                self._hDevices[deviceName],
                "Ipv4If.GatewayMacResolveState"))
            if arpstate:
                return self._stc.get(self._hDevices[deviceName], "Ipv4If.GatewayMac")
            else:
                return None
        except:
            raise FHSTCCmdError("stc_getDeviceARPResult", "获取ARP解析结果", traceback.format_exc())
