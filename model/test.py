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
from global_data import list_base, list_destination, list_trunk
from model.order import Order
from model.trunk import Trunk

inquriry_info = InquiryInfo()
baseNum = 40
destination_num = 2000
trunk_num = 2400
for base_index in range(baseNum):
    temp_base = BaseStation(base_index, inquriry_info)
    list_base.append(temp_base)

for destination_index in range(destination_num):
    temp_destination = Destination(destination_index, inquriry_info)
    list_destination.append(temp_destination)

for trunk_index in range(trunk_num):
    temp_trunk = Trunk(trunk_index, inquriry_info)
    list_trunk.append(temp_trunk)
    order1 = Order(1, 12, 0, destination=list_destination[1], car_num=1, group=0)
    order2 = Order(1, 12, 0, destination=list_destination[2], car_num=1, group=1)
    order3 = Order(1, 12, 0, destination=list_destination[3], car_num=1, group=2)
    order4 = Order(1, 12, 0, destination=list_destination[4], car_num=1, group=3)

list_position = [list_destination[1], list_destination[2], list_destination[3], list_destination[4]]
list_trunk[0].add_target_position_list(list_position)
order_list = [order1,order2,order3,order4]
list_trunk[0].add_order_list(order_list)

days = 10
for day in range(days):
    list_trunk[0].trunk_update_day()
    print("")
    print(day)
    print(list_trunk[0].trunk_target_position_list)
    print(list_trunk[0].trunk_target_time_list)
    print(list_trunk[0].trunk_finish_order_time)
    print(list_trunk[0].trunk_state)
    print(list_trunk[0].trunk_car_order_list)
    print(list_trunk[0].trunk_future_base_station_id)
