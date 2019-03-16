# coding: utf-8
import json, xlrd
from xlutils.copy import copy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # 须设置为utf8


def read_data(file_name):
    xls = xlrd.open_workbook(file_name)
    sht = xls.sheet_by_index(0)

    xlsc = copy(xls)
    shtc = xlsc.get_sheet(0)
    id_ = 0
    data = {}
    for rows in range(0, 305):
        dest_name = sht.cell(rows, 0).value
        data[dest_name] = rows
    for rows in range(0, 305):
        dest_name = sht.cell(rows, 4).value
        if dest_name not in data:
            print dest_name, 1
            continue
        shtc.write(data[dest_name], 12, sht.cell(rows, 5).value)
        shtc.write(data[dest_name], 13, sht.cell(rows, 6).value)
    for rows in range(0, 305):
        dest_name = sht.cell(rows, 1).value[:-1]
        if dest_name not in data:
            print dest_name, 2
            continue
        shtc.write(data[dest_name], 12, sht.cell(rows, 2).value)
        shtc.write(data[dest_name], 13, sht.cell(rows, 3).value)
    xlsc.save('result.xls')
    return data

if __name__ == '__main__':
    read_file = 'test.xlsx'
    data = read_data(read_file)
    for item in data:
        print item
    json.dump(data, open('test.txt', 'w'), indent=2)
