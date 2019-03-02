#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   trunk.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-01 11:02   liuhao      1.0         None
"""
from data.StatueData import TRUNK_IN_ORDER, TRUNK_TYPE_BIG, TRUNK_TYPE_MIDDLE, TRUNK_TYPE_SMALL
from model.inquiry_info import InquiryInfo
import logging
import sys


class Trunk:

    def __init__(self, trunk_id, inquiry_info):
        self.trunk_id = trunk_id

        if self.trunk_id < 800:
            self.trunk_type = TRUNK_TYPE_SMALL
        elif self.trunk_id < 1600:
            self.trunk_type = TRUNK_TYPE_MIDDLE
        else:
            self.trunk_type = TRUNK_TYPE_BIG

        self.trunk_base_id = trunk_id % 40
        self.trunk_state = TRUNK_IN_ORDER
        if not isinstance(inquiry_info, InquiryInfo):
            logging.error("Please enter right InquiryInfo")
            sys.exit(1)
        self.inquiry_info = inquiry_info
        self.position = inquiry_info.inquiry_base_position_by_id(self.trunk_base_id)
        self.trunk_target_position_list = []
        self.trunk_target_time_list = []
        self.trunk_finish_order_time = 0
        self.trunk_car_order_list = []
        self.trunk_cost = 1

    def add_target_position(self, place):
        self.trunk_target_position_list.append(place)

    def remove_target_position(self):
        if len(self.trunk_target_position_list) > 0:
            self.trunk_target_position_list.remove(self.trunk_target_position_list[0])

    def update_trunk_statue(self, statue=TRUNK_IN_ORDER):
        self.trunk_state = statue
