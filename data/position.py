#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   position.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-01 10:46   liuhao      1.0         None
"""
from math import sqrt


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_position_distance(self, other_position):
        return sqrt(pow(other_position.x - self.x, 2) + pow(other_position.y - self.y, 2))

