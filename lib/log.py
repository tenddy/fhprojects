#! /usr/bin/python3
# -*- encoding: utf-8 -*-
'''
#####################################################################
# @Filename    : log.py
# @Desc        : None
# @Author      : teddy_tu
# @Version     : V1.0
# @Create Time : 2019/08/03 11:11:19
# @Modify Time : 2019/08/03 11:11:19
# @License     : (c)Copyright 2019-2020 Teddy_tu
#####################################################################
'''
from functools import wraps
import logging
import os

INFO = 1
WARNING = 2
ERROR = 3


class Logger():
    def __init__(self, logfile=None, level=logging.DEBUG):
        self.log__ = logging.getLogger(None)
        self.log__.setLevel(level)

        if logfile is None:
            log = logging.StreamHandler()
        else:
            log = logging.FileHandler(logfile)

            log.setLevel(level)
            fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
            log.setFormatter(fomatter)
        self.log__.addHandler(log)

    def __del__(self):
        pass

    def log_info(self, msg):
        self.log__.info(msg)

    def log_error(self, msg):
        self.log__.error(msg)

    def log_warning(self, msg):
        self.log__.warning(msg)


##################
# log打印装饰器函数
#################
def log_decare(func):
    def wraper_func(*args, **kwargs):
        try:
            # print("call", func.__name__)
            log = Logger()
            for ret in func(*args, **kwargs):
                log.log_info(ret)
        except Exception as err:
            print("print log error!", err)
            exit(-1)
    return wraper_func


if __name__ == "__main__":
    log = Logger()
    # print('test...')
    log.log_info("info")
    log.log_warning("warning")
    log.log_error("error")

    flog = Logger("./log/log_test.log")
    flog.log_info("info")
    flog.log_warning("warning")
    flog.log_error("error")
