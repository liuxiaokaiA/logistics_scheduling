# coding: utf-8
import xlwt
import logging
import os

from model.base.utils import model_time_to_date_time

log = logging.getLogger('default')


# 获取字符串长度，一个中文的长度为2
def len_byte(value):
    length = len(value)
    utf8_length = len(value.encode('utf-8'))
    return int((utf8_length - length) / 2 + length)


# 确定栏位宽度
def set_width(result, worksheet):
    col_width = []
    for i in range(len(result)):
        col_width.append(len_byte(result[i]))
    # 设置栏位宽度，栏位宽度小于10时候采用默认宽度
    for i in range(len(col_width)):
        if col_width[i] > 10:
            worksheet.col(i).width = 256 * (col_width[i] + 1)


class Writer(object):
    def __init__(self, day):
        self.file_name = 'output/' + str(model_time_to_date_time(day, 0)[0:10]) + '.xls'
        self.whandle = xlwt.Workbook(encoding='utf-8')
        self.rows = {
            'base': 1,
            'trunk': 1,
            'order': 1,
            # 'statistic': 1,
        }
        self.worksheet = {
            'base': self.whandle.add_sheet(u'网点信息'),
            'trunk': self.whandle.add_sheet(u'车辆信息'),
            'order': self.whandle.add_sheet(u'订单信息'),
            # 'statistic': self.whandle.add_sheet(u'指标统计'),
        }

    def write_data(self, name, data):
        if name not in self.worksheet:
            return
        for i in range(len(data)):
            rows = i + self.rows[name]
            for columns in range(len(data[i])):
                self.worksheet[name].write(rows, columns, label=data[i][columns])
        self.rows[name] += len(data)

    def write_title(self, name, title_list):
        if name not in self.worksheet:
            return
        set_width(title_list, self.worksheet[name])
        for columns in range(len(title_list)):
            self.worksheet[name].write(0, columns, label=title_list[columns])

    def save(self):
        if not os.path.exists('output'):
            os.mkdir('output')
        self.whandle.save(self.file_name)


if __name__ == '__main__':
    base_title = [u'网点名称', u'地理位置', u'未发车辆（本地）', u'未发车辆（外地）', u'今天发车（本地）',
                  u'今天发车（外地）', u'未归车辆（本地）', u'今日订单', u'压板订单（1-5）', u'压板订单（5-10）',
                  u'压板订单（10-?）', u'网点可调度车', u'周边200公里网点', u'周边200公里可调用车',
                  u'周边500公里网点', u'周边500公里可调度用车']
    trunk_title = [u'板车ID', u'板车类型', u'归属车队', u'板车状态', u'当前位置',
                   u'目的地编号', u'时间', u'订单1', u'订单2']
    for day in range(10):
        writer = Writer(day)
        writer.write_title('base', base_title)
        writer.write_title('trunk', trunk_title)
        for i in range(5):
            l = []
            for j in range(len(base_title)):
                l.append(i+j)
            writer.write_data('base', [l])
        for i in range(5):
            l = []
            for j in range(len(trunk_title)):
                l.append(i+j)
            writer.write_data('trunk', [l])
        writer.save()
