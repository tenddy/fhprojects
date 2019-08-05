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
import logging


class Logger():
    def __init__(self, logfile=None, level=logging.DEBUG):
        self.log__ = logging.getLogger(None)
        self.log__.setLevel(level)

        if logfile:
            file_log__ = logging.FileHandler(logfile)
        else:
            file_log__ = logging.StreamHandler()

        file_log__.setLevel(level)
        fomatter__ = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
        file_log__.setFormatter(fomatter__)

        self.log__.addHandler(file_log__)

    def log_info(self, msg):
        self.log__.info(msg)

    def log_error(self, msg):
        self.log__.error(msg)

    def log_warning(self, msg):
        self.log__.warning(msg)


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
