# coding: utf-8
import xlrd
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # 须设置为utf8


def read_data(file_name):
    xls = xlrd.open_workbook(file_name)
    sht = xls.sheet_by_index(2)
    data = {}
    level_data = {}
    for rows in range(0, 3292):
        dest_name = sht.cell(rows, 6).value
        if dest_name not in data:
            data[dest_name] = {'count': 0, 'level': {}}
        data[dest_name]['count'] += 1
        level = sht.cell(rows, 5).value
        if level not in data[dest_name]['level']:
            data[dest_name]['level'][level] = 0
        data[dest_name]['level'][level] += 1
        if level not in level_data:
            level_data[level] = 0
        level_data[level] += 1
    return data, level_data


def read_trunk(file_name):
    xls = xlrd.open_workbook(file_name)
    sht = xls.sheet_by_index(1)
    data = {}
    orders = {}
    for rows in range(0, 1117):
        dest_name = sht.cell(rows, 3).value
        if dest_name not in data:
            data[dest_name] = 0
        data[dest_name] += 1
        for c in range(7, 15):
            value = sht.cell(rows, c).value
            try:
                int(value)
                continue
            except:
                pass
            if value not in orders:
                orders[value] = 0
            orders[value] += 1
    print data
    return data

if __name__ == '__main__':
    read_file = '2019-02-19.xls'
    data, level_data = read_data(read_file)
    for item in data:
        print item, data[item]
    print level_data
    # read_trunk(read_file)  # 828
    # json.dump(data, open('test.txt', 'w'), indent=2)
