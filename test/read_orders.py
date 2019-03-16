# coding: utf-8
import json, xlrd
import pandas as pd
from xlutils.copy import copy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # 须设置为utf8


def set_delay_time(delay_time):
    if delay_time <= 5:
        return 1
    elif 5 < delay_time <= 10:
        return 2
    elif delay_time > 10:
        return 3
    else:
        print('delay_time error!!')
        return 0


def read_data(file_name):
    id_file = 'test.xlsx'
    xls_id = xlrd.open_workbook(id_file)
    sht_id = xls_id.sheet_by_index(0)
    id_ = 0
    data = []
    base_dict = {}
    dest_dict = {}
    for rows in range(305):
        base_name = sht_id.cell(rows, 8).value
        base_dict[base_name] = rows
        dest_name = sht_id.cell(rows, 0).value
        dest_dict[dest_name] = rows
    xls = xlrd.open_workbook(file_name)
    sht = xls.sheet_by_index(0)
    for rows in range(1, 1970):
        base_name = sht.cell(rows, 1).value
        dest_name = sht.cell(rows, 8).value
        delay_time = int(sht.cell(rows, 6).value)
        class_of_delay_time = set_delay_time(delay_time)
        car_num = int(sht.cell(rows, 9).value)
        if base_name not in base_dict:
            print 'base_name ', base_name, 'not in base_dict'
            continue
        if dest_name not in dest_dict:
            print 'dest_name ', dest_name, 'not in dest_dict'
            continue
        for i in range(car_num):
            cell = [id_, base_dict[base_name], dest_dict[dest_name], delay_time, class_of_delay_time]
            data.append(cell)
            id_ += 1

    return data


if __name__ == '__main__':
    read_file = 'orders_.xlsx'
    data = read_data(read_file)
    for item in data:
        id_, base_name, dest_name, delay_time, class_of_delay_time = item
        # print id_, base_name.encode('utf-8'), \
        #     dest_name.encode('utf-8'), delay_time, class_of_delay_time
        print item
    json.dump(data, open('orders.txt', 'w'), indent=2)
