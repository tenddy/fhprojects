#!/usr/bin/env python
# coding=UTF-8
"""
##################################################
# @FilePath    : /fhat/src/indonesia/testcases/demo.py
# @Author      : ddtu
# @Version     : V1.0
# @EMAIL       : ddtu@fiberhome.com
# @License     : (c)Copyright 2019-2020, Fiberhome(ddtu)
# @Date        : 2020-08-12 10:39:51
# @LastEditors : ddtu
# @LastEditTime: 2020-08-12 10:40:10
# @Descption   :  ONU 端口业务配置
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
TC_RET = True  # 测试结果, 默认为True


def main():
    try:
        TC_RET = True  # 测试结果, 默认为True
        logger.info("OLT物理标识认证模式测试")
        # olt 命令行操作对象
        oltobj = FH_OLT()
        oltobj.init_olt(**SETTINGS['OLT'])

        # 仪表操作对象
        # stc = FHSTC()
        oltobj.connect_olt()
        logger.info("测试结束!")
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
