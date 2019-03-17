# coding: utf-8
from global_data import list_base, list_destination, list_trunk, max_day_stay_base
from model.base.utils import is_near
from statistic.output import set_empty_num
import copy


def get_empty_trunks(base, count):
    trunks = []
    while 1:
        trunk = base.get_trunk(8)
        if trunk is not None:
            trunks.append(trunk)
        else:
            break
        if len(trunks) == count:
            break
    return trunks


def get_trunk_max_order():
    trunk_max_order = {}
    for base in list_base:
        order_num = len(base.new_orders)
        trunks = get_empty_trunks(base, (order_num/8)+1)
        for trunk_id in trunks:
            trunk = list_trunk[trunk_id]
            if trunk.trunk_state in (1, 2, 3, 4):
                continue
            max_order = trunk.trunk_type
            trunk_max_order[trunk.trunk_id] = max_order

    # 行驶状态先不考虑调度
    # 到达状态可调度
    # for trunk in list_trunk:
    #     # 不在自己本身网点的状态和行驶状态
    #     if trunk.trunk_state not in (3, ):
    #         continue
    #     max_order = trunk.trunk_type - len(trunk.trunk_car_order_list)
    #     if max_order and trunk.trunk_id not in trunk_max_order:
    #         trunk_max_order[trunk.trunk_id] = max_order - len(trunk.trunk_car_order_list)
    # print trunk_max_order
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
                if order.class_of_delay_time in (1, 2):
                    if trunk.trunk_future_base_station_id is None:
                        if order.destination in list_base[trunk.trunk_base_id].near_destination_list:
                            data[trunk_id].append(order.id)
                        continue
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
        if trunk.wait_day >= max_day_stay_base:
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
    empty = 0
    print gene_data
    for trunk_id in gene_data:
        print trunk_id, gene_data[trunk_id]
        trunk = list_trunk[trunk_id]
        orders = gene_data[trunk_id]
        is_must = 0
        for order_id in orders:
            order = all_order[order_id]
            if order in trunk.trunk_car_order_list:
                print('error!order already in trunk')
                return
            # 添加order到trunk
            if order.delay_time > 10:
                is_must = 1
            trunk.add_order(order)
            # 删掉base中的order
            base = list_base[order.base]
            base.new_orders.remove(order)
        if len(orders) == 0:
            continue
        if not is_must and len(orders) not in (0, 8):
            print('error!trunk is not full')
            return
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

        if trunk.trunk_state in (0, ):
            if list_base[trunk.trunk_current_base_station_id] not in position_list:
                position_list.insert(0, list_base[trunk.trunk_current_base_station_id])
        if trunk.trunk_state == 0:
            list_base[trunk.trunk_base_id].trunk_in_station.remove(trunk.trunk_id)
        # elif trunk.trunk_state == 3:
        #     pass
            # 一次计算，否则不能注释掉
            # print trunk.trunk_id, trunk.trunk_current_base_station_id
            # list_base[trunk.trunk_current_base_station_id].trunk_other_in_station.remove(trunk.trunk_id)
        print len(position_list)
        trunk.add_target_position_list(position_list)

    print 'empty trunk return.number : ', empty
    set_empty_num(empty)
    # return gene_data


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

    if trunk.trunk_state in (0, 3):
        if list_base[trunk.trunk_current_base_station_id] not in position_list:
            position_list.insert(0, list_base[trunk.trunk_current_base_station_id])

    trunk.add_target_position_list(position_list)


# 从base中选择trunk添加order
def get_trunk_to_work(base, type_, all_orders, is_log):
    if is_log:
        print type_
    trunk_id = base.get_trunk(type_)
    if trunk_id is None:
        if is_log:
            print 'trunk is none. base:', base.b_id
        return False
    trunk = list_trunk[trunk_id]
    list_base[trunk.trunk_base_id].trunk_in_station.remove(trunk.trunk_id)
    if type_ < len(all_orders):
        orders = all_orders[:type_]
        trunk_take_orders(trunk, orders)
    else:
        trunk_take_orders(trunk, all_orders)
    return True


def get_trunk_from_base(base, orders, is_log=False):
    while 1:
        if len(orders) >= 8:
            if get_trunk_to_work(base, 8, orders, is_log):
                orders = orders[8:]
            else:
                break
        else:
            break
    return orders


