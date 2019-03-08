# coding: utf-8
import logging

from data.StatueData import TRUNK_ON_ROAD, TRUNK_ON_ROAD_NOT_USE, TRUNK_IN_ORDER, TRUNK_IN_ORDER_DESTINATION
from global_data import list_base, list_trunk, max_day_stay_base
from base.write_excel import Writer


log = logging.getLogger('default')
history_order_num = 0
list_trunk_not_in_base = []


def add_history_order_num(num):
    global history_order_num
    history_order_num += num


def out_print(day):
    # 统计空车率和搭载率
    trunk_empty = 0
    trunk_sum = 0
    trunk_transport_car = 0
    trunk_sum_transport = 0

    # 统计在途和等计划车辆数
    trunk_on_road_num = 0
    trunk_in_order_destination = 0
    trunk_wait_time = {}
    trunk_in_order_base = 0
    temp_trunk_not_in_base = []
    for trunk in list_trunk:
        if trunk.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            temp_trunk_not_in_base.append(trunk.trunk_id)
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
            if trunk.wait_day not in trunk_wait_time:
                trunk_wait_time[trunk.wait_day] = 0
            trunk_wait_time[trunk.wait_day] += 1
            trunk_in_order_destination += 1
    num = 0
    global list_trunk_not_in_base
    for id in list_trunk_not_in_base:
        if id not in temp_trunk_not_in_base:
            num += 1
    print ('异地车返回数量%d' % num)
    list_trunk_not_in_base = temp_trunk_not_in_base
    trunk_empty_rate = (trunk_empty * 1.0) / trunk_sum
    if trunk_sum_transport != 0:
        trunk_transport_rate = (trunk_transport_car * 1.0) / trunk_sum_transport
    else:
        trunk_transport_rate = 0
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
            if delay_time <= max_day_stay_base:
                order_delay_low += 1
            elif delay_time <= 10:
                order_delay_middle += 1
            elif delay_time > 10:
                order_delay_high += 1
        base_sum_delay_order_list.append(base_sum_delay_order)
        base.update_in_station_trunk(list_trunk)
        base_trunk_in_station_list.append(len(base.trunk_in_station))
        print("网点%d : 剩余未运订单数 :%d 本网点等计划车数目%d"
              % (base.b_id, base_sum_delay_order_list[base.b_id], base_trunk_in_station_list[base.b_id]))

    average_delay_day = (sum_delay_day * 1.0) / (order_delay_low + order_delay_middle + order_delay_high)
    print("历史订单总数为    ：%d" % history_order_num)
    print("已经运载的订单数  ：%d" % (history_order_num - sum(base_sum_delay_order_list)))
    print("当前空车率%f，当前搭载率%f" % (trunk_empty_rate, trunk_transport_rate))
    print("当前正在运输车辆%d，当前在base等计划车辆%d，当前异地base等计划车辆%d" % (
        trunk_on_road_num, trunk_in_order_base, trunk_in_order_destination,))
    print('异地车辆统计: %s' % str(trunk_wait_time))
    print("当前压板五天以下订单数%d，当前压板五天以上十天以下订单数%d，当前压板十天以上订单数%d" % (order_delay_low, order_delay_middle, order_delay_high))
    print("当前平均压板时间%f" % average_delay_day)


def write_base(day):
    pass


def write_trunk(day):
    pass


def write_order(day):
    pass


def write_statistic(day):
    pass


def write_excel(day):
    writer = Writer(day)
    write_base(day)
    write_base(day)
    write_base(day)
    write_base(day)

    writer.save()
