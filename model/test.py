#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@File    :   test.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-01 17:39   liuhao      1.0         None
"""

import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

from model.base_station import BaseStation
from model.destination import Destination
from model.inquiry_info import InquiryInfo
from global_data import list_base, list_destination, list_trunk, trunk_num, base_num, destination_num
from model.trunk import Trunk

inquriry_info = InquiryInfo()

for base_index in range(base_num):
    temp_base = BaseStation(base_index, inquriry_info)
    list_base.append(temp_base)
#
for destination_index in range(destination_num):
    temp_destination = Destination(destination_index, inquriry_info)
    list_destination.append(temp_destination)

for trunk_index in range(trunk_num):
    temp_trunk = Trunk(trunk_index, inquriry_info)
    list_trunk.append(temp_trunk)
    if trunk_index == 9:
        print temp_trunk.license

for base in list_base:
    base.update_in_station_trunk(list_trunk)
    base.update_near_trunk(list_trunk)
#     if base.b_id == 11:
#         print base.trunk_in_station

# base = list_base[12]
# city = list_destination[217]
# print(inquriry_info.inquiry_index_to_base(5))
#
# print(u"base name : %s 坐标 x ：%f 坐标 ：y: %f" % (base.name, base.position.x, base.position.y))
# print(u"city name : %s 坐标 x ：%f 坐标 ：y% f" % (city.name, city.position.x, city.position.y))
# print (inquriry_info.inquiry_distance(base, city))
# print (inquriry_info.inquiry_distance_by_id(b_id_1=base.b_id, d_id_1=city.d_id))
#
position = [u'房山', u'天津', u'顺义', u'北京', u'天津', u'沧州']
trunk_target_position_list = []
listBase = []

for index, p in enumerate(position):
    if index < 3:
        trunk_target_position_list.append(list_base[inquriry_info.inquiry_base_to_index(p)])
    else:
        trunk_target_position_list.append(list_destination[inquriry_info.inquiry_city_to_index(p)])


index = 0
while index < len(trunk_target_position_list):
        if index > 0 and isinstance(trunk_target_position_list[index], BaseStation):
            city_name = inquriry_info.inquiry_index_to_base(trunk_target_position_list[index].b_id)
            destination = inquriry_info.inquiry_city_to_index(city_name)
            if destination is not None:
                trunk_target_position_list.insert(index, list_destination[destination])
                index += 2
            else:
                index += 1
        elif isinstance(trunk_target_position_list[index], Destination):
            city_name = inquriry_info.inquiry_index_to_city(trunk_target_position_list[index].d_id)
            base = inquriry_info.inquiry_base_to_index(city_name)
            if base:
                trunk_target_position_list.insert(index + 1, list_base[base])
                index += 2
            else:
                index += 1

        else:
            index += 1
print len(trunk_target_position_list)