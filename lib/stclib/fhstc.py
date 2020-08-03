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
    def __init__(self, stcip):
        self._stc = STC(tcl=settings.TCL_PATH, stcpath=settings.STC_PATH)
        self._stcip = stcip
        self._project = "project1"
        self._ports = dict()
        self._hPorts = dict()
        self._hStreamBlock = dict()
        self._hDevices = dict()

    def __del__(self):
        del self._stc
        # pass

    def stc_init(self, path=None):
        """ 初始化仪表, 导入仪表库文件 """
        try:
            fhlog.logger.info("初始化仪表，导入仪表库文件")
            self._stc.load_stc_lib()
        except:
            raise FHSTCCmdError('stc_init', '初始化仪表失败', traceback.format_exc())

    def stc_connect(self):
        """连接STC仪表"""
        try:
            fhlog.logger.info("连接仪表STC,仪表IP(%s)" % self._stcip)
            self._stc.connect(self._stcip)
        except:
            raise FHSTCCmdError('stc_connect', '连接仪表失败.', traceback.format_exc())

    def stc_disconnect(self):
        """端口仪表连接"""
        try:
            fhlog.logger.info("断开仪表连接")
            self._stc.disconnect(self._stcip)
        except:
            raise FHSTCCmdError('stc_disconnect', '断开仪表失败.', traceback.format_exc())

    def stc_apply(self):
        try:
            fhlog.logger.info("Apply仪表配置")
            self._stc.apply()
        except:
            raise FHSTCCmdError('stc_apply', 'Apply仪表配置失败.', traceback.format_exc())

    def stc_createProject(self):
        """创建仪表根工程名称"""
        try:
            fhlog.logger.info("创建仪表操作工程")
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
        except:
            raise FHSTCCmdError('stc_createPorts', '初始化端口失败', stderr=traceback.format_exc())

    def stc_modify_port(self, portName:str, ethernetType:str, **portSpeed):
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
                self._stc.release(tuple(self._ports.values()))
            else:
                self._stc.release((self._ports[portName],))
        except Exception as err:
            raise FHSTCCmdError("stc_release", "释放端口失败")

    def stc_autoAttachPorts(self, **kargs):
        """绑定端口属性，并连接端口"""
        try:
            self._stc.perform("AttachPorts", **kargs)
        except Exception as err:
            raise FHSTCCmdError('stc_autoAttachPorts', '绑定端口失败', traceback.format_exc())

    def stc_createTrafficRaw(self, streamName: str, portName: str, **kargs):
        """
        函数功能: 
            创建裸流
        函数参数:
            @portName: 创建数据流的仪表端口命令
            @streamName: 数据流名称
            @param **kargs(dict):
                frameLengthMode：报文长度模式
                FixedFrameLength：报文长度为Fixed模式，报文长度
                Load: 流量大小
                LoadUnit: 流量单位
                srcMac:源MAC地址，默认值00:00:10:00:00:01
                dstMac:目的MAC地址，默认值00:00:94:00:00:01

                cvlan(tuple): CVLAN, 格式为(cvlan-id, cvlan-pri)
                svlan(tuple):SVLAN, 格式为(svlan-id, svlan-pri)
                IPv4(tuple): IPv4报文头, 格式为(srcIPv4, dstIpv4, gateway)

                IPv6(tuple): #TODO

        返回值: None

        使用说明:
        """
        try:
            fhlog.logger.info("创建数据流，端口名称-{0},数据流名称-{1}".format(portName, streamName))

            if '_ports' in self.__dict__.keys() and portName not in self._ports.keys():
                fhlog.logger.error("port %s not reserved!!!" % self._ports[portName])
                exit(-1)

            keys = kargs.keys()
            # 设置数据流基本属性
            stream_basic = dict()
            stream_basic['insertSig'] = kargs['insertSig'] if 'insertSig' in keys else 'True'
            stream_basic['frameConfig'] = ' "" '
            stream_basic['Name'] = streamName
            stream_basic['frameLengthMode'] = kargs['frameLengthMode'] if 'frameLengthMode' in keys else 'FIXED'
            stream_basic['FixedFrameLength'] = kargs['FixedFrameLength'] if 'FixedFrameLength' in keys else '512'
            stream_basic['MaxFrameLength'] = kargs['MaxFrameLength'] if 'MaxFrameLength' in keys else '1518'
            stream_basic['Load'] = kargs['Load'] if 'Load' in keys else '100'
            stream_basic['LoadUnit'] = kargs['LoadUnit'] if 'LoadUnit' in keys else 'MEGABITS_PER_SECOND'
            if '_hStreamBlock' not in self.__dict__.keys():
                self._hStreamBlock = dict()
            self._hStreamBlock[streamName] = self._stc.create(
                'streamBlock', under=self._hPorts[portName], **stream_basic)

            # L2 header
            srcMac = kargs['srcMac'] if 'srcMac' in keys else '00:00:10:00:00:01'
            dstMac = kargs['dstMac'] if 'dstMac' in keys else '00:10:94:00:00:01'
            # hEthernet = 'hEthernet_%s' % streamName
            if '_hEthernet' not in self.__dict__.keys():
                self._hEthernet = dict()
            self._hEthernet[streamName] = self._stc.create('ethernet:EthernetII', under=self._hStreamBlock[streamName],
                                                           srcMac=srcMac, dstMac=dstMac)

            # vlan tag
            # vlan_tag = dict()
            if 'cvlan' in keys or 'svlan' in keys:
                if '_hVlanContainer' not in self.__dict__.keys():
                    self._hVlanContainer = dict()
                self._hVlanContainer[streamName] = self._stc.create('vlans', under=self._hEthernet[streamName])
                if 'svlan' in keys:
                    svlan = kargs["svlan"][0]
                    scos = bin(kargs["svlan"][1])[2:]
                    hSvlan = 'hSvlan_%s' % streamName
                    if '_hSvlan' not in self.__dict__.keys():
                        self._hSvlan = dict()
                    self._hSvlan[streamName] = self._stc.create('Vlan', under=self._hVlanContainer[streamName],
                                                                pri=scos, cfi=0, id=svlan, name=hSvlan)
                if 'cvlan' in keys:
                    cvlan = kargs["cvlan"][0]
                    ccos = bin(kargs["cvlan"][1])[2:]
                    hCvlan = 'hCvlan_%s' % streamName
                    if '_hCvlan' not in self.__dict__.keys():
                        self._hCvlan = dict()
                    self._hCvlan[streamName] = self._stc.create('Vlan', under=self._hVlanContainer[streamName],
                                                                pri=ccos, cfi=0, id=cvlan, name=hCvlan)

            # ipv4
            if 'IPv4' in keys:
                srcIPv4, dstIPv4, gateway = kargs['IPv4']
                if '_hIPv4Header' not in self.__dict__.keys():
                    self._hIPv4Header = dict()
                self._hIPv4Header[streamName] = self._stc.create('ipv4:IPv4', under=self._hStreamBlock[streamName],
                                                                 sourceAddr=srcIPv4, destAddr=dstIPv4, gateway=gateway)
        except Exception as err:
            raise FHSTCCmdError('stc_createTrafficRaw', "创建数据流，端口名称-{0},数据流名称-{1}失败".format(portName, streamName),
                                stderr=traceback.format_exc())

    def stc_modifyTrafficRaw(self, streamName, portName, **kargs):
        pass

    def stc_RangeModifer(self, streamName, reference):
        pass

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

    def stc_saveAsXML(self, filepath="../instruments/config.xml"):
        try:
            fhlog.logger.info("保存仪表配置为XML文件(%s)" % filepath)
            self._stc.perform("SaveAsXml", FileName=filepath)
        except:
            raise FHSTCCmdError('stc_saveAsXML', '保存仪表配置为XML文件(%s)失败', traceback.format_exc())

    def stc_loadFromXml(self, filepath="./instruments/config.xml"):
        """导入仪表配置，并初始化仪表参数
            TODO: Device 对象的获取 
        """
        try:
            fhlog.logger.info("导入仪表配置文件")
            self._stc.perform("LoadFromXml", FileName=filepath)
            # 获取仪表
            info = self._stc.perform("GetConfigInfo", QueryRoots="project1")

            # 获取仪表端口数量
            ports_info = re.findall(r"-Values {(\d*) (\d*) (\d*) (\d*)}", info)
            portsCount = int(ports_info[0][0])
            for port in range(portsCount):
                # 获取端口名称
                portName = self._stc.get('project1.port(%d)' % (port+1), "Name")
                portName = portName.split()[0]   # 去掉(offline)字段
                fhlog.logger.debug("portName:" + portName)
                # 获取端口操作句柄
                self._hPorts[portName] = self._stc.get('project1.port(%d)' % (port+1), "Handle")
                # 获取每个端口下数据流的名称及操作句柄
                hStreamBlock = self._stc.get(self._hPorts[portName], "Children-StreamBlock")
                fhlog.logger.debug(hStreamBlock)
                # 获取数据流名称和对应的操作句柄
                for item in hStreamBlock.split():
                    streamName = self._stc.get(item, "Name")
                    self._hStreamBlock[streamName] = item
                fhlog.logger.debug(self._hStreamBlock)
                fhlog.logger.debug(self._hPorts)

            # 获取Device对象
            # ToDo

        except:
            raise FHSTCCmdError('stc_loadFromXml', '导入仪表配置文件(%s)失败', traceback.format_exc())

    def stc_analyzer(self, portName):
        # todo
        pass

    def stc_generator_start(self, portName=None):
        """基于端口启动generator"""
        try:
            if portName is None:
                for name in self._hGenerator.keys():
                    fhlog.logger.info('端口(%s)发送流量' % name)
                    self._stc.perform("GeneratorStart", GeneratorList=self._hGenerator[name])
            else:
                hGenerator = "hGenerator_{0}".format(portName)
                self._stc.perform("GeneratorStart", GeneratorList=hGenerator)
        except Exception as err:
            raise FHSTCCmdError('stc_generator_start', "端口发送流量失败", traceback.format_exc())

    def stc_generator_stop(self, portName):
        """基于端口停止generator"""
        # hGenerator = "hGenerator_{0}".format(portName)
        self._stc.perform("GeneratorStop", GeneratorList=self._hGenerator[portName])

    def stc_streamBlockStart(self, streamName):
        """基于streamBlock启动generator"""
        self._stc.perform("StreamBlockStart", StreamBlockList=self._hStreamBlock[streamName])

    def stc_streamBlockStop(self, streamName):
        """基于streamBlock停止generator"""
        self._stc.perform("StreamBlockStop", StreamBlockList=self._hStreamBlock[streamName])

    def stc_ClearAllResults(self, portName):
        """基于端口清空仪表流量统计"""
        self._stc.perform('ResultsClearAllCommand', PortList=self._hPorts[portName])

    def stc_DRVConfig(self, **kargs):
        """配置DynamicResultView"""
        self._hdrv = self._stc.create('DynamicResultView', under=self._project,
                                      ResultSourceClass='StreamBlock', Name='DRV1')

        # 配置select 参数
        self.selectProperties = [
            'Port.Name', 'StreamBlock.Name', 'StreamBlock.TxL1BitRate', 'StreamBlock.RxL1BitRate',
            'StreamBlock.TxFrameRate', 'StreamBlock.RxFrameRate', 'StreamBlock.DroppedFrameCount',
            'StreamBlock.DroppedFramePercent']
        selectParams = "{%s}" % (' '.join(self.selectProperties))

        # 配置仪表显示的数据流的个数，默认是100
        limitSize = kargs['LimitSize'] if 'LimitSize' in kargs.keys() else 100
        self.hprq = self._stc.create("PresentationResultQuery", under=self._hdrv,
                                     SelectProperties=selectParams, LimitSize=limitSize, FromObjects=self._project)
        self._stc.perform('SubscribeDynamicResultView', DynamicResultView=self._hdrv)

    def stc_get_DRV_ResulstData(self, loops=5):
        """获取DynamicResultView结果,通过DynamicResultView获取结果，不需要停流;
           通过DynamicResultView获取结果，需要先调用stc_DRVConfig函数。
        """
        self._hDRVData = self._stc.get(self._hdrv, 'children-PresentationResultQuery')
        resultsData = {}
        for loop in range(loops):
            # Since these are not realtime results, the view has to be manually updated
            self._stc.perform('UpdateDynamicResultView', DynamicResultView=self._hdrv)
            time.sleep(2)

            _hrvd = self._stc.get(self._hDRVData, 'children-ResultViewData')
            _hrvd = _hrvd.split()
            for index in _hrvd:
                ret = self._stc.get(index, 'ResultData')
                if loop == loops - 1:
                    ret_s = ret.split()
                    key = "%s.%s" % (tuple(ret_s[:2]))
                    value = tuple(ret_s[2:-2])
                    resultsData[key] = value

        # 打印 DRV_ResulstData结果
        title = ('StreamName', 'TxL1Rate', 'RxL1Rate', 'TxFrameRate', 'RxFrameRate', 'DropFrame', 'DropPct')
        result = '\n' + "\t".join(title)
        for key in resultsData:
            raw_result = "\t".join(list(map(lambda x: "{0:12}".format(x), resultsData[key])))
            result += "\n%s\t%s" % (key, raw_result)
        fhlog.logger.info(result)

        return resultsData

    def stc_get_ResultDataSet(self, **kargs):
        """"""
        print("Create and subscribe a ResultDataSet...")
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

            if '_hCapture' not in self.__dict__.keys():
                self._hCapture = dict()
            # Create a capture object. Automatically created.
            self._hCapture[portName] = self._stc.get(self._hPorts[portName], 'children-Capture')
            self._stc.config(self._hCapture[portName], mode='REGULAR_MODE', srcMode='TX_RX_MODE')

            # if "_hCaptureFilter" not in self.__dict__.keys():
            #     self._hCaptureFilter = dict()
            # self._hCaptureFilter[portName] = self._stc.get(self._hCapture[portName], 'children-CaptureFilter')

            # frameconfig = "{<frame><config><pdus><pdu name=\"eth1\" pdu=\"ethernet:EthernetII\"> <dstMac>00:00:01:00:00:01</dstMac> </pdu> <pdu name=\"ip_1\" pdu=\"ipv4:IPv4\"> </pdu> </pdus></config></frame>}"
            # _hCaptureAnalyzerFilter = self._stc.create(
            #     'CaptureAnalyzerFilter', under=self._hCaptureFilter[portName], IndexNum="0", IsSelected="TRUE",
            #     FilterDescription="{EthernetII:Destination MAC}", FrameConfig=frameconfig, RelationToNextFilter="OR",
            # )

            # self._stc.config(_hCaptureAnalyzerFilter, IndexNum="0", IsSelected="TRUE",
            #                  FilterDescription="{EthernetII:Destination MAC}", RelationToNextFilter="OR",
            #                  ValueToBeMatched="00:00:01:00:00:01")

            # self._stc.config(_hCaptureAnalyzerFilter, IndexNum="1", IsSelected="TRUE",
            #                  FilterDescription="{IPv4 Header:Source}", RelationToNextFilter="AND",
            #                  ValueToBeMatched="10.10.10.10")

            # ret = self._stc.get(self._hCaptureFilter[portName], "FilterExpression")
            # print("ret:", ret)
            self._stc.perform("CaptureStart", captureProxyId=self._hCapture[portName])
        except Exception as err:
            raise FHSTCCmdError("stc_captureStart", "启动抓包失败", traceback.format_exc())

    def stc_captureStop(self, portName, filepath=None):
        """停止抓包，并保存抓包结果"""
        self._stc.perform('CaptureStop', captureProxyId=self._hCapture[portName])
        if filepath is None:
            filename = time.strftime("%Y%M%m%H%m%S") + 'capature.pacp'
            self._stc.perform(
                'CaptureDataSave', captureProxyId=self._hCapture[portName],
                FileName=filename, SFileNameFormat='PCAP')
        else:
            filename = os.path.basename(filepath)
            path = os.path.dirname(filepath)
            self._stc.perform(
                'CaptureDataSave', captureProxyId=self._hCapture[portName],
                FileName=filename,  FileNamePath=path, FileNameFormat='PCAP')

    def stc_captureFilter(self, portName, filterExp=''):
        """过滤报文"""
        if "_hCaptureFilter" not in self.__dict__.keys():
            self._hCaptureFilter = dict()
        self._hCaptureFilter[portName] = self._stc.get(self._hCapture[portName], 'children-CaptureFilter')
        self._stc.config(self._hCaptureFilter[portName], FilterExpression=filterExp)

    def package_analyze(self, pcapfile, filter_exp):
        self._stc.cap_general = self._stc._tclsh.eval(
            "exec {%s} -r {%s} -Y %s" % (settings.TSHARK, pcapfile, filter_exp))
        print(self._stc.cap_general)

    def stc_createBasicDevice(
            self, deviceName, portName, srcMac="00:10:94:00:00:01", srcMacCount=1, IPv4Addr="192.18.10.1",
            IPv4gw="192.18.10.1", ipv6Addr="2000::1", ipv6gw="fe80::1", **kargs):
        """创建基本Device"""
        try:
            fhlog.logger.info("创建基本Device")
            self._hDevices[deviceName] = self._stc.create("EmulatedDevice", under=self._project, DeviceCount=1)

            _hEthClientIf = self._stc.create(
                "EthIIIf", under=self._hDevices[deviceName],
                IsRange="TRUE", SourceMac=srcMac, SrcMacRepeatCount=srcMacCount)

            _hIPv4ClientIf = self._stc.create(
                "Ipv4If", under=self._hDevices[deviceName],
                address=IPv4Addr, gateway=IPv4gw)
            self._stc.config(self._hDevices[deviceName], TopLevelIf=_hIPv4ClientIf, PrimaryIf=_hIPv4ClientIf)
            self._stc.config(_hIPv4ClientIf, stackedOnEndpoint=_hEthClientIf)
            self._stc.config(self._hDevices[deviceName], AffiliationPort=self._hPorts[portName])
        except:
            raise FHSTCCmdError("stc_createBasicDevice", "创建Device失败", traceback.format_exc())
