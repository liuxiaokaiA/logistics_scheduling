# coding: utf-8
import logging

from data.StatueData import TRUNK_ON_ROAD, TRUNK_ON_ROAD_NOT_USE, TRUNK_IN_ORDER, TRUNK_IN_ORDER_DESTINATION
from model.trunk import Trunk
from log import MyLogging
from read_configure import read_fuc
from algorithm.ga import update_global, GA
from algorithm.model_data import get_trunk_max_order, get_orders_trunk_can_take, \
    modify_model, get_whole_trunk
from global_data import list_base, list_destination, list_trunk, all_scheduling, trunk_num, destination_num, base_num


def update(day):
    log.info('update base')
    new_order_num = 0
    for base in list_base:
        base.create_orders(day)
        base.update_in_station_trunk(list_trunk)
        base.update_near_trunk(list_trunk)
        for order in base.new_orders:
            if order.timestamp == day:
                new_order_num += 1
            order.update_order(day)
    for trunk in list_trunk:
        trunk.trunk_update_day()
    global history_order_num
    history_order_num += new_order_num

    print("今日新产生订单数为 ：%d" % new_order_num)
    print("历史订单总数为    ：%d" % history_order_num)


def compute(day):
    get_whole_trunk()
    trunk_max_order = get_trunk_max_order()
    data = get_orders_trunk_can_take(trunk_max_order)
    # print data
    ga = GA()
    log.info('start to compute')
    ga.GA_main(data, trunk_max_order)
    log.info('ga down.start to get best gene')
    best_gene = ga.selectBest()
    gene_data = best_gene.gene_to_data(ga.order, ga.key_order)
    log.info('start to modify_model')
    modify_model(gene_data)
    all_scheduling[day] = gene_data


def output(day):
    # 统计空车率和搭载率
    trunk_empty = 0
    trunk_sum = 0
    trunk_transport_car = 0
    trunk_sum_transport = 0

    # 统计在途和等计划车辆数
    trunk_on_road_num = 0
    trunk_in_order_destination = 0
    trunk_in_order_base = 0

    for trunk in list_trunk:
        if trunk.trunk_state == TRUNK_ON_ROAD or trunk.trunk_state == TRUNK_ON_ROAD_NOT_USE:
            trunk_sum += 1
            trunk_on_road_num += 1
            if len(trunk.trunk_car_order_list) == 0:
                trunk_empty += 0
            else:
                trunk_sum_transport += trunk.trunk_type
                trunk_transport_car += len(trunk.trunk_car_order_list)
        elif trunk.trunk_state == TRUNK_IN_ORDER:
            trunk_in_order_base += 1
        elif trunk.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            trunk_in_order_destination += 1
    trunk_empty_rate = (trunk_empty * 1.0) / trunk_sum
    trunk_transport_rate = (trunk_transport_car * 1.0) / trunk_sum_transport

    # 统计订单压板分类
    order_delay_low = 0
    order_delay_middle = 0
    order_delay_high = 0

    # 统计平均压板时间
    sum_delay_day = 0

    # 统计每个网点压板订单
    base_sum_delay_order_list = []
    # 统计每个网点可用车辆
    base_trunk_in_station_list = []

    for base in list_base:
        base_sum_delay_order = 0
        for order in base.new_orders:
            base_sum_delay_order += 1
            delay_time = day - order.timestamp
            sum_delay_day += delay_time
            if delay_time <= 5:
                order_delay_low += 1
            elif delay_time <= 10:
                order_delay_middle += 1
            elif delay_time > 10:
                order_delay_high += 1
        base_sum_delay_order_list.append(base_sum_delay_order)
        base.update_in_station_trunk(list_trunk)
        base_trunk_in_station_list.append(len(base.trunk_in_station))
        print("网点%d : 剩余未运订单数 :%d 本网点等计划车数目%d"
              % (base.bid, base_sum_delay_order_list[base.bid], base_trunk_in_station_list[base.bid]))

    average_delay_day = (sum_delay_day * 1.0) / (order_delay_low + order_delay_middle + order_delay_high)

    print("当前空车率%f，当前搭载率%f" % (trunk_empty_rate, trunk_transport_rate))
    print("当前正在运输车辆%d，当前在base等计划车辆%d，当前异地base等计划车辆%d" % (
        trunk_on_road_num, trunk_in_order_base, trunk_in_order_destination,))
    print("当前压板五天以下订单数%d，当前压板五天以上十天以下订单数%d，当前压板十天以上订单数%d" % (order_delay_low, order_delay_middle, order_delay_high))
    print("当前平均压板时间%f" % average_delay_day)


def init():
    from model.base_station import BaseStation
    from model.destination import Destination
    from model.inquiry_info import InquiryInfo

    inquiry_info = InquiryInfo()
    for base_index in range(base_num):
        temp_base = BaseStation(base_index, inquiry_info)
        list_base.append(temp_base)

    for destination_index in range(destination_num):
        temp_destination = Destination(destination_index, inquiry_info)
        list_destination.append(temp_destination)

    for trunk_index in range(trunk_num):
        temp_trunk = Trunk(trunk_index, inquiry_info)
        list_trunk.append(temp_trunk)


if __name__ == "__main__":
    MyLogging()
    log = logging.getLogger('debug')
    default_conf = read_fuc('conf/')
    update_global(default_conf)
    log.info('start to init')
    init()
    log.info('init down.')
    days = 100
    for day in range(days):
        log.info('days: %d ' % day)
        update(day)
        log.info('update down, start to compute')
        compute(day)
        log.info('compute down, start to output')
        output(day)
