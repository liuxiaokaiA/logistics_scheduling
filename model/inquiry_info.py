#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   inquiry_info.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-01 17:51   liuhao      1.0         None
"""
import pandas as pd
import logging
from data.position import Position
from global_data import base_num, destination_num


class InquiryInfo:
    def __init__(self):
        try:
            self.base_position = pd.read_csv('../generate/base_position0315.csv')
            self.shop_position = pd.read_csv('../generate/city_position0315.csv')
            self.distance = pd.read_csv('../generate/distance0315.csv')
            self.trunk = pd.read_csv("../generate/trunk.csv")
            self.base_to_index = pd.read_csv("../generate/base_to_index.csv")
            self.city_to_index = pd.read_csv("../generate/city_to_index.csv")
        except Exception as e:
            print e
            self.base_position = pd.read_csv('generate/base_position0315.csv')
            self.shop_position = pd.read_csv('generate/city_position0315.csv')
            self.distance = pd.read_csv('generate/distance0315.csv')
            self.trunk = pd.read_csv("generate/trunk.csv")
            self.base_to_index = pd.read_csv("generate/base_to_index.csv")
            self.city_to_index = pd.read_csv("generate/city_to_index.csv")

    def inquiry_base_to_index(self, base):
        return (self.base_to_index[self.base_to_index['city'] == base]).index[0]

    def inquiry_city_to_index(self, city):
        return (self.city_to_index[self.city_to_index['city' == city]]).index[0]

    def inquiry_base_position(self, base_station):
        from model.base_station import BaseStation
        """用base_station来查询网点坐标"""
        if not isinstance(base_station, BaseStation):
            logging.error("this is not an instance of BaseStation")
        return self.inquiry_base_position_by_id(base_station.b_id)

    def inquiry_base_position_by_id(self, b_id):
        """用base_station.bid来查询网点坐标"""
        b_index = b_id
        position = Position(self.base_position['x'][b_index], self.base_position['y'][b_index])
        return position

    def inquiry_base_name_by_id(self, b_id):
        return self.base_position['city'][b_id]

    def inquiry_destination_position(self, destination):
        from model.destination import Destination
        """用destination来查询4S店坐标"""
        if not isinstance(destination, Destination):
            logging.error("this is not an instance of Destination")
        return self.inquiry_destination_position_by_id(destination.d_id)

    def inquiry_destination_position_by_id(self, d_id):
        """用destination.d_id来查询4S店坐标"""
        d_index = d_id
        position = Position(self.shop_position['x'][d_index], self.shop_position['y'][d_index])
        return position

    def inquiry_destination_name_by_id(self, d_id):
        return self.shop_position['city'][d_id]

    def inquiry_distance(self, place_one, place_two):
        from model.base_station import BaseStation
        from model.destination import Destination
        """用来查询网点与网点，4S店与4S店以及网点与4S店之间的距离"""
        if isinstance(place_one, BaseStation) and isinstance(place_two, BaseStation):
            return self.distance.values[place_one.b_id, place_two.b_id]
        elif isinstance(place_one, BaseStation) and isinstance(place_two, Destination):
            return self.distance.values[place_one.b_id, place_two.d_id + 60]
        elif isinstance(place_one, Destination) and isinstance(place_two, BaseStation):
            return self.distance.values[place_one.d_id + 60, place_two.b_id]
        elif isinstance(place_one, Destination) and isinstance(place_two, Destination):
            return self.distance.values[place_one.d_id + 60, place_two.d_id + 60]
        else:
            logging.error("Please return right place")

    def inquiry_distance_by_id(self, b_id_1=-1, b_id_2=-1, d_id_1=-1, d_id_2=-1):
        """用id来查询网点与网点，4S店与4S店以及网点与4S店之间的距离
           b_id_1:
           b_id_2:
           d_id_1:
           d_id_2:
        """
        wrongNum = 0
        if b_id_1 < 0 or b_id_1 > base_num:
            wrongNum += 1
        if b_id_2 < 0 or b_id_2 > base_num:
            wrongNum += 1
        if d_id_1 < 0 or d_id_1 > destination_num:
            wrongNum += 1
        if d_id_2 < 0 or d_id_2 > destination_num:
            wrongNum += 1
        if wrongNum == 0 or wrongNum == 1 or wrongNum == 3 or wrongNum == 4:
            logging.error("inquiry id wrong ")
            pass
        else:
            if b_id_1 > -1 and b_id_2 > -1:
                return self.distance.values[b_id_1, b_id_2]
            elif b_id_1 > -1 and d_id_1 > -1:
                return self.distance.values[b_id_1, d_id_1 + 60]
            elif d_id_1 > -1 and d_id_2 > -1:
                return self.distance.values[d_id_1 + 60, d_id_2 + 60]
            else:
                logging.error("inquiry parameter id wrong")
                return 0

    def inquiry_nearest_base_station(self, d_id):
        temp_id = 0
        nearest_distance = 99999999
        for i in range(base_num):
            current_distance = self.inquiry_distance_by_id(b_id_1=i, d_id_1=d_id)
            if current_distance < nearest_distance:
                nearest_distance = current_distance
                temp_id = i
        return temp_id, nearest_distance

    # fleet, license, current, day, base
    def inquiry_trunk_info(self, trunk_id):
        base = self.inquiry_base_to_index(self.trunk.loc[trunk_id]['base'])
        current_base = self.inquiry_base_to_index(self.trunk.loc[trunk_id]['current'])
        license = self.trunk.loc[trunk_id]['license']
        day = self.trunk.loc[trunk_id]['day']
        fleet = self.trunk.loc[trunk_id]['fleet']
        return base, current_base, license, day, fleet
