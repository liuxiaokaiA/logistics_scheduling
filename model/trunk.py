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
import random
from cmath import sqrt

from data.StatueData import TRUNK_IN_ORDER, TRUNK_TYPE_BIG, TRUNK_TYPE_MIDDLE, TRUNK_TYPE_SMALL, TRUNK_ON_ROAD, \
    TRUNK_IN_ORDER_DESTINATION, TRUNK_NOT_USE
from data.position import Position
from model.base_station import BaseStation
from model.destination import Destination
from model.inquiry_info import InquiryInfo
import logging
import sys


class Trunk:

    def __init__(self, trunk_id, inquiry_info, trunk_speed=100):

        # 车辆编号
        self.trunk_id = trunk_id
        # 车辆类型,数字表示运载量
        if self.trunk_id < 800:
            self.trunk_type = TRUNK_TYPE_SMALL
        elif self.trunk_id < 1600:
            self.trunk_type = TRUNK_TYPE_MIDDLE
        else:
            self.trunk_type = TRUNK_TYPE_BIG

        # 车类归属网点
        self.trunk_base_id = trunk_id % 40
        # 车辆状态
        self.trunk_state = TRUNK_IN_ORDER
        if not isinstance(inquiry_info, InquiryInfo):
            logging.error("Please enter right InquiryInfo")
            sys.exit(1)
        # 辅助查询类
        self.inquiry_info = inquiry_info
        # 车辆位置
        self.trunk_position = inquiry_info.inquiry_base_position_by_id(self.trunk_base_id)
        # 车辆目的地序列，由所加订单确定
        self.trunk_target_position_list = []
        # 车辆到达目的地序列时间
        self.trunk_target_time_list = []
        # 预计车辆进入等计划状态时间
        self.trunk_finish_order_time = 0
        # 所运小汽车所属订单序列
        self.trunk_car_order_list = []
        # 当前状态每公里费用
        self.trunk_cost = 1
        # 汽车速度
        self.trunk_speed = trunk_speed
        # 等计划的时候,表示现在所在能用。运货时候，此坐标表示未来空车将去的网点
        self.trunk_future_base_station_id = self.trunk_base_id

        # 前一天车坐标
        self.trunk_before_day_position = self.trunk_position
        # 汽车在网点等待时间
        self.wait_day = 0
        # 汽车因为各种原因等待时间
        self.sleep_day = 0
        # 车辆所停驻4S店信息
        self.wait_destination = Destination()

    def add_target_position_list(self, position_list):
        if len(self.trunk_target_position_list) != 0:
            self.trunk_target_position_list = []

        # 车辆目的地序列更新
        self.trunk_target_position_list = position_list
        self.trunk_state = TRUNK_ON_ROAD

        # # 自动搜素最近一个网点作为最后目的地
        # self.trunk_future_base_station_id, last_distance = self.inquiry_info.inquiry_nearest_base_station(
        #     position_list[-1])

        self.trunk_target_time_list = []
        # 车辆预计到达时间更新
        for index in range(len(self.trunk_target_position_list)):
            distance = 0.0
            if index == 0:
                if isinstance(self.trunk_target_position_list[0], BaseStation):
                    distance = self.inquiry_info.inquiry_distance_by_id(b_id_1=self.trunk_future_base_station_id,
                                                                        b_id_2=self.trunk_target_position_list[0].b_id)
                else:
                    distance = self.inquiry_info.inquiry_distance_by_id(b_id_1=self.trunk_future_base_station_id,
                                                                        d_id_1=self.trunk_target_position_list[0].d_id)
            else:
                distance = self.inquiry_info.inquiry_distance(self.trunk_target_position_list[index - 1],
                                                              self.trunk_target_position_list[index])

            evaluate_time = distance / self.trunk_speed
            if index == 0:
                self.trunk_target_time_list.append(evaluate_time)
            else:
                self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + evaluate_time)

        # # 计算进入最后网点等待时间
        # self.trunk_target_time_list.append(self.trunk_target_time_list[-1]+last_distance/self.trunk_speed)
        # 车辆预计进入等待时间更新
        self.trunk_finish_order_time = self.trunk_target_time_list[-1]

    def add_order(self, order):
        # 添加单个 order
        if len(self.trunk_car_order_list) == self.trunk_type:
            logging.error("不能再添加车辆，车辆已满")
            sys.exit(1)
        # 目的地序列增加
        self.trunk_car_order_list.append(order)

    def add_order_list(self, order_list):
        if len(order_list) > self.trunk_type:
            logging.error("车辆过多，位置不足")
            sys.exit(1)
        else:
            self.trunk_car_order_list = []
            self.trunk_car_order_list = order_list

    def trunk_update_day(self):

        temp_time_list = []
        for index in range(len(self.trunk_target_time_list)):
            if self.trunk_target_time_list[index] > 24:
                temp_time_list.append(self.trunk_target_time_list[index] - 24)
        if len(temp_time_list) == 0:
            if self.trunk_state == TRUNK_IN_ORDER:
                self.random_sleep()
                self.trunk_position = self.trunk_before_day_position
            elif self.trunk_state == :
                self.trunk_state = TRUNK_IN_ORDER_DESTINATION
                self.wait_destination = self.trunk_target_position_list[-1]
                self.trunk_position = self.inquiry_info.inquiry_destination_position(
                    self.trunk_target_position_list[-1])
                self.wait_day += 1
            elif self.trunk_state == TRUNK_IN_ORDER_DESTINATION:
                self.trunk_position = self.trunk_before_day_position
                self.wait_day += 1
            elif self.trunk_state == TRUNK_NOT_USE:
                self.sleep_day -= 1
                if self.sleep_day == 0:
                    self.trunk_state = TRUNK_IN_ORDER
                self.trunk_position = self.trunk_before_day_position
            self.trunk_finish_order_time = 0
            self.trunk_target_position_list = []
            self.trunk_car_order_list = []
            self.trunk_target_time_list = []
        else:
            if len(temp_time_list) == len(self.trunk_target_time_list):
                self.trunk_position = self.calculate_position(self.trunk_before_day_position,
                                                              self.trunk_target_position_list[0].position,
                                                              temp_time_list[0])
            else:
                self.trunk_position = self.calculate_position(
                    self.trunk_target_position_list[-1 * len(temp_time_list) - 1].position,
                    self.trunk_target_position_list[-1 * len(temp_time_list)].position,
                    temp_time_list[0]
                )
                reach_position_list = self.trunk_target_position_list[
                                      0:len(self.trunk_target_position_list) - len(temp_time_list)]
                for i in range(len(self.trunk_car_order_list) - 1, -1, -1):
                    for j in range(len(reach_position_list)):
                        if self.trunk_car_order_list[i].destination.d_id == reach_position_list[j].destination.d_id:
                            self.trunk_car_order_list.remove(self.trunk_car_order_list[i])

                self.trunk_target_position_list = self.trunk_target_position_list[-1 * len(temp_time_list):]

            self.trunk_target_time_list = temp_time_list
            self.trunk_finish_order_time -= 24
            self.trunk_state = TRUNK_ON_ROAD
        self.trunk_before_day_position = self.trunk_position

    def calculate_position(self, position1, position2, time):
        distance1 = position1.get_position_distance(position2)
        distance2 = self.trunk_speed * time
        x = position2.x - distance2 / distance1 * (position2.x - position1.x)
        y = position2.y - distance2 / distance1 * (position2.y - position1.y)
        return Position(x, y)

    def random_sleep(self):
        num = random.randint() % 100
        if num == 0 or num == 1:
            self.sleep_day = random.randint() % 3
            self.trunk_state = TRUNK_NOT_USE

    def trunk_cost(self, car_number):
        if self.trunk_type == TRUNK_TYPE_SMALL:
            return 1 * (1 + car_number * 0.05)
        elif self.trunk_type == TRUNK_TYPE_MIDDLE:
            return 1.1 * (1 + car_number * 0.05)
        else:
            return 1.2 * (1 + car_number * 0.05)


def get_cost(car_num, start, end):
    pass
