# coding: utf-8
from global_data import list_base, list_destination, list_trunk
from model.base.utils import is_near
import random


def get_empty_trunks(base, count):
    trunks = []
    types = [6, 7, 8]
    while 1:
        type = random.randint(6, 8)
        if type not in types:
            types.append(type)
        if len(types) == 3:
            break
    while 1:
        type = random.randint(6, 8)
        trunk = base.get_trunk(type)
        if trunk is not None:
            trunks.append(trunk)
            list_base[list_trunk[trunk].trunk_base_id].trunk_in_station.remove(trunk)
        else:
            type1 = None
            while 1:
                type1 = random.randint(6, 8)
                if type1 != type:
                    break
            trunk = base.get_trunk(type1)
            if trunk is not None:
                trunks.append(trunk)
                list_base[list_trunk[trunk].trunk_base_id].trunk_in_station.remove(trunk)
            else:
                type2 = None
                while 1:
                    type2 = random.randint(6, 8)
                    if type2 not in (type, type1):
                        break
                trunk = base.get_trunk(type2)
                if trunk is not None:
                    trunks.append(trunk)
                    list_base[list_trunk[trunk].trunk_base_id].trunk_in_station.remove(trunk)
                else:
                    return trunks
        if len(trunks) == count:
            break
    return trunks


def get_trunk_max_order():
    trunk_max_order = {}
    for base in list_base:
        order_num = len(base.new_orders)
        trunks = get_empty_trunks(base, (order_num/7)+1)
        for trunk_id in trunks:
            trunk = list_trunk[trunk_id]
            if trunk.trunk_state in (2, 4):
                continue
            max_order = trunk.trunk_type
            trunk_max_order[trunk.trunk_id] = max_order

    # 行驶状态先不考虑调度
    # 到达状态可调度
    for trunk in list_trunk:
        # 不在自己本身网点的状态和行驶状态
        if trunk.trunk_state not in (3, 1):
            continue
        max_order = trunk.trunk_type
        if trunk.trunk_id not in trunk_max_order:
            trunk_max_order[trunk.trunk_id] = max_order - len(trunk.trunk_car_order_list)

    return trunk_max_order


def get_orders_list(trunk_max_order, data):
    trunk_data = {}
    order_list = set()
    trunk_count = 1
    for trunk_id in data:
        for i in range(trunk_max_order[trunk_id]):
            trunk_data[trunk_count] = trunk_id
            trunk_count += 1
        for order_id in data[trunk_id]:
            order_list.add(order_id)
    order_list = list(order_list)
    return trunk_data, order_list


def get_orders_trunk_can_take(trunk_max_order):
    data = {}
    order_must_take = []
    # 获取所有大于10天的order
    for base in list_base:
        for order in base.new_orders:
            if order.class_of_delay_time == 3:
                order_must_take.append(order)
    # trunk附近的网点的订单
    for trunk_id in trunk_max_order:
        # print 'trunk_id: %d' % trunk_id
        trunk = list_trunk[trunk_id]
        bases = trunk.near_base_list
        if trunk_id not in data:
            data[trunk_id] = []
        for base_id in bases:
            # print 'base: %d' % base_id
            base = list_base[base_id]
            for order in base.new_orders:
                # print 'order: %d' % order.id
                # 1-5天不着急，顺路才运
                if order.class_of_delay_time == 1:
                    if trunk.trunk_future_base_station_id is None:
                        if order.destination in list_base[trunk.trunk_base_id].near_destination_list:
                            data[trunk_id].append(order.id)
                        continue
                    dest = list_base[trunk.trunk_future_base_station_id]
                    if order.destination in dest.near_destination_list:
                        data[trunk_id].append(order.id)
                # 5-10天，不顺路也运
                elif order.class_of_delay_time == 2:
                    data[trunk_id].append(order.id)
        # 大于10天，1000公里内的运
        for order in order_must_take:
            if is_near(trunk.trunk_position, list_base[order.base].position, 1000):
                data[trunk_id].append(order.id)
    return data


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
    for trunk in list_trunk:
        if trunk.wait_day >= 5:
            if trunk.trunk_id not in gene_data_:
                gene_data_[trunk.trunk_id] = []
    return gene_data_


def modify_model(gene_data_, trunk_data):
    # gene_data = {trunk: [order]}
    # 获取所有的order
    if not gene_data_:
        return
    gene_data = change_gene_data(gene_data_, trunk_data)
    all_order = {}
    for base in list_base:
        for order in base.new_orders:
            all_order[order.id] = order
    for trunk_id in gene_data:
        trunk = list_trunk[trunk_id]
        orders = gene_data[trunk_id]
        for order_id in orders:
            order = all_order[order_id]
            if order in trunk.trunk_car_order_list:
                print('error!order already in trunk')
                return
            # 添加order到trunk
            trunk.add_order(order)
            # 删掉base中的order
            base = list_base[order.base]
            base.new_orders.remove(order)
        # 更新trunk的行程
        position_list = []
        bases = {}
        for order_id in orders:
            order = all_order[order_id]
            if order.base not in bases:
                bases[order.base] = []
            bases[order.base].append(order)
        for base_id in bases:
            base = list_base[base_id]
            position_list.append(base)

        dests = {}
        for order_id in orders:
            order = all_order[order_id]
            if order.destination not in dests:
                dests[order.destination] = []
            dests[order.destination].append(order)
        for order in trunk.trunk_car_order_list:
            if order.destination not in dests:
                dests[order.destination] = []
            dests[order.destination].append(order)
        for dest_id in dests:
            dest = list_destination[dest_id]
            position_list.append(dest)

        if trunk.trunk_current_base_station_id != trunk.trunk_base_id:
            if trunk.wait_day >= 5 and not position_list:
                # print 'empty trunk return.trunk id : ', trunk.trunk_id
                position_list.append(list_base[trunk.trunk_base_id])
            elif trunk.wait_day < 5 and not position_list:
                continue
        trunk.add_target_position_list(position_list)
    return gene_data


