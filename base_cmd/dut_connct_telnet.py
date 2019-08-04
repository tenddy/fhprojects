import logging
import telnetlib
from base_cmd import log


promot = [b'Login:', b'Password:', b'User>',  b'stop--', b'#']

# console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
console.setFormatter(fomatter)

logger.addHandler(console)

filelog = log.Logger()

# Fiberhome OLT 登录 用户名及密码
USERNAME = b'GEPON'
PASSWORD = b'GEPON'
ENABLE = b'enable'

# 重连次数
CONNECT_TIMES = 5


def login_olt_telnet(host, username=USERNAME, password=PASSWORD, enable=ENABLE):
    """
    OLT telnet login
    """
    tn = telnetlib.Telnet(host)
    count = 1
    # logger.info("login...")
    logger.info("try login %s..." % host)
    while True:

        i, m, data = tn.expect(promot, 5)
        # logger.info("status:%s" % i)
        logger.info(bytes.decode(data))
        filelog.log_info(bytes.decode(data))
        print('i is ' + str(i))

        if i == 0:                                 # Login
            # logger.info("Login: %s" % username)
            tn.write(username + b"\n")
            # i, m, data = tn.expect(promot, 5)
            continue

        if i == 1:                                  # Password
            # logger.info("Password: %s" % password)
            tn.write(password + b"\n")
            # i, m, data = tn.expect(promot, 5)
            continue

        if i == 2:
            # logger.info("User> %s" % enable)        # User>
            tn.write(enable + b"\n")
            # i, m, data = tn.expect(promot, 5)
            continue

        if i == 3:
            tn.write(b' \r\n')
            continue

        if i == 4:                                  # Admin#
            logger.info("Login OLT(%s) success!\n" % host)

            return tn

        if i == -1:
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


if __name__ == "__main__":
    ip = '192.168.10.80'
    ret = login_olt_telnet(ip)
    print(ret)
    if ret:
        ret.close()
