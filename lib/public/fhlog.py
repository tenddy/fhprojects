#! /usr/bin/python3
# -*- encoding: utf-8 -*-
'''
#####################################################################
# @Filename    : log.py
# @Desc        : 打印log日志
#             级别排序:CRITICAL > ERROR > WARNING > INFO > DEBUG
#             其中级别为DEBUG打印全部
# @Author      : teddy_tu
# @Version     : V1.0
# @Create Time : 2019/08/03 11:11:19
# @Modify Time : 2019/08/03 11:11:19
# @License     : (c)Copyright 2019-2020 Teddy_tu
#####################################################################
'''

import logging
import os
import traceback
import time
import random
from lib import settings
# CRITICAL = 0
# ERROR = 1
# WARNING = 2
# INFO = 3
# DEBUG = 4

# LEVEL = (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)

# LEVEL = {'CRITICAL': logging.Level, 'ERROR': logging.ERROR,
#          'WARNING': logging.WARNING, 'INFO': logging.INFO, 'DEBUG': logging.DEBUG}

_log_level = logging.DEBUG if settings.DEBUG else logging.INFO

# logger = logging.getLogger(time.strftime('%Y%m%d%H%M%S') + 'log')
logger = logging.getLogger(__name__)
logger.setLevel(_log_level)

# console
console = logging.StreamHandler()
console.setLevel(_log_level)
fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(filename)s:%(message)s')
console.setFormatter(fomatter)

# File log
filename = time.strftime('%Y%m%d%H%M%S') + '_log.txt'
# logger.info(filename)
# 判断log目录是否存在，如果不存在就新创建文件夹
# if not os.path.isdir(settings.LOG_PATH):
#     os.mkdir(settings.LOG_PATH)
file_log = logging.FileHandler(os.path.join(settings.LOG_PATH, filename), encoding='utf-8')
file_log.setLevel(_log_level)
fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(filename)s:%(message)s')
file_log.setFormatter(fomatter)


logger.addHandler(file_log)
logger.addHandler(console)


# console.close()
# file_log.close()

# for f in os.listdir(settings.LOG_PATH):
#     if os.path.getsize(os.path.join(settings.LOG_PATH, f)) == 0:
#         os.remove(os.path.join(settings.LOG_PATH, f))

# print(os.listdir(settings.LOG_PATH))


def log_decare(func):
    # log打印装饰器函数
    def wraper_func(*args, **kwargs):
        try:
            # log = Logger()
            for ret in func(*args, **kwargs):
                # log.info(ret)
                logger.info(ret)
        except Exception as err:
            logger.error("print log error!\n　%s" % traceback.print_exc())
            exit(-1)
    return wraper_func
