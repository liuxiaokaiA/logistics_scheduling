# coding: utf-8
"""
@File    :   position_generate.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-01 14:10   liuhao      1.0         None
"""
from cmath import sqrt
import numpy as np

from data.StatueData import TRUNK_TYPE_SMALL, TRUNK_IN_ORDER, TRUNK_IN_ORDER_DESTINATION, TRUNK_TYPE_MIDDLE, \
    TRUNK_TYPE_BIG
from global_data import trunk_num, distance_around, base_num, destination_num, order_num
from model.inquiry_info import InquiryInfo
import logging

from model.order import Order
from .base.distribution_model import Poisson, get_destination
from .base.order_id import OrderGroupId
from .base.utils import get_time_torday


class BaseStation:
    """网点类"""

    def __init__(self, b_id, inquiry_info):
        """网点id和查询类获得网点实例"""
        self.b_id = b_id
        self.inquiry_info = inquiry_info
        if not isinstance(inquiry_info, InquiryInfo):
            logging.error("Please enter right InquiryInfo")
        self.position = inquiry_info.inquiry_base_position_by_id(b_id)
        self.name = inquiry_info.inquiry_base_name_by_id(b_id)
        self.near_trunk_list = []
        self.near_destination_list = []
        self.near_base_list = []
        self.trunk_in_station = []
        self.trunk_other_in_station = []
        for index in range(trunk_num):
            if index % base_num == self.b_id:
                self.trunk_in_station.append(index)
        for i in range(destination_num):
            if (inquiry_info.inquiry_distance_by_id(b_id_1=b_id, d_id_1=i)) < distance_around:
                self.near_destination_list.append(i)
        for j in range(base_num):
            if (inquiry_info.inquiry_distance_by_id(b_id_1=b_id, b_id_2=j)) < distance_around and j != self.b_id:
                self.near_base_list.append(j)
        self.new_orders = set()
        self.new_orders_num = 0
        # 统计数据
        # 网点     self.b_id
        # 地理位置  self.position
        # 未出发车辆（本地）：len（self.trunk_in_station)（output)
        # 未出发车辆（外地）：len（self.trunk_other_in_station)(output)
        # 今日发车       ：  len（self.trunk_in_station)（update)-len（self.trunk_in_station)（output)
        # 今日发车（外地）：  len（self.trunk_other_in_station)（update)-len（self.trunk_other_in_station)（output)
        # 未归车辆：trunk_num/base_num - len（self.trunk_in_station)（update)
        # 今日订单数:self.new_orders_num(output)
        # 压板订单 ：self.new_order[i].class_of_delay_time 1,2,3
        # 网点可调度车：len（self.trunk_in_station)（output)+ len（self.trunk_other_in_station)(output)
        # 周围200公里网点 ：self.near_destination_list
        # 200公里可调度车：get_near_trunk（base，trunk_list）
        # 500公里可调度车：get_near_trunk（base，trunk_list，500）

    def get_position(self):
        """获取网点position"""
        return self.position

    def get_distance(self, place):
        """查询网点与某个网点或某个4S店的距离"""
        return self.inquiry_info.inquiry_distance(self, place)

    def update_near_trunk(self, trunk_list, distance=distance_around):
        """获取附近指定距离内车辆"""
        self.near_trunk_list = []
        for index in range(len(trunk_list)):
            if self.position.get_position_distance(trunk_list[index].trunk_position) < distance:
                self.near_trunk_list.append(trunk_list[index].trunk_id)

    def update_in_station_trunk(self, trunk_list):
        self.trunk_in_station = []
        self.trunk_other_in_station = []
        for trunk in trunk_list:
            if trunk.trunk_state == TRUNK_IN_ORDER and trunk.trunk_base_id == self.b_id:
                self.trunk_in_station.append(trunk.trunk_id)
            elif trunk.trunk_state == TRUNK_IN_ORDER_DESTINATION and trunk.trunk_current_base_station_id == self.b_id:
                self.trunk_other_in_station.append(trunk.trunk_id)

    def create_orders(self, day):
        # 泊松分布获取生成订单个数，传入参数
        param = order_num
        order_count = Poisson(param).get_num()
        # 获取今天0点的时间
        timestamp = day
        now = day
        # 获取4S点分布以及每个4S点的订单个数
        destination_data = get_destination(order_count)
        default_car_num = 1
        # 自动获取组id
        group = OrderGroupId().id
        # 生成订单
        self.new_orders_num = 0
        for destination in destination_data:
            car_num = destination_data[destination]
            self.new_orders_num += car_num
            for i in range(car_num):
                # order = Order(self.b_id, timestamp, now, destination, default_car_num, group,)
                # order.set_delay_time()
                # self.new_orders.add(order)
                pass

    def get_trunk(self, trunk_type=TRUNK_TYPE_SMALL):
        for id in self.trunk_in_station:
            if trunk_type == TRUNK_TYPE_SMALL:
                if id < trunk_num / 3:
                    return id
            elif trunk_type == TRUNK_TYPE_MIDDLE:
                if trunk_num * 2 / 3 > id >= trunk_num / 3:
                    return id
            elif trunk_type == TRUNK_TYPE_BIG:
                if id >= trunk_num * 2 / 3:
                    return id
            else:
                return None
        else:
            return None


def get_near_trunk(base, trunk_list, distance=distance_around):
    """获取附近指定距离内车辆"""
    near_trunk_list = []
    for index in range(len(trunk_list)):
        if base.position.get_position_distance(trunk_list[index].trunk_position) < distance:
            near_trunk_list.append(trunk_list[index].trunk_id)
    return near_trunk_list
