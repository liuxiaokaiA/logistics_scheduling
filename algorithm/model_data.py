# coding: utf-8
from global_data import list_base, list_destination, list_trunk


def get_trunk_max_order():
    trunk_max_order = {}
    for trunk in list_trunk:
        if trunk.trunk_state in (2, 4):
            continue
        max_order = trunk.trunk_type
        exist_order = len(trunk.trunk_car_order_list)
        if exist_order < max_order:
            trunk_max_order[trunk.trunk_id] = max_order - exist_order
    return trunk_max_order


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
                        data[trunk_id].append(order.id)
                        continue
                    dest = list_base[trunk.trunk_future_base_station_id]
                    if order.destination in dest.near_destination_list:
                        data[trunk_id].append(order.id)
                elif order.class_of_delay_time == 2:
                    data[trunk_id].append(order.id)
        for order in order_must_take:
            data[trunk_id].append(order.id)
    return data


def modify_model(gene_data):
    # gene_data = {trunk: [order]}
    # 获取所有的order
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
        for order_id in trunk.trunk_car_order_list:
            order = all_order[order_id]
            if order.destination not in dests:
                dests[order.destination] = []
            dests[order.destination].append(order)
        for dest_id in dests:
            dest = list_destination[dest_id]
            position_list.append(dest)

        trunk.add_target_position_list(position_list)
