# coding: utf-8
import numpy as np


class Poisson(object):
    def __init__(self, parameter):
        self.parameter = parameter

    def get_num(self):
        return np.random.poisson(lam=self.parameter, size=1)[0]


# 获取目的4S店的分布以及订单个数
def get_destination(count, destination_count):
    return {1: count/3, 2: count/3, 3: count/3}
