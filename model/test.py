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
from data.StatueData import TRUNK_TYPE_SMALL, TRUNK_IN_ORDER_DESTINATION, TRUNK_IN_ORDER
from model.base_station import BaseStation
from model.destination import Destination
from model.inquiry_info import InquiryInfo
from global_data import list_base, list_destination, list_trunk, trunk_num, base_num, destination_num
from model.order import Order
from model.trunk import Trunk

inquriry_info = InquiryInfo()

for base_index in range(base_num):
    temp_base = BaseStation(base_index, inquriry_info)
    list_base.append(temp_base)

for destination_index in range(destination_num):
    temp_destination = Destination(destination_index, inquriry_info)
    print(destination_index)
    list_destination.append(temp_destination)

for trunk_index in range(trunk_num):
    temp_trunk = Trunk(trunk_index, inquriry_info)
    list_trunk.append(temp_trunk)
order1 = Order(1, 12, 0, destination=list_destination[1], car_num=1, group=0)
order2 = Order(1, 12, 0, destination=list_destination[2], car_num=1, group=1)
order3 = Order(1, 12, 0, destination=list_destination[3], car_num=1, group=2)
order4 = Order(1, 12, 0, destination=list_destination[4], car_num=1, group=3)

list_position = [list_base[1], list_base[5], list_destination[1]]
# list_trunk[1].add_target_position_list(list_position)
order_list = [order1, order2, order3, order4]
for trunk in list_trunk:
    trunk.add_target_position_list(list_position)
    trunk.add_order_list(order_list)
print(list_trunk[1].trunk_position.x, list_trunk[1].trunk_position.y)
#
days = 10
for day in range(days):
    num = 0
    for trunk in list_trunk:
        trunk.trunk_update_day()
        if trunk.wait_day > 5:
            list1 = [list_base[trunk.trunk_base_id]]
            trunk.add_target_position_list(list1)
        if trunk.trunk_state == TRUNK_IN_ORDER:
            num += 1

    print("day %d"% day)
    print (num)


    # for position in list_trunk[1].trunk_target_position_list:
    #     print(position.position.x, position.position.y)

        # list_trunk[1].add_target_position_list(list1)
    # position = list_trunk[1].trunk_position
    # print(position.x, position.y)
    #     print(list_trunk[1].trunk_target_position_list)
    #     print(list_trunk[1].trunk_target_time_list)
    #     print(list_trunk[1].trunk_finish_order_time)
    # print(list_trunk[1].trunk_state)
    # print(list_trunk[1].trunk_future_base_station_id)
#     print(list_trunk[1].trunk_car_order_list)
#     print(list_trunk[1].trunk_future_base_station_id)
#     print(list_trunk[1].trunk_current_base_station_id)
