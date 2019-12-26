
import re

def autho_onu_config(version="V4"):
    send_cmd = []
    with open(r'E:/epon_onu_list.txt', 'r') as f:
        onulist = f.readlines()
    if version == "V4":
        # set white phy addr 123456789012 pas null ac add sl 3 p 5 o 30 ty 5006-07B
        for item in onulist:
            onu = item.split()
            # print(onu)
            auth_str = 'set white phy addr %s pas null ac add sl %s p %s o %s ty %s\n' % (onu[2], '7', '4', str(int(onu[0])), onu[5][2:])
            send_cmd.append(auth_str)
            print(auth_str)
        # print(send_cmd)
    if version == "V5":
        slotno = '3'
        ponno = '16'
        for item in onulist:
            onu = item.split()
            # print(onu)
            auth_str = ' whitelist add phy-id %s type %s slot %s pon %s onuid %s \n' % (onu[2], onu[5][2:], slotno, ponno, str(int(onu[0])))
            send_cmd.append(auth_str)
            print(auth_str)
    
    return send_cmd

def get_onu_type():
    file = r'E:/DDTU Workplace/测试项目/广西/配置文件/梧州/现网AN5000配置/10.104.80.19_20191126(梧州AN5516 gpon配置文件).txt'
    file1 = r'E:/DDTU Workplace/测试项目/广西/FTP/version/10.182.5.69_AN5516_1105.txt'
    with open(file, 'r') as f1, open("onu.txt", 'w' ) as f2:
        lines = str(f1.readlines())
        p = re.compile(r'set white phy addr \S* pas null ac add sl \d* p \d* o \d* ty (\S*)')
        p1 = re.compile(r'set white log sn \S* pas null ac add sl \d* p \d* o \d* ty (\S*)')

        # p = re.compile(r'(set white phy addr \S* pas null ac add sl 3 p 5 o \d* ty \S*)')
        items = p1.findall(lines)
        # print(items)
        # 获取ONU类型
        onu_type_list = set(items)
        print("ONU类型:", onu_type_list, "\nONU数量:", len(items))

        p1 = re.compile(r'set white phy addr \S* pas null ac add sl (\d*) p (\d*) o (\d*) ty (\S*)')
        onu_items = p1.findall(lines)
        # print(onu_items, len(onu_items))
        for item in onu_items:
            print(list(item))
        # for item in items:
        #     print(item)
        #     f2.write(item[0] + '\t' + item[1] + '\t' + item[2] + '\t' + item[3] + '\n') 

def switch_config():
    port = 32
    with open("e:/sw.txt", 'w') as f:
        for p in range(1, port+1):
            # str = "interface gigaethernet 1/0/%d \n port link-type access\nport default vlan %d\n" % (p+1, 101+p)
            str1 = 'interface gigaethernet 1/0/%d \n port default vlan 1\n port link-type hybrid\n port hybrid vlan %d tagged\n port hybrid vlan %d untagged \nport hybrid pvid %d\n' % (p, 1500+p, 500+p, 500+p)
            print(str1)
            # f.write("interface gigaethernet 1/0/%d \n port link-type access\nport default vlan %d" % (p+1, 101+p))
            f.write(str1)

