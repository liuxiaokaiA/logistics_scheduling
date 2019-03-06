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
    TRUNK_IN_ORDER_DESTINATION, TRUNK_NOT_USE, TRUNK_ON_ROAD_NOT_USE
from data.position import Position
from global_data import trunk_num, base_num, distance_around
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
        if self.trunk_id < trunk_num / 3:
            self.trunk_type = TRUNK_TYPE_SMALL
        elif self.trunk_id < trunk_num * 2 / 3:
            self.trunk_type = TRUNK_TYPE_MIDDLE
        else:
            self.trunk_type = TRUNK_TYPE_BIG

        # 车类归属网点
        self.trunk_base_id = trunk_id % base_num
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
        # 汽车速度
        self.trunk_speed = trunk_speed
        # 此坐标表示未来运输车将去的网点
        self.trunk_future_base_station_id = None
        # 此坐标表示车当前所在网点id
        self.trunk_current_base_station_id = self.trunk_base_id

        # 前一天车坐标
        self.trunk_before_day_position = self.trunk_position
        # 汽车在网点等待时间
        self.wait_day = 0
        # 汽车因为各种原因等待时间
        self.sleep_day = 0

        # 附近网点
        self.near_base_list = []
        self.get_near_base_list()

    def add_target_position_list(self, position_list):
        self.wait_day = 0
        # 从当前网点返回base_station
        if isinstance(position_list[-1], BaseStation):
            self.trunk_state = TRUNK_ON_ROAD
            distance = self.inquiry_info.inquiry_distance_by_id(b_id_1=self.trunk_current_base_station_id,
                                                                b_id_2=self.trunk_base_id)
            self.trunk_future_base_station_id = position_list[-1].b_id
            self.trunk_target_time_list = []
            self.trunk_target_time_list.append(distance / self.trunk_speed)
            return

        # 前往运送订单
        # 表示正在运货，在网点200公里附近，前往网点取货，不可调度
        if len(self.trunk_target_position_list) != 0:
            self.trunk_state = TRUNK_ON_ROAD_NOT_USE

        # 车辆目的地序列更新
        self.trunk_target_position_list = position_list

        # 车辆到底目的地时间更新
        self.trunk_target_time_list = []

        # 车辆预计到达时间更新
        # 第一种情况从网点出发
        if self.trunk_state == TRUNK_IN_ORDER or self.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            for index in range(len(self.trunk_target_position_list)):
                distance = 0.0
                if index == 0:
                    distance = self.trunk_position.get_position_distance(self.trunk_target_position_list[0].position)
                    # if isinstance(self.trunk_target_position_list[0], BaseStation):
                    #     distance = self.inquiry_info.inquiry_distance_by_id(b_id_1=self.trunk_current_base_station_id,
                    #                                                         b_id_2=self.trunk_target_position_list[
                    #                                                             0].b_id)
                    # else:
                    #     distance = self.inquiry_info.inquiry_distance_by_id(b_id_1=self.trunk_current_base_station_id,
                    #                                                         d_id_1=self.trunk_target_position_list[
                    #                                                             0].d_id)
                else:
                    distance = self.inquiry_info.inquiry_distance(self.trunk_target_position_list[index - 1],
                                                                  self.trunk_target_position_list[index])

                evaluate_time = distance / self.trunk_speed
                if index == 0:
                    self.trunk_target_time_list.append(evaluate_time)
                else:
                    self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + evaluate_time)
            # 车辆状态更新
            self.trunk_state = TRUNK_ON_ROAD

        elif self.trunk_state == TRUNK_ON_ROAD:
            for index in range(len(self.trunk_target_position_list)):
                distance = 0.0
                if index == 0:
                    distance = self.trunk_position.get_position_distance(self.trunk_target_position_list[0].position)
                else:
                    distance = self.inquiry_info.inquiry_distance(self.trunk_target_position_list[index - 1],
                                                                  self.trunk_target_position_list[index])

                evaluate_time = distance / self.trunk_speed
                if index == 0:
                    self.trunk_target_time_list.append(evaluate_time)
                else:
                    self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + evaluate_time)
            # 车辆状态更新
            self.trunk_state = TRUNK_ON_ROAD_NOT_USE

        # 自动搜素最近一个网点作为最后目的地
        if self.trunk_current_base_station_id == self.trunk_base_id:
            self.trunk_future_base_station_id, last_distance = self.inquiry_info.inquiry_nearest_base_station(
                position_list[-1].d_id)
            # 计算进入最后网点等待时间
            self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + last_distance / self.trunk_speed)
        # 异地等待网点出发送单，回到最初base
        else:
            self.trunk_future_base_station_id = self.trunk_base_id
            last_distance = self.inquiry_info.inquiry_distance_by_id(b_id_1=self.trunk_base_id,
                                                                     d_id_1=position_list[-1].d_id)
            # 计算进入最后网点等待时间
            self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + last_distance / self.trunk_speed)

        # 车辆预计进入等待时间更新
        self.trunk_finish_order_time = self.trunk_target_time_list[-1]
        self.trunk_current_base_station_id = None

    def add_order(self, order):
        # 添加单个 order
        if len(self.trunk_car_order_list) == self.trunk_type:
            logging.error("不能再添加车辆，车辆已满")
            sys.exit(1)
        # 目的地序列增加
        self.trunk_car_order_list.append(order)

    def add_order_list(self, order_list):
        """给予车辆订单list"""
        if len(order_list) > self.trunk_type:
            logging.error("车辆过多，位置不足")
            sys.exit(1)
        else:
            self.trunk_car_order_list = []
            self.trunk_car_order_list = order_list

    def trunk_update_day(self):
        """每辆车每天进行更新"""
        temp_time_list = []
        for index in range(len(self.trunk_target_time_list)):
            if self.trunk_target_time_list[index] > 24:
                temp_time_list.append(self.trunk_target_time_list[index] - 24)

        if len(temp_time_list) == 0:
            if self.trunk_state == TRUNK_IN_ORDER:
                self.wait_day = 0
                self.trunk_position = self.trunk_before_day_position
            elif self.trunk_state == TRUNK_ON_ROAD:
                self.trunk_current_base_station_id = self.trunk_future_base_station_id
                self.trunk_future_base_station_id = None
                self.trunk_position = self.inquiry_info.inquiry_base_position_by_id(
                    self.trunk_current_base_station_id)
                if self.trunk_current_base_station_id != self.trunk_base_id:
                    self.trunk_state = TRUNK_IN_ORDER_DESTINATION
                    self.wait_day += 1
                else:
                    self.trunk_state = TRUNK_IN_ORDER
            elif self.trunk_state == TRUNK_IN_ORDER_DESTINATION:
                self.trunk_position = self.trunk_before_day_position
                if self.trunk_current_base_station_id != self.trunk_base_id:
                    self.wait_day += 1
            elif self.trunk_state == TRUNK_NOT_USE:
                """暂时不使用进入NOT_USE状态"""
                self.sleep_day -= 1
                if self.sleep_day == 0:
                    self.trunk_state = TRUNK_IN_ORDER
                self.trunk_position = self.trunk_before_day_position
            elif self.trunk_state == TRUNK_ON_ROAD_NOT_USE:
                self.trunk_current_base_station_id = self.trunk_future_base_station_id
                self.trunk_future_base_station_id = None
                self.trunk_position = self.inquiry_info.inquiry_base_position_by_id(self.trunk_current_base_station_id)
                if self.trunk_current_base_station_id != self.trunk_base_id:
                    self.trunk_state = TRUNK_IN_ORDER_DESTINATION
                    self.wait_day += 1
                else:
                    self.trunk_state = TRUNK_IN_ORDER
            self.trunk_finish_order_time = 0
            self.trunk_target_position_list = []
            self.trunk_car_order_list = []
            self.trunk_target_time_list = []
        else:
            if len(temp_time_list) == len(self.trunk_target_time_list):
                self.trunk_position = self.calculate_position(self.trunk_before_day_position,
                                                              self.trunk_target_position_list[0].position,
                                                              temp_time_list[0])
                # if isinstance(self.trunk_target_position_list[0], BaseStation):
                #     self.trunk_state = TRUNK_ON_ROAD_NOT_USE
                # else:
                #     self.trunk_state = TRUNK_ON_ROAD

            else:
                self.trunk_position = self.calculate_position(
                    self.trunk_target_position_list[-1 * len(temp_time_list)].position,
                    self.trunk_target_position_list[-1 * len(temp_time_list) + 1].position,
                    temp_time_list[0]
                )

                reach_position_list = self.trunk_target_position_list[
                                      0:len(self.trunk_target_position_list) - len(temp_time_list) + 1]

                # 倒着删掉订单
                for i in range(len(self.trunk_car_order_list) - 1, -1, -1):
                    for j in range(len(reach_position_list)):
                        if isinstance(reach_position_list[j], Destination):
                            if self.trunk_car_order_list[i].destination == reach_position_list[j].d_id:
                                self.trunk_car_order_list.remove(self.trunk_car_order_list[i])
                if len(temp_time_list) > 1:
                    self.trunk_target_position_list = self.trunk_target_position_list[-1 * len(temp_time_list) + 1:]
                elif len(temp_time_list) == 1:
                    self.trunk_target_position_list = []

            # 更新状态
            # if len(self.trunk_target_position_list) != 0 and isinstance(self.trunk_target_position_list[0], BaseStation):
            #     self.trunk_state = TRUNK_ON_ROAD_NOT_USE
            # else:
            self.trunk_state = TRUNK_ON_ROAD
            self.trunk_target_time_list = temp_time_list
            self.trunk_finish_order_time -= 24
        self.trunk_before_day_position = self.trunk_position
        self.get_near_base_list()

    def calculate_position(self, position1, position2, time):
        """计算位置辅助"""
        distance1 = position1.get_position_distance(position2)
        distance2 = self.trunk_speed * time
        x = position2.x - distance2 / distance1 * (position2.x - position1.x)
        y = position2.y - distance2 / distance1 * (position2.y - position1.y)
        return Position(x, y)

    def random_sleep(self):
        """车辆随机进入休息状态"""
        num = random.randint() % 100
        if num == 0 or num == 1:
            self.sleep_day = random.randint() % 3
            self.trunk_state = TRUNK_NOT_USE

    def trunk_cost(self, car_number):
        """该车运输一定数量的轿车每公里费用"""
        if self.trunk_type == TRUNK_TYPE_SMALL:
            return 1.0 * (1 + car_number * 0.05)
        elif self.trunk_type == TRUNK_TYPE_MIDDLE:
            return 1.1 * (1 + car_number * 0.05)
        else:
            return 1.2 * (1 + car_number * 0.05)

    def trunk_cost_one_road(self, car_number, position1, position2):
        """一段路程的费用"""
        return self.trunk_cost(car_number) * (position1.get_position_distance(position2))

    def get_near_base_list(self):
        self.near_base_list = []
        for i in range(base_num):
            if self.trunk_position.get_position_distance(
                    self.inquiry_info.inquiry_base_position_by_id(i)) < distance_around:
                self.near_base_list.append(i)
        return self.near_base_list
