# coding: utf-8
import logging
from model.trunk import Trunk
from log import MyLogging
from read_configure import read_fuc
from algorithm.ga import update_global, GA
from algorithm.model_data import get_trunk_max_order, get_orders_trunk_can_take, modify_model
from global_data import list_base, list_destination, list_trunk, all_scheduling


def update(day):
    pass


def comput(day):
    trunk_max_order = get_trunk_max_order()
    data = get_orders_trunk_can_take(trunk_max_order)
    ga = GA()
    ga.GA_main(data, trunk_max_order)
    best_gene = ga.selectBest()
    gene_data = best_gene.gene_to_data(ga.order, ga.key_order)
    modify_model(gene_data)
    all_scheduling[day] = gene_data


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
        comput(day)
        output(day)
