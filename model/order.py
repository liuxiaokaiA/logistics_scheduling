# coding: utf-8
from .base.order_id import OrderId
from global_data import list_base, list_destination


All_order = []


class Order(object):
    def __init__(self, id_, base, destination, delay_time, class_of_delay_time, car_num=1):
        # 编号自动生成

        # self.id = OrderId(day).id
        self.id = id_
        # 发运部编号
        self.base = base
        self.base_name = list_base[base].name
        # 时间戳
        # self.timestamp = timestamp
        # 当前时间
        # self.now = now
        # 延迟发货时间
        self.delay_time = delay_time
        # 目的地4S点编号
        self.destination = destination
        self.destination_name = list_destination[destination].name
        # 订单汽车数量（为1）
        self.car_num = car_num
        # 延迟等级
        self.class_of_delay_time = class_of_delay_time
        self.trunk_id = None
        global All_order
        All_order.append(self)

    def set_delay_time(self):
        if self.delay_time <= 5:
            self.class_of_delay_time = 1
        elif 5 < self.delay_time <= 10:
            self.class_of_delay_time = 2
        elif self.delay_time > 10:
            self.class_of_delay_time = 3
        else:
            print('delay_time error!!,order id: %s' % str(self.id))

    '''
    def update_order(self, day):
        self.now = day
        self.set_delay_time()
    '''
