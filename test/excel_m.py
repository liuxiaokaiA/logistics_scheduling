import xlwt, xlrd
from xlutils.copy import copy


def read_data(file_name):
    xls = xlrd.open_workbook(file_name)
    sht = xls.sheet_by_index(0)
    rows = 1
    columns = 12
    data = []
    for i in range(40):
        cell = sht.cell(rows, columns).value
        rows += 1
        data.append(cell)
    return data


def write_data(file_name, data):
    xls = xlrd.open_workbook(file_name, formatting_info=True)
    xlsc = copy(xls)
    shtc = xlsc.get_sheet(0)
    rows = 1
    columns = 12
    for item in data:
        shtc.write(rows, columns, str(item))
        rows += 1
    file_ = 'result/'+file_name[-14:]
    print file_
    xlsc.save(file_)


if __name__ == '__main__':
    read_file = 'output/2019-03-10.xls'
    data = read_data(read_file)
    print data
    write_file = 'output/2019-03-10.xls'
    write_data(write_file, data)
