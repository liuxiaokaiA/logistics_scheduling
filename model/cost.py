# coding: utf-8
import logging, time
from global_data import list_base, list_destination, list_trunk, max_day_stay_base
from data.StatueData import TRUNK_IN_ORDER, TRUNK_ON_ROAD, TRUNK_IN_ORDER_DESTINATION


log = logging.getLogger('default')


VALUE_MAX = 1000000000
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
    order_data = {}
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
        cost_ += trunk.trunk_cost_one_road(car_num, temp_position, base.position)
        temp_position = base.position
        car_num += len(bases[base_id])

    dests = {}
    for order_id in orders:
        order = order_data[order_id]['object']
        if order.destination not in dests:
            dests[order.destination] = []
        dests[order.destination].append(order)
    for order in trunk.trunk_car_order_list:
        if order.destination not in dests:
            dests[order.destination] = []
        dests[order.destination].append(order)

    # 可以优化
    for dest_id in dests:
        dest = list_destination[dest_id]
        cost_ += trunk.trunk_cost_one_road(car_num, temp_position, dest.position)
        temp_position = dest.position
        car_num -= len(dests[dest_id])

    old_dests = {}
    for order in trunk.trunk_car_order_list:
        if order.destination not in old_dests:
            old_dests[order.destination] = []
        old_dests[order.destination].append(order)

    temp_position = trunk.trunk_position
    car_num = len(trunk.trunk_car_order_list)
    for dest_id in old_dests:
        dest = list_destination[dest_id]
        cost_ -= trunk.trunk_cost_one_road(car_num, temp_position, dest.position)
        temp_position = dest.position
        car_num -= len(dests[dest_id])

    return cost_


# 起始点去接单
def get_cost_trunk_in_order(trunk, orders):
    bases = {}
    for order_id in orders:
        order_data[order_id]['is_loading'] += 1
        if order_data[order_id]['is_loading'] > 1:
            print "order_data[order_id]['is_loading'] > 1"
            return VALUE_MAX
        order = order_data[order_id]['object']
        if order.base not in bases:
            bases[order.base] = []
        bases[order.base].append(order)
    cost_ = 0
    car_num = 0
    temp_position = list_base[trunk.trunk_base_id].position
    if trunk.trunk_base_id in bases:
        car_num += len(bases[trunk.trunk_base_id])
    for base_id in bases:
        if base_id == trunk.trunk_base_id:
            continue
        base = list_base[base_id]
        cost_ += trunk.trunk_cost_one_road(car_num, temp_position, base.position)
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
        cost_ += trunk.trunk_cost_one_road(car_num, temp_position, dest.position)
        temp_position = dest.position
        car_num -= len(dests[dest_id])

    return cost_


# 终点去接单
def get_cost_trunk_in_order_dest(trunk, orders):
    cost_ = 0
    trunk_base_id = trunk.trunk_base_id
    trunk_base = list_base[trunk_base_id]
    cost_ += trunk.trunk_cost_one_road(0, trunk.trunk_position, trunk_base.position)
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
        return_cost += trunk.trunk_cost_one_road(car_num, temp_position, base.position)
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
        return_cost += trunk.trunk_cost_one_road(car_num, temp_position, dest.position)
        temp_position = dest.position
        car_num -= len(dests[dest_id])

    # 大于5天停留惩罚成本
    if trunk.wait_day >= max_day_stay_base:
        cost_ += trunk_penalty_cost(0) + 1000
    # 运完回去
    return_cost += trunk.trunk_cost_one_road(0, temp_position, trunk_base.position)
    if return_cost:
        cost_ = return_cost - cost_ + trunk_penalty_cost(float(len(orders))/trunk.trunk_type)
        if trunk.wait_day >= max_day_stay_base:
            cost_ -= trunk_penalty_cost(0) + 1000
    return cost_


def get_order_cost():
    sum_cost = 0
    for order_id in order_data:
        if order_data[order_id]['is_loading'] == 0:
            order = order_data[order_id]['object']
            sum_cost += list_trunk[-1].trunk_cost_one_road(1, list_base[order.base].position,
                                                           list_destination[order.destination].position)
            if order.class_of_delay_time == 2:
                sum_cost += trunk_penalty_cost(0.5)+10
            if order.class_of_delay_time == 3:
                sum_cost += trunk_penalty_cost(0)+10
        elif order_data[order_id]['is_loading'] == 1:
            continue
        else:
            return VALUE_MAX
    return sum_cost


def trunk_penalty_cost(car_num_rate):
    cost = base_penalty - car_num_rate * base_penalty
    return cost


def change_gene(gene_data):
    order_data = {}
    gene_data_ok = {}
    for key in gene_data:
        for order in gene_data[key]:
            if order not in order_data:
                order_data[order] = []
            order_data[order].append(key)
    for order in order_data:
        # print order, order_data[order]
        if order_data[order][0] not in gene_data_ok:
            gene_data_ok[order_data[order][0]] = []
        gene_data_ok[order_data[order][0]].append(order)
    return gene_data_ok


def change_gene_data(gene_data, trunk_data):
    # gene_data = {order_id: trunk_count]}
    # trunk_data[trunk_count] = trunk_id
    if not gene_data:
        return
    gene_data_ = {}
    for order_id in gene_data:
        if gene_data[order_id]:
            trunk_id = trunk_data[gene_data[order_id]]
            if trunk_id not in gene_data_:
                gene_data_[trunk_id] = []
            gene_data_[trunk_id].append(order_id)
    for trunk_count in trunk_data:
        trunk_id = trunk_data[trunk_count]
        trunk = list_trunk[trunk_id]
        if trunk.wait_day >= max_day_stay_base:
            gene_data_[trunk_id] = []
    return gene_data_


def compute_cost(gene, trunk_data):
    get_order_data()
    # trunk: [order]
    gene_data_ = gene.gene_data
    gene_data = change_gene_data(gene_data_, trunk_data)
    sum_cost = 0
    if not gene_data:
        return VALUE_MAX
    gene_data = change_gene(gene_data)
    # print gene_data
    for trunk_id in gene_data:
        trunk = list_trunk[trunk_id]
        # 在途可运车
        if trunk.trunk_state == TRUNK_ON_ROAD:
            # print 'error, can not be here. TRUNK_ON_ROAD'
            sum_cost += get_cost_trunk_on_road(trunk, gene_data[trunk_id])
        # 起始等待车
        elif trunk.trunk_state == TRUNK_IN_ORDER:
            sum_cost += get_cost_trunk_in_order(trunk, gene_data[trunk_id])
        # 终点等待车
        elif trunk.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            # print 'error, can not be here. TRUNK_IN_ORDER_DESTINATION'
            sum_cost += get_cost_trunk_in_order_dest(trunk, gene_data[trunk_id])
        else:
            print 'error, can not be here, other statuse'
            sum_cost += VALUE_MAX

        if sum_cost >= VALUE_MAX:
            # print 'trunk_id', trunk_id, gene_data[trunk_id]
            time.sleep(100)
            gene.value = sum_cost
            return
    sum_cost += get_order_cost()
    if sum_cost >= VALUE_MAX:
        gene.value = sum_cost
        # print 'get_order_cost'
        time.sleep(100)
        return
    # print gene.value
    gene.value = sum_cost
