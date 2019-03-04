# coding: utf-8
import logging
from global_data import list_base, list_destination, list_trunk
from data.StatueData import TRUNK_IN_ORDER, TRUNK_ON_ROAD, TRUNK_IN_ORDER_DESTINATION


log = logging.getLogger('default')


VALUE_MAX = 10000000
order_data = {}
base_penalty = 6000

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
        cost_ += trunk.get_cost(car_num, temp_position, base.position)
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
        cost_ += trunk.get_cost(car_num, temp_position, dest.position)
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
        cost_ -= trunk.get_cost(car_num, temp_position, dest.position)
        temp_position = dest.position
        car_num -= len(dests[dest_id])

    return cost_


# 起始点去接单
def get_cost_trunk_in_order(trunk, orders):
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
    car_num = 0
    temp_position = None
    if trunk.trunk_base_id in bases:
        base = list_base[trunk.trunk_base_id]
        car_num += len(bases[trunk.trunk_base_id])
        temp_position = base.position
    for base_id in bases:
        if base_id == trunk.trunk_base_id:
            continue
        base = list_base[base_id]
        cost_ += trunk.get_cost(car_num, temp_position, base.position)
        temp_position = base.position
        car_num += len(bases[base_id])

    dests = {}
    for order_id in orders:
        order = order_data[order_id]['object']
        if order.destination not in dests:
            dests[order.destination] = []
        dests[order.destination].append(order)

    # 可以优化
    for dest_id in dests:
        dest = list_destination[dest_id]
        cost_ += trunk.get_cost(car_num, temp_position, dest.position)
        temp_position = dest.position
        car_num -= len(dests[dest_id])

    return cost_


# 终点去接单
def get_cost_trunk_in_order_dest(trunk, orders):
    cost_ = 0
    trunk_base_id = trunk.trunk_base_id
    trunk_base = list_base[trunk_base_id]
    cost_ += trunk.get_cost(0, trunk.trunk_position, trunk_base.position)
    bases = {}
    for order_id in orders:
        order_data[order_id]['is_loading'] += 1
        if order_data[order_id]['is_loading'] > 1:
            return VALUE_MAX
        order = order_data[order_id]['object']
        if order.base not in bases:
            bases[order.base] = []
        bases[order.base].append(order)
    car_num = 0
    temp_position = trunk.trunk_position
    return_cost = 0
    for base_id in bases:
        base = list_base[base_id]
        if base.position == trunk.trunk_position:
            continue
        return_cost += trunk.get_cost(car_num, temp_position, base.position)
        temp_position = base.position
        car_num += len(bases[base_id])

    dests = {}
    for order_id in orders:
        order = order_data[order_id]['object']
        if order.destination not in dests:
            dests[order.destination] = []
        dests[order.destination].append(order)

    # 可以优化
    for dest_id in dests:
        dest = list_destination[dest_id]
        return_cost += trunk.get_cost(car_num, temp_position, dest.position)
        temp_position = dest.position
        car_num -= len(dests[dest_id])

    # 运完回去
    return_cost += trunk.get_cost(0, temp_position, trunk_base.position)
    if return_cost:
        cost_ = return_cost - cost_ + trunk_penalty_cost(float(len(orders))/trunk.trunk_type)
    else:
        # 大于5天停留惩罚成本
        if trunk.wait_day > 5:
            cost_ += trunk_penalty_cost(0) + 1000
        # 空车惩罚
        else:
            cost_ += trunk_penalty_cost(0)
    return cost_


def get_order_cost():
    sum_cost = 0
    for order_id in order_data:
        if order_data[order_id]['is_loading'] == 0:
            order = order_data[order_id]['object']
            sum_cost += list_trunk[-1].get_cost(1, order.base, order.destination)
            if order.class_of_delay_time == 2:
                sum_cost += trunk_penalty_cost(0.5)+10
            if order.class_of_delay_time == 3:
                sum_cost += trunk_penalty_cost(0.8)+10
        elif order_data[order_id]['is_loading'] == 1:
            continue
        else:
            return VALUE_MAX


def trunk_penalty_cost(car_num_rate):
    cost = base_penalty - car_num_rate * base_penalty
    return cost


def compute_cost(gene):
    get_order_data()
    # trunk: [order]
    gene_data = gene.gene_data
    sum_cost = 0

    for trunk_id in gene_data:
        trunk = list_trunk[trunk_id]
        # 在途可运车
        if trunk.trunk_state == TRUNK_ON_ROAD:
            sum_cost += get_cost_trunk_on_road(trunk, gene_data[trunk_id])
        # 起始等待车
        elif trunk.trunk_state == TRUNK_IN_ORDER:
            sum_cost += get_cost_trunk_in_order(trunk, gene_data[trunk_id])
        # 终点等待车
        elif trunk.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            sum_cost += get_cost_trunk_in_order_dest(trunk, gene_data[trunk_id])
        else:
            sum_cost += VALUE_MAX

        if sum_cost >= VALUE_MAX:
            return sum_cost
    sum_cost += get_order_cost()
    if sum_cost >= VALUE_MAX:
        return sum_cost
    return sum_cost
