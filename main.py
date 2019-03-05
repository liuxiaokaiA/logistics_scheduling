# coding: utf-8
import logging

from data.StatueData import TRUNK_ON_ROAD, TRUNK_ON_ROAD_NOT_USE
from model.trunk import Trunk
from log import MyLogging
from read_configure import read_fuc
from algorithm.ga import update_global, GA
from algorithm.model_data import get_trunk_max_order, get_orders_trunk_can_take,\
    modify_model, get_whole_trunk
from global_data import list_base, list_destination, list_trunk, all_scheduling,\
    trunk_num, destination_num, base_num


def update(day):
    log.info('update base')
    for base in list_base:
        base.create_orders(day)
        base.update_in_station_trunk(list_trunk)
        base.update_near_trunk(list_trunk)
        for order in base.new_orders:
            order.update_order(day)
    for trunk in list_trunk:
        trunk.trunk_update_day()


def comput(day):
    get_whole_trunk()
    trunk_max_order = get_trunk_max_order()
    data = get_orders_trunk_can_take(trunk_max_order)
    gene_len = 0
    for key in data:
        gene_len += len(data[key])
    print gene_len
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
    trunk_empty = 0
    trunk_sum = 0
    trunk_transport_car = 0
    trunk_sum_transport = 0
    for trunk in list_trunk:
        if trunk.trunk_state == TRUNK_ON_ROAD or trunk.trunk_state == TRUNK_ON_ROAD_NOT_USE:
            trunk_sum += 1
            if len(trunk.trunk_car_order_list) == 0:
                trunk_empty += 0
            else:
                trunk_sum_transport += trunk.trunk_type
                trunk_transport_car += len(trunk.trunk_car_order_list)
    trunk_empty_rate = trunk_empty/trunk_sum
    trunK_transport_rate = trunk_transport_car/trunk_sum_transport
    order_low = 0
    order_middle = 0
    order_high = 0


def init():
    from model.base_station import BaseStation
    from model.destination import Destination
    from model.inquiry_info import InquiryInfo

    inquriry_info = InquiryInfo()
    for base_index in range(base_num):
        temp_base = BaseStation(base_index, inquriry_info)
        list_base.append(temp_base)

    for destination_index in range(destination_num):
        temp_destination = Destination(destination_index, inquriry_info)
        list_destination.append(temp_destination)

    for trunk_index in range(trunk_num):
        temp_trunk = Trunk(trunk_index, inquriry_info)
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
        comput(day)
        log.info('compute down, start to output')
        output(day)
