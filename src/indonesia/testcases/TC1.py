#!/usr/bin/env python
# coding=UTF-8
"""
##################################################
# @FilePath    : /fhat/src/indonesia/testcases/TC1.py
# @Author      : ddtu
# @Version     : V1.0
# @EMAIL       : ddtu@fiberhome.com
# @License     : (c)Copyright 2019-2020, Fiberhome(ddtu)
# @Date        : 2020-08-11 12:42:30
# @LastEditors : ddtu
# @LastEditTime: 2020-08-12 10:38:50
# @Descption   : OLT物理标识认证模式测试, OLT物理标识认证自动发现（ONU未授权列表功能）
                测试步骤：
                1. 配置PON口认证模式
                2. 发现ONU，并授权ONU
                3. 去授权ONU
##################################################
"""


import time
import os
import sys
import traceback
import re
from Globals import SETTINGS
from lib.oltlib import fhlib
from lib.oltlib.fhat import FH_OLT
from lib.stclib.fhstc import FHSTC
from lib.public.fhlog import logger
from lib.public.fhTimer import waitTime


def main():
    try:
        TC_RET = True  # 测试结果, 默认为True

        logger.info("OLT物理标识认证模式测试")
        # olt 命令行操作对象
        oltobj = FH_OLT()
        oltobj.init_olt(**SETTINGS['OLT'])

        # 仪表操作对象
        # stc = FHSTC()
        logger.info("配置PON口认证模式")
        slotno, ponno = SETTINGS['SLOTNO'], SETTINGS['PONNO']
        logger.info("配置PON口认证模式为物理认证模式")
        oltobj.connect_olt()
        cmds = fhlib.OLT_V5.pon_auth_mode(slotno, ponno, fhlib.PONAuthMode.PHYID)
        oltobj.sendcmdlines(cmds)
        # oltobj.disconnet_olt()
        TC_RET = oltobj.verify_cmds_exec() if TC_RET else TC_RET

        # 获取未授权ONU列表
        logger.info("获取未授权ONU列表")
        onulist = oltobj.get_discovery_onu(slotno, ponno)

        # 授权ONU,根据Globals.py中ONU信息与未授权的ONU信息对比， 如果信息一致进进行授权，否则不进行授权
        logger.info("授权ONU")
        for sn in onulist.keys():
            oltobj.sendcmdlines(
                fhlib.OLT_V5.authorize_onu(
                    fhlib.ONUAuthType.PHYID, sn,
                    onulist[sn][1],
                    *(slotno, ponno, "null")))
            TC_RET = oltobj.verify_cmds_exec() if TC_RET else TC_RET

        logger.info("等待ONU正常上线")
        waitTime(30)

        logger.info("验证待测试ONU是否可正常上线")
        authONUlist = oltobj.get_authorization_onu(slotno, ponno)
        # print(authONUlist)
        for item in SETTINGS['ONU']:
            if item['PHYID'] in authONUlist.keys():
                if authONUlist[item["PHYID"]][6] == 'dw':
                    logger.error("ONU(%s)授权成功,无法上线" % item['PHYID'])
                    TC_RET = False
                else:
                    logger.error("ONU(%s)授权成功并已成功上线" % item['PHYID'])
            else:
                logger.error("待测试ONU(%s)未授权" % item['PHYID'])
                TC_RET = False

        # 去授权ONU
        logger.info("去授权ONU")
        for key in authONUlist.keys():
            oltobj.sendcmdlines(fhlib.OLT_V5.unauth_onu(fhlib.ONUAuthType.PHYID,
                                                        authONUlist[key][0], authONUlist[key][1], key))
            if TC_RET:
                TC_RET = oltobj.verify_cmds_exec()

        logger.info("测试结束!")
        oltobj.disconnet_olt()
        # stc.stc_disconnect()
    except:
        TC_RET = False
        print(traceback.format_exc())
    finally:
        result = "PASS" if TC_RET else "FAILED"
        logger.info("【OLT物理标识认证模式】 测试结果：%s" % result)
        return TC_RET


def run():
    main()


if __name__ == "__main__":
    run()
