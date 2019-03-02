# coding: utf-8
"""
一些基本的工具函数
"""
import time


def get_time_torday():
    return int(time.mktime(time.strptime(time.time(), '%Y%m%d')))