def model1_config(version="V5", file=r'E:/config_model1.txt'):
    '''
    onu port vlan 1 eth 1 service count 1
    onu port vlan 1 eth 1 service 1 tag priority 1 tpid 33024 vid 301 
    onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
    '''
    onu_count = 21
    ONUID_NEW = range(1,onu_count+1)
    PORTNO = [16,16,8,24,24,16,24,24,16,16,16,16,24,24,4,4,4,4,4,8,8]
    with open(file,'w') as f:
        ser_count = 1
        svlan = 2701
        send_cmd = []
        for index in range(onu_count):
            onuid = ONUID_NEW[index]
            portno = PORTNO[index]
            for p in range(portno):
                if version == "V5":
                    onuno = onuid
                    cmd0 = 'onu port vlan %d eth %d service count %d\n' % (onuno, p+1, 0)
                    send_cmd.append(cmd0)
                    cmd1 = 'onu port vlan %d eth %d service count %d\n' % (onuno, p+1, ser_count)
                    send_cmd.append(cmd1)
                    cmd2 = 'onu port vlan %d eth %d service %d tag priority 1 tpid 33024 vid %d\n' % (onuno, p+1, 1, 301+(onuid-1)*24 + p)
                    send_cmd.append(cmd2)
                    cmd4 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (onuno, p+1, 1, svlan, 'FTTB_QINQ', 'SVLAN2')
                    if index < 14:
                        send_cmd.append(cmd4)
                if version == "V4":
                    slotno = 7
                    ponno = 8
                    onuno = onuid + 10
                    cmd0 = 'set epon slot {0} pon {1} onu {2} port {3} serv num {4}\napply onu {0} {1} {2} vlan\n'.format(slotno, ponno, onuno, p+1, 0)
                    send_cmd.append(cmd0)
                    cmd1 = 'set epon slot {0} pon {1} onu {2} port {3} serv num {4}\n'.format(slotno, ponno, onuno, p+1, 1)
                    send_cmd.append(cmd1)
                    cmd2 = 'set epon slot {0} pon {1} onu {2} port {3} serv {4} vlan_m tag 1 33024 {5}\n'.format(slotno, ponno, onuno, p+1, 1, 301+(onuid-1)*24 + p )
                    send_cmd.append(cmd2)
                    cmd4 = 'set epon slot %d pon %d onu %d port %d serv %d qinq en 1 33024 %s %s %d\n' % (slotno, ponno, onuno, p+1, 1, 'internet_qinq', 'pppoeSVLAN', svlan)
                    send_cmd.append(cmd4)
        f.write(''.join(send_cmd))


def model2_config(version="V5", file=r'E:/config_model2.txt'):
    '''
    onu port vlan 1 eth 1 service count 1
    onu port vlan 1 eth 1 service 1 tag priority 1 tpid 33024 vid 301 
    onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
    '''
    onu_count = 21
    ONUID_NEW = range(1,onu_count+1)
    PORTNO = [16,16,8,24,24,16,24,24,16,16,16,16,24,24,4,4,4,4,4,8,8]
    with open(file,'w') as f:
        ser_count = 1
        svlan = 2701
        send_cmd = []
        for index in range(onu_count):
            onuid = ONUID_NEW[index]
            portno = PORTNO[index]
            for p in range(portno):
                if version == "V5":
                    onuno = onuid
                    cmd0 = 'onu port vlan %d eth %d service count %d\n' % (onuno, p+1, 0)
                    send_cmd.append(cmd0)
                    cmd1 = 'onu port vlan %d eth %d service count %d\n' % (onuno, p+1, ser_count)
                    send_cmd.append(cmd1)
                    cmd2 = 'onu port vlan %d eth %d service %d tag priority 1 tpid 33024 vid %d\n' % (onuno, p+1, 1, 301+(onuid-1)*24 + p)
                    send_cmd.append(cmd2)
                if version == "V4":
                    slotno = 7
                    ponno = 8
                    onuno = onuid + 10
                    cmd0 = 'set epon slot {0} pon {1} onu {2} port {3} serv num {4}\napply onu {0} {1} {2} vlan\n'.format(slotno, ponno, onuno, p+1, 0)
                    send_cmd.append(cmd0)
                    cmd1 = 'set epon slot {0} pon {1} onu {2} port {3} serv num {4}\n'.format(slotno, ponno, onuno, p+1, 1)
                    send_cmd.append(cmd1)
                    cmd2 = 'set epon slot {0} pon {1} onu {2} port {3} serv {4} vlan_m tag 1 33024 {5}\n'.format(slotno, ponno, onuno, p+1, 1, 301+(onuid-1)*24 + p )
                    send_cmd.append(cmd2)
        f.write(''.join(send_cmd))



