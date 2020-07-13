#!/usr/bin/python3
# coding=UTF-8

'''
@Description: 
采用Python操作Excel
@Author:  Teddy.tu
@Date: 2020-01-05 16:52:02
@LastEditTime: 2020-06-09 08:03:00
@LastEditors: Teddy.tu
@Email:  teddy_tu@126.com
@License:  (c)Copyright 2019-2020 Teddy_tu
'''

# from lib import dut_connect
import pandas as pd
import sys
import os
print(sys.path)
df = pd.read_excel(u'./etc/gpon.xlsx', sheet_name=0)
print(df.head(100))
print(df.iloc[0].values)

# x1 = xlrd.open_workbook(u'./config/广西四川M版本测试项_第三轮.xls')
# print(x1.sheet_names())

# device_info = x1.sheet_by_name(u'设备信息')
# print(device_info.row_values(0))

# device_info1 = x1.sheet_by_index(4)
# print(device_info1.row_values(0))
