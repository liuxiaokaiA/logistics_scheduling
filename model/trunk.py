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
from itertools import permutations

from data.StatueData import TRUNK_IN_ORDER, TRUNK_TYPE_BIG, TRUNK_TYPE_MIDDLE, TRUNK_TYPE_SMALL, TRUNK_ON_ROAD, \
    TRUNK_IN_ORDER_DESTINATION, TRUNK_NOT_USE, TRUNK_ON_ROAD_NOT_USE
from data.position import Position
from global_data import trunk_num, base_num, distance_around, list_base
from model.base_station import BaseStation
from model.destination import Destination
from model.inquiry_info import InquiryInfo
import logging
import sys


class Trunk:

    def __init__(self, trunk_id, inquiry_info, trunk_speed=100):

        # 车辆编号
        self.trunk_id = trunk_id

        self.trunk_type = TRUNK_TYPE_BIG
        # 车类归属网点
        base, current_base, license, day, fleet = inquiry_info.inquiry_trunk_info(trunk_id)
        self.trunk_base_id = base
        self.fleet = fleet
        self.license = license

        # 车辆状态
        if base == current_base:
            self.trunk_state = TRUNK_IN_ORDER
        else:
            self.trunk_state = TRUNK_IN_ORDER_DESTINATION
        if not isinstance(inquiry_info, InquiryInfo):
            logging.error("Please enter right InquiryInfo")
        # 辅助查询类
        self.inquiry_info = inquiry_info
        # 车辆位置
        self.trunk_position = inquiry_info.inquiry_base_position_by_id(current_base)

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
        self.trunk_current_base_station_id = current_base
        # 此位置用于0315输出当前位置
        self.current_base_name = inquiry_info.inquiry_index_to_base(current_base)
        # 前一天车坐标
        self.trunk_before_day_position = self.trunk_position
        # 汽车在网点等待时间
        self.wait_day = day
        # 汽车因为各种原因等待时间
        self.sleep_day = 0
        # 附近网点
        self.near_base_list = []
        self.get_near_base_list()
        # 统计时间
        self.empty_transport = False
        # 最大装载
        self.max_transport = 0
        # 统计信息
        # 1 板车ID   ： trunk_base_id
        # 2 板车类型 ： trunk_type
        # 3 归属车队 ： trunk_base_id
        # 4 板车状态 ： trunk_state
        # 5 当前位置 ： trunk_position
        # 6 当前目的地序列：trunk_target_position_list
        # 7 到达时间预计：trunk_target_time_list
        # 8 订单情况：trunk_car_order_list
        # 9 最终入库：trunk_future_base_station_id
        # 10 最终入库时间 ：trunk_finish_order_time

    def trunk_init(self):
        pass

    def add_target_position_list(self, position_list_input):
        # 处理错误情况
        if len(position_list_input) == 0:
            logging.error("can not go without no position")
            return
        # if isinstance(position_list_input[-1], BaseStation) and len(position_list_input) > 1:
        #     logging.warning("we suggest the last position should not be BaseStation")

        # 等待时间置为0
        self.wait_day = 0

        #  单独处理卡车召回到起点情况
        if isinstance(position_list_input[-1], BaseStation):
            self.empty_transport = True
            self.trunk_state = TRUNK_ON_ROAD
            distance = self.inquiry_info.inquiry_distance_by_id(b_id_1=self.trunk_current_base_station_id,
                                                                b_id_2=self.trunk_base_id)
            self.trunk_future_base_station_id = position_list_input[-1].b_id
            self.trunk_target_time_list = []
            self.trunk_target_time_list.append(distance / self.trunk_speed)
            return
        # 首先优化路径
        position_list = self.sort_position_list(position_list_input)
        self.empty_transport = False
        # 处理卡车从起点出发状态量
        if self.trunk_state == TRUNK_IN_ORDER:
            # 车的状态更新
            if isinstance(position_list[0], BaseStation):
                self.trunk_state = TRUNK_ON_ROAD_NOT_USE
            elif isinstance(position_list[0], Destination):
                self.trunk_state = TRUNK_ON_ROAD
            # 目的地序列更新
            self.trunk_target_position_list = position_list
            # 车辆到底目的地时间更新
            self.trunk_target_time_list = []
            for index in range(len(self.trunk_target_position_list)):
                if index == 0:
                    distance = self.trunk_position.get_position_distance(self.trunk_target_position_list[0].position)
                else:
                    distance = self.inquiry_info.inquiry_distance(self.trunk_target_position_list[index - 1],
                                                                  self.trunk_target_position_list[index])

                road_time = distance / self.trunk_speed
                if index == 0:
                    self.trunk_target_time_list.append(road_time)
                else:
                    self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + road_time)
            # 判断最后位置是否未base_station, 若不是，返回最近base_station
            if isinstance(self.trunk_target_position_list[-1], BaseStation):
                logging.warning("last station should not be BaseStation, you indeed do may cause problem ")
                # 当前base_station 更新
                self.trunk_current_base_station_id = None
                # 未来入库 base_station 更新
                self.trunk_future_base_station_id = self.trunk_target_position_list[-1].b_id
                # 预计入库时间更新
                self.trunk_finish_order_time = self.trunk_target_time_list[-1]
            elif isinstance(self.trunk_target_position_list[-1], Destination):
                # 当前base_station 更新
                self.trunk_current_base_station_id = None
                # 未来入库 base_station 为距离最后4S店最近的base_station
                self.trunk_future_base_station_id, last_distance = self.inquiry_info.inquiry_nearest_base_station(
                    position_list[-1].d_id)
                # 计算进入最后网点等待时间
                last_road_time = last_distance / self.trunk_speed
                # 时间序列添加
                self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + last_road_time)
                # 预计入库时间更新
                self.trunk_finish_order_time = self.trunk_target_time_list[-1]
        elif self.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            # 车的状态更新
            if isinstance(position_list[0], BaseStation):
                self.trunk_state = TRUNK_ON_ROAD_NOT_USE
            elif isinstance(position_list[0], Destination):
                self.trunk_state = TRUNK_ON_ROAD
            # 目的地序列更新
            self.trunk_target_position_list = position_list
            # 车辆到底目的地时间更新
            self.trunk_target_time_list = []
            for index in range(len(self.trunk_target_position_list)):
                if index == 0:
                    distance = self.trunk_position.get_position_distance(self.trunk_target_position_list[0].position)
                else:
                    distance = self.inquiry_info.inquiry_distance(self.trunk_target_position_list[index - 1],
                                                                  self.trunk_target_position_list[index])

                road_time = distance / self.trunk_speed
                if index == 0:
                    self.trunk_target_time_list.append(road_time)
                else:
                    self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + road_time)
            # 判断最后位置是否为base_station, 若不是，返回车队
            if isinstance(self.trunk_target_position_list[-1], BaseStation):
                logging.warning("last station should not be BaseStation, you indeed do may cause problem ")
                # 当前base_station 更新
                self.trunk_current_base_station_id = None
                # 未来入库 base_station 更新
                self.trunk_future_base_station_id = self.trunk_target_position_list[-1].b_id
                # 预计入库时间更新
                self.trunk_finish_order_time = self.trunk_target_time_list[-1]
            elif isinstance(self.trunk_target_position_list[-1], Destination):
                # 当前base_station 更新
                self.trunk_current_base_station_id = None
                # 未来入库 base_station 为距离最后4S店最近的base_station
                self.trunk_future_base_station_id = self.trunk_base_id
                last_distance = self.inquiry_info.inquiry_distance_by_id(b_id_1=self.trunk_base_id,
                                                                         d_id_1=position_list[-1].d_id)
                # 计算进入最后网点等待时间
                last_road_time = last_distance / self.trunk_speed
                # 时间序列添加
                self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + last_road_time)
                # 预计入库时间更新
                self.trunk_finish_order_time = self.trunk_target_time_list[-1]
        elif self.trunk_state == TRUNK_ON_ROAD:
            if isinstance(position_list[0], Destination):
                logging.error("This truck which statue is on road is dispatched but not go Base Station")
            self.trunk_state = TRUNK_ON_ROAD_NOT_USE
            temp_before_position_list = self.trunk_target_position_list
            # 最后，目的地序列更新，需用之前目的地序列判断卡车
            self.trunk_target_position_list = position_list
            # 车辆到底目的地时间更新
            self.trunk_target_time_list = []
            for index in range(len(self.trunk_target_position_list)):
                if index == 0:
                    distance = self.trunk_position.get_position_distance(self.trunk_target_position_list[0].position)
                else:
                    distance = self.inquiry_info.inquiry_distance(self.trunk_target_position_list[index - 1],
                                                                  self.trunk_target_position_list[index])
                road_time = distance / self.trunk_speed
                if index == 0:
                    self.trunk_target_time_list.append(road_time)
                else:
                    self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + road_time)
                    # 判断最后位置是否未base_station, 若不是，返回最近base_station
            if isinstance(self.trunk_target_position_list[-1], BaseStation):
                # 未来入库 base_station 更新
                self.trunk_future_base_station_id = self.trunk_target_position_list[-1].b_id
                # 预计入库时间更新
                self.trunk_finish_order_time = self.trunk_target_time_list[-1]
            elif isinstance(self.trunk_target_position_list[-1], Destination):
                # 此段代码无错。这里表示只有此时需要改变trunk_future_base_station_id
                if len(temp_before_position_list) > 0 and isinstance(temp_before_position_list[-1], BaseStation):
                    self.trunk_future_base_station_id, temp_distance = self.inquiry_info.inquiry_nearest_base_station(
                        self.trunk_target_position_list[-1].d_id)

                # 未来入库 base_station 为之前行驶时候最终入库
                last_distance = self.inquiry_info.inquiry_distance_by_id(b_id_1=self.trunk_future_base_station_id,
                                                                         d_id_1=self.trunk_target_position_list[
                                                                             -1].d_id)
                # 计算进入最后网点等待时间
                last_road_time = last_distance / self.trunk_speed
                # 时间序列添加
                self.trunk_target_time_list.append(self.trunk_target_time_list[-1] + last_road_time)
                # 预计入库时间更新
                self.trunk_finish_order_time = self.trunk_target_time_list[-1]
        else:
            logging.error("The trunk can not be dispatch")

    def add_order(self, order):
        self.max_transport += 1
        # 添加单个 order
        if len(self.trunk_car_order_list) == self.trunk_type:
            logging.error("不能再添加车辆，车辆已满")
        # 目的地序列增加
        self.trunk_car_order_list.append(order)
        order.trunk_id = self.trunk_id

    def add_order_list(self, order_list):
        self.max_transport = len(order_list)
        """给予车辆订单list"""
        if len(order_list) > self.trunk_type:
            logging.error("车辆过多，位置不足")
            sys.exit(1)
        else:
            self.trunk_car_order_list = []
            self.trunk_car_order_list = order_list
        for order in self.trunk_car_order_list:
            order.trunk_id = self.trunk_id

    def trunk_update_day(self):
        """每辆车每天进行更新"""

        # 按照车的前一天状态进行更新
        if self.trunk_state == TRUNK_IN_ORDER:
            pass
        elif self.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            # 异地等待时间增加
            self.wait_day += 1
        elif self.trunk_state == TRUNK_ON_ROAD or self.trunk_state == TRUNK_ON_ROAD_NOT_USE:
            # 添加判断空驶逻辑
            if self.trunk_target_position_list and isinstance(self.trunk_target_position_list[-1], BaseStation):
                self.empty_transport = True
            else:
                self.empty_transport = False
            # 新的时间序列
            temp_time_list = []
            for time in self.trunk_target_time_list:
                if time > 24:
                    temp_time_list.append(time - 24)
            # 根据时间序列长度更新状态信息
            if len(temp_time_list) == 0:
                self.max_transport = 0
                # 所在base_station更新
                self.trunk_current_base_station_id = self.trunk_future_base_station_id
                self.trunk_future_base_station_id = None
                # 车队状态更新
                if self.trunk_current_base_station_id == self.trunk_base_id:
                    self.trunk_state = TRUNK_IN_ORDER
                else:
                    self.trunk_state = TRUNK_IN_ORDER_DESTINATION
                    self.wait_day += 1
                self.trunk_position = self.inquiry_info.inquiry_base_position_by_id(self.trunk_current_base_station_id)
                self.trunk_finish_order_time = 0
                self.trunk_target_position_list = []
                self.trunk_car_order_list = []
                self.trunk_target_time_list = []
            # 暂时知只处理Base全部在前面的情况
            else:
                if len(temp_time_list) == len(self.trunk_target_time_list):
                    # 一天一个目的地也未到达，只更新时间和位置
                    if len(self.trunk_target_position_list) != 0:
                        position = self.trunk_target_position_list[0].position
                    else:
                        position = self.inquiry_info.inquiry_base_position_by_id(self.trunk_future_base_station_id)

                    self.trunk_position = self.calculate_position(self.trunk_before_day_position, position,
                                                                  temp_time_list[0])
                    self.trunk_target_time_list = temp_time_list
                    self.trunk_finish_order_time -= 24
                else:
                    # 一天到达过目的地，需全部更新
                    reach_position_num = len(self.trunk_target_time_list) - len(temp_time_list)
                    reach_position_list = self.trunk_target_position_list[0:reach_position_num]
                    # 计算当前位置
                    if len(reach_position_list) != len(self.trunk_target_position_list):
                        self.trunk_position = self.calculate_position(
                            self.trunk_target_position_list[reach_position_num - 1].position,
                            self.trunk_target_position_list[reach_position_num].position, temp_time_list[0])
                    else:
                        self.trunk_position = self.calculate_position(
                            self.trunk_target_position_list[reach_position_num - 1].position,
                            self.inquiry_info.inquiry_base_position_by_id(self.trunk_future_base_station_id),
                            temp_time_list[0])
                    # 卸载货物
                    self.unload_order(reach_position_list)
                    # 更新目的地序列
                    self.trunk_target_position_list = self.trunk_target_position_list[reach_position_num:]
                    # 更新到达目的地时间序列
                    self.trunk_target_time_list = temp_time_list
                    # 更新预计入库时间
                    self.trunk_finish_order_time -= 24
                    # 更新车当前的状态
                    if len(self.trunk_target_position_list) > 0 and isinstance(self.trunk_target_position_list[0],
                                                                               BaseStation):
                        pass
                    else:
                        self.trunk_state = TRUNK_ON_ROAD
        self.trunk_before_day_position = self.trunk_position
        self.get_near_base_list()

    def calculate_position(self, position1, position2, time):
        """计算位置辅助"""
        distance1 = position1.get_position_distance(position2)
        distance2 = self.trunk_speed * time
        x = position2.x
        if abs(position2.x - position1.x) > 0.005:
            x = position2.x - distance2 / distance1 * (position2.x - position1.x)
        y = position2.y
        if abs(position2.y - position1.y) > 0.005:
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

    def unload_order(self, reach_position_list):
        remove_order_list = []
        for place in reach_position_list:
            for order in self.trunk_car_order_list:
                if isinstance(place, Destination) and order.destination == place.d_id:
                    remove_order_list.append(order)
        for order in remove_order_list:
            self.trunk_car_order_list.remove(order)

    def sort_position_list(self, position_list):
        if len(position_list) == 1:
            return position_list
        base_list = []
        destination_list = []
        for index in range(len(position_list)):
            if isinstance(position_list[index], Destination):
                base_list = position_list[0:index]
                destination_list = position_list[index:]
                break
        all_list = []
        for temp1 in permutations(destination_list):
            if base_list:
                for temp2 in permutations(base_list):
                    all_list.append(list(temp2 + temp1))
            else:
                all_list.append(list(temp1))
        nearest_list = []
        nearest_distance = 9999999

        if self.trunk_state in (TRUNK_IN_ORDER, TRUNK_IN_ORDER_DESTINATION):
            for current_list in all_list:
                last_position, last_distance = self.inquiry_info.inquiry_nearest_base_station(current_list[-1].d_id)
                sum_distance = last_distance
                current_list.insert(0, list_base[self.trunk_current_base_station_id])
                for index in range(len(current_list) - 1):
                    sum_distance += self.inquiry_info.inquiry_distance(current_list[index], current_list[index + 1])
                if sum_distance < nearest_distance:
                    nearest_list = current_list
                    nearest_distance = sum_distance
                current_list.remove(current_list[0])
        elif self.trunk_state == TRUNK_ON_ROAD:
            for current_list in all_list:
                last_position, last_distance = self.inquiry_info.inquiry_nearest_base_station(current_list[-1].d_id)
                sum_distance = last_distance
                sum_distance += self.trunk_position.get_position_distance(current_list[0].position)
                for index in range(len(current_list) - 1):
                    sum_distance += self.inquiry_info.inquiry_distance(current_list[index], current_list[index + 1])
                if sum_distance < nearest_distance:
                    nearest_list = current_list
                    nearest_distance = sum_distance
        return nearest_list
