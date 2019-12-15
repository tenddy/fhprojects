import logging
import telnetlib
import time

promot = [b'Login:', b'Password:', b'User>', b'# ']

# console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
console.setFormatter(fomatter)

# logger.addHandler(console)

# File log
# log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)

file_log = logging.FileHandler('log.txt')
file_log.setLevel(logging.DEBUG)
fomatter = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
file_log.setFormatter(fomatter)

# log.addHandler(file_log)
logger.addHandler(console)
# Fiberhome OLT 登录 用户名及密码
USERNAME = b'GEPON'
PASSWORD = b'GEPON'
ENABLE = b'enable'

# 重连次数
CONNECT_TIMES = 5


def connect_olt_telnet(host, port=23, username=USERNAME, password=PASSWORD, enable=ENABLE):
    """
    OLT telnet login
    """
    tn = telnetlib.Telnet(host, port=port)
    count = 1
    logger.info("login...")
    while True:
        # logger.warning("try connect %s of %d times" % (host, count))
        print("try connect %s of %d times" % (host, count))
        i, m, data = tn.expect(promot, 5)
        # print("status:%s" % i)
        if i == -1:
            tn.write(b' \r\n')
            count += 1
            continue

        if i == 0:                                 # Login
            logger.info("Login: %s" % username)
            tn.write(username + b"\n")
            i, m, data = tn.expect(promot, 5)

        if i == 1:                                  # Password
            logger.info("Password: %s" % password)
            tn.write(password + b"\n")
            i, m, data = tn.expect(promot, 5)
            time.sleep(1)

        if i == 2:
            logger.info("User> %s" % enable)        # User>
            tn.write(b"enable\n")
            i, m, data = tn.expect(promot, 5)

        if i == 3:                                  # Admin#
            logger.info("Login OLT(%s) success!\n" % host)
            return tn

        if count > CONNECT_TIMES:
            logger.error("login Devices(%s) Failed!\n" % host)
            return None


def dut_connect_tl1(host, port=3337, username='admin', password='admin'):
    # tn = telnetlib.Telnet(host, port=port, timeout=5)
    # login_str = "LOGIN:::CTAG::UN=%s,PWD=%s;" % (username, password)
    # tn.write(bytes(login_str, encoding='utf-8'))
    # ret = tn.read_until(";")
    # print(ret)

    try:
        tn = telnetlib.Telnet(host, port=port)
        login_str = "LOGIN:::CTAG::UN=%s,PWD=%s;\n" % (username, password)

        ret = tn.write(bytes(login_str, encoding='utf8'))
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
        ret = tn_obj.write(bytes(logout_str, encoding='utf8'))
        line_b = tn_obj.read_until(b';', 5)
        line_s = str(line_b, encoding='utf8')
        logger.info(line_s)
        tn_obj.close()
        return True
    except Exception as err:
        print(err)
        return None


if __name__ == "__main__":
    ip = '10.182.1.161'
    # ret = login_olt_telnet(ip)
    # print(ret)
    olt_ip = '35.35.35.109'
    slotno = "17"
    ponno = "16"
    svlan = "2701"
    cvlan = ["41", "45", "46"]
    uv = ["1701", "45", "46"]

    tn_obj = dut_connect_tl1(ip)
    for i in range(1, 33):
        onu_sn = "fiberhome6666%02d" % i
        internet_uv = 1700 + i*1

        print(onu_sn)

        qinq_tl1_cmd1 = "ADD-PONVLAN::OLTID=%s,PONID=NA-NA-%s-%s,ONUIDTYPE=LOID,ONUID=%s:CTAG::SVLAN=%s,CVLAN=%s,UV=%d,SCOS=1,CCOS=1;\n" \
            % (olt_ip, slotno, ponno, onu_sn, svlan, cvlan[0], internet_uv)
        qinq_tl1_cmd2 = "ADD-PONVLAN::OLTID=%s,PONID=NA-NA-%s-%s,ONUIDTYPE=LOID,ONUID=%s:CTAG::SVLAN=%s,CVLAN=%s,UV=%s,SCOS=5,CCOS=5;\n" \
            % (olt_ip, slotno, ponno, onu_sn, svlan, cvlan[1], uv[1])
        qinq_tl1_cmd3 = "ADD-PONVLAN::OLTID=%s,PONID=NA-NA-%s-%s,ONUIDTYPE=LOID,ONUID=%s:CTAG::SVLAN=%s,CVLAN=%s,UV=%s,SCOS=7,CCOS=7;\n" \
            % (olt_ip, slotno, ponno, onu_sn, svlan, cvlan[2], uv[2])
        qinq_cmd = qinq_tl1_cmd1 + qinq_tl1_cmd2 + qinq_tl1_cmd3
        print("cmd:", qinq_cmd)
        cmd_ret = tn_obj.write(bytes(qinq_cmd, encoding="utf8"))
        ret = tn_obj.read_until(b';', 5)
        print(str(ret, encoding="utf8"))
        time.sleep(0.5)
    dut_disconnect_tl1(tn_obj)
    # # manage vlan
    # cmd_vlan10 = b'CFG-LANPORTVLAN::OLTID=10.182.32.15,PONID=NA-NA-1-1,ONUIDTYPE=ONU_NUMBER,ONUID=9,ONUPORT=NA-NA-NA-2:CTAG::UV=10,CVLAN=10;'
    # send_cmd_tl1(ip, cmd_vlan10)

    # cmd_uni_vlan = ''

    # # voice
    # cmd_voice = 'CFG-VOIPSERVICE::OLTID=10.182.32.15,PONID=NA-NA-1-1,ONUIDTYPE=ONU_NUMBER,ONUID=8,ONUPORT=NA-NA-NA-1:CTAG::PHONENUMBER=g1yRFDs7nD,PT=SIP,VOIPVLAN=3900,SIPREGDM=3900@VoIP,SIPUSERNAME=g1yRFDs7nD,SIPUSERPWD=MLvbt9Qs,IPMODE=STATIC,IP=10.100.200.1,IPMASK=255.255.0.0,IPGATEWAY=10.100.0.1,VOICECODEC=G.711A;'
    # sebd_cmd_tl1(ip, cmd_vlan10)
    # obj_tn = dut_connect_tl1(ip)
    # send_cmd_tl1_tn(obj_tn, cmd_vlan10)
