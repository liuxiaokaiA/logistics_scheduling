# coding: utf-8
import numpy as np
import time

from model.inquiry_info import InquiryInfo
import logging
from .base.distribution_model import Poisson, get_destination
from .base.order_id import OrderGroupId
from order import Order


class BaseStation:
    """网点类"""

    def __init__(self, b_id, inquiry_info):
        """网点id和查询类获得网点实例"""
        self.b_id = b_id
        self.inquiry_info = inquiry_info
        if not isinstance(inquiry_info, InquiryInfo):
            logging.error("Please enter right InquiryInfo")
        self.position = inquiry_info.inquiry_base_position_by_id(b_id)

    def get_position(self):
        """获取网点position"""
        return self.position

    def get_distance(self, place):
        """查询网点与某个网点或某个4S店的距离"""
        return self.inquiry_info.inquiry_distance(self, place)

    def update_nearly_trunk(self, trunk_list, distance=200):
        """获取附近指定距离内车辆"""
        pass

    def create_orders(self):
        order_count = Poisson(50).get_num()
        timestamp = time.time()
        now = timestamp
        delay_time = 0
        destination_data = get_destination(order_count)
        class_of_delay_time = 1
        default_car_num = 1

        group = OrderGroupId().id
        for destination in destination_data:
            car_num = destination_data[destination]
            for num in car_num:
                Order(self.b_id, timestamp, now, delay_time,
                        destination, default_car_num, class_of_delay_time, group)

