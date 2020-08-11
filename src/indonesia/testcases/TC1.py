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

    测试步骤：
    1. 配置PON口认证模式
    2. 发现ONU，并授权ONU
    3. 去授权ONU
"""

import time
import os
import sys
import traceback
from Globals import SETTINGS
from lib import settings
from lib.oltlib import fhlib
from lib.oltlib.fhat import FH_OLT
from lib.stclib.fhstc import FHSTC
from lib.public.fhlog import logger
from lib.public.fhTimer import waitTime


TC_RET = "PASSED"  # 测试结果, 默认为PASSED

# 初始化测试环境
# init(__file__)


def main():
    try:
        logger.info("OLT物理标识认证模式测试")
        logger.info("配置PON口认证模式")
        oltobj = FH_OLT()
        oltobj.connect_olt(**SETTINGS['OLT'])
        oltobj.disconnet_olt()
    except:
        global TC_RET
        TC_RET = "FAILED"
        print(traceback.format_exc())
    finally:
        logger.info("OLT物理标识认证模式测试结果：%s" % TC_RET)
        return TC_RET


def run():
    main()


if __name__ == "__main__":
    run()
