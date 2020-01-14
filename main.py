#!/usr/bin/python3
# coding=UTF-8
'''
@Description: 
@Author:  Teddy.tu
@Date: 2019-07-07 21:53:46
@LastEditTime : 2020-01-10 22:10:45
@LastEditors  :  Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''
import sys
import time
import re
from lib import log
from lib import dut_connect
from lib.fhlib import OLT_V5
from lib.fhat import ServiceConfig
from lib.fhat import send_cmd_file

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Error: 缺少文件路径")
        exit(-1)

    host = "35.35.35.109"