def trunk_take_orders(trunk, orders):
    all_order = {}
    for base in list_base:
        for order in base.new_orders:
            all_order[order.id] = order
    for order in orders:
        # 添加order到trunk
        trunk.add_order(order)
        # 删掉base中的order
        base = list_base[order.base]
        # print [od.id for od in base.new_orders], '    ', order.id
        base.new_orders.remove(order)
    # 更新trunk的行程
    bases = {}
    position_list = []
    for order in orders:
        if order.base not in bases:
            bases[order.base] = []
        bases[order.base].append(order)
    for base_id in bases:
        base = list_base[base_id]
        position_list.append(base)

    dests = {}
    for order in orders:
        if order.destination not in dests:
            dests[order.destination] = []
        dests[order.destination].append(order)
    for dest_id in dests:
        dest = list_destination[dest_id]
        position_list.append(dest)

    trunk.add_target_position_list(position_list)


# 从base中选择trunk添加order
def get_trunk_to_work(base, type, all_orders, is_log):
    if is_log:
        print type
    trunk_id = base.get_trunk(type)
    if trunk_id is None:
        if is_log:
            print 'trunk is none. base:', base.b_id
        return False
    trunk = list_trunk[trunk_id]
    list_base[trunk.trunk_base_id].trunk_in_station.remove(trunk.trunk_id)
    if type <= len(all_orders):
        orders = all_orders[:type]
        trunk_take_orders(trunk, orders)
    else:
        trunk_take_orders(trunk, all_orders)
    return True


def get_trunk_from_base(base, orders, is_log=False):
    while 1:
        if len(orders) >= 8:
            if get_trunk_to_work(base, 8, orders, is_log):
                orders = orders[8:]
            elif get_trunk_to_work(base, 7, orders, is_log):
                orders = orders[7:]
            elif get_trunk_to_work(base, 6, orders, is_log):
                orders = orders[6:]
            else:
                break
        elif len(orders) == 7:
            if get_trunk_to_work(base, 7, orders, is_log):
                orders = []
            elif get_trunk_to_work(base, 6, orders, is_log):
                orders = orders[6:]
            elif get_trunk_to_work(base, 8, orders, is_log):
                orders = []
            else:
                break
        elif 4 <= len(orders) <= 6:
            if get_trunk_to_work(base, 6, orders, is_log):
                orders = []
            elif get_trunk_to_work(base, 7, orders, is_log):
                orders = []
            elif get_trunk_to_work(base, 8, orders, is_log):
                orders = []
            else:
                break
        else:
            break
    return orders


def get_whole_trunk():
    # 一个网点的整订单往外派
    print '一个网点的整订单往外派'
    for base in list_base:
        base_order = {}
        for order in base.new_orders:
            if order.destination not in base_order:
                base_order[order.destination] = []
            base_order[order.destination].append(order)
        for destid in base_order:
            get_trunk_from_base(base, base_order[destid])

    # 周围网点，同路线的整订单外派
    print '周围网点，同路线的整订单外派'
    for base in list_base:
        # print 'base: ', base.b_id
        # 附近目的地，订单
        dest_order = {}
        # 附近的所有网点,包含本身
        base_list = base.near_base_list
        if base.b_id not in base_list:
            base_list.append(base.b_id)
        for base_near_id in base_list:
            base_near = list_base[base_near_id]
            for order in base_near.new_orders:
                if order.destination not in dest_order:
                    dest_order[order.destination] = set()
                dest_order[order.destination].add(order)

        for destid in dest_order:
            destination = list_destination[destid]
            # 目的地附近目的地
            dest_list = destination.near_destination_list
            # 本目的地的order
            near_order = dest_order[destid]
            # 再遍历附近目的地
            for dest_near_id in dest_order:
                # 是周围网点，但不是本网点
                if dest_near_id in dest_list and dest_near_id != destid:
                    near_order |= dest_order[dest_near_id]
            # 所有顺路order
            temp = near_order
            # print 'temp: ', [od.id for od in temp]
            for base_near_id in base_list[::-1]:
                base = list_base[base_near_id]
                temp = get_trunk_from_base(base, list(temp), False)
                if len(temp) < 4:
                    break
            temp_id = [order_.id for order_ in temp]
            # print temp_id
            del_order = [order_ for order_ in near_order if order_.id not in temp_id]
            # print 'del_order: ', [od.id for od in del_order]
            for order_ in del_order:
                if order_.destination in dest_order:
                    # print dest_order[order_.destination]
                    # print 'dest_order: ', [od.id for od in dest_order[order_.destination]], order_.id
                    dest_order[order_.destination].remove(order_)
                    # import time
                    # time.sleep(100)
