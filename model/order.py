# coding: utf-8
from .base.order_id import OrderId


class Order(object):
    def __init__(self, base, timestamp, now, delay_time, destination, car_num,
                 class_of_delay_time, group):
        # 编号自动生成
        self.id = OrderId
        # 发运部编号
        self.base = base
        # 时间戳
        self.timestamp = timestamp
        # 当前时间
        self.now = now
        # 延迟发货时间
        self.delay_time = delay_time
        # 目的地4S点编号
        self.destination = destination
        # 订单汽车数量（为1）
        self.car_num = car_num
        # 延迟等级
        self.class_of_delay_time = class_of_delay_time
        # 订单分组编号
        self.group = group
