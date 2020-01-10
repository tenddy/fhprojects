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


class logit(object):
    def __init__(self, msglevel=INFO, logfile='./log/log.log'):
        self.logfile__ = logfile

    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = "Running " +  func.__name__
            # print(log_string)
            # 打开logfile并写入
            
            ret = func(*args, **kwargs)
            with open(self.logfile__, 'a') as opened_file:
                # 现在将日志打到指定的文件
                opened_file.write(log_string + '\n')
                opened_file.write(str(ret) + '\n')
                #发送一个通知
                self.notify(str(ret))
            return ret
            
        return wrapped_function

    def notify(self, msg):
        # logit只打日志，不做别的
        print(msg)

@logit(INFO, './log/demo.log')
def test(s='ddd'):
    cmdlines = []
    cmdlines.append(s)
    return cmdlines




if __name__ == "__main__":
    log = Logger()
    # print('test...')
    log.log_info("info")
    log.log_warning("warning")
    log.log_error("error")

    # flog = Logger("./log/log.txt")
    # flog.log_info("info")
    # flog.log_warning("warning")
    # flog.log_error("error")
    test()