def create_config1():
    '''
    onu port vlan 1 eth 1 service count 3
    onu port vlan 1 eth 1 service 1 transparent priority 1 tpid 33024 vid 41 
    onu port vlan 1 eth 1 service 1 translate enable priority 1 tpid 33024 vid 301
    onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
    
    onu port vlan 1 eth 1 service 2 tag priority 3 tpid 33024 vid 45 
    onu port vlan 1 eth 1 service 2 qinq enable priority 3 tpid 33024 vid 2701 iptv SVLAN2

    onu port vlan 1 eth 1 service 3 tag priority 7 tpid 33024 vid 46 
    onu port vlan 1 eth 1 service 3 qinq enable priority 7 tpid 33024 vid 2701 voip SVLAN2
    '''
    onu_count = 21
    PORTNO =  [16,16,8,24,24,16,24,24,16,16,16,16,24,24,4,4,4,4,4,8,8]
    with open(r'E:/config_model4.txt','w') as f:
        # onu1
        # onuid = 1
        # portno = 8
        ser_count = 3
        # trans_ser_vlan = 41
        svlan = 2701
        for index in range(onu_count):
            onuid = index+1
            portno = PORTNO[index]
            ser_count = 3
            for p in range(portno):
                if p != 1:
                    continue
                send_cmd = []
                cmd0 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, 0)
                send_cmd.append(cmd0)
                cmd1 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, ser_count)
                send_cmd.append(cmd1)
                cmd2 = 'onu port vlan %d eth %d service %d transparent priority 1 tpid 33024 vid %d\n' % (onuid, p+1, 1, 2001+index)
                send_cmd.append(cmd2)
                cmd3 = 'onu port vlan %d eth %d service %d translate enable priority 1 tpid 33024 vid %d\n' % (onuid, p+1, 1, 301+(onuid-1)*24 + p)
                send_cmd.append(cmd3)
                cmd4 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 1, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd4)
                cmd5 = 'onu port vlan %d eth %d service %d transparent priority 1 tpid 33024 vid %d\n' % (onuid, p+1, 2, 45)
                send_cmd.append(cmd5)
                cmd6 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 2, svlan, 'iptv', 'SVLAN2')
                send_cmd.append(cmd6)
                cmd7 = 'onu port vlan %d eth %d service %d transparent priority 7 tpid 33024 vid %d\n' % (onuid, p+1, 3, 46)
                send_cmd.append(cmd7)
                cmd8 = 'onu port vlan %d eth %d service %d qinq enable priority 7 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 3, svlan, 'voip', 'SVLAN2')
                send_cmd.append(cmd8)
                f.write(''.join(send_cmd))
     
def create_config2():
    '''
    onu port vlan 1 eth 1 service count 3
    onu port vlan 1 eth 1 service 1 tag priority 1 tpid 33024 vid 41 
    onu port vlan 1 eth 1 service 1 qinq enable priority 1 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
    
    onu port vlan 1 eth 1 service 2 tag priority 3 tpid 33024 vid 45 
    onu port vlan 1 eth 1 service 2 qinq enable priority 3 tpid 33024 vid 2701 FTTB_QINQ SVLAN2

    onu port vlan 1 eth 1 service 3 tag priority 7 tpid 33024 vid 46 
    onu port vlan 1 eth 1 service 3 qinq enable priority 7 tpid 33024 vid 2701 FTTB_QINQ SVLAN2
    '''
    onu_count = 14
    PORTNO = [16,16,8,24,24,16,24,24,16,16,16,16,24,24]
    with open(r'E:/create_config2.txt','w') as f:
        # onu1
        # onuid = 1
        # portno = 8
        ser_count = 3
        # trans_ser_vlan = 41
        svlan = 2701
        for index in range(onu_count):
            onuid = index+61
            portno = PORTNO[index]
            ser_count = 3
            for p in range(portno):
                send_cmd = []
                cmd0 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, 0)
                send_cmd.append(cmd0)
                cmd1 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, ser_count)
                send_cmd.append(cmd1)
                cmd2 = 'onu port vlan %d eth %d service %d tag priority 1 tpid 33024 vid %d\n' % (onuid, p+1, 1, 301+(onuid-61)*24 + p)
                send_cmd.append(cmd2)
                cmd4 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 1, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd4)
                cmd5 = 'onu port vlan %d eth %d service %d transparent priority 1 tpid 33024 vid %d\n' % (onuid, p+1, 2, 45)
                send_cmd.append(cmd5)
                cmd6 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 2, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd6)
                cmd7 = 'onu port vlan %d eth %d service %d transparent priority 7 tpid 33024 vid %d\n' % (onuid, p+1, 3, 46)
                send_cmd.append(cmd7)
                cmd8 = 'onu port vlan %d eth %d service %d qinq enable priority 7 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 3, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd8)
                f.write(''.join(send_cmd))      


