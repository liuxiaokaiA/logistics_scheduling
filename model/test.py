#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   test.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-01 17:39   liuhao      1.0         None
"""

# import lib
from model.base_station import BaseStation
from model.destination import Destination
from model.inquiry_info import InquiryInfo

inquriry_info = InquiryInfo()
list_base = []
list_destination = []
list_trunk = []
baseNum = 40
destination_num = 2000
trunk_num = 2400
for base_index in range(baseNum):
    temp_base = BaseStation(base_index, inquriry_info)
    list_base.append(temp_base)
for i in range(len(list_base)):
    print(inquriry_info.inquiry_base_position(list_base[i]).x, inquriry_info.inquiry_base_position(list_base[i]).y)

for destination_index in range(destination_num):
    temp_destination = Destination(destination_index, inquriry_info)
    list_destination.append(temp_destination)
for i in range(len(list_destination)):
    print(inquriry_info.inquiry_destination_position(list_destination[i]).x, inquriry_info.inquiry_destination_position(list_destination[i]).y)
print(len(list_destination))

print(list_base[6].get_distance(list_destination[100]))
