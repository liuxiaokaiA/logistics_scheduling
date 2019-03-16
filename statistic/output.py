# coding: utf-8
import logging

from data.StatueData import TRUNK_ON_ROAD, TRUNK_ON_ROAD_NOT_USE, TRUNK_IN_ORDER, TRUNK_IN_ORDER_DESTINATION, \
    TRUNK_TYPE_SMALL, TRUNK_TYPE_MIDDLE
from global_data import list_base, list_trunk, max_day_stay_base, base_num, trunk_num
from base.write_excel import Writer
from model.base.utils import model_time_to_date_time
from model.base_station import get_near_trunk, BaseStation
from model.order import All_order
import numpy as np

import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

log = logging.getLogger('default')
history_order_num = 0
today_order_num = 0
empty_num = 0
list_trunk_not_in_base = []
All_statistic = {}
trunk_in_station_num_list = []
trunk_other_in_station_num_list = []
trunk_transport_car_new = 0


def add_history_order_num(num):
    global history_order_num
    history_order_num += num


def set_today_order_num(num):
    global today_order_num
    today_order_num = num


def set_empty_num(num):
    global empty_num
    empty_num = num


def add_trunk_transport_car_new_num(num):
    global trunk_transport_car_new
    trunk_transport_car_new = num


def out_print(day):
    # 统计空车率和搭载率
    trunk_empty = 0
    trunk_sum = 0
    trunk_transport_car = 0
    trunk_sum_transport = 0

    # 统计在途和等计划车辆数
    trunk_on_road_num = 0
    trunk_in_order_destination = 0
    trunk_wait_time = {}
    trunk_in_order_base = 0
    temp_trunk_not_in_base = []
    for trunk in list_trunk:
        if trunk.empty_transport:
            trunk_empty += 1
        if trunk.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            temp_trunk_not_in_base.append(trunk.trunk_id)
        if trunk.trunk_state == TRUNK_ON_ROAD or trunk.trunk_state == TRUNK_ON_ROAD_NOT_USE:
            trunk_sum += 1
            trunk_on_road_num += 1
            if len(trunk.trunk_car_order_list) == 0:
                pass
            else:
                trunk_sum_transport += trunk.trunk_type
                trunk_transport_car += trunk.max_transport
        elif trunk.trunk_state == TRUNK_IN_ORDER:
            trunk_in_order_base += 1
        elif trunk.trunk_state == TRUNK_IN_ORDER_DESTINATION:
            if trunk.wait_day not in trunk_wait_time:
                trunk_wait_time[trunk.wait_day] = 0
            trunk_wait_time[trunk.wait_day] += 1
            trunk_in_order_destination += 1
    num = 0
    global list_trunk_not_in_base
    for id in list_trunk_not_in_base:
        if id not in temp_trunk_not_in_base:
            num += 1
    print ('异地车返回数量%d' % num)
    list_trunk_not_in_base = temp_trunk_not_in_base
    trunk_empty_rate = (trunk_empty * 1.0) / trunk_sum
    # 搭载率
    if trunk_sum_transport != 0:
        # trunk_transport_rate = (trunk_transport_car_new * 1.0) / trunk_sum_transport
        trunk_transport_rate = (trunk_transport_car * 1.0) / trunk_sum_transport
    else:
        trunk_transport_rate = 0
    # 统计订单压板分类
    order_delay_low = 0
    order_delay_middle = 0
    order_delay_high = 0

    # 统计平均压板时间
    sum_delay_day = 0

    # 统计每个网点压板订单
    base_sum_delay_order_list = []
    # 统计每个网点可用车辆
    base_trunk_in_station_list = []

    for base in list_base:
        base_sum_delay_order = 0
        for order in base.new_orders:
            base_sum_delay_order += 1
            # delay_time = day - order.timestamp
            delay_time = order.delay_time
            sum_delay_day += delay_time
            if delay_time <= max_day_stay_base:
                order_delay_low += 1
            elif delay_time <= 10:
                order_delay_middle += 1
            elif delay_time > 10:
                order_delay_high += 1
        base_sum_delay_order_list.append(base_sum_delay_order)
        base.update_in_station_trunk(list_trunk)
        base_trunk_in_station_list.append(len(base.trunk_in_station))
        print("网点%d : 剩余未运订单数 :%d 本网点等计划车数目%d"
              % (base.b_id, base_sum_delay_order_list[base.b_id], base_trunk_in_station_list[base.b_id]))

    average_delay_day = (sum_delay_day * 1.0) / (order_delay_low + order_delay_middle + order_delay_high)
    print("历史订单总数为    ：%d" % history_order_num)
    print("已经运载的订单数  ：%d" % (history_order_num - sum(base_sum_delay_order_list)))
    print("当前空车率%f，当前搭载率%f" % (trunk_empty_rate, trunk_transport_rate))
    print("当前正在运输车辆%d，当前在base等计划车辆%d，当前异地base等计划车辆%d" % (
        trunk_on_road_num, trunk_in_order_base, trunk_in_order_destination,))
    print('异地车辆统计: %s' % str(trunk_wait_time))
    print("当前压板五天以下订单数%d，当前压板五天以上十天以下订单数%d，当前压板十天以上订单数%d" % (order_delay_low, order_delay_middle, order_delay_high))
    print("当前平均压板时间%f" % average_delay_day)
    if day not in All_statistic:
        All_statistic[day] = []
    one_day = [model_time_to_date_time(day, 0)[:10], history_order_num - sum(base_sum_delay_order_list),
               sum(base_sum_delay_order_list),
               history_order_num, order_delay_low, order_delay_middle, order_delay_high, average_delay_day,
               today_order_num, trunk_empty_rate, trunk_transport_rate, trunk_on_road_num, empty_num,
               trunk_in_order_base, trunk_in_order_destination]
    All_statistic[day] = one_day


