#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   caculate_ditance.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-01 16:30   liuhao      1.0         None
"""
from math import sqrt

import pandas as pd
base_data = pd.read_csv('base_position0315.csv')
shop_data = pd.read_csv('city_position0315.csv')
all_data = pd.concat([base_data, shop_data], axis=0, ignore_index=True)
all_data_distance = []
for i in range(len(all_data)):
    temp_list = []
    for j in range(len(all_data)):
        temp_distance = sqrt(pow(all_data['x'][i]-all_data['x'][j], 2)+pow(all_data['y'][i]-all_data['y'][j], 2))
        temp_list.append(temp_distance)
        if i == j:
            print(i, j, temp_distance)
    all_data_distance.append(temp_list)
df = pd.DataFrame(all_data_distance)
df.to_csv('distance0315.csv', index=False)
