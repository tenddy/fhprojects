#!/usr/bin/python3
# coding=UTF-8
'''
@Description:
通过分析AN5516 OLT的配置文件，提取对应ONU的所有的配置信息。

提取信息：
1、白名单（物理和逻辑）
set white phy addr 544b104068d8 pas null ac add sl 14 p 4 o 11 ty 5006-10B
set white log sn 0773000000589996 pas null ac add sl 4 p 2 o 18 ty OTHER2

2、端口业务配置
set ep sl 17 p 8 o 1,6-7 p 4 serv num 1
(set ep sl \d* p \d* o [-,0-9]* p \d* serv num \d*)

set ep sl 17 p 8 o 1,6-7 p 4 serv 1 vlan_m tag 255 33024 1000,1006,1007
(set ep sl \d* p \d* o [-,0-9]* p \d* serv \d* vlan_m \S* \d* 33024 [\d,]*)
multicast： set ep sl \d* p \d* o [-,0-9]* p \d* serv \d* ty multi

set ep sl 14 p 2 o 1-9,11-13,17-19 p 13 serv 1 qinq en 3 33024 qing ftthdata 2545,2545,2545,2545,2545,2545,2545,2545,2545,2545,2545,2545,2545,2545,2545

3、OLT qinq域模板

4、MAC地址限制

5、语音配置

6、带宽模板

7、端口限速
@Author:  Teddy.tu
@Date: 2019-12-06 21:38:44
@LastEditTime: 2019-12-06 21:40:59
@LastEditors:  Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''
import re
import os
import sys

ONUTYPE = 1
ONUID = 2


class GetONUConfig():
    def __init__(self, configfile, *args):
        with open(configfile, 'r', encoding='utf-8') as f:
            self.__config = str(f.readlines())

        self.onu_type = None
        self.slot = None
        self.pon = None
        self.onu = None
        print(args)
        len_args = len(args)

        if len_args == 1:
            self.method__ = ONUTYPE
            self.onu_type = args[0]
        elif len_args == 3:
            self.method__ = ONUID
            self.slot = args[0]
            self.pon = args[1]
            self.onu = args[2]
        else:
            self.method__ = 0
            print("Invalid input parameters count!")
            exit(-1)

        self.service_mode = None

    def get_onu_whitelist(self):
        items = []
        if self.method__ == ONUTYPE:
            p = re.compile(
                r'(set white phy addr \w{12} pas null ac add sl (\d*) p (\d*) o (\d*) ty %s)' % self.onu_type)
            items.extend(p.findall(self.__config))

            p1 = re.compile(r'(set white log sn \S* pas null ac add sl (\d*) p (\d*) o (\d*) ty %s)' % self.onu_type)
            items.extend(p1.findall(self.__config))
            # print(items)
        if self.method__ == ONUID:
            p = re.compile(
                r'(set white phy addr \w{12} pas null ac add sl %s p %s o %s ty (\S*))' %
                (self.slot, self.pon, self.onu))
            items.extend(p.findall(self.__config))

            p1 = re.compile(r'(set white log sn \S* pas null ac add sl %s p %s o %s ty (\S*))' %
                            (self.slot, self.pon, self.onu))
            items.extend(p1.findall(self.__config))
            # print(items)
        # print(p1.group())
        return items

    def get_onu_fe_config(self, slotno, ponno, onuno):
        # ONU FE service num
        onu_p = re.compile(r'set ep sl %s p %s o ([-,0-9]*) p (\d*) serv num (\d*)' %
                           (slotno, ponno))  # onuno, portno, service num
        onu_items = onu_p.findall(self.__config)
        # print(onu_items)

        # 获取ONU, 过滤端口已经配置了业务的ONU
        onu_service_nums = []
        for index in onu_items:
            onuid_list = []
            onuno_sp = index[0].split(',')
            for index_sp in onuno_sp:
                if r"-" in index_sp:
                    onu_l = index_sp.split("-")
                    onuid_list.extend(list(range(int(onu_l[0]), int(onu_l[1])+1)))
                else:
                    onuid_list.append(int(index_sp))
            # print("onuid_list:", onuid_list)
            if int(onuno) in onuid_list:
                onu_service_nums.append(index)
                # print("index:", index)

        # print("onu_service:", onu_service_nums)

        # 获取端口业务
        # set ep sl \d* p \d* o [-,0-9]* p \d* serv \d* vlan_m \S* \d* 33024 [\d,]*
        onu_service = []
        service_model = []
        for onuindex in onu_service_nums:
            # {serviceType: unicast|multicast, cvlan:tag|translate, tvlan: boolean, svlan: boolean}
            onu_model = [{'serviceType': None}] * int(onuindex[2])
            model = None
            # print("fe port:", onuindex[1])
            # 获取端口业务配置
            onu_fe_services = re.compile(
                r'set ep sl (%s) p (%s) o ([-,0-9]*) p (%s) serv (\d*) vlan_m (\S*) (\d*) 33024 ([\d,]*)' %
                (slotno, ponno, onuindex[1]))
            # (slotno, ponno, onuno, portno, serid, cvlanmode, cos, clvan)
            onu_fe_items = onu_fe_services.findall(self.__config)
            for index in onu_fe_items:
                onufe_vlans = index[-1].split(',')
                onuid_lists = []
                onuno_sp = index[2].split(',')
                # print("onufe_vlans:", onufe_vlans)
                # print("onuno_sp:", onuno_sp)
                for index_sp in onuno_sp:
                    if r"-" in index_sp:
                        onu_l = index_sp.split("-")
                        onuid_lists.extend(list(range(int(onu_l[0]), int(onu_l[1])+1)))
                    else:
                        onuid_lists.append(int(index_sp))
                try:
                    # print("onuid_list:", onuid_lists)
                    # print("index:", onuid_lists.index(int(onuno)))
                    # print("{onuno:vlan}:", onuno, onufe_vlans[onuid_lists.index(int(onuno))])
                    # vlan = onufe_vlans[onuid_lists.index(int(onuno))]
                    # onu_service.append((slotno, ponno, onuno, index[3], index[4], index[5], vlan))
                    # onu_model[int(index[4])-1]['serviceType'] = 'unicast'
                    # onu_model[int(index[4])-1]['cvlan'] = index[5]  # cvlan
                    if index[5] == 'tag':
                        model = 0x0     # tag
                    else:
                        model = 0x1     # transparent
                except ValueError as err:
                    print("ONUID not match!!!")

            # 获取组播业务
            onu_fe_multicast = re.compile(
                r'set ep sl (%s) p (%s) o ([-,0-9]*) p (%s) serv (%s) ty multi' %
                (slotno, ponno, onuindex[1],
                 onuindex[2]))
            onu_fe_items = onu_fe_multicast.findall(self.__config)
            for index in onu_fe_items:
                onuid_lists = []
                onuno_sp = index[2].split(',')
                for index_sp in onuno_sp:
                    if r"-" in index_sp:
                        onu_l = index_sp.split("-")
                        onuid_lists.extend(list(range(int(onu_l[0]), int(onu_l[1])+1)))
                    else:
                        onuid_lists.append(int(index_sp))
                try:
                    # print("onuid_lists:", onuid_lists)
                    # print("index:", onuid_lists.index(int(onuno)))
                    # print("{onuno:vlan}:", onuno, onufe_vlans[onuid_lists.index(int(onuno))])
                    # onu_index = onuid_lists.index(int(onuno))
                    # onu_service.append((slotno, ponno, onuno, index[3], index[4], 'multicast'))
                    # onu_model[int(index[4])-1]['serviceType'] = 'multicast'
                    if model is not None:   
                        model = 0x8 | model
                except ValueError as err:
                    # print("serviceType is unicast!")
                    print("ONUID not match!!!")

            # 获取qinq域
            # set ep sl \d* p \d* o [-,0-9]* p \d* serv \d* qinq en \d* 33024 \S* \S* [,0-9]*
            onu_qinq_prf = re.compile(
                r'set ep sl (%s) p (%s) o ([-,0-9]*) p (%s) serv (%s) qinq en (\d*) 33024 (\S*) (\S*) ([,0-9]*)' %
                (slotno, ponno, onuindex[1], onuindex[2]))
            # (slot, pon, onuid, portno, servid, scos, qinqprf, servicename, svlan)
            onu_qinq_items = onu_qinq_prf.findall(self.__config)
            for index in onu_qinq_items:
                qinq_svlan = index[-1].split(',')
                onuno_sp = index[2].split(',')
                onuid_lists = []
                for index_sp in onuno_sp:
                    if r"-" in index_sp:
                        onu_l = index_sp.split("-")
                        onuid_lists.extend(list(range(int(onu_l[0]), int(onu_l[1])+1)))
                    else:
                        onuid_lists.append(int(index_sp))
                try:
                    # print("onuid_list:", onuid_lists)
                    # print("index:", onuid_lists.index(int(onuno)))
                    # print("{onuno:vlan}:", onuno, onufe_vlans[onuid_lists.index(int(onuno))])
                    # svlan = qinq_svlan[onuid_lists.index(int(onuno))]
                    # onu_service.append((slotno, ponno, onuno, index[3], index[4], index[5], index[6], index[7],  svlan))
                    # onu_model[int(index[4])-1]['qinq'] = True
                    if model is not None:
                        model = 0x4 | model
                except ValueError as err:
                    # print("Qinq disable")
                    print("ONUID not match!!!")

            # print("{slotno} {ponno} {onuno} {portno} {serviceid} {servicemodel}".format(slotno=slotno,
                                                                                        # ponno=ponno, onuno=onuno, portno=onuindex[1],  serviceid=onuindex[2], servicemodel=onu_model))
            # print("model:%d" % model)
            service_model.append(model)
        # print("ONU Service:", onu_service)
        print("service_model:", set(service_model))
        return tuple((slotno, ponno, onuno, list(set(service_model))))


    def get_onu_OLT_qinq(self):
        pass

    def get_onu_mac_limit(self):
        pass

    def get_onu_bd_profile(self):
        pass

    def get_onu_fe_bd_limit(self):
        pass

    def display_configs(self):
        onu_whitelist = self.get_onu_whitelist()
        if onu_whitelist:
            # print(onu_whitelist)
            # print("!!!!onu fe:\n")
            onu_service_model = []
            for item in onu_whitelist:
                print("\n!!!!onu fe:")
                print(item)
                onu_config = self.get_onu_fe_config(item[1], item[2], item[3])
                # input("Enter any key to continue!")
                onu_service_model.extend(onu_config[-1])
            print(self.onu_type, set(onu_service_model))

    def test_configs(self):
        self.get_onu_fe_config(14, 2, 18)


if __name__ == "__main__":
    print(os.getcwd())
    path = os.path.join(os.getcwd(), '.\etc\lingui_AN5516_10.103.111.221.txt')
    print(path)
    get_onu_obj = GetONUConfig(path, "5006-10B")
    #a = get_onu_obj.get_onu_whitelist()
    get_onu_obj.display_configs()
    # get_onu_obj.test_configs()
    # get_onu_obj = GetONUConfig(path, '5', '1', '6')
    # get_onu_obj.display_configs()
