import logging
import telnetlib
import time
from functools import wraps

fh_promot = [b'ogin:', b'assword:', b'ser>', b'# ']


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
# Fiberhome OLT 登录 用户名及密码
USERNAME = b'GEPON'
PASSWORD = b'GEPON'
ENABLE = b'enable'

# 重连次数
CONNECT_TIMES = 3


def dut_connect_telnet(host, port=23, username='GEPON', password='GEPON', enable='enable', promot=None):
    """
    OLT telnet login
    """ 
    dut_promot = fh_promot   
    if promot is not None:
        dut_promot.append(bytes(promot, encoding='utf8'))

    tn = telnetlib.Telnet(host, port=port)
    count = 1
    logger.info("login...")
    while True:
        if count > CONNECT_TIMES:
            logger.error("login Devices(%s) Failed!\n" % host)
            return None

        print("try connect %s of %d times" % (host, count)) 
        i, m, data = tn.expect(dut_promot, 5)
        # print("status:%s" % i)
        if i == -1:
            tn.write(b' \n')
            count += 1
            continue

        if i == 0:                                 # Login:
            logger.info("Login: %s" % username)
            tn.write(bytes("%s\n" % username, encoding='utf8'))
            i = tn.expect(dut_promot, 5)[0]

        if i == 1:                                  # Password:
            logger.info("Password: %s" % password)
            tn.write(bytes("%s\n" % password, encoding='utf8'))
            i = tn.expect(dut_promot, 5)[0]

        if i == 2:
            logger.info("User> %s" % enable)        # User>
            tn.write(bytes("%s\n" % enable, encoding='utf8'))
            i = tn.expect(dut_promot, 5)[0]

        if i == 3 or (len(dut_promot)>4 and i>=4):                      # Admin# or promot
            logger.info("Login Device(%s) success!\n" % host)
            return tn

def dut_disconnect_telnet(tn):
    try:
        tn.close()
    except Exception as err:
        logger.error(err)

class Send_CMD():
    def __init__(self, tn):
        self.tn = tn

    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            ret = func(*args, **kwargs)
            self.tn.write(ret)
            return ret
        return wrapped_function


def dut_connect_tl1(host, port=3337, username='admin', password='admin',timeout=5):
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

    
def auth_onu_cmd(meth='ADD'):
    olt_ip = '35.35.35.109'
    tn_obj = dut_connect_telnet(olt_ip, 23, 'admin', 'admin123')
    onulist = r'./config/HGU list.txt'
    with open(onulist, 'r') as f:
        onuinfo = f.readlines()
    for item in onuinfo:
        onu = item.split()
        slotno = onu[0]
        ponno = onu[1]
        # onuno = onu[2]
        onutype = 'OTHER_ONU2'
        onu_sn = onu[8]
        if meth == "ADD":
            slotno = '3'
            ponno = '8'
            tl1_cmd = 'ADD-ONU::OLTID=%s,PONID=NA-NA-%s-%s:CTAG::AUTHTYPETYPE=LOID,ONUTYPE=%s,ONUID=%s;\n' % (
                olt_ip, slotno, ponno, onutype, onu_sn)
        elif meth == "DEL":
            tl1_cmd = 'DEL-ONU::OLTID=%s,PONID=NA-NA-%s-%s:CTAG::ONUIDTYPE=LOID,ONUID=%s;\n' % (
                olt_ip, slotno, ponno, onu_sn)
        else:
            print("meth need ADD or DEL!")
        print(tl1_cmd)
        # cmd_ret = tn_obj.write(bytes(tl1_cmd, encoding="utf8"))
        # print(cmd_ret)
        ret = tn_obj.read_until(b';', 5)
        print(str(ret, encoding="utf8"))
        time.sleep(0.5)
    dut_disconnect_tl1(tn_obj)


def auth_onu_tl1(meth='ADD'):
    unm_ip = '10.182.1.161'
    olt_ip = '35.35.35.109'
    tn_obj = dut_connect_tl1(unm_ip, 3337, 'admin', 'admin123')
    # onulist = r'./config/HGU list.txt'
    onulist = r'./config/EPON HGU 32.txt'

    with open(onulist, 'r') as f:
        onuinfo = f.readlines()
    for item in onuinfo:
        onu = item.split()
        # slotno = onu[0]
        # ponno = onu[1]
        slotno = '13'
        ponno = '14'
        onuno = onu[2]
        # onutype = onu[3]
        onutype = '10GEPONHGU'       
        onu_sn = onu[8]
        if meth == "ADD":
            tl1_cmd = 'ADD-ONU::OLTID=%s,PONID=NA-NA-%s-%s:CTAG::AUTHTYPE=LOID,ONUTYPE=%s,ONUID=%s;\n' % (
                olt_ip, slotno, ponno, onutype, onu_sn)
        elif meth == "DEL":
            tl1_cmd = 'DEL-ONU::OLTID=%s,PONID=NA-NA-%s-%s:CTAG::ONUIDTYPE=LOID,ONUID=%s;\n' % (
                olt_ip, slotno, ponno, onu_sn)
        else:
            print("meth need ADD or DEL!")
        print(tl1_cmd)
        tn_obj.write(bytes(tl1_cmd, encoding="utf8"))
        ret = tn_obj.read_until(b';')
        print(str(ret, encoding="utf8"))
        time.sleep(0.5)
    dut_disconnect_tl1(tn_obj)


