import time
from lib.public.fhlog import logger

def waitTime(t):
    """倒计时功能"""
    for i in range(t, 0, -1):
        if i > 10:
            if i == t:
                logger.info("倒计时{}秒！".format(i))
                time.sleep(1)
            else:
                if i%10 == 0:
                    logger.info("倒计时{}秒！".format(i))
                    time.sleep(1)
        else:
            logger.info("倒计时{}秒！".format(i))
            time.sleep(1)