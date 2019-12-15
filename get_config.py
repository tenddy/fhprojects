#!/usr/bin/python3
# coding=UTF-8
'''
@Description:
通过AN5516 OLT的配置文件，提取对应ONU的所有的配置信息。

提取信息：
1、白名单（物理和逻辑）
set white phy addr 544b104068d8 pas null ac add sl 14 p 4 o 11 ty 5006-10B
set white log sn 0773000000589996 pas null ac add sl 4 p 2 o 18 ty OTHER2

2、端口业务配置
set ep sl 17 p 8 o 1,6-7 p 4 serv num 1
(set ep sl \d* p \d* o [-,0-9]* p \d* serv num \d*)
set ep sl 17 p 8 o 1,6-7 p 4 serv 1 vlan_m tag 255 33024 1000,1006,1007
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


ONUTYPE = 1
ONUID = 2


class GetONUConfig():
    def __init__(self, configfile, *args):
        with open(configfile, 'r', encoding='utf-8') as f:
            self.config__ = str(f.readlines())

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

    def get_onu_whitelist(self):
        items = []
        if self.method__ == ONUTYPE:
            p = re.compile(
                r'(set white phy addr \w{12} pas null ac add sl (\d*) p (\d*) o (\d*) ty %s)' % self.onu_type)
            items.extend(p.findall(self.config__))

            p1 = re.compile(r'(set white log sn \S* pas null ac add sl (\d*) p (\d*) o (\d*) ty %s)' % self.onu_type)
            items.extend(p1.findall(self.config__))
            # print(items)
        if self.method__ == ONUID:
            p = re.compile(
                r'(set white phy addr \w{12} pas null ac add sl %s p %s o %s ty (\S*))' %
                (self.slot, self.pon, self.onu))
            items.extend(p.findall(self.config__))

            p1 = re.compile(r'(set white log sn \S* pas null ac add sl %s p %s o %s ty (\S*))' %
                            (self.slot, self.pon, self.onu))
            items.extend(p1.findall(self.config__))
            # print(items)
        # print(p1.group())
        return items

    def get_onu_fe_config(self, slotno, ponno, onuno):
        onu_p = re.compile(r'set ep sl %s p %s o ([-,0-9]*) p (\d*) serv num (\d*)' %
                           (slotno, ponno))  # onuno, portno, service num
        onu_items = onu_p.findall(self.config__)
        print(onu_items)

        # 获取ONU
        onu_item = None
        for index in onu_items:
            onuid_list = []
            onuno_sp = index[0].split(',')
            for index_sp in onuno_sp:
                if r"-" in index_sp:
                    onu_l = index_sp.split("-")
                    onuid_list.extend(list(range(int(onu_l[0]), int(onu_l[1])+1)))
                else:  
                    onuid_list.append(int(index_sp))
            print("onuid_list:", onuid_list)
            if int(onuno) in onuid_list:
                onu_item = index

        print("onu_item:", onu_item)

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
            for item in onu_whitelist:
                print(item)
                print("!!!!onu fe:\n")
                self.get_onu_fe_config(item[1], item[2], item[3])
                # input("Enter any key to continue!")


if __name__ == "__main__":
    path = r'./lingui_AN5516_10.103.111.221.txt'
    get_onu_obj = GetONUConfig(path, "5006-10B")
    #a = get_onu_obj.get_onu_whitelist()
    get_onu_obj.display_configs()
    # get_onu_obj = GetONUConfig(path, '5', '1', '6')
    # get_onu_obj.display_configs()