def create_config3():
    '''
    onu port vlan 1 eth 1 service count 2
    onu port vlan 1 eth 1 service 1 tag priority 1 tpid 33024 vid 3966
    
    onu port vlan 1 eth 1 service 2 tag priority 3 tpid 33024 vid 2506 
    onu port vlan 1 eth 1 service 2 qinq enable priority 3 tpid 33024 vid 502 FTTB_QINQ SVLAN2
    '''
    ONUID = [1, 2, 3, 6, 7, 10, 15, 20, 30, 58, 59, 60, 61, 62]
    ONUID_NEW = [3, 4, 5, 2, 6, 10, 9, 10, 11, 14, 12, 1, 8, 14]
    PORTNO = [8, 24, 24, 16, 16, 16, 24, 16, 16, 24, 16, 16, 24, 24]
    with open(r'E:/config2_new.txt','w') as f:
        # onu1
        # onuid = 1
        # portno = 8
        ser_count = 3
        # trans_ser_vlan = 41
        svlan = 2701
        for index in range(14):
            onuid = ONUID_NEW[index]
            portno = PORTNO[index]
            ser_count = 3
            for p in range(portno):
                send_cmd = []
                cmd0 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, 0)
                send_cmd.append(cmd0)
                cmd1 = 'onu port vlan %d eth %d service count %d\n' % (onuid, p+1, ser_count)
                send_cmd.append(cmd1)
                cmd2 = 'onu port vlan %d eth %d service %d transparent priority 1 tpid 33024 vid %d\n' % (onuid, p+1, 1, 1001+index)
                send_cmd.append(cmd2)
                cmd3 = 'onu port vlan %d eth %d service %d translate enable priority 1 tpid 33024 vid %d\n' % (onuid, p+1, 1, 301+(onuid-1)*24 + p)
                send_cmd.append(cmd3)
                cmd4 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 1, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd4)
                cmd5 = 'onu port vlan %d eth %d service %d transparent priority 1 tpid 33024 vid %d\n' % (onuid, p+1, 2, 45)
                send_cmd.append(cmd5)
                cmd6 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 2, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd6)
                cmd7 = 'onu port vlan %d eth %d service %d transparent priority 7 tpid 33024 vid %d\n' % (onuid, p+1, 3, 46)
                send_cmd.append(cmd7)
                cmd8 = 'onu port vlan %d eth %d service %d qinq enable priority 7 tpid 33024 vid %d %s %s\n' % (onuid, p+1, 3, svlan, 'FTTB_QINQ', 'SVLAN2')
                send_cmd.append(cmd8)
                f.write(''.join(send_cmd))


