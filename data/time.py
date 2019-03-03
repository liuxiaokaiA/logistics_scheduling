#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   time.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-02 17:29   liuhao      1.0         None
"""


class Time:
    def __init__(self):
        self.day = 0

    def time_update(self):
        self.day += 1
