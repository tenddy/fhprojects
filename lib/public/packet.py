#!/usr/bin/env python
# coding=UTF-8
"""
###############################################################################
# @FilePath    : /fhat/lib/public/packet.py
# @Author      : ddtu
# @Version     : V1.0
# @EMAIL       : ddtu@fiberhome.com
# @License     : (c)Copyright 2019-2020, Fiberhome(ddtu)
# @Date        : 2020-08-14 08:30:15
# @LastEditors : ddtu
# @LastEditTime: 2020-08-14 08:30:22
# @Descption   : 报文分析处理
###############################################################################
"""

import os
import sys
import traceback
import pyshark
from lib.public.fhlog import logger
from lib import settings


def filter_packet(pcapfile, filter=None, count=0):
    """
    功能：
        验证是否存在满足过滤规则的报文，如存在则返回报文
    参数：
        @pcapfile
    返回值：过滤之后的报文
    说明：	
    """
    logger.info("正在分析报文...")

    filepath = settings.CAP_PATH + "/" + pcapfile if os.path.dirname(pcapfile) == "" else pcapfile
    cap = pyshark.FileCapture(pcapfile, display_filter=filter)

    packets = []

    def counter(*args):
        packets.append(args[0])

    cap.apply_on_packets(counter, timeout=100000)
    cap.close()
    if len(packets) > 0:
        if count == 0:
            return packets
        else:
            return packets[:count]
    else:
        return None


class AnalyzePacket():
    def __init__(self, pcapfile):
        self._pcapfile = settings.CAP_PATH + "/" + pcapfile if os.path.dirname(pcapfile) == "" else pcapfile
        self._filterPackets = None

    def filter_packet(self, filter=None, count=0):
        """
        功能：
            验证是否存在满足过滤规则的报文，如存在则返回报文
        参数：
            @filter: 过滤规则，根据wireshark过滤规则语法
            @count: 返回报文个数
        返回值：过滤之后的报文, 如果没有满足条件的报文，就返回None
        说明：	
        """
        try:
            logger.info("正在分析报文...")

            # 文件路径，默认的报文路径为当前运行的测试用例文件目录下
            filepath = settings.CAP_PATH + "/" + self._pcapfile if os.path.dirname(
                self._pcapfile) == "" else self._pcapfile
            cap = pyshark.FileCapture(self._pcapfile, display_filter=filter)
            packets = []

            def counter(*args):
                packets.append(args[0])
            cap.apply_on_packets(counter, timeout=100000)
            cap.close()
            if len(packets) > 0:
                if count == 0:
                    self._filterPackets = packets       # 保存过滤之后的报文
                    return packets
                else:
                    self._filterPackets = packets
                    return packets[:count]
            else:
                return None
        except:
            logger.error("报文分析失败，{}".format(traceback.format_exc()))
            return None

    def get_packetEthIf(self):
        """获取报文的Ethernet 信息, srcMac, dstMac"""
        pass

    def filter_pppoes(self):
        """分析pppoe session报文，返回pppoe Session 信息，
        {'version': 1, 'type': 1, 'code': 0, 'session_id': 2, 'payload_length': 112}
        """
        try:
            logger.info("分析pppoes报文")
            packets = self.filter_packet(filter="pppoes", count=1)
            if packets is None:
                return None
            else:
                pppoe_session = packets[0].pppoes
                logger.debug(pppoe_session)
                pppoes = dict()
                pppoes['version'] = int(pppoe_session.pppoe_version)
                pppoes['type'] = int(pppoe_session.pppoe_type)
                pppoes['code'] = int(pppoe_session.pppoe_code, 16)
                pppoes['session_id'] = int(pppoe_session.pppoe_session_id, 16)
                pppoes['payload_length'] = int(pppoe_session.pppoe_payload_length)
                return pppoes
        except:
            logger.error("分析pppoes报文失败")
            return None