def get_trunk_return():
    for base in list_base:
        # print 'base: ', base.b_id
        # 附近目的地，订单
        dest_order = {}
        # 附近的所有网点,包含本身
        base_list = copy.deepcopy(base.near_base_list)
        if base.b_id not in base_list:
            base_list.append(base.b_id)
        for base_near_id in base_list:
            base_near = list_base[base_near_id]
            for order in base_near.new_orders:
                if order.destination not in dest_order:
                    dest_order[order.destination] = set()
                dest_order[order.destination].add(order)
        print_dest = {}
        for dest in dest_order:
            print_dest[dest] = [order_.id for order_ in dest_order[dest]]

        other_t = [list_trunk[id_] for id_ in base.trunk_other_in_station]
        return_trunks = [trunk.trunk_id for trunk in sorted(other_t, key=lambda trunk_: trunk_.wait_day, reverse=True)]
        for trunk_id in return_trunks:
            near_order = set()
            trunk = list_trunk[trunk_id]
            trunk_base = list_base[trunk.trunk_base_id]
            # 目的地附近4S
            dest_list = trunk_base.near_destination_list
            # 再遍历附近目的地
            for dest_near_id in dest_order:
                # 周围网点订单
                if dest_near_id in dest_list:
                    near_order |= dest_order[dest_near_id]
            # 所有顺路order
            near_order = sorted(list(near_order), key=lambda _order: _order.delay_time, reverse=True)
            del_order = []
            if trunk.trunk_type <= len(near_order):
                del_order = near_order[:trunk.trunk_type]
            if del_order:
                trunk_take_orders(trunk, del_order)
                base.trunk_other_in_station.remove(trunk.trunk_id)

            for order_ in del_order:
                if order_.destination in dest_order:
                    dest_order[order_.destination].remove(order_)


def get_whole_trunk():
    # 顺路回去的整车
    print '顺路回去的整车'
    get_trunk_return()

    # 一个网点的整订单往外派
    print '一个网点的整订单往外派'
    # for base in list_base:
    #     base_order = {}
    #     for order in base.new_orders:
    #         if order.destination not in base_order:
    #             base_order[order.destination] = []
    #         base_order[order.destination].append(order)
    #     for destid in base_order:
    #         orders = sorted(base_order[destid], key=lambda _order: _order.delay_time, reverse=True)
    #         get_trunk_from_base(base, orders)

    # 周围网点，同路线的整订单外派
    print '周围网点，同路线的整订单外派'
    for base in list_base:
        # print 'base: ', base.b_id
        # 附近目的地，订单
        dest_order = {}
        # 附近的所有网点,包含本身
        base_list = copy.deepcopy(base.near_base_list)
        if base.b_id not in base_list:
            base_list.append(base.b_id)
        for base_near_id in base_list:
            base_near = list_base[base_near_id]
            for order in base_near.new_orders:
                if order.destination not in dest_order:
                    dest_order[order.destination] = set()
                dest_order[order.destination].add(order)

        print_dest = {}
        for dest in dest_order:
            print_dest[dest] = [order_.id for order_ in dest_order[dest]]

        all_near = {}
        all_near_del = {}
        for destid in dest_order:
            all_order = {}
            destination = list_destination[destid]
            # 目的地附近目的地
            dest_list = destination.near_destination_list
            # 本目的地的order
            for order in dest_order[destid]:
                all_order[order.id] = order
            # 再遍历附近目的地
            for dest_near_id in dest_order:
                # 是周围网点，但不是本网点
                if dest_near_id in dest_list and dest_near_id != destid:
                    for order in dest_order[dest_near_id]:
                        all_order[order.id] = order
            # 所有顺路order
            temp = []
            for id_ in all_order:
                temp.append(all_order[id_])
            temp = sorted(temp, key=lambda _order: _order.delay_time, reverse=True)
            all_near[destid] = temp
            # print 'temp: ', [od.id for od in temp]
            for base_near_id in base_list[::-1]:
                base = list_base[base_near_id]
                try:
                    temp = get_trunk_from_base(base, temp, False)
                except Exception as e:
                    temp_dest = {}
                    for dest in dest_order:
                        temp_dest[dest] = [order_.id for order_ in dest_order[dest]]
                    print e
                    print 'dest_order', print_dest
                    print 'temp_dest', temp_dest
                    print 'all_order', list(all_order)
                    print 'temp', [order_.id for order_ in temp]
                    print 'all near', all_near
                    print 'all near del', all_near_del
                    import sys
                    sys.exit()
                if len(temp) < 8:
                    break
            temp_id = [order_.id for order_ in temp]
            # print temp_id
            del_order = [all_order[order_id] for order_id in all_order if order_id not in temp_id]
            all_near_del[destid] = [order_.id for order_ in del_order]
            # print 'del_order: ', [od.id for od in del_order]
            for order_ in del_order:
                if order_.destination in dest_order:
                    # print dest_order[order_.destination]
                    # print 'dest_order: ', [od.id for od in dest_order[order_.destination]], order_.id
                    dest_order[order_.destination].remove(order_)
                    # import time
                    # time.sleep(100)
