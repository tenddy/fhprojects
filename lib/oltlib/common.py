#!/usr/bin/env python
# coding=UTF-8
"""
###############################################################################
# @FilePath    : /fhat/lib/oltlib/common.py
# @Author      : ddtu
# @Version     : V1.0
# @EMAIL       : ddtu@fiberhome.com
# @License     : (c)Copyright 2019-2020, Fiberhome(ddtu)
# @Date        : 2020-08-15 15:50:09
# @LastEditors : ddtu
# @LastEditTime: 2020-08-15 15:50:19
# @Descption   : OLT 通用参数配置
###############################################################################
"""

from enum import Enum


class VLAN_MODE(Enum):
    """ONU 端口业务模式"""
    UNTAG = 0
    TAG = 1
    TRANSLATE = 2
    TRANSPARENT = 3
    mode = ('untag', 'tag', 'translate', 'transparent')


class SericeType(Enum):
    """业务类型"""
    UNICAST = 0
    MULTICAST = 1
    service = ('unicast', 'multicast')


class ONUAuthType(Enum):
    """授权ONU方式"""
    PHYID = 0
    PASSWORD = 1
    LOID = 2
    LOIDPSW = 3


class PONAuthMode(Enum):
    """PON口授权模式

        @LOID             Authenticate onu by logical SN without password.

        @LOID_AND_PSW     Authenticate onu by logical SN with password.

        @NO_AUTH          Authorize onu directly, needn't authentication.

        @PASSWORD         Authenticate onu by physical password.

        @PHYID            Authenticate onu by physical ID.

        @PHYID_AND_PSW    Authenticate onu by physical ID and physical password.

        @PHYID_OR_LOID     Authenticate onu by physical ID or logical SN without password or physical password or registration ID.

        @PHYID_OR_LOIDPSW  Authenticate onu by physical ID or logical SN with password or physical password or registration ID.

        @PHYID_OR_PSW       Authenticate onu by physical ID or physical password.

        @REGID             Authenticate onu by registration ID.
    """
    NO_AUTH = 0
    PHYID = 1
    LOID = 2
    PASSWORD = 3
    PHYID_AND_PSW = 4
    LOID_ADN_PSW = 5
    PHYID_OR_LOID = 6
    PHYID_OR_PSW = 7
    PHYID_OR_LOIDPSW = 8
    REGID = 9

