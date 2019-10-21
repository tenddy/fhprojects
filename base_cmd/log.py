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

        if logfile is None:
            log = logging.StreamHandler()
        else:
            log = logging.FileHandler(logfile)

            log.setLevel(level)
            fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
            log.setFormatter(fomatter)
        self.log__.addHandler(log)

    def __del__(self):
        handlers = self.log__.handlers
        for hd in handlers:
            hd_thread = hd.acquire()
            hd.release()
            hd.close()
            print("log debug del")

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
