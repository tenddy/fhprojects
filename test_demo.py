#!/usr/bin/python3
# coding=UTF-8
'''
@Description:
@Author:  Teddy.tu
@Date: 2020-01-01 20:13:11
@LastEditTime: 2020-06-15 14:39:37
@LastEditors: Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''

from lib.log import log_decare
from lib import fhlib


@log_decare
def test_func():
    return "test func."


def test_auth_onu_v4():

    cmds = fhlib.OLT_V4.authorize_onu(fhlib.ONUAuthType.PHYID, 12, 1, 1, 'HG260',
                                      phyid='FHTT01010001', password='psw0001')
    print(cmds)
    cmds = fhlib.OLT_V4.authorize_onu(fhlib.ONUAuthType.PASSWORD, 12, 1, 2, 'HG260', password="S01010001")
    print(cmds)
    cmds = fhlib.OLT_V4.authorize_onu(fhlib.ONUAuthType.LOID, 12, 1, 3, 'HG260', loid='Fasdf')
    print(cmds)
    cmds = fhlib.OLT_V4.authorize_onu(fhlib.ONUAuthType.LOIDPSW, 12, 1, 4, 'HG260', loid='f0101', logicpsw='adfad')
    print(cmds)


if __name__ == "__main__":
    test_auth_onu_v4()
