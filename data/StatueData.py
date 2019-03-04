#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   StatueData.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-02 11:58   liuhao      1.0         None
"""

# import lib

TRUNK_TYPE_SMALL = 6
TRUNK_TYPE_MIDDLE = 7
TRUNK_TYPE_BIG = 8
# 初始状态
TRUNK_IN_ORDER = 0
# 行驶状态
TRUNK_ON_ROAD = 1
# 请假状态
TRUNK_NOT_USE = 2
# 拉过货，在网点等待状态
TRUNK_IN_ORDER_DESTINATION = 3
# 正在赶往一个网点拉货，不可调度
TRUNK_ON_ROAD_NOT_USE = 4
