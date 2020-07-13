import logging
import telnetlib
import time
from functools import wraps

# Fiberhome OLT telnet 登录提示符,用户名及密码
fh_olt_promot = {'Login': 'GEPON', 'Password': 'GEPON',  'User>': 'enable'}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
console.setFormatter(fomatter)

# File log
file_log = logging.FileHandler('./log/dut_log.txt')
file_log.setLevel(logging.DEBUG)
fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
file_log.setFormatter(fomatter)

# log.addHandler(file_log)
logger.addHandler(console)


# 重连次数
CONNECT_TIMES = 3


def dut_connect_telnet(host, port=23, login_promot=fh_olt_promot, promot=None):
    """
    函数功能:
       通过telnet登录dut设备

    参数说明：
        @param host: string
            dut设备的IP地址, 字符串类型 
        @param port: int
            telnet登录端口号, 范围（0~65535)默认23
        @param login_promot: dict
            key为提示字符, value为对应用户名或者密码, 默认采用烽火OLT登录的默认提示符及用户名和密码
        @param promot: string
            设备登录成功提示符,正常输入命令提示符
    
    使用说明：
        dut_connect_telnet('10.182.3.100', port=8006, login_promot={"Username:":"admin", "Password:":"12345"}, '#')
    """
    promot_keys = []
    promot_times = {}
    for key in login_promot.keys():
        promot_keys.append(bytes(key, encoding='utf8'))

    promot_keys.append(bytes(promot, encoding='utf8'))

    try:
        logger.info("Connect to Host(%s) by telnet." % host)
        tn = telnetlib.Telnet(host, port=port)
        i, m, data = tn.expect(promot_keys, 5)
        m = str(m.group(), encoding='utf8')

        while i != -1:  # 没有登录成功，并且提示符正确
            if m == promot:
                logger.info("Connect to Host(%s) success!\n" % host)   # 登录成功，返回tn
                return tn

            if m in promot_times.keys():
                promot_times[m] += 1
                if promot_times[m] > 2:
                    logger.info("Connect to Host(%s) Failed!\n" % host)   # 登录失败，返回 None
                    tn.close()
                    return None
            else:
                promot_times[m] = 1

            # logger.info("%s:%s" % (m, login_promot[m]))
            tn.write(bytes(login_promot[m] + '\n', encoding='utf8'))
            i, m, data = tn.expect(promot_keys, 5)
            m = str(m.group(), encoding='utf8')

    except Exception as err:
        logger.error(err)
        tn = None

    return tn


def dut_disconnect_telnet(tn):
    try:
        logger.info("Telnet disconnect!")
        tn.close()
    except Exception as err:
        logger.error(err)


def dut_connect_tl1(host, port=3337, username='admin', password='admin', timeout=5):
    try:
        tn = telnetlib.Telnet(host, port=port)
        login_str = "LOGIN:::CTAG::UN=%s,PWD=%s;\n" % (username, password)
        print(login_str)
        tn.write(bytes(login_str, encoding='utf8'))
        line_b = tn.read_until(b';', 5)
        line_s = str(line_b, encoding='utf8')
        logger.info(line_s)
        return tn
    except Exception as err:
        print(err)
        return None


def dut_disconnect_tl1(tn_obj):
    try:
        # tn = telnetlib.Telnet(host, port=port)
        logout_str = "LOGOUT:::CTAG::;\n"
        print(logout_str)
        tn_obj.write(bytes(logout_str, encoding='utf8'))
        line_b = tn_obj.read_until(b';', 5)
        line_s = str(line_b, encoding='utf8')
        logger.info(line_s)
        tn_obj.close()
        return True
    except Exception as err:
        print(err)
        return None


def send_cmdlines_tl1(tn_obj, cmds, promot=b';', timeout=5, delay=0):
    try:
        for cmd in cmds:
            tn_obj.write(bytes(cmd, encoding='utf8'), timeout=timeout)
            line_ret = str(tn_obj.read_until(promot, timeout), encoding='utf8')
            logger.info(line_ret)
            time.sleep(delay)
        return True
    except Exception as err:
        print(err)
        return None


if __name__ == "__main__":
    fh_login = {'Login': 'GEPON', 'Password': 'GEPON',  '>': 'enable'}
    hw_login = {'>': 'system-view'}
    hw_promot = "]"
    hostip = '10.182.0.240'
    dut_tn = dut_connect_telnet(hostip, 23, hw_login, hw_promot)
    if dut_tn is not None:
        dut_disconnect_telnet(dut_tn)