# 网点      id =  self.b_id
# 地理位置  position = self.position
# 未出发车辆（本地）：trunk_num_1 =len（self.trunk_in_station)（output)
# 未出发车辆（外地）：trunk_num_2 = len（self.trunk_other_in_station)(output)
# 今日发车       ：  trunk_num_3= len（self.trunk_in_station)（update)-len（self.trunk_in_station)（output)
# 今日发车（外地）：  trunk_num_4 = len（self.trunk_other_in_station)（update)-len（self.trunk_other_in_station)（output)
# 未归车辆：trunk_num_5 = trunk_num/base_num - len（self.trunk_in_station)（update)+trunk_num3
# 今日订单数: order_num = self.new_orders_num(output)
# 压板订单 ：delay_order_num = self.new_order[i].class_of_delay_time 1,2,3
# 网点可调度车：dispatch_trunk_num =len（self.trunk_in_station)（output)+ len（self.trunk_other_in_station)(output)
# 周围200公里网点 ：around_base = self.near_destination_list
# 200公里可调度车：trunk_id_list_1 = get_near_trunk（base，trunk_list）
# 500公里可调度车：trunk_id_list_2 = get_near_trunk（base，trunk_list，500）


def write_base(writer, day):
    base_title = [u'网点名称', u'地理位置（建模坐标）', u'未发车辆（本地）', u'未发车辆（外地）', u'今天发车（本地）',
                  u'今天发车（外地）', u'未归车辆（本地）', u'今日订单', u'压板订单（1-5）', u'压板订单（5-10）',
                  u'压板订单（10-?）', u'网点可调度车', u'周边200公里网点', u'周边200公里可调用车数量', u'周边500公里可调度用车数量']
    writer.write_title('base', base_title)
    global trunk_in_station_num_list
    global trunk_other_in_station_num_list
    l = []
    for index, base in enumerate(list_base):
        id = base.b_id
        position = '(' + str(np.around(base.position.x, decimals=1)) + ',' + str(
            np.around(base.position.y, decimals=1)) + ')'
        trunk_num_1 = len(base.trunk_in_station)
        trunk_num_2 = len(base.trunk_other_in_station)
        trunk_num_3 = trunk_in_station_num_list[index] - len(base.trunk_in_station)
        trunk_num_4 = trunk_other_in_station_num_list[index] - len(base.trunk_other_in_station)
        trunk_num_5 = trunk_num / base_num - trunk_in_station_num_list[index] + trunk_num_3
        order_num = base.new_orders_num
        delay_1 = 0
        delay_2 = 0
        delay_3 = 0
        for order in base.new_orders:
            if order.class_of_delay_time == 1:
                delay_1 += 1
            elif order.class_of_delay_time == 2:
                delay_2 += 1
            elif order.class_of_delay_time == 3:
                delay_3 += 1
        dispatch_trunk_num = len(base.trunk_in_station) + len(base.trunk_other_in_station)
        around_base = str(base.near_base_list)
        trunk_id_list_1 = len(get_near_trunk(base, list_trunk))
        trunk_id_list_2 = len(get_near_trunk(base, list_trunk, 500))
        temp_list = [id, position, trunk_num_1, trunk_num_2, trunk_num_3, trunk_num_4, trunk_num_5, order_num, delay_1,
                     delay_2, delay_3, dispatch_trunk_num, around_base, trunk_id_list_1, trunk_id_list_2]
        l.append(temp_list)
        # print temp_list

    writer.write_data('base', l)
    # writer.save()


