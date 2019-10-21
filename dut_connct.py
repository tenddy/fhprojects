import logging
import telnetlib


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


def connect_olt_telnet(host, username=USERNAME, password=PASSWORD, enable=ENABLE):
    """
    OLT telnet login
    """
    tn = telnetlib.Telnet(host)
    count = 1
    logger.info("login...")
    while True:
        # logger.warning("try connect %s of %d times" % (host, count))
        print("try connect %s of %d times" % (host, count))
        i, m, data = tn.expect(promot, 5)
        print("status:%s" % i)
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

        if i == 2:
            logger.info("User> %s" % enable)        # User>
            tn.write(b"enable\n")
            i, m, data = tn.expect(promot, 5)

        if i == 3:                                  # Admin#
            logger.info("Login OLT(%s) success!\n" % host)
            print("handlers", logger.handlers)
            hd = logger.handlers
            for h in hd:
                h.flush()
                h.close()
                print("close", h)
            return tn

        if count > CONNECT_TIMES:
            logger.error("login Devices(%s) Failed!\n" % host)
            return None


if __name__ == "__main__":
    ip = '10.182.32.243'
    # ret = login_olt_telnet(ip)
    # print(ret)
    # dut_connect_tl1(ip)
    # # manage vlan
    # cmd_vlan10 = b'CFG-LANPORTVLAN::OLTID=10.182.32.15,PONID=NA-NA-1-1,ONUIDTYPE=ONU_NUMBER,ONUID=9,ONUPORT=NA-NA-NA-2:CTAG::UV=10,CVLAN=10;'
    # send_cmd_tl1(ip, cmd_vlan10)

    # cmd_uni_vlan = ''

    # # voice
    # cmd_voice = 'CFG-VOIPSERVICE::OLTID=10.182.32.15,PONID=NA-NA-1-1,ONUIDTYPE=ONU_NUMBER,ONUID=8,ONUPORT=NA-NA-NA-1:CTAG::PHONENUMBER=g1yRFDs7nD,PT=SIP,VOIPVLAN=3900,SIPREGDM=3900@VoIP,SIPUSERNAME=g1yRFDs7nD,SIPUSERPWD=MLvbt9Qs,IPMODE=STATIC,IP=10.100.200.1,IPMASK=255.255.0.0,IPGATEWAY=10.100.0.1,VOICECODEC=G.711A;'
    # sebd_cmd_tl1(ip, cmd_vlan10)
    # obj_tn = dut_connect_tl1(ip)
    # send_cmd_tl1_tn(obj_tn, cmd_vlan10)
