# coding: utf-8
from model.order import Order
from model.trunk import Trunk
from log import MyLogging
from read_configure import read_fuc
from algorithm.ga import update_global
from global_data import list_base, list_destination, list_trunk


def update(day):
    pass


def comput(day):
    pass


def output(day):
    pass


def init():
    from model.base_station import BaseStation
    from model.destination import Destination
    from model.inquiry_info import InquiryInfo

    inquriry_info = InquiryInfo()
    baseNum = 40
    destination_num = 2000
    trunk_num = 2400
    for base_index in range(baseNum):
        temp_base = BaseStation(base_index, inquriry_info)
        list_base.append(temp_base)

    for destination_index in range(destination_num):
        temp_destination = Destination(destination_index, inquriry_info)
        list_destination.append(temp_destination)

    for trunk_index in range(trunk_num):
        temp_trunk = Trunk(trunk_index, inquriry_info)
        list_trunk.append(temp_trunk)


if __name__ == "main":
    MyLogging()
    default_conf = read_fuc('conf/default.conf')
    update_global(default_conf)
    init()

    order1 = Order(1, 12, 0, destination=list_destination[1], car_num=1)
    order2 = Order(1, 12, 0, destination=list_destination[2], car_num=1)
    order3 = Order(1, 12, 0, destination=list_destination[3], car_num=1)
    order4 = Order(1, 12, 0, destination=list_destination[4], car_num=1)
    trunk1 = list_trunk[0]
    list_position = [list_destination[1], list_destination[2], list_destination[3], list_destination[4]]
list_trunk.add_target_position_list(list_position)
list_trunk.add_order_list([order1, order2, order3, order4])

    days = 100
    for day in range(days):
        list_trunk[0].trunk_update_day()
        update(day)
        comput(day)
        output(day)
