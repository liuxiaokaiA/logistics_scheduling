# coding: utf-8
import numpy as np
import random


class Poisson(object):
    def __init__(self, parameter):
        self.parameter = parameter

    def get_num(self):
        return np.random.poisson(lam=self.parameter, size=1)[0]


def get_destination_id(destination_count):
    while 1:
        id = destination_count / 4 * np.matlib.randn() + destination_count / 2
        if 0 <= int(id) < 2000:
            return id


# 获取目的4S店的分布以及订单个数
def get_destination(count, destination_count):
    sum_ = count
    dests = {}
    while sum_:
        rate = 0
        while 1:
            rate = random.random()
            if 0.1 <= rate <= 0.3:
                break
        n_dest = int(rate * count)
        if n_dest > sum_:
            n_dest = sum_
        sum_ -= n_dest
        while 1:
            id = get_destination_id(destination_count)
            if id not in dests:
                dests[id] = n_dest
            else:
                continue

    return dests
