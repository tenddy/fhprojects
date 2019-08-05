import logging
import telnetlib
from base_cmd import log
# import log


PROMOT = [b'ogin:', b'assword:', b'ser>',  b'stop--', b'#', b'$']

# console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
console.setFormatter(fomatter)

logger.addHandler(console)

# 文档log
consolelog = log.Logger()
filelog = log.Logger("./log/log_test.log")

# Fiberhome OLT 登录 用户名及密码
USERNAME = b'GEPON'
PASSWORD = b'GEPON'
ENABLE = b'enable'

# 重连次数
CONNECT_TIMES = 5

def login_olt_telnet(host, username=USERNAME, password=PASSWORD, enable=ENABLE, promot=b'#'):
    """
    OLT telnet login
    """
    tn = telnetlib.Telnet(host)
    count = 1
    # logger.info("login...")
    logger.info("try login %s..." % host)
    while True:

        i, m, data = tn.expect(PROMOT, 5)
        filelog.log_info(data.decode('utf-8'))

        if i == 0:                                 # Login
            tn.write(username + b"\n")
            continue

        if i == 1:                                  # Password
            tn.write(password + b"\n")
            continue

        if i == 2:                                    # User>
            tn.write(enable + b"\n")
            continue

        if i == 3:
            tn.write(b' \r\n')
            continue

        if i in (4, 5):                                  # Admin#
            filelog.log_info("Login Host(%s) successful!\n" % host)
            return tn

        if m is None:
            return None


def send_cmd_once(host, cmd, promot=b'#'):
    obj_tn = login_olt_telnet(host)
    try:
        bytes_cmd = bytes(cmd + '\n', encoding='utf8')
        obj_tn.write(bytes_cmd)
        lines = obj_tn.read_until(promot, 3)
        logger.info(str(lines, encoding='utf8'))
        filelog.log_info(str(lines, encoding='utf8'))
        obj_tn.close()
        return lines
    except Exception as err:
        logger.error("Error!")
        filelog.log_error("Error!")
        obj_tn.close()
        return None


def send_cmd(tn, cmd, promot=b'#'):
    try:
        tn.write(cmd)
        lines = tn.read_until(promot, 3)
        logger.info(str(lines, encoding='utf8'))
        filelog.log_info(str(lines, encoding='utf8'))
        return lines
    except Exception as err:
        logger.error("Error!")
        filelog.log_error("Error!")
        return None

