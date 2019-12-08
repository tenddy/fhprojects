#!/usr/bin/python3
# coding=UTF-8
'''
@Description:
@Author:  Teddy.tu
@Date: 2019-12-06 21:38:44
@LastEditTime: 2019-12-08 22:10:25
@LastEditors:  Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''
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
set ep sl 17 p 8 o 1,6-7 p 4 serv 1 vlan_m tag 255 33024 1000,1006,1007
set ep sl 17 p 8 o 7 p 4 serv 1 qinq en 255 33024 LGPPPOE_LAN ftthdata1 2567

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
            p = re.compile(r'set white phy addr \w{12} pas null ac add sl (\d*) p (\d*) o (\d*) ty %s' % self.onu_type)
            items.extend(p.findall(self.config__))

            p1 = re.compile(r'set white log sn \S* pas null ac add sl (\d*) p (\d*) o (\d*) ty %s' % self.onu_type)
            items.extend(p1.findall(self.config__))
            # print(items)
        if self.method__ == ONUID:
            p = re.compile(
                r'set white phy addr \w{12} pas null ac add sl %s p %s o %s ty (\S*)' % (self.slot, self.pon, self.onu))
            items.extend(p.findall(self.config__))

            p1 = re.compile(r'set white log sn \S* pas null ac add sl %s p %s o %s ty (\S*)' %
                            (self.slot, self.pon, self.onu))
            items.extend(p1.findall(self.config__))
            # print(items)
        return items

    def get_onu_fe_config(self):
        pass

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
            print(onu_whitelist)


if __name__ == "__main__":
    path = r'E:/Python/code/pyFHAT/lingui_AN5516_10.103.111.221.txt'
    get_onu_obj = GetONUConfig(path, "5006-10B")
    #a = get_onu_obj.get_onu_whitelist()
    get_onu_obj.display_configs()
    get_onu_obj = GetONUConfig(path, '5', '1', '6')
    get_onu_obj.display_configs()
