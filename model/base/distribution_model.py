# coding: utf-8


class Poisson(object):
    def __init__(self, parameter):
        self.parameter = parameter

    def get_num(self):
        # 暂时直接返回
        return self.parameter


# 获取目的4S店的分布以及订单个数
def get_destination(count, destination_count):
    return {1: count/3, 2: count/3, 3: count/3}