def del_ngn_voice_server(version="V5"):
    '''
    no onu ngn-voice-service 62 pots 1
    '''
    file=r'e:/dd.txt'
    onu_count = 14
    ONUID_NEW = range(1,onu_count+1)
    PORTNO = [16,16,8,24,24,16,24,24,16,16,16,16,24,24,4,4,4,4,4,8,8]
    with open(file,'w') as f:
        ser_count = 1
        svlan = 2701
        send_cmd = []
        for index in range(onu_count):
            onuid = ONUID_NEW[index]
            portno = PORTNO[index]
            for p in range(portno):
                if version == "V5":
                    onuno = onuid
                    cmd0 = 'onu port vlan %d eth %d service count %d\n' % (onuno, p+1, 0)
                    send_cmd.append(cmd0)
                    cmd1 = 'onu port vlan %d eth %d service count %d\n' % (onuno, p+1, ser_count)
                    send_cmd.append(cmd1)
                    cmd2 = 'onu port vlan %d eth %d service %d tag priority 1 tpid 33024 vid %d\n' % (onuno, p+1, 1, 301+(onuid-1)*24 + p)
                    send_cmd.append(cmd2)
                    cmd4 = 'onu port vlan %d eth %d service %d qinq enable priority 1 tpid 33024 vid %d %s %s\n' % (onuno, p+1, 1, svlan, 'FTTB_QINQ', 'SVLAN2')
                    if index < 14:
                        send_cmd.append(cmd4)
                if version == "V4":
                    slotno = 7
                    ponno = 8
                    onuno = onuid + 10
                    cmd0 = 'set epon slot {0} pon {1} onu {2} port {3} serv num {4}\napply onu {0} {1} {2} vlan\n'.format(slotno, ponno, onuno, p+1, 0)
                    send_cmd.append(cmd0)
                    cmd1 = 'set epon slot {0} pon {1} onu {2} port {3} serv num {4}\n'.format(slotno, ponno, onuno, p+1, 1)
                    send_cmd.append(cmd1)
                    cmd2 = 'set epon slot {0} pon {1} onu {2} port {3} serv {4} vlan_m tag 1 33024 {5}\n'.format(slotno, ponno, onuno, p+1, 1, 301+(onuid-1)*24 + p )
                    send_cmd.append(cmd2)
                    cmd4 = 'set epon slot %d pon %d onu %d port %d serv %d qinq en 1 33024 %s %s %d\n' % (slotno, ponno, onuno, p+1, 1, 'internet_qinq', 'pppoeSVLAN', svlan)
                    send_cmd.append(cmd4)
        f.write(''.join(send_cmd))


def alarm_threshold_profile():
    '''
    onu port optical-threshold-profile 1/3/5 onu 1 port 0 prof-id 2
    '''
    onu_count = 23
    send_cmd = []
    for index in range(onu_count):
        prof_id = 2
        slotno = 3
        ponno = 5
        onuid = index+1
        portno = 1
        cmd0 = 'onu port optical-threshold-profile 1/%d/%d onu %d port %d prof-id %d\n' % (slotno, ponno, onuid, portno, prof_id)
        send_cmd.append(cmd0)
    with open(r'E:/ararm_profile.txt','w') as f:
        f.write(''.join(send_cmd)) 

def config_onu_bandwidth():
    '''
    onu bandwidth 1 upstream-pir 1000000 downstream-pir 1000000 upstream-cir 640 upstream-fir 0 
    '''
    onu_count = 23
    send_cmd = []
    for index in range(onu_count):
        onuid = index+1
        uppir = 10000
        dwpir = 10000
        cmd0 = ' onu bandwidth %d upstream-pir %d downstream-pir %d upstream-cir 640 upstream-fir 0 \n' % (onuid, uppir, dwpir)
        send_cmd.append(cmd0)
    with open(r'E:/onu_bandwidth.txt','w') as f:
        f.write(''.join(send_cmd)) 


def onu_auth_8K():
    slot_list = [1,2,4,8,11,13,15,18]
    # slot_list = [3, 16]
    file = r'e:/8K.txt'
    with open(file, 'w') as f:
        for s in slot_list:
            for p in range(1, 17):
                for onu in range(1, 65):
                    sn = 'FHTT%02d%02d%04d' % (s, p, onu)
                    onutype = "OTHER2"
                    auth_str = 'whitelist add logic-id %s type %s slot %d pon %d onuid %d \n' % (sn, onutype, s, p, onu)
                    f.write(auth_str)
                


if __name__ == "__main__":
    # get_onu_config()
    # f = open(r"E:/d.txt", "w")
    # f.write("ddd\n")
    # f.close()
    create_config1()
    create_config2()
    autho_onu_config(version='V5')
    # model1_config('V4', r'E:/config_model1_AN5516.txt')
    # model1_config('V5', r'E:/config_model1_AN6000.txt')
    # switch_config()
    # alarm_threshold_profile()
    # config_onu_bandwidth()
    # onu_auth_8K()