# 1 板车ID   ： trunk_base_id
# 2 板车类型 ： trunk_type
# 3 归属车队 ： trunk_base_id
# 4 板车状态 ： trunk_state
# 5 当前位置 ： trunk_position
# 6 当前目的地序列：trunk_target_position_list
# 7 到达时间预计：trunk_target_time_list
# 8 订单情况：trunk_car_order_list
# 9 最终入库：trunk_future_base_station_id
# 10 最终入库时间 ：trunk_finish_order_time


def write_trunk(writer, day,inquiry_info):
    trunk_title = [u'板车ID', u'所属车队', u'所属网点', u'板车状态', u'当前位置（建模坐标）',
                   u'目的地编号   ', u'预计到达时间    ', u'订单编号1     ', u'订单编号2     ', u'订单编号3     ',
                   u'订单编号4     ', u'订单编号5     ', u'订单编号6     ', u'订单编号7     ', u'订单编号8     ']
    writer.write_title('trunk', trunk_title)
    l = []
    for index, trunk in enumerate(list_trunk):
        all_list = []
        id = trunk.license
        fleet = trunk.fleet
        trunk_base = inquiry_info.inquiry_index_to_base(trunk.trunk_base_id)
        trunk_state = ''
        position = ''
        target_position = ''
        target_time = ''
        order1 = ''
        order2 = ''
        order3 = ''
        order4 = ''
        order5 = ''
        order6 = ''
        order7 = ''
        order8 = ''
        if trunk.trunk_state in (TRUNK_IN_ORDER_DESTINATION, TRUNK_IN_ORDER):
            if trunk.trunk_state == TRUNK_IN_ORDER:
                trunk_state = u'本地等计划'
            else:
                trunk_state = u'异地等计划'
            position = trunk.current_base_name
            temp_list = [id, fleet, trunk_base, trunk_state, position, target_position, target_time, order1, order2,
                         order3, order4, order5, order6, order7, order8]
            all_list.append(temp_list)
        else:
            if trunk.trunk_target_position_list and isinstance(trunk.trunk_target_position_list, BaseStation):
                trunk_state = u'返回车队'
                position = trunk.current_base_name
                target_position = u'空车回车队'
                target_time = model_time_to_date_time(day, trunk.trunk_target_time_list[0])

                temp_list = [id, fleet, trunk_base, trunk_state, position, target_position, target_time, order1, order2,
                             order3, order4, order5, order6, order7, order8]
                all_list.append(temp_list)
            elif not trunk.trunk_target_position_list:
                trunk_state = u"入库途中"
                position = trunk.current_base_name
                if trunk.trunk_finish_order_time == 0:
                    target_time = ''
                else:
                    target_time = model_time_to_date_time(day, trunk.trunk_finish_order_time)
                if trunk.trunk_finish_order_time == 0:
                    if trunk.trunk_position.get_position_distance(list_base[trunk.trunk_base_id].position) < 0.5:
                        trunk_state = u"本地等计划"
                    else:
                        trunk_state = u"异地等计划"
                else:
                    target_position = u'入库网点 : ' + str(trunk.trunk_future_base_station_id)

                temp_list = [id, fleet, trunk_base, trunk_state, position, target_position, target_time, order1, order2,
                             order3, order4, order5, order6, order7, order8]
                all_list.append(temp_list)
            else:
                for index_position in range(len(trunk.trunk_target_position_list) + 2):
                    if index_position == 0:
                        if trunk.trunk_state == TRUNK_ON_ROAD_NOT_USE:
                            trunk_state = u'运输中(提货)'
                        elif trunk.trunk_state == TRUNK_ON_ROAD and trunk.trunk_car_order_list:
                            trunk_state = u'运输中(交货)'
                        else:
                            trunk_state = u'运输中'
                        position = trunk.current_base_name
                        target_position = ''
                        target_time = ''
                        if len(trunk.trunk_car_order_list) > 0:
                            order1 = trunk.trunk_car_order_list[0].id
                        if len(trunk.trunk_car_order_list) > 1:
                            order2 = trunk.trunk_car_order_list[1].id
                        if len(trunk.trunk_car_order_list) > 2:
                            order3 = trunk.trunk_car_order_list[2].id
                        if len(trunk.trunk_car_order_list) > 3:
                            order4 = trunk.trunk_car_order_list[3].id
                        if len(trunk.trunk_car_order_list) > 4:
                            order5 = trunk.trunk_car_order_list[4].id
                        if len(trunk.trunk_car_order_list) > 5:
                            order6 = trunk.trunk_car_order_list[5].id
                        if len(trunk.trunk_car_order_list) > 6:
                            order7 = trunk.trunk_car_order_list[6].id
                        if len(trunk.trunk_car_order_list) > 7:
                            order8 = trunk.trunk_car_order_list[7].id
                        temp_list = [id, fleet, trunk_base, trunk_state, position, target_position, target_time, order1,
                                     order2, order3, order4, order5, order6, order7, order8]
                        all_list.append(temp_list)
                    if 0 < index_position < len(trunk.trunk_target_position_list) + 1:
                        trunk_base = ''
                        trunk_state = ''
                        position = ''
                        order_list = ['', '', '', '', '', '', '', '']
                        if isinstance(trunk.trunk_target_position_list[index_position - 1], BaseStation):
                            flag = False
                            for order in trunk.trunk_car_order_list:
                                if order.base == trunk.trunk_target_position_list[index_position - 1].b_id:
                                    flag = True
                            if flag:
                                target_position = u'提货网点 : ' + inquiry_info.inquiry_index_to_base(
                                   trunk.trunk_target_position_list[index_position - 1].b_id)
                            else:
                                target_position = u'出发网点 : ' + inquiry_info.inquiry_index_to_base(
                                   trunk.trunk_target_position_list[index_position - 1].b_id)
                            for order_index, order in enumerate(trunk.trunk_car_order_list):
                                if order.base == trunk.trunk_target_position_list[index_position - 1].b_id:
                                    order_list[order_index] = u"装车"
                        else:
                            target_position = u'交货4S店 : ' + inquiry_info.inquiry_index_to_city(
                                trunk.trunk_target_position_list[index_position - 1].d_id)
                            for order_index, order in enumerate(trunk.trunk_car_order_list):
                                if order.destination == trunk.trunk_target_position_list[index_position - 1].d_id:
                                    order_list[order_index] = u"卸载"
                        target_time = model_time_to_date_time(day, trunk.trunk_target_time_list[index_position - 1])
                        temp_list = ['', '', trunk_base, trunk_state, position, target_position, target_time,
                                     order_list[0],
                                     order_list[1], order_list[2], order_list[3], order_list[4], order_list[5],
                                     order_list[6], order_list[7]]
                        all_list.append(temp_list)
                    if index_position == (len(trunk.trunk_target_position_list) + 1):
                        trunk_base = ''
                        trunk_state = ''
                        position = ''
                        target_position = u"入库网点 : " + inquiry_info.inquiry_index_to_base(trunk.trunk_future_base_station_id)
                        target_time = model_time_to_date_time(day, trunk.trunk_finish_order_time)
                        order_list = ['', '', '', '', '', '', '', '']
                        temp_list = ['', '', trunk_base, trunk_state, position, target_position, target_time,
                                     order_list[0],
                                     order_list[1], order_list[2], order_list[3], order_list[4], order_list[5],
                                     order_list[6], order_list[7]]
                        all_list.append(temp_list)

        l += all_list
    writer.write_data('trunk', l)


