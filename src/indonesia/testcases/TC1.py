# -*- encoding: utf-8 -*-
"""
@File    : TC1.py
@Date    : 2020/07/13 15:37:04
@Author  : ddtu
@Version : V1.0
@EMAIL   : ddtu@fiberhome.com
@License : (c)Copyright 2019-2020, Fiberhome,Teddy.tu
@Desc    : 
    OLT物理标识认证模式测试
    OLT物理标识认证自动发现（ONU未授权列表功能）
    测试步骤：
    1. 配置PON口认证模式
    2. 发现ONU，并授权ONU
    3. 去授权ONU
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


TC_RET = True  # 测试结果, 默认为True


def main():
    try:
        logger.info("OLT物理标识认证模式测试")
        # olt 命令行操作对象
        oltobj = FH_OLT()

        # 仪表操作对象
        # stc = FHSTC()
        logger.info("配置PON口认证模式")
        oltobj.connect_olt(**SETTINGS['OLT'])
        slotno, ponno, onuid = SETTINGS['ONU1']['ONUID']
        logger.info("配置PON口认证模式为物理认证模式")
        cmds = fhlib.OLT_V5.pon_auth_mode(slotno, ponno, fhlib.PONAuthMode.PHYID)
        oltobj.sendcmdlines(cmds)
        global TC_RET
        if TC_RET:
            TC_RET = oltobj.verify_cmds_exec()

        # 获取未授权ONU列表
        logger.info("获取为授权ONU列表")
        onulist = oltobj.get_discovery_onu(slotno, ponno)

        # 验证方式，待测试ONU信息，均需要在Globals.py文件中添加信息，
        # 并根据Globals.py中ONU信息与未授权的ONU信息对比， 如果信息一致进进行授权，否则不进行授权，
        # 保证所有的ONU都能进行授权成功。
        onuKeys = []
        onucount = 1
        while True:
            key = "ONU%d" % onucount
            if key in SETTINGS.keys():
                onuKeys.append(key)
                onucount += 1
            else:
                break

        # 授权ONU
        logger.info("授权ONU")
        for key in onuKeys:
            if SETTINGS[key]['PHYID'] in onulist.keys():
                # 用PhyId方式授权ONU
                oltobj.sendcmdlines(
                    fhlib.OLT_V5.authorize_onu(
                        fhlib.ONUAuthType.PHYID, SETTINGS[key]['PHYID'],
                        SETTINGS[key]['ONUTYPE'],
                        *SETTINGS[key]['ONUID']))
                waitTime(10)
                onulist = oltobj.get_discovery_onu(slotno, ponno)
                if TC_RET:
                    TC_RET = oltobj.verify_cmds_exec()
            else:
                logger.error("待测试ONU（%s）不在未授权ONU列表" % SETTINGS[key]['PHYID'])
                TC_RET = False
        logger.info("等待ONU正常上线")
        waitTime(30)

        logger.info("验证授权ONU是否可正常上线")
        authONUlist = oltobj.get_authorization_onu(slotno, ponno)
        for key in authONUlist.keys():
            if authONUlist[key][6] == "dw":
                logger.error("已授权ONU(%s),无法上线" % key)
                TC_RET = False
        else:
            logger.info("所有授权ONU可正常上线")

        # 去授权ONU
        logger.info("去授权ONU")
        for key in authONUlist.keys():
            oltobj.sendcmdlines(fhlib.OLT_V5.unauth_onu(fhlib.ONUAuthType.PHYID,
                                                        authONUlist[key][0], authONUlist[key][1], key))
            if TC_RET:
                TC_RET = oltobj.verify_cmds_exec()

        oltobj.disconnet_olt()

        # stc.stc_disconnect()
    except:
        TC_RET = False
        print(traceback.format_exc())
    finally:
        result = "PASS" if TC_RET else "FAILED"
        logger.info("OLT物理标识认证模式测试结果：%s" % TC_RET)
        return TC_RET


def run():
    main()


if __name__ == "__main__":
    run()
