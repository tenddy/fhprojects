import logging
import telnetlib
import time
from functools import wraps
from lib.public.fhlog import logger
# Fiberhome OLT telnet 登录提示符,用户名及密码
fh_olt_promot = {'Login': 'GEPON', 'Password': 'GEPON',  'User>': 'enable'}


def dut_connect_telnet(host: str, port=23, login_promot=fh_olt_promot, promot=None):
    """
    函数功能:
       通过telnet连接设备

    参数说明：
        @param host(str): 
            dut设备的IP地址, 字符串类型 
        @param port(int): 
            telnet登录端口号, 范围（0~65535)默认23
        @param login_promot（dict): 
        key为提示字符, value为对应用户名或者密码, 默认采用烽火OLT登录的默认提示符及用户名和密码
        @param promot: 
            设备登录成功提示符,正常输入命令提示符

    使用说明：
        dut_connect_telnet('10.182.3.100', port=8006, login_promot={"Username:":"admin", "Password:":"12345"}, '#')
    """

    # 针对烽火OLT，默认都添加 'User>' 对应命令行'enable'
    if 'User>' not in login_promot:
        login_promot['User>'] = 'enable'

    promot_keys = list(bytes(key, encoding='utf8') for key in login_promot.keys())
    promot_keys.append(bytes(promot, encoding='utf8'))

    try:
        logger.info("Connect to Host(%s) by telnet." % host)
        tn = telnetlib.Telnet(host, port=port)
        i, m, data = tn.expect(promot_keys, 5)
        m = str(m.group(), encoding='utf8')

        promot_times = dict()
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

            logger.debug("%s:%s" % (m, login_promot[m]))
            tn.write(bytes(login_promot[m] + '\n', encoding='utf8'))
            i, m, data = tn.expect(promot_keys, 5)
            m = str(m.group(), encoding='utf8')

    except Exception as err:
        logger.error(err)
        tn = None

    return tn


def dut_disconnect_telnet(tn):
    """断开连接"""
    try:
        logger.info("Telnet disconnect!")
        tn.close()
    except Exception as err:
        logger.error(err)


def dut_connect_tl1(host, port=3337, username='admin', password='admin', timeout=5):
    """通过TL1连接网管"""
    try:
        tn = telnetlib.Telnet(host, port=port)
        login_str = "LOGIN:::CTAG::UN=%s,PWD=%s;\n" % (username, password)
        logger.info(login_str)
        tn.write(bytes(login_str, encoding='utf8'))
        line_b = tn.read_until(b';', 5)
        logger.info(str(line_b, encoding='utf8'))
        return tn
    except Exception as err:
        logger.error("TL1 Connect Failed")
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
