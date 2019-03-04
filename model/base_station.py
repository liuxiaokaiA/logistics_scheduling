# coding: utf-8
from cmath import sqrt
import numpy as np
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
        self.near_trunk_list = []
        self.near_destination_list = []
        self.new_orders = set()

    def get_position(self):
        """获取网点position"""
        return self.position

    def get_distance(self, place):
        """查询网点与某个网点或某个4S店的距离"""
        return self.inquiry_info.inquiry_distance(self, place)

    def update_near_trunk(self, trunk_list, distance=200):
        """获取附近指定距离内车辆"""
        for index in range(len(trunk_list)):
            self.near_trunk_list = []
            if self.position.get_position_distance(trunk_list[index].position) < 200:
                self.near_trunk_list.append(trunk_list[index].trunk_id)

    def create_orders(self):
        # 泊松分布获取生成订单个数，传入参数
        param = 50
        order_count = Poisson(param).get_num()
        # 获取今天0点的时间
        timestamp = get_time_torday()
        now = timestamp
        # 获取4S点分布以及每个4S点的订单个数
        destination_data = get_destination(order_count)
        default_car_num = 1
        # 自动获取组id
        group = OrderGroupId().id
        # 生成订单
        for destination in destination_data:
            car_num = destination_data[destination]
            for num in car_num:
                order = Order(self.b_id, timestamp, now, destination, default_car_num, group)
                order.set_delay_time()
                self.new_orders.add(order)

