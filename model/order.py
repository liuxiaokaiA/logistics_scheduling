# coding: utf-8
from .base.order_id import OrderId
from .base.utils import get_time_torday


class Order(object):
    def __init__(self, base, timestamp, now, destination, car_num, group):
        # 编号自动生成
        self.id = OrderId().id
        # 发运部编号
        self.base = base
        # 时间戳
        self.timestamp = timestamp
        # 当前时间
        self.now = now
        # 延迟发货时间
        self.delay_time = 0
        # 目的地4S点编号
        self.destination = destination
        # 订单汽车数量（为1）
        self.car_num = car_num
        # 延迟等级
        self.class_of_delay_time = 0
        # 订单分组编号
        self.group = group

    def set_delay_time(self):
        self.delay_time = (self.now - self.timestamp) / 24*3600
        if self.delay_time <= 5:
            self.class_of_delay_time = 1
        elif 5 < self.delay_time <= 10:
            self.class_of_delay_time = 2
        elif self.delay_time > 10:
            self.class_of_delay_time = 3
        else:
            print 'delay_time error!!,order id: %s' % str(self.id)

    def update_order(self):
        self.now = get_time_torday()
        self.set_delay_time()