def config_service_tl1(method='add', onufile=r'./config/HGU list.txt', n_slotno=None, n_ponno=None):
    unm_ip = '10.182.1.161'
    olt_ip = '35.35.35.109'
    svlan = "2410"
    cvlan = ["41", "45", "46"]
    uv = ["1601", "45", "46"]
    slotno = '13'

    tn_obj = dut_connect_tl1(unm_ip, 3337, 'admin', 'admin123')

    # 回读ONU信息
    with open(onufile, 'r') as f:
        onuinfo = f.readlines()
        # print(onuinfo)
        for item in onuinfo:
            onu = item.split()
            if len(onu) < 9:
                continue
            print(onu)
            if n_slotno is None:
                slotno = onu[0]
            else:
                slotno = n_slotno

            if n_ponno is None:
                ponno = onu[0]
            else:
                ponno = n_ponno

            onuno = onu[2]
            onu_sn = onu[8]
            internet_uv = int(uv[0]) + int(onuno)-1
            # create
            qinq_tl1_cmd1 = "ADD-PONVLAN::OLTID=%s,PONID=NA-NA-%s-%s,ONUIDTYPE=LOID,ONUID=%s:CTAG::SVLAN=%s,CVLAN=%d,UV=%s,SCOS=1,CCOS=1;\n" \
                % (olt_ip, slotno, ponno, onu_sn, svlan, internet_uv, cvlan[0])
            qinq_tl1_cmd2 = "ADD-PONVLAN::OLTID=%s,PONID=NA-NA-%s-%s,ONUIDTYPE=LOID,ONUID=%s:CTAG::SVLAN=%s,CVLAN=%s,UV=%s,SCOS=5,CCOS=5;\n" \
                % (olt_ip, slotno, ponno, onu_sn, svlan, uv[1], cvlan[1])
            qinq_tl1_cmd3 = "ADD-PONVLAN::OLTID=%s,PONID=NA-NA-%s-%s,ONUIDTYPE=LOID,ONUID=%s:CTAG::SVLAN=%s,CVLAN=%s,UV=%s,SCOS=7,CCOS=7;\n" \
                % (olt_ip, slotno, ponno, onu_sn, svlan, uv[2], cvlan[2])
            add_qinq_cmd = qinq_tl1_cmd1 + qinq_tl1_cmd2 + qinq_tl1_cmd3

            # delete
            """
            DEL-PONVLAN::OLTID=35.35.35.109,PONID=NA-NA-16-7,ONUIDTYPE=LOID,ONUID=fiberhomeHG221GS:CTAG::UV=46;
            DEL-PONVLAN::OLTID=35.35.35.109,PONID=NA-NA-16-7,ONUIDTYPE=LOID,ONUID=fiberhomeHG221GS:CTAG::UV=41;
            DEL-PONVLAN::OLTID=35.35.35.109,PONID=NA-NA-16-7,ONUIDTYPE=LOID,ONUID=fiberhomeHG221GS:CTAG::UV=45;
            """
            del_qinq_tl1_cmd1 = "DEL-PONVLAN::OLTID=%s,PONID=NA-NA-%s-%s,ONUIDTYPE=LOID,ONUID=%s:CTAG::UV=%s;\n" \
                % (olt_ip, slotno, ponno, onu_sn,  cvlan[0])
            del_qinq_tl1_cmd2 = "DEL-PONVLAN::OLTID=%s,PONID=NA-NA-%s-%s,ONUIDTYPE=LOID,ONUID=%s:CTAG::UV=%s;\n" \
                % (olt_ip, slotno, ponno, onu_sn, cvlan[1])
            del_qinq_tl1_cmd3 = "DEL-PONVLAN::OLTID=%s,PONID=NA-NA-%s-%s,ONUIDTYPE=LOID,ONUID=%s:CTAG::UV=%s;\n" \
                % (olt_ip, slotno, ponno, onu_sn, cvlan[2])
            del_qinq_cmd = del_qinq_tl1_cmd1 + del_qinq_tl1_cmd2 + del_qinq_tl1_cmd3

            if method == "add":
                qinq_cmd = add_qinq_cmd
            else:
                qinq_cmd = del_qinq_cmd
            print("cmd:", qinq_cmd)
            tn_obj.write(bytes(qinq_cmd, encoding="utf8"))
            ret = tn_obj.read_until(b';', 5)
            print(str(ret, encoding="utf8"))
            time.sleep(0.5)
    dut_disconnect_tl1(tn_obj)


if __name__ == "__main__":
    ip = '10.182.1.161'
    onulist = r'./config/EPON HGU 32.txt'
    dut_onu = r'./config/HGU list.txt'
    # auth_onu_tl1('DEL')
    # auth_onu_tl1('ADD')
    config_service_tl1('add', onulist, '13', '14')
    # config_service_tl1('add', onulist, '11', '8')
