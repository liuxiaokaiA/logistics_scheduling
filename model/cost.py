# coding: utf-8
import logging
from global_data import list_base, list_destination, list_trunk
from data.StatueData import TRUNK_IN_ORDER, TRUNK_TYPE_BIG, TRUNK_TYPE_MIDDLE, TRUNK_TYPE_SMALL, TRUNK_ON_ROAD, \
    TRUNK_IN_ORDER_DESTINATION, TRUNK_NOT_USE
from model.trunk import get_cost


log = logging.getLogger('default')


VALUE_MAX = 10000000
order_data = {}

'''
order_data = {
    order_id: {
        'is_loading': 0,
        'object': order_object
    }
}
'''


def get_order_data():
    global order_data
    for base in list_base:
        for order in base.new_orders:
            if order.id in order_data:
                continue
            order_data[order.id] = {
                'is_loading': 0,
                'object': order
            }


# 改变路线去接单
def get_cost_trunk_on_road(trunk, orders):
    bases = {}
    for order_id in orders:
        order_data[order_id]['is_loading'] += 1
        if order_data[order_id]['is_loading'] > 1:
            return VALUE_MAX
        order = order_data[order_id]['object']
        if order.base not in bases:
            bases[order.base] = []
        bases[order.base].append(order)
    cost_ = 0
    car_num = len(trunk.trunk_car_order_list)
    temp_position = trunk.trunk_position
    for base_id in bases:
        base = list_base[base_id]
        cost_ += get_cost(car_num, temp_position, base.position)
        temp_position = base.position
        car_num += len(bases[base_id])

    dests = {}
    for order_id in orders:
        order = order_data[order_id]['object']
        if order.destination not in dests:
            dests[order.destination] = []
        dests[order.destination].append(order)
    for order_id in trunk.trunk_car_order_list:
        order = order_data[order_id]['object']
        if order.destination not in dests:
            dests[order.destination] = []
        dests[order.destination].append(order)

    # 可以优化
    for dest_id in dests:
        dest = list_destination[dest_id]
        cost_ += get_cost(car_num, temp_position, dest.position)
        temp_position = dest.position
        car_num -= len(dests[dest_id])

    old_dests = {}
    for order_id in trunk.trunk_car_order_list:
        order = order_data[order_id]['object']
        if order.destination not in old_dests:
            old_dests[order.destination] = []
        old_dests[order.destination].append(order)

    temp_position = trunk.trunk_position
    car_num = len(trunk.trunk_car_order_list)
    for dest_id in old_dests:
        dest = list_destination[dest_id]
        cost_ -= get_cost(car_num, temp_position, dest.position)
        temp_position = dest.position
        car_num -= len(dests[dest_id])

    return cost_


def compute_cost(gene):
    get_order_data()
    # trunk: [order]
    gene_data = gene.gene_data
    sum_cost = 0

    # 起始等待车
    # 终点等待车
    for trunk_id in gene_data:
        trunk = list_trunk[trunk_id]
        # 在途可运车
        if trunk.trunk_state == TRUNK_ON_ROAD:
            sum_cost += get_cost_trunk_on_road(trunk, gene_data[trunk_id])
        elif trunk.trunk_state == TRUNK_IN_ORDER:
            sum_cost += get_cost_trunk_on_road(trunk, gene_data[trunk_id])
        elif trunk.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            sum_cost += get_cost_trunk_on_road(trunk, gene_data[trunk_id])
        else:
            sum_cost += VALUE_MAX