#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   position_generate.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-01 14:10   liuhao      1.0         None
"""
import random
from data.position import Position
import pandas as pd
import matplotlib.pyplot as plt


def position(num, baes_position_list):
    x_list = []
    y_list = []
    position_list = []
    while len(position_list) < 2000:
        position_available = True
        x = random.randint(0, 5600)
        y = random.randint(0, 5200)
        temp_position = Position(x, y)
        for m in range(len(position_list)):
            if Position.get_position_distance(temp_position, position_list[m]) < 25:
                position_available = False
                break
        for j in range(len(baes_position_list)):
            if Position.get_position_distance(temp_position, baes_position_list[j]) < 25:
                position_available = False
                break
        if position_available:
            position_list.append(temp_position)
            x_list.append(x)
            y_list.append(y)

    return x_list, y_list


base_data = pd.read_csv('base_position.csv')
base_position_list = []
for i in range(len(base_data)):
    position1 = Position(base_data.x[i], base_data.y[i])
    base_position_list.append(position1)

list_x, list_y = position(2000, base_position_list)
df = pd.DataFrame({'x': list_x, 'y': list_y})
df.to_csv("shop_position.csv", index=False)

plt.scatter(list_x, list_y)
plt.show()

# import lib