def write_order(writer, day):
    order_title = [u'订单ID         ', u'发运部编号', u'目的编号',
                   u'压板数量', u'压板天数', u'滞留天数级别', u'运输车ID']
    writer.write_title('order', order_title)
    day_data = []
    for order in All_order:
        order_time = order.id
        order_now = model_time_to_date_time(day, 0)[:10]
        data = [order.id, order.base, order.destination, 1,
                order.delay_time, order.class_of_delay_time]
        if order.trunk_id is None:
            data.append(u'未派单')
        else:
            data.append(order.trunk_id)
        day_data.append(data)
    writer.write_data('order', day_data)


def write_statistic(writer, day):
    statistic_title = [u'日期', u'已运载订单数', u'未运载订单数', u'历史总订单数',
                       u'压板1-5订单数', u'压板5-10订单数', u'压板10天以上订单数',
                       u'平均压板天数', u'当日产生订单', u'空车率',
                       u'搭载率', u'重驶车数量', u'空驶车数量',
                       u'本地等计划车数量', u'异地等计划车数量']
    writer.write_title('statistic', statistic_title)
    day_data = []
    for day_ in All_statistic:
        data = All_statistic[day_]
        day_data.append(data)
        # print data
    writer.write_data('statistic', day_data)


def write_excel(day, inquiry_info):
    writer = Writer(day)
    write_base(writer, day)
    write_trunk(writer, day, inquiry_info)
    write_order(writer, day)
    write_statistic(writer, day)

    writer.save()
