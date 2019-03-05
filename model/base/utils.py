# coding: utf-8
"""
一些基本的工具函数
"""
import time

from global_data import distance_around


def get_time_torday():
    return int(time.mktime(time.strptime(time.time(), '%Y%m%d')))


def is_near(position1, position2, distance):
    if position1.get_position_distance(position2) < distance:
        return True
    else:
        return False
