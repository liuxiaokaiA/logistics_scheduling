# coding: utf-8
import logging

from model.inquiry_info import InquiryInfo
from model.trunk import Trunk
from log import MyLogging
from read_configure import read_fuc
from algorithm.ga import update_global, GA
from algorithm.model_data import get_trunk_max_order, get_orders_trunk_can_take, \
    modify_model, get_whole_trunk, get_orders_list
from global_data import list_base, list_destination, list_trunk, all_scheduling, trunk_num, destination_num, \
    base_num, gene_bits
from statistic.output import out_print, add_history_order_num, write_excel, \
    trunk_in_station_num_list, trunk_other_in_station_num_list, set_today_order_num


def update(day):
    log.info('update base')
    new_order_num = 0

    trunk_in_station_num_list[:] = []
    trunk_other_in_station_num_list[:] = []
    for base in list_base:
        base.create_orders(day)
        base.update_in_station_trunk(list_trunk)
        base.update_near_trunk(list_trunk)
        for order in base.new_orders:
            if order.timestamp == day:
                new_order_num += 1
            order.update_order(day)
        trunk_in_station_num_list.append(len(base.trunk_in_station))
        trunk_other_in_station_num_list.append(len(base.trunk_other_in_station))
    add_history_order_num(new_order_num)
    print("今日新产生订单数为 ：%d" % new_order_num)
    set_today_order_num(new_order_num)


def compute():
    get_whole_trunk()
    trunk_max_order = get_trunk_max_order()
    data = get_orders_trunk_can_take(trunk_max_order)
    trunk_data, order_list = get_orders_list(trunk_max_order, data)
    gene_len = 0
    gene_len += len(order_list) * gene_bits
    print 'gene length: ', len(order_list) * gene_bits, len(order_list)

    ga = GA()
    log.info('start to compute')
    # ga.GA_main(data, trunk_max_order)
    ga.GA_main2(trunk_data, order_list)
    log.info('ga down.start to get best gene')
    best_gene = ga.selectBest()
    best_gene.gene_to_data(ga.gene_bits, ga.order_list)
    log.info('start to modify_model')
    modify_model(best_gene.gene_data, trunk_data)


def output(day,inquiry_info):
    out_print(day)
    write_excel(day,inquiry_info)


def init_order():
    import xlrd
    xls = xlrd.open_workbook(file_name)
    sht = xls.sheet_by_index(0)
    id_ = 0
    data = []
    for rows in range(1, 1970):
        base_name = sht.cell(rows, 1).value.encode('utf-8')
        dest_name = sht.cell(rows, 8).value.encode('utf-8')
        delay_time = int(sht.cell(rows, 6).value)
        class_of_delay_time = set_delay_time(delay_time)
        car_num = int(sht.cell(rows, 9).value)
        for i in range(car_num):
            cell = [id_, base_dict[base_name], dest_dict[dest_name], delay_time, class_of_delay_time]
            data.append(cell)
            id_ += 1

    return data


def init(inquiry_info):
    from model.base_station import BaseStation
    from model.destination import Destination

    for base_index in range(base_num):
        temp_base = BaseStation(base_index, inquiry_info)
        list_base.append(temp_base)

    for destination_index in range(destination_num):
        temp_destination = Destination(destination_index, inquiry_info)
        list_destination.append(temp_destination)

    for trunk_index in range(trunk_num):
        temp_trunk = Trunk(trunk_index, inquiry_info)
        list_trunk.append(temp_trunk)
    for base in list_base:
        base.update_in_station_trunk(list_trunk)
        base.update_near_trunk(list_trunk)

    init_order()


if __name__ == "__main__":
    inquiry_info = InquiryInfo()
    MyLogging()
    log = logging.getLogger('debug')
    default_conf = read_fuc('conf/')
    update_global(default_conf)
    log.info('start to init')
    init(inquiry_info)
    log.info('init down.')
    days = 1
    for day in range(days):
        log.info('days: %d ' % day)
        update(day)
        log.info('update down, start to compute')
        compute()
        log.info('compute down, start to output')
        output(day,inquiry_info)